"""Rough expected tempo from the score's written markings.

Some movements switch between slow and fast sections (Adagio ... Allegro).
If we stretch the score evenly over the recording, the slow parts look
"too fast" and the fast parts "too slow", and the aligner struggles. So we
first warp the score with a rough tempo guess taken from metronome marks
or Italian tempo words. Only the *ratios* between sections matter.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from ..score import Score
from ..unfold import PlayingOrder, measure_timeline

# Typical quarter-note speeds. Rough on purpose: only relative changes matter.
TEMPO_WORDS_QPM = [
    ("prestissimo", 200), ("presto", 180), ("vivacissimo", 180), ("vivace", 160), ("allegro assai", 160),
    ("allegro molto", 160), ("allegretto", 115), ("allegro", 140), ("moderato", 105), ("andantino", 95),
    ("andante", 85), ("larghetto", 65), ("adagio", 55), ("lento", 55), ("largo", 48), ("grave", 45),
]
_MM = re.compile(r"(?P<note>[\U0001D15D\U0001D15E\U0001D15F\U0001D160\U0001D161♩♪]?)(?P<dot>\.?)\s*=\s*(?P<num>\d+)")
_NOTE_QB = {"\U0001D15D": 4.0, "\U0001D15E": 2.0, "\U0001D15F": 1.0, "\U0001D160": 0.5, "\U0001D161": 0.25,
            "♩": 1.0, "♪": 0.5, "": 1.0}


# OCR of printed marks such as "(♩=66)": the note often comes out as J/d and "=" as z or ":".
_MM_OCR = re.compile(r"\(\s*[Jjd♩]?\s*[=:zZ]\s*(?P<num>\d{2,3})\s*\)?|(?:^|\s)[Jj♩]\s*[=:zZ]\s*(?P<num2>\d{2,3})")


def parse_tempo(text: str) -> float | None:
    """Text -> quarter notes per minute, or None if no tempo information."""
    t = str(text)
    m = _MM.search(t)
    if not m:
        o = _MM_OCR.search(t)
        if o:
            num = float(o.group("num") or o.group("num2"))
            if 30 <= num <= 240:
                return num
    if m:
        qb = _NOTE_QB.get(m.group("note"), 1.0) * (1.5 if m.group("dot") else 1.0)
        return float(m.group("num")) * qb
    low = t.lower()
    for word, qpm in TEMPO_WORDS_QPM:
        if word in low:
            return float(qpm)
    if "a tempo" in low or "tempo i" in low or "tempo primo" in low:
        return -1.0      # "back to the first tempo"
    return None


def is_metronome(text) -> bool:
    """A number mark such as "♩=72" (also as OCR reads it, e.g. "(Jz72)")."""
    t = str(text)
    return bool(_MM.search(t)) or (parse_tempo(t) is not None and bool(_MM_OCR.search(t)))


def metronome_marks(score: Score) -> dict[int, tuple[float, bool]]:
    """mc -> (qpm, is_number) for every tempo mark (numbers win over words in a measure)."""
    ev = score.events
    marks: dict[int, tuple[float, bool]] = {}
    if ev is None or ev.empty:
        return marks
    for _, r in ev[ev["kind"].isin(["tempo", "text"])].sort_values("onset_qb").iterrows():
        q = parse_tempo(r["value"])
        if q is None:
            continue
        mc, num = int(r["mc"]), is_metronome(r["value"])
        if mc not in marks or (num and not marks[mc][1]):
            marks[mc] = (q, num)
    return marks


def tempo_marking_kind(score: Score, hint_qpm: float | None = None) -> str | None:
    """How well we know the intended speed: "metronome" (a number, or a user hint), "word" (Allegro...), or None."""
    if hint_qpm:
        return "metronome"
    ev = score.events
    if ev is None or ev.empty:
        return None
    values = list(ev[ev["kind"].isin(["tempo", "text"])]["value"])
    if any(is_metronome(v) for v in values):
        return "metronome"
    if any(parse_tempo(v) not in (None, -1.0) for v in values):
        return "word"
    return None


def tempo_by_measure(score: Score, hint_qpm: float | None = None) -> dict[int, float]:
    """Expected qpm for every measure (score order), carried forward.

    hint_qpm: the starting tempo if the score has no marking (e.g. OMR could not read the text).
    """
    ev = score.events
    marks: dict[int, float] = {}
    if ev is not None and not ev.empty:
        for _, r in ev[ev["kind"].isin(["tempo", "text"])].sort_values("onset_qb").iterrows():
            q = parse_tempo(r["value"])
            if q is not None:
                mc = int(r["mc"])
                # a metronome mark beats a word in the same measure
                if mc not in marks or is_metronome(r["value"]):
                    marks[mc] = q
    out: dict[int, float] = {}
    first = next((q for q in marks.values() if q > 0), hint_qpm or 100.0)
    current = first
    for mc in score.measures["mc"].astype(int):
        if mc in marks:
            current = first if marks[mc] < 0 else marks[mc]
        out[mc] = current
    return out


def warp_function(score: Score, order: PlayingOrder,
                  hint_qpm: float | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Breakpoints (perf_qb, expected seconds) for the playing order."""
    tl = measure_timeline(score, order)
    qpm = tempo_by_measure(score, hint_qpm)
    qb_pts = [0.0]
    sec_pts = [0.0]
    for _, r in tl.iterrows():
        dq = float(r["perf_end_qb"] - r["perf_start_qb"])
        qb_pts.append(float(r["perf_end_qb"]))
        sec_pts.append(sec_pts[-1] + dq * 60.0 / qpm[int(r["mc"])])
    return np.array(qb_pts), np.array(sec_pts)


def warp_notes(notes: pd.DataFrame, qb_pts: np.ndarray, sec_pts: np.ndarray) -> pd.DataFrame:
    """Replace perf_qb/dur_qb by expected seconds (columns keep their names for reuse)."""
    n = notes.copy()
    start = np.interp(n["perf_qb"].values, qb_pts, sec_pts)
    end = np.interp((n["perf_qb"] + n["dur_qb"]).values, qb_pts, sec_pts)
    n["perf_qb"] = start
    n["dur_qb"] = end - start
    return n
