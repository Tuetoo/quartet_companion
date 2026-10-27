"""Render the score as SVG pages for the web player (with Verovio).

For every page we keep the SVG, and for every measure (mc) the page it is
on and its SVG element id, so the player can highlight the measure that is
playing and turn pages.

Where the notation comes from:
* scores loaded from a file (MusicXML, MuseScore export, OMR result): that file;
* ABC (Beethoven) scores: we write MusicXML from our own note tables with
  music21. It shows the right notes and rhythms, but not every marking of
  the printed edition (slurs, articulation).
"""
from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import pandas as pd

from .score import Score

VEROVIO_OPTIONS = {
    "pageWidth": 2100, "pageHeight": 2970, "pageMarginLeft": 60, "pageMarginRight": 60,
    "pageMarginTop": 40, "pageMarginBottom": 40, "scale": 40, "adjustPageHeight": True,
    "breaks": "auto", "footer": "none", "header": "none", "svgViewBox": True, "svgHtml5": True,
    "mnumInterval": 1, "condense": "none",
}


# ---------------------------------------------------------------- MusicXML
def _q(x: float) -> Fraction:
    return Fraction(x).limit_denominator(96)


def _snap(x: Fraction) -> Fraction:
    """Snap to a grid MusicXML can write: 32nd notes (1/8 beat) or triplet 16ths (1/6 beat)."""
    a = Fraction(round(x * 8), 8)
    b = Fraction(round(x * 6), 6)
    return a if abs(a - x) <= abs(b - x) else b


def score_to_musicxml(score: Score, path: str | Path) -> Path:
    """Write our Score as MusicXML (one measure per mc, voices split when notes overlap)."""
    from music21 import chord, clef, key, meter, note, stream

    measures = score.measures.reset_index(drop=True)
    by = {k: v for k, v in score.notes[~score.notes["grace"]].groupby(["part", "mc"])}
    clefs = {"Violin 1": clef.TrebleClef, "Violin 2": clef.TrebleClef, "Violin": clef.TrebleClef,
             "Viola": clef.AltoClef, "Cello": clef.BassClef, "Double bass": clef.BassClef,
             "Piano": clef.TrebleClef}
    sc = stream.Score()
    for pi, name in enumerate(score.parts):
        part = stream.Part(id=f"P{pi + 1}")
        part.partName = name
        prev_ts, prev_ks = None, None
        for i, m in measures.iterrows():
            mc = int(m["mc"])
            meas = stream.Measure(number=int(m["mn"]))
            if i == 0:
                meas.insert(0, (clefs.get(name, clef.TrebleClef))())
            if m["timesig"] != prev_ts and m["timesig"]:
                try:
                    meas.insert(0, meter.TimeSignature(str(m["timesig"])))
                except Exception:
                    pass
                prev_ts = m["timesig"]
            if int(m["keysig"]) != prev_ks:
                meas.insert(0, key.KeySignature(int(m["keysig"])))
                prev_ks = int(m["keysig"])
            start, dur = _q(m["start_qb"]), _q(m["dur_qb"])
            notes = by.get((pi, mc))
            voices: list[list[tuple[Fraction, Fraction, list[int]]]] = []
            if notes is not None:
                notes = notes.assign(spelled=_spell(notes, int(m["keysig"])))
                # group simultaneous notes with equal length into chords
                groups = notes.groupby([notes["onset_qb"].round(5), notes["dur_qb"].round(5)])["spelled"].apply(list)
                for (on, du), pitches in sorted(groups.items()):
                    o = _snap(_q(on) - start)
                    d = min(max(_snap(_q(du)), Fraction(1, 8)), dur - o)
                    if d <= 0 or o < 0:
                        continue
                    for v in voices:                       # first voice without overlap
                        if v[-1][0] + v[-1][1] <= o:
                            v.append((o, d, pitches))
                            break
                    else:
                        voices.append([(o, d, pitches)])
            if not voices:
                r = note.Rest(quarterLength=float(dur))
                meas.append(r)
            for vi, v in enumerate(voices[:3]):
                container = stream.Voice(id=str(vi + 1)) if len(voices) > 1 else meas
                pos = Fraction(0)
                for o, d, pitches in v:
                    if o > pos:
                        container.append(note.Rest(quarterLength=float(o - pos)))
                    el = note.Note(pitches[0]) if len(pitches) == 1 else chord.Chord(pitches)
                    el.quarterLength = float(d)
                    container.append(el)
                    pos = o + d
                if pos < dur:
                    container.append(note.Rest(quarterLength=float(dur - pos)))
                if container is not meas:
                    meas.insert(0, container)
            if i == 0 and dur < _q(meas.barDuration.quarterLength if meas.timeSignature else 4):
                meas.paddingLeft = float(_q(meas.barDuration.quarterLength) - dur)
            part.append(meas)
        sc.insert(0, part)
    path = Path(path)
    sc.write("musicxml", fp=str(path))
    return path


_SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_FLAT_NAMES = ["C", "D-", "D", "E-", "E", "F", "G-", "G", "A-", "A", "B-", "B"]


def _spell(notes: pd.DataFrame, keysig: int) -> list[str]:
    """Pitch names for drawing: the edition's spelling if we have it, else sharps/flats by key."""
    out = []
    names = notes["name"] if "name" in notes.columns else [""] * len(notes)
    for midi, name in zip(notes["midi"], names):
        if isinstance(name, str) and len(name) >= 2 and name[0] in "ABCDEFG":
            out.append(name.replace("b", "-") if len(name) > 2 else name)
        else:
            table = _FLAT_NAMES if keysig < 0 else _SHARP_NAMES
            out.append(f"{table[int(midi) % 12]}{int(midi) // 12 - 1}")
    return out


def read_musicxml_text(path: str | Path) -> str:
    """Text of a .musicxml/.xml file, or of the main file inside a compressed .mxl."""
    path = Path(path)
    if path.suffix.lower() != ".mxl":
        return path.read_bytes().decode("utf-8", errors="replace")
    import zipfile
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        main = None
        if "META-INF/container.xml" in names:
            m = re.search(r'full-path="([^"]+)"', z.read("META-INF/container.xml").decode("utf-8", "replace"))
            main = m.group(1) if m else None
        if main is None:
            main = next(n for n in names if n.lower().endswith((".xml", ".musicxml")) and not n.startswith("META-INF"))
        return z.read(main).decode("utf-8", errors="replace")


def with_part_names(src: str | Path, names: list[str], dst: str | Path) -> Path:
    """Copy a MusicXML file, replacing part names (OMR calls them 'Voice 1', 'Voice 2'...)."""
    text = read_musicxml_text(src)
    parts = re.findall(r"<score-part\b.*?</score-part>", text, flags=re.S)
    if len(parts) == len(names):
        for block, name in zip(parts, names):
            new = re.sub(r"<part-name\b[^>]*>.*?</part-name>", f"<part-name>{name}</part-name>", block, flags=re.S)
            new = re.sub(r"<part-abbreviation\b[^>]*>.*?</part-abbreviation>", "", new, flags=re.S)
            text = text.replace(block, new, 1)
    Path(dst).write_text(text)
    return Path(dst)


# ------------------------------------------------------------------ render
def render_pages(xml_path: str | Path, out_dir: str | Path, n_measures: int) -> dict:
    """Render in a separate process: Verovio can crash on unusual files, and a
    crash must not take the whole site build down."""
    import os
    import subprocess
    import sys
    env = dict(os.environ)
    pkg_parent = str(Path(__file__).resolve().parents[1])          # make the package importable
    env["PYTHONPATH"] = pkg_parent + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run([sys.executable, "-m", "quartet_companion.score_render", str(xml_path), str(out_dir),
                           str(n_measures)], capture_output=True, text=True, timeout=600, env=env)
    info_path = Path(out_dir) / "score.json"
    if proc.returncode != 0 or not info_path.exists():
        raise RuntimeError(f"Verovio failed (exit {proc.returncode})")
    return json.loads(info_path.read_text())


def _render_pages_inproc(xml_path: str | Path, out_dir: str | Path, n_measures: int) -> dict:
    """Render with Verovio. Returns {"pages": n, "measures": [{"page": p, "id": id, "n": n}, ...]}."""
    import verovio
    tk = verovio.toolkit()
    tk.setOptions(VEROVIO_OPTIONS)
    ok = tk.loadData(read_musicxml_text(xml_path))
    if not ok:
        raise RuntimeError(f"Verovio could not read {xml_path}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = tk.getPageCount()
    for p in range(1, pages + 1):
        (out_dir / f"page-{p}.svg").write_text(tk.renderToSVG(p))
    mei = tk.getMEI()
    # measures in document order (MEI keeps the score order)
    measures = []
    for tag in re.findall(r'<measure\b[^>]*>', mei):
        mid = re.search(r'xml:id="([^"]+)"', tag)
        if not mid:
            continue
        num = re.search(r'\bn="([^"]*)"', tag)
        measures.append({"id": mid.group(1), "n": num.group(1) if num else "",
                         "page": tk.getPageWithElement(mid.group(1))})
    info = {"pages": pages, "measures": measures, "matches_score": len(measures) == n_measures}
    (out_dir / "score.json").write_text(json.dumps(info))
    return info


def measure_map(score: Score, info: dict) -> dict[int, dict]:
    """mc -> {page, id}. Uses order when the counts match, else printed numbers."""
    mcs = list(score.measures["mc"].astype(int))
    rendered = info["measures"]
    if len(rendered) == len(mcs):
        return {mc: {"page": r["page"], "id": r["id"]} for mc, r in zip(mcs, rendered)}
    by_n: dict[str, dict] = {}
    for r in rendered:
        by_n.setdefault(str(r["n"]), r)
    out = {}
    for mc, mn in zip(mcs, score.measures["mn"].astype(int)):
        r = by_n.get(str(mn))
        if r:
            out[mc] = {"page": r["page"], "id": r["id"]}
    return out


if __name__ == "__main__":
    import sys
    _render_pages_inproc(sys.argv[1], sys.argv[2], int(sys.argv[3]))
