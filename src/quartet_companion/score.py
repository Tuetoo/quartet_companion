"""The score model that every other module works with.

A Score is a few plain pandas tables. Every loader (ABC dataset, MusicXML,
MuseScore) produces the same tables, so the analysis, alignment and guide
code never needs to know where a score came from.

Key ideas
---------
* ``mc`` ("measure count") is a unique id for each written measure, in the
  order it appears on the page, starting at 1. Two endings of a repeat are
  two different ``mc`` values.
* ``mn`` ("measure number") is the number a musician sees printed in the
  score. First and second endings share one ``mn``.
* ``label`` is how we show a measure to people: "12", or "79a"/"79b" for
  first/second endings.
* All positions are in quarter-note beats ("qb"), counted from the start of
  the written score (not the performance, which may repeat sections).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

import pandas as pd

NOTE_COLUMNS = ["mc", "mn", "onset_qb", "dur_qb", "part", "midi", "is_onset", "grace"]
MEASURE_COLUMNS = ["mc", "mn", "label", "start_qb", "dur_qb", "timesig", "keysig", "volta", "repeats", "next"]
HARMONY_COLUMNS = ["mc", "mn", "onset_qb", "dur_qb", "label", "globalkey", "localkey", "key_name",
                   "chord", "numeral", "cadence", "source"]
EVENT_COLUMNS = ["mc", "mn", "onset_qb", "part", "kind", "value"]

DEFAULT_QUARTET_PARTS = ["Violin 1", "Violin 2", "Viola", "Cello"]


def to_float(value) -> float:
    """Turn '3/8', '1.5', 2, Fraction(1, 2) or '' into a float (NaN when empty)."""
    if value is None:
        return float("nan")
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, Fraction):
        return float(value)
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return float("nan")
    return float(Fraction(text))


def parse_next(value) -> list[int]:
    """Parse the 'next' column ('2', '79, 80', '-1') into a list of ints."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [int(v) for v in value]
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return []
    return [int(float(v)) for v in text.split(",") if v.strip() != ""]


@dataclass
class Score:
    piece_id: str
    title: str
    parts: list[str]
    measures: pd.DataFrame
    notes: pd.DataFrame
    harmony: pd.DataFrame | None = None
    events: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=EVENT_COLUMNS))
    meta: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ checks
    def validate(self) -> list[str]:
        """Return a list of human-readable problems. Empty list means OK."""
        problems: list[str] = []
        for name, table, cols in [("measures", self.measures, MEASURE_COLUMNS),
                                  ("notes", self.notes, NOTE_COLUMNS)]:
            missing = [c for c in cols if c not in table.columns]
            if missing:
                problems.append(f"{name} table is missing columns {missing}")
        if problems:
            return problems
        if self.measures.empty:
            problems.append("score has no measures")
        if self.notes.empty:
            problems.append("score has no notes")
        if not self.measures["mc"].is_unique:
            problems.append("measure ids (mc) are not unique")
        unknown = set(self.notes["mc"]) - set(self.measures["mc"])
        if unknown:
            problems.append(f"notes refer to unknown measures {sorted(unknown)[:5]}")
        bad_parts = set(self.notes["part"]) - set(range(len(self.parts)))
        if bad_parts:
            problems.append(f"notes refer to unknown parts {sorted(bad_parts)}")
        if (self.notes["midi"] < 0).any() or (self.notes["midi"] > 127).any():
            problems.append("some MIDI pitches are out of range 0-127")
        return problems

    # --------------------------------------------------------------- helpers
    def measure_label(self, mc: int) -> str:
        row = self.measures.loc[self.measures["mc"] == mc]
        return str(row["label"].iloc[0]) if len(row) else str(mc)

    def label_to_mcs(self) -> dict[str, list[int]]:
        """Map a display label to all measure ids that carry it."""
        out: dict[str, list[int]] = {}
        for label, mc in zip(self.measures["label"].astype(str), self.measures["mc"].astype(int)):
            out.setdefault(label, []).append(mc)
        return out

    @property
    def n_parts(self) -> int:
        return len(self.parts)


def make_labels(measures: pd.DataFrame) -> list[str]:
    """Display labels for measures.

    Normally the printed measure number. First/second endings share a
    printed number, so they get 'a', 'b', ... ("79a", "79b"). A measure
    split in two around a repeat sign keeps the same plain number for
    both halves.
    """
    labels: list[str] = []
    voltas = measures["volta"] if "volta" in measures.columns else [0] * len(measures)
    for mn, volta in zip(measures["mn"], voltas):
        volta = int(volta) if str(volta) not in ("", "nan") else 0
        labels.append(f"{mn}{'abcdefgh'[volta - 1]}" if volta > 0 else str(mn))
    return labels


def default_next(measures: pd.DataFrame) -> list[list[int]]:
    """Straight-through 'next' pointers (used when a loader knows no repeats)."""
    mcs = list(measures["mc"])
    return [[mcs[i + 1]] if i + 1 < len(mcs) else [-1] for i in range(len(mcs))]
