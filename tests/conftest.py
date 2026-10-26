"""Shared test fixtures.

Small hand-made scores live here, so tests run fast and do not need the
datasets. Tests that need the ABC dataset are skipped when it is missing.
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest

from quartet_companion.score import Score, default_next, make_labels

ROOT = Path(__file__).resolve().parents[1]
ABC_DIR = Path(os.environ.get("QC_ABC_DIR", ROOT / "data" / "ABC"))


def make_score(note_rows, n_measures, beats_per_measure=4.0, parts=None, next_=None, volta=None,
               events=None, repeats=None):
    """note_rows: list of (measure_index_from_1, beat_in_measure, dur, part, midi)."""
    parts = parts or ["Violin 1", "Violin 2", "Viola", "Cello"]
    measures = pd.DataFrame({
        "mc": list(range(1, n_measures + 1)),
        "mn": list(range(1, n_measures + 1)),
        "start_qb": [i * beats_per_measure for i in range(n_measures)],
        "dur_qb": [beats_per_measure] * n_measures,
        "timesig": ["4/4"] * n_measures,
        "keysig": [0] * n_measures,
        "volta": volta or [0] * n_measures,
        "repeats": repeats or [""] * n_measures,
    })
    measures["next"] = next_ or default_next(measures)
    measures["label"] = make_labels(measures)
    notes = pd.DataFrame([{
        "mc": m, "mn": m, "onset_qb": (m - 1) * beats_per_measure + b, "dur_qb": d, "part": p,
        "midi": midi, "is_onset": True, "grace": False} for (m, b, d, p, midi) in note_rows])
    ev = pd.DataFrame(events or [], columns=["mc", "mn", "onset_qb", "part", "kind", "value"])
    return Score("test", "Test piece", parts, measures[["mc", "mn", "label", "start_qb", "dur_qb", "timesig",
                                                        "keysig", "volta", "repeats", "next"]], notes,
                 None, ev, {"composer": "Test"})


@pytest.fixture
def melody_in_viola_score():
    """4 measures: the viola has a moving tune, the others repeat one note in quarters."""
    tune = [62, 64, 66, 67, 69, 67, 66, 64, 62, 66, 69, 74, 72, 71, 69, 67]
    rows = []
    for i, midi in enumerate(tune):
        m, b = i // 4 + 1, (i % 4) * 1.0
        rows.append((m, b, 1.0, 2, midi))           # viola tune
    for m in range(1, 5):
        for b in range(4):
            rows.append((m, b, 1.0, 0, 74))         # violin 1 repeats D5 (higher!)
            rows.append((m, b, 1.0, 1, 69))
            rows.append((m, b, 1.0, 3, 50))
    return make_score(rows, 4)


@pytest.fixture(scope="session")
def abc_dir():
    if not (ABC_DIR / "notes").exists():
        pytest.skip("ABC dataset not found (set QC_ABC_DIR)")
    return ABC_DIR
