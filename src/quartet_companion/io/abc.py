"""Load a movement from the DCML "Annotated Beethoven Corpus" (ABC).

The ABC repository already contains tab-separated tables extracted from
the MuseScore files (folders ``notes/``, ``measures/``, ``harmonies/``,
``chords/``). We read those tables directly, so MuseScore itself is not
needed.

Example
-------
>>> score = load_abc_movement("data/ABC", "n05op18-5_03")
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..keys import dcml_local_key_name
from ..score import (DEFAULT_QUARTET_PARTS, EVENT_COLUMNS, HARMONY_COLUMNS, Score,
                     make_labels, parse_next, to_float)

_TAG_RE = re.compile(r"<[^>]+>")


def _read_tsv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)


def _col(df: pd.DataFrame, *names: str) -> pd.Series:
    """Return the first existing column among `names` (ABC versions differ)."""
    for name in names:
        if name in df.columns:
            return df[name]
    return pd.Series([""] * len(df), index=df.index)


def _qb(df: pd.DataFrame) -> pd.Series:
    """Position in quarter beats, counting every ending (score order)."""
    all_end = _col(df, "quarterbeats_all_endings")
    plain = _col(df, "quarterbeats")
    values = [a if a != "" else p for a, p in zip(all_end, plain)]
    return pd.Series([to_float(v) for v in values], index=df.index)


def clean_text(text: str) -> str:
    return _TAG_RE.sub("", text or "").strip()


def list_pieces(abc_root: str | Path) -> list[str]:
    root = Path(abc_root)
    return sorted(p.name.replace(".notes.tsv", "") for p in (root / "notes").glob("*.notes.tsv"))


def _title_from_id(piece_id: str, metadata: pd.DataFrame | None) -> str:
    m = re.match(r"n(\d+)op(\d+)(?:-(\d+))?_(\d+)", piece_id)
    if not m:
        return piece_id
    number, opus, sub, mvt = m.groups()
    work = f"Op. {opus}" + (f" No. {int(sub)}" if sub else "")
    return f"Beethoven: String Quartet No. {int(number)}, {work}, movement {int(mvt)}"


def load_abc_movement(abc_root: str | Path, piece_id: str) -> Score:
    root = Path(abc_root)
    notes_raw = _read_tsv(root / "notes" / f"{piece_id}.notes.tsv")
    measures_raw = _read_tsv(root / "measures" / f"{piece_id}.measures.tsv")
    harm_path = root / "harmonies" / f"{piece_id}.harmonies.tsv"
    chords_path = root / "chords" / f"{piece_id}.chords.tsv"

    # ---------------------------------------------------------------- measures
    measures = pd.DataFrame({
        "mc": measures_raw["mc"].astype(int),
        "mn": measures_raw["mn"].astype(int),
        "start_qb": _qb(measures_raw),
        "dur_qb": [to_float(v) for v in _col(measures_raw, "duration_qb")],
        "timesig": _col(measures_raw, "timesig"),
        "keysig": [int(v) if v not in ("", None) else 0 for v in _col(measures_raw, "keysig")],
        "volta": [int(float(v)) if v != "" else 0 for v in _col(measures_raw, "volta")],
        "repeats": _col(measures_raw, "repeats"),
        "next": [parse_next(v) for v in _col(measures_raw, "next")],
    })
    measures["label"] = make_labels(measures)

    # ------------------------------------------------------------------- notes
    tied = _col(notes_raw, "tied")
    grace = _col(notes_raw, "gracenote")
    notes = pd.DataFrame({
        "mc": notes_raw["mc"].astype(int),
        "mn": notes_raw["mn"].astype(int),
        "onset_qb": _qb(notes_raw),
        "dur_qb": [to_float(v) for v in _col(notes_raw, "duration_qb")],
        "part": notes_raw["staff"].astype(int) - 1,
        "midi": notes_raw["midi"].astype(int),
        # tied = 0 (middle) or -1 (end) means the note continues an earlier one
        "is_onset": [t not in ("0", "-1") for t in tied],
        "grace": [g != "" for g in grace],
        "name": list(_col(notes_raw, "name")),        # spelled pitch, e.g. "F#5" (for drawing the score)
    })
    notes = notes.sort_values(["onset_qb", "part", "midi"]).reset_index(drop=True)

    # ----------------------------------------------------------------- harmony
    harmony = None
    if harm_path.exists():
        h = _read_tsv(harm_path)
        h = h[_col(h, "chord") != ""].copy()
        harmony = pd.DataFrame({
            "mc": h["mc"].astype(int),
            "mn": h["mn"].astype(int),
            "onset_qb": _qb(h),
            "dur_qb": [to_float(v) for v in _col(h, "duration_qb")],
            "label": _col(h, "label"),
            "globalkey": _col(h, "globalkey"),
            "localkey": _col(h, "localkey"),
            "chord": _col(h, "chord"),
            "numeral": _col(h, "numeral"),
            "cadence": _col(h, "cadence"),
        })
        harmony["key_name"] = [dcml_local_key_name(g, l) for g, l in zip(harmony["globalkey"], harmony["localkey"])]
        harmony["source"] = "expert"
        harmony = harmony[HARMONY_COLUMNS].reset_index(drop=True)

    # ------------------------------------------------------------------ events
    events_rows: list[dict] = []
    if chords_path.exists():
        c = _read_tsv(chords_path)
        qb = _qb(c)
        event = _col(c, "event")
        dyn = _col(c, "dynamics")
        text = _col(c, "staff_text")
        tempo = _col(c, "tempo")
        cresc = _col(c, "crescendo_hairpin")
        decresc = _col(c, "decrescendo_hairpin")
        for i in range(len(c)):
            base = {"mc": int(c["mc"].iloc[i]), "mn": int(c["mn"].iloc[i]),
                    "onset_qb": qb.iloc[i], "part": int(c["staff"].iloc[i]) - 1}
            if event.iloc[i] == "Dynamic" and dyn.iloc[i]:
                events_rows.append({**base, "kind": "dynamic", "value": dyn.iloc[i].strip()})
            elif event.iloc[i] == "StaffText" and text.iloc[i]:
                value = clean_text(text.iloc[i])
                if value in ("cresc.", "dim.", "decresc.", "cresc", "dim"):
                    events_rows.append({**base, "kind": "hairpin", "value": "cresc" if value.startswith("cresc") else "dim"})
                elif value:
                    events_rows.append({**base, "kind": "text", "value": value})
            elif event.iloc[i] == "Tempo":
                value = clean_text(text.iloc[i]) or clean_text(tempo.iloc[i])
                if value:
                    events_rows.append({**base, "kind": "tempo", "value": value})
            elif event.iloc[i] == "Spanner":
                if cresc.iloc[i] != "":
                    events_rows.append({**base, "kind": "hairpin", "value": "cresc"})
                if decresc.iloc[i] != "":
                    events_rows.append({**base, "kind": "hairpin", "value": "dim"})
    events = pd.DataFrame(events_rows, columns=EVENT_COLUMNS)
    if not events.empty:
        events = events.sort_values(["onset_qb", "part"]).reset_index(drop=True)

    metadata = None
    meta_path = root / "metadata.tsv"
    if meta_path.exists():
        metadata = _read_tsv(meta_path)

    score = Score(
        piece_id=piece_id,
        title=_title_from_id(piece_id, metadata),
        parts=list(DEFAULT_QUARTET_PARTS),
        measures=measures[["mc", "mn", "label", "start_qb", "dur_qb", "timesig", "keysig",
                           "volta", "repeats", "next"]],
        notes=notes,
        harmony=harmony,
        events=events,
        meta={"source": "ABC (DCML Annotated Beethoven Corpus), CC BY",
              "composer": "Ludwig van Beethoven", "harmony_source": "expert"},
    )
    if not events.empty:
        # The written tempo word (e.g. "Andante cantabile") is usually a text in
        # the first measure; the metronome mark is a separate "tempo" event.
        first_text = events[(events["kind"] == "text") & (events["mc"] <= 2)]["value"].tolist()
        tempo_marks = events[events["kind"] == "tempo"]["value"].tolist()
        if first_text:
            score.meta["tempo_marking"] = first_text[0]
        elif tempo_marks:
            score.meta["tempo_marking"] = tempo_marks[0]
    return score


def has_nan(series: pd.Series) -> bool:
    return bool(np.isnan(series.astype(float)).any())
