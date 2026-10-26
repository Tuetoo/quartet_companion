"""Optical music recognition (OMR): turn a PDF score into MusicXML.

We use Audiveris, a free open-source OMR program (https://audiveris.github.io).
Install it once:
  * macOS: download the .dmg for your chip from the Audiveris releases page
    on GitHub and drag Audiveris into Applications.
  * Linux: install the .deb package.
Set QC_AUDIVERIS to the program path if it is somewhere else.

OMR is never perfect. `quality_report` lists the measures that look wrong
(their notes do not add up to the time signature, or a part has an odd
range) so you can fix them in MuseScore before analysis.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import pandas as pd

from ..score import Score

CANDIDATES = [
    "/Applications/Audiveris.app/Contents/MacOS/Audiveris",
    str(Path.home() / "Applications/Audiveris.app/Contents/MacOS/Audiveris"),
    "/opt/audiveris/bin/Audiveris",
    "C:/Program Files/Audiveris/Audiveris.exe",
]

# Normal ranges (MIDI) for each instrument, with a little slack.
RANGES = {"Violin 1": (55, 105), "Violin 2": (55, 105), "Violin": (55, 105), "Viola": (48, 93),
          "Cello": (36, 84), "Double bass": (24, 67), "Piano": (21, 108)}


def find_audiveris() -> str | None:
    env = os.environ.get("QC_AUDIVERIS")
    if env and Path(env).exists():
        return env
    for c in CANDIDATES:
        if Path(c).exists():
            return c
    return shutil.which("Audiveris") or shutil.which("audiveris")


MAX_PIXELS = 18_000_000     # Audiveris refuses pages above 20 million pixels
TARGET_DPI = 300


def prepare_pdf(pdf: Path, work_dir: Path, dpi: int = TARGET_DPI) -> Path:
    """Render every page at 300 dpi grayscale into a new PDF.

    Scans on IMSLP are often 600+ dpi; Audiveris refuses pages above 20
    million pixels. 300 dpi is what Audiveris is tuned for.
    Returns the original file if pypdfium2 is not installed.
    """
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return pdf
    doc = pdfium.PdfDocument(str(pdf))
    images = []
    for i in range(len(doc)):
        page = doc[i]
        w_pt, h_pt = page.get_size()
        scale = dpi / 72.0
        if w_pt * h_pt * scale * scale > MAX_PIXELS:
            scale = (MAX_PIXELS / (w_pt * h_pt)) ** 0.5
        img = page.render(scale=scale, grayscale=True).to_pil().convert("L")
        images.append(img)
    work_dir.mkdir(parents=True, exist_ok=True)
    dst = work_dir / f"{pdf.stem}.pdf"
    images[0].save(str(dst), save_all=True, append_images=images[1:], resolution=float(dpi))
    return dst


def run_omr(pdf: str | Path, out_dir: str | Path, timeout_sec: int = 3600) -> list[Path]:
    """Run Audiveris on a PDF/image. Returns the exported .mxl files (one per movement)."""
    exe = find_audiveris()
    if exe is None:
        raise RuntimeError("Audiveris is not installed. See the docstring of quartet_companion.io.omr "
                           "or the README (section 'Optical music recognition').")
    pdf, out_dir = Path(pdf), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if pdf.suffix.lower() == ".pdf":
        pdf = prepare_pdf(pdf, out_dir / "prepared")
    # Read text too (tempo marks such as "Allegro" or "(♩=72)" help to choose repeats).
    # Needs Tesseract language files in Audiveris' "tessdata" folder; without them OMR still works.
    langs = os.environ.get("QC_OCR_LANGS", "eng+ita+deu")
    cmd = [exe, "-batch", "-export", "-option", f"org.audiveris.omr.text.Language.defaultSpecification={langs}",
           "-output", str(out_dir), str(pdf)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    (out_dir / f"{pdf.stem}.audiveris.log").write_text(proc.stdout + "\n" + proc.stderr)
    files = sorted(out_dir.glob(f"{pdf.stem}*.mxl"))
    if not files:
        raise RuntimeError(f"Audiveris produced no MusicXML; see {out_dir / (pdf.stem + '.audiveris.log')}")
    return files


def _expected_qb(timesig: str) -> float | None:
    try:
        num, den = timesig.split("/")
        return float(Fraction(int(num) * 4, int(den)))
    except (ValueError, ZeroDivisionError):
        return None


def quality_report(score: Score) -> dict:
    """Problems a person should check after OMR (or in any hand-made file)."""
    m = score.measures.reset_index(drop=True)
    bad_length = []
    # A printed measure may be split in two around a repeat sign (same number):
    # judge the total length of all parts that share a measure number.
    totals = m.groupby("mn")["dur_qb"].sum().to_dict()
    for i, r in m.iterrows():
        exp = _expected_qb(str(r["timesig"]))
        if exp is None:
            continue
        # a pickup at the start, the last bar, and repeat endings may legally be short
        if i in (0, len(m) - 1) or int(r["volta"]) > 0:
            continue
        found = float(totals.get(r["mn"], r["dur_qb"]))
        if abs(found - exp) > 1e-3 and abs(float(r["dur_qb"]) - exp) > 1e-3:
            bad_length.append({"label": r["label"], "found_beats": round(found, 3), "expected_beats": exp})
    range_issues = []
    for p, name in enumerate(score.parts):
        lo, hi = RANGES.get(name, (0, 127))
        sel = score.notes[score.notes["part"] == p]
        out = sel[(sel["midi"] < lo) | (sel["midi"] > hi)]
        if len(out):
            labels = sorted({score.measure_label(int(mc)) for mc in out["mc"]}, key=lambda x: (len(x), x))
            range_issues.append({"part": name, "n_notes": int(len(out)), "measures": labels[:20]})
    empty = [name for p, name in enumerate(score.parts) if (score.notes["part"] == p).sum() == 0]
    with_notes = set(score.notes["mc"].astype(int))
    empty_measures = [str(r["label"]) for _, r in m.iterrows() if int(r["mc"]) not in with_notes]
    n = len(m)
    share_bad = len(bad_length) / max(1, n - 2)
    verdict = ("good" if share_bad < 0.05 else "usable (alignment will work; check rhythm details)"
               if share_bad < 0.4 else "poor: please correct the file in MuseScore before analysis")
    return {"n_measures": n, "parts": score.parts, "measures_with_wrong_length": bad_length,
            "share_wrong_length": round(share_bad, 3), "notes_out_of_range": range_issues,
            "empty_parts": empty, "empty_measures": empty_measures, "verdict": verdict}


def rename_parts(score: Score, names: list[str]) -> Score:
    """OMR often names parts 'Voice 1', 'Voice 2'... Give them real names."""
    if len(names) != len(score.parts):
        raise ValueError(f"score has {len(score.parts)} parts {score.parts}, got {len(names)} names")
    score.parts = list(names)
    return score


def quality_table(report: dict) -> pd.DataFrame:
    return pd.DataFrame(report["measures_with_wrong_length"])


# ------------------------------------------------------------------ fragments
def _base_name(name: str) -> str:
    """'Piano 2' -> 'Piano', 'Violin 1' stays (it is a real name)."""
    m = re.match(r"^(Piano|Cello|Viola|Double bass)\s+\d+$", name)
    return m.group(1) if m else name


def consolidate_parts(score: Score, targets: list[str]) -> Score:
    """Map the parts OMR found onto the real instruments.

    Audiveris sometimes splits one instrument into several parts ("Voice",
    "Voice", ...) when a system looks different (a new page, a missing staff),
    and a piano comes out as two staves. We merge:
      1. parts whose name matches a target ("Violino." -> Violin, "Piano 1/2" -> Piano);
      2. every other part goes to the target it does not overlap in time with
         (one instrument plays in one place at a time) and whose register is closest.
    """
    import numpy as np
    src_names = [_base_name(n) for n in score.parts]
    notes = score.notes
    info = []
    for i, name in enumerate(src_names):
        sel = notes[notes["part"] == i]
        info.append({"name": name, "mcs": set(sel["mc"].astype(int)),
                     "median": float(np.median(sel["midi"])) if len(sel) else None})
    assign: dict[int, int] = {}
    for i, inf in enumerate(info):
        if inf["name"] in targets:
            assign[i] = targets.index(inf["name"])
    # targets nobody matched by name: take unmatched parts in score order (top to bottom)
    free_targets = [t for t in range(len(targets)) if t not in assign.values()]
    unnamed = [i for i in range(len(info)) if i not in assign and info[i]["mcs"]]
    if free_targets and not assign:
        for t, i in zip(free_targets, sorted(unnamed, key=lambda k: -(info[k]["median"] or 0))):
            assign[i] = t
        unnamed = [i for i in unnamed if i not in assign]

    typical = {"Violin 1": 77, "Violin 2": 72, "Violin": 76, "Viola": 64, "Cello": 52, "Double bass": 40,
               "Piano": 64}

    def target_state(t):
        mcs, med = set(), []
        for i, tt in assign.items():
            if tt == t:
                mcs |= info[i]["mcs"]
                if info[i]["median"] is not None:
                    med.append(info[i]["median"])
        return mcs, (float(np.median(med)) if med else typical.get(targets[t]))

    for i in sorted(unnamed, key=lambda k: -len(info[k]["mcs"])):
        best, best_cost = None, None
        for t in range(len(targets)):
            mcs, med = target_state(t)
            overlap = len(info[i]["mcs"] & mcs) / max(1, len(info[i]["mcs"]))
            reg = abs((info[i]["median"] or 60) - (med if med is not None else 60)) / 12.0
            cost = 5.0 * overlap + reg
            if best_cost is None or cost < best_cost:
                best, best_cost = t, cost
        assign[i] = best
    mapping = {i: assign.get(i, 0) for i in range(len(info))}
    score.notes = notes.assign(part=notes["part"].map(mapping).astype(int))
    if score.events is not None and len(score.events) and "part" in score.events.columns:
        ev = score.events.copy()
        ev["part"] = ev["part"].map(lambda p: mapping.get(int(p), 0) if str(p) not in ("", "nan") else p)
        score.events = ev
    score.parts = list(targets)
    score.meta["part_mapping"] = {targets[t]: [f"{i}: {src_names[i]}" for i, tt in mapping.items() if tt == t]
                                  for t in range(len(targets))}
    return score


def concat_scores(scores: list[Score]) -> Score:
    """Join pieces of one movement that OMR cut in two (same parts, in order)."""
    import dataclasses
    from ..score import make_labels
    first = scores[0]
    meas, notes, events = [first.measures.copy()], [first.notes.copy()], [first.events.copy()]
    mc_off = int(first.measures["mc"].max())
    qb_off = float((first.measures["start_qb"] + first.measures["dur_qb"]).max())
    mn_off = int(first.measures["mn"].max())
    for sc in scores[1:]:
        if sc.parts != first.parts:
            raise ValueError(f"parts differ: {first.parts} vs {sc.parts}")
        first_mc_next = int(sc.measures["mc"].min()) + mc_off
        # the end of the previous piece now continues here
        prev = meas[-1]
        prev["next"] = [[first_mc_next if int(x) == -1 else int(x) for x in nx] for nx in prev["next"]]
        m = sc.measures.copy()
        m["mc"] = m["mc"].astype(int) + mc_off
        m["mn"] = m["mn"].astype(int) + mn_off
        m["start_qb"] = m["start_qb"].astype(float) + qb_off
        m["next"] = [[int(x) + mc_off if int(x) != -1 else -1 for x in nx] for nx in m["next"]]
        n = sc.notes.copy()
        n["mc"] = n["mc"].astype(int) + mc_off
        n["mn"] = n["mn"].astype(int) + mn_off
        n["onset_qb"] = n["onset_qb"].astype(float) + qb_off
        e = sc.events.copy()
        if len(e):
            e["mc"] = e["mc"].astype(int) + mc_off
            e["mn"] = e["mn"].astype(int) + mn_off
            e["onset_qb"] = e["onset_qb"].astype(float) + qb_off
        meas.append(m), notes.append(n), events.append(e)
        mc_off = int(m["mc"].max())
        qb_off = float((m["start_qb"] + m["dur_qb"]).max())
        mn_off = int(m["mn"].max())
    measures = pd.concat(meas, ignore_index=True)
    measures["label"] = make_labels(measures)
    ev = pd.concat([e for e in events if len(e)], ignore_index=True) if any(len(e) for e in events) else first.events
    return dataclasses.replace(first, measures=measures, notes=pd.concat(notes, ignore_index=True), events=ev,
                               harmony=None)
