"""Harmony: keys, modulations and cadences.

Two sources:
* "expert": hand-made Roman-numeral labels (the ABC dataset). Reliable.
* "auto":   estimated by this program for new scores. Less reliable, and
            always marked as such so the guide can say so.

The automatic method is deliberately simple and transparent:
1. Key: Krumhansl-Kessler key profiles compared with the pitch-class
   durations of a sliding window of measures, then smoothed so the key
   does not flicker.
2. Chords: for each half measure, the triad or seventh-chord template
   that covers the most sounding time.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..keys import key_label, tpc_to_name
from ..score import HARMONY_COLUMNS, Score

# Krumhansl-Kessler probe-tone profiles (index 0 = tonic).
KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Preferred spelling of each pitch class as a key tonic (line-of-fifths tpc).
MAJOR_TONIC_TPC = {0: 0, 1: -5, 2: 2, 3: -3, 4: 4, 5: -1, 6: 6, 7: 1, 8: -4, 9: 3, 10: -2, 11: 5}
MINOR_TONIC_TPC = {0: 0, 1: 7, 2: 2, 3: -3, 4: 4, 5: -1, 6: 6, 7: 1, 8: 8, 9: 3, 10: -2, 11: 5}

CADENCE_NAMES = {
    "PAC": "perfect authentic cadence (a strong, final-sounding close)",
    "IAC": "imperfect authentic cadence (a close, but less final)",
    "HC": "half cadence (the music pauses on the dominant, like a comma)",
    "EC": "evaded cadence (a close is expected but avoided)",
    "DC": "deceptive cadence (a surprise chord instead of the expected close)",
    "PC": "plagal cadence ('amen' close)",
}

CHORD_TEMPLATES = {
    "major": [0, 4, 7], "minor": [0, 3, 7], "diminished": [0, 3, 6],
    "dominant seventh": [0, 4, 7, 10], "diminished seventh": [0, 3, 6, 9],
}


# --------------------------------------------------------------- summaries
def key_regions(harmony: pd.DataFrame, score: Score) -> pd.DataFrame:
    """Consecutive runs of the same local key.

    Columns: key_name, start_mc, end_mc, start_label, end_label, n_labels
    """
    if harmony is None or harmony.empty:
        return pd.DataFrame(columns=["key_name", "start_mc", "end_mc", "start_label", "end_label", "n_labels"])
    rows = []
    h = harmony.sort_values("onset_qb").reset_index(drop=True)
    run_start = 0
    for i in range(1, len(h) + 1):
        if i == len(h) or h.loc[i, "key_name"] != h.loc[run_start, "key_name"]:
            start_mc = int(h.loc[run_start, "mc"])
            end_mc = int(h.loc[i - 1, "mc"])
            rows.append({"key_name": h.loc[run_start, "key_name"], "start_mc": start_mc, "end_mc": end_mc,
                         "start_label": score.measure_label(start_mc), "end_label": score.measure_label(end_mc),
                         "n_labels": i - run_start})
            run_start = i
    return pd.DataFrame(rows)


def cadences(harmony: pd.DataFrame, score: Score) -> pd.DataFrame:
    if harmony is None or harmony.empty or "cadence" not in harmony.columns:
        return pd.DataFrame(columns=["mc", "label", "cadence", "meaning", "key_name"])
    c = harmony[harmony["cadence"].astype(str).str.len() > 0]
    rows = []
    for _, r in c.iterrows():
        code = str(r["cadence"]).split(".")[0]
        rows.append({"mc": int(r["mc"]), "label": score.measure_label(int(r["mc"])), "cadence": code,
                     "meaning": CADENCE_NAMES.get(code, code), "key_name": r["key_name"]})
    return pd.DataFrame(rows, columns=["mc", "label", "cadence", "meaning", "key_name"])


def key_by_measure(harmony: pd.DataFrame, score: Score) -> dict[int, str]:
    """Key in force at the start of each measure (carried forward)."""
    out: dict[int, str] = {}
    if harmony is None or harmony.empty:
        return out
    h = harmony.sort_values("onset_qb")
    first = {int(mc): grp["key_name"].iloc[0] for mc, grp in h.groupby("mc", sort=False)}
    current = h["key_name"].iloc[0]
    for mc in score.measures["mc"].astype(int):
        current = first.get(mc, current)
        out[mc] = current
    return out


def chords_by_measure(harmony: pd.DataFrame) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    if harmony is None or harmony.empty:
        return out
    for mc, grp in harmony.sort_values("onset_qb").groupby("mc"):
        out[int(mc)] = [str(c) for c in grp["chord"]]
    return out


# ----------------------------------------------------- automatic estimation
def _pc_durations(notes: pd.DataFrame, start: float, end: float) -> np.ndarray:
    v = np.zeros(12)
    sel = notes[(notes["onset_qb"] < end) & (notes["onset_qb"] + notes["dur_qb"] > start) & ~notes["grace"]]
    for onset, dur, midi in zip(sel["onset_qb"], sel["dur_qb"], sel["midi"]):
        overlap = min(onset + dur, end) - max(onset, start)
        if overlap > 0:
            v[int(midi) % 12] += overlap
    return v


def key_scores(pcd: np.ndarray) -> np.ndarray:
    """24 correlations: 0-11 major keys on C..B, 12-23 minor keys."""
    if pcd.sum() == 0:
        return np.zeros(24)
    out = np.zeros(24)
    for tonic in range(12):
        out[tonic] = np.corrcoef(pcd, np.roll(KK_MAJOR, tonic))[0, 1]
        out[12 + tonic] = np.corrcoef(pcd, np.roll(KK_MINOR, tonic))[0, 1]
    return np.nan_to_num(out)


def key_index_name(idx: int) -> str:
    if idx < 12:
        return key_label(MAJOR_TONIC_TPC[idx], False)
    return key_label(MINOR_TONIC_TPC[idx - 12], True)


def estimate_keys(score: Score, window: int = 4, stay_bonus: float = 0.15) -> tuple[list[str], list[float]]:
    """Key per measure (score order) with Viterbi smoothing. Returns (names, confidences)."""
    m = score.measures.reset_index(drop=True)
    starts = m["start_qb"].astype(float).values
    ends = starts + m["dur_qb"].astype(float).values
    n = len(m)
    scores = np.zeros((n, 24))
    for i in range(n):
        lo, hi = max(0, i - window // 2), min(n, i + window // 2 + 1)
        scores[i] = key_scores(_pc_durations(score.notes, starts[lo], ends[hi - 1]))
    best = scores[0].copy()
    back = np.zeros((n, 24), dtype=int)
    for i in range(1, n):
        new = np.zeros(24)
        for k in range(24):
            cand = best.copy()
            cand[k] += stay_bonus
            back[i, k] = int(np.argmax(cand))
            new[k] = cand[back[i, k]] + scores[i, k]
        best = new
    path = [int(np.argmax(best))]
    for i in range(n - 1, 0, -1):
        path.append(int(back[i, path[-1]]))
    path.reverse()
    conf = []
    for i, k in enumerate(path):
        s = np.sort(scores[i])[::-1]
        conf.append(float(np.clip((scores[i, k] - s[1]) * 5 + 0.5, 0, 1)) if scores[i, k] >= s[1] else 0.3)
    return [key_index_name(k) for k in path], conf


def _best_chord(pcd: np.ndarray) -> tuple[int, str, float]:
    total = pcd.sum()
    if total == 0:
        return -1, "", 0.0
    best = (-1, "", -1.0)
    for root in range(12):
        for name, tmpl in CHORD_TEMPLATES.items():
            pcs = [(root + t) % 12 for t in tmpl]
            covered = pcd[pcs].sum() / total
            # Prefer chords whose root actually sounds, and simpler chords on ties.
            score = covered + 0.05 * (pcd[root] > 0) - 0.02 * (len(tmpl) - 3)
            if score > best[2]:
                best = (root, name, score)
    return best


def auto_harmony(score: Score) -> pd.DataFrame:
    """Estimated keys and chords (two chords per measure at most)."""
    keys, conf = estimate_keys(score)
    rows = []
    m = score.measures.reset_index(drop=True)
    for i, r in m.iterrows():
        start, dur = float(r["start_qb"]), float(r["dur_qb"])
        halves = [(start, start + dur / 2), (start + dur / 2, start + dur)] if dur >= 2 else [(start, start + dur)]
        for (s, e) in halves:
            root, kind, cover = _best_chord(_pc_durations(score.notes, s, e))
            if root < 0:
                continue
            chord = f"{tpc_to_name(MAJOR_TONIC_TPC[root])} {kind}"
            rows.append({"mc": int(r["mc"]), "mn": int(r["mn"]), "onset_qb": s, "dur_qb": e - s,
                         "label": chord, "globalkey": keys[0], "localkey": keys[i], "key_name": keys[i],
                         "chord": chord, "numeral": "", "cadence": "", "source": "auto",
                         "key_confidence": round(conf[i], 2), "chord_fit": round(float(cover), 2)})
    df = pd.DataFrame(rows)
    return df[HARMONY_COLUMNS + ["key_confidence", "chord_fit"]] if not df.empty else df
