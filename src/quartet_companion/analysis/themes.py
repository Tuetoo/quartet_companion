"""Find where a theme comes back, in which part, and in what form.

A theme is stored as a list of melodic intervals (in semitones) plus the
rhythm (time between note starts). Comparing intervals instead of pitches
means we also find the theme when it is transposed to another key.

Match types
-----------
* exact      - same intervals (any transposition)
* tonal      - each interval differs by at most 1 semitone (the same tune
               moved inside a key, e.g. major third becomes minor third)
* inverted   - the tune turned upside down (intervals negated)
Rhythm similarity is reported separately (1.0 = same rhythm, also when the
whole theme is played twice as fast or slow).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..score import Score

DEFAULT_THEME_NOTES = 8


@dataclass
class Theme:
    name: str
    part: int
    start_mc: int
    intervals: list[int]
    iois: list[float]               # inter-onset intervals, length = len(intervals)
    pitches: list[int] = field(default_factory=list)


@dataclass
class ThemeMatch:
    theme: str
    part: int
    start_mc: int
    end_mc: int
    onset_qb: float
    kind: str                       # exact | tonal | inverted | original
    transposition: int              # semitones relative to the original
    rhythm_similarity: float


def melodic_line(score: Score, part: int) -> pd.DataFrame:
    """Top note at each onset of one part: columns onset_qb, mc, midi, ioi."""
    n = score.notes
    n = n[(n["part"] == part) & n["is_onset"] & ~n["grace"]]
    if n.empty:
        return pd.DataFrame(columns=["onset_qb", "mc", "midi", "ioi"])
    line = n.sort_values("onset_qb").groupby("onset_qb").agg(mc=("mc", "first"), midi=("midi", "max")).reset_index()
    line["ioi"] = line["onset_qb"].shift(-1) - line["onset_qb"]
    return line


def _rhythm_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Share of positions where the rhythms agree, allowing one global scale factor."""
    if len(a) == 0 or np.any(a <= 0) or np.any(b <= 0):
        return 0.0
    ratios = b / a
    scale = float(np.median(ratios))
    if scale <= 0:
        return 0.0
    return float(np.mean(np.isclose(b, a * scale, rtol=0.05)))


def extract_theme(score: Score, part: int, start_mc: int, n_notes: int = DEFAULT_THEME_NOTES,
                  name: str = "main theme", end_mc: int | None = None) -> Theme | None:
    line = melodic_line(score, part)
    line = line[line["mc"] >= start_mc]
    if end_mc is not None:
        line = line[line["mc"] <= end_mc]
    line = line.head(n_notes + 1 if end_mc is None else len(line))
    if len(line) < 4:
        return None
    pitches = line["midi"].astype(int).tolist()
    intervals = np.diff(pitches).astype(int).tolist()
    iois = line["onset_qb"].diff().dropna().astype(float).tolist()
    return Theme(name=name, part=part, start_mc=int(line["mc"].iloc[0]), intervals=intervals,
                 iois=iois, pitches=pitches)


def is_distinctive(theme: Theme) -> bool:
    """Reject themes that are just repeated notes or scales of one step."""
    return len(set(theme.pitches)) >= 3 and sum(1 for i in theme.intervals if i != 0) >= 3


def auto_main_theme(score: Score, lead_table: pd.DataFrame | None = None,
                    n_notes: int = DEFAULT_THEME_NOTES) -> Theme | None:
    """Take the opening melody: the first part that plays a distinctive line."""
    first_mc = int(score.measures["mc"].iloc[0])
    candidates: list[int] = []
    if lead_table is not None and not lead_table.empty:
        opening = lead_table[lead_table["lead"] >= 0].head(4)
        if not opening.empty:
            candidates.append(int(opening["lead"].mode().iloc[0]))
    candidates += [p for p in range(score.n_parts) if p not in candidates]
    for part in candidates:
        line = melodic_line(score, part)
        if line.empty:
            continue
        start = int(line["mc"].iloc[0])
        if start > first_mc + 4:
            continue
        theme = extract_theme(score, part, start, n_notes)
        if theme and is_distinctive(theme):
            return theme
    return None


def find_matches(score: Score, theme: Theme, min_rhythm: float = 0.5) -> list[ThemeMatch]:
    k = len(theme.intervals)
    t_int = np.array(theme.intervals)
    t_ioi = np.array(theme.iois)
    matches: list[ThemeMatch] = []
    for part in range(score.n_parts):
        line = melodic_line(score, part)
        if len(line) < k + 1:
            continue
        pitches = line["midi"].astype(int).values
        onsets = line["onset_qb"].astype(float).values
        mcs = line["mc"].astype(int).values
        ints = np.diff(pitches)
        iois = np.diff(onsets)
        i = 0
        while i + k <= len(ints):
            w_int = ints[i:i + k]
            w_ioi = iois[i:i + k]
            kind = None
            if np.array_equal(w_int, t_int):
                kind = "exact"
            elif np.all(np.abs(w_int - t_int) <= 1) and np.all(np.sign(w_int) == np.sign(t_int)) \
                    and np.mean(w_int == t_int) >= 0.6:
                kind = "tonal"
            elif np.all(np.abs(w_int + t_int) <= 1) and np.all(np.sign(w_int) == -np.sign(t_int)) \
                    and np.count_nonzero(t_int) >= 3:
                kind = "inverted"
            if kind:
                rhythm = _rhythm_similarity(t_ioi, w_ioi)
                if kind == "exact" or rhythm >= min_rhythm:
                    is_original = part == theme.part and int(mcs[i]) == theme.start_mc
                    matches.append(ThemeMatch(
                        theme=theme.name, part=part, start_mc=int(mcs[i]), end_mc=int(mcs[i + k]),
                        onset_qb=float(onsets[i]), kind="original" if is_original else kind,
                        transposition=int(pitches[i] - theme.pitches[0]),
                        rhythm_similarity=round(rhythm, 2)))
                    i += k            # do not report overlapping copies
                    continue
            i += 1
    matches.sort(key=lambda m: (m.onset_qb, m.part))
    return matches


def matches_table(matches: list[ThemeMatch]) -> pd.DataFrame:
    return pd.DataFrame([m.__dict__ for m in matches],
                        columns=["theme", "part", "start_mc", "end_mc", "onset_qb", "kind",
                                 "transposition", "rhythm_similarity"])


def theme_parts_by_measure(matches: list[ThemeMatch]) -> dict[int, set[int]]:
    """For the lead-voice bonus: which parts carry a theme in which measures."""
    out: dict[int, set[int]] = {}
    for m in matches:
        for mc in range(m.start_mc, m.end_mc + 1):
            out.setdefault(mc, set()).add(m.part)
    return out
