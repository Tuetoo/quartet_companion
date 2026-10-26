"""Texture: who plays, how, and who carries the melody.

For every measure and every part we compute simple, explainable numbers
(how many notes start, how much of the measure sounds, how varied the
pitches are, how often the line moves by step...). From those numbers we
pick the "lead" part: the one a listener is most likely to follow.

The lead choice is a heuristic, not a fact. We therefore also return a
confidence value, and a second part when two parts are nearly equal
(a dialogue or a duet).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..score import Score

# Weights of the lead score. Each term is between 0 and 1.
WEIGHTS = {
    "pitch_variety": 0.25,    # a melody uses several different pitches
    "not_repeated": 0.20,     # accompaniment often repeats one note
    "stepwise": 0.15,         # melodies move by step more than by leap
    "rhythm_variety": 0.10,   # melodies mix long and short notes
    "independence": 0.15,     # rhythm differs from the other parts
    "highest": 0.15,          # listeners follow the top voice by default
}
THEME_BONUS = 0.35            # a known theme in this part is a strong cue
SWITCH_PENALTY = 0.12         # the lead does not jump around every measure
CO_LEAD_MARGIN = 0.06         # two parts this close are both "leading"


@dataclass
class PartMeasureFeatures:
    n_onsets: int
    sounding: float
    n_pitches: int
    mean_pitch: float
    repeat_ratio: float
    stepwise_ratio: float
    leap_ratio: float
    rhythm_variety: int
    double_stops: float


def _union_length(intervals: list[tuple[float, float]]) -> float:
    total, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(intervals):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        total += cur_e - cur_s
    return total


def part_measure_features(notes: pd.DataFrame, m_start: float, m_dur: float) -> PartMeasureFeatures:
    """Features of one part in one measure. `notes` holds only that part and measure."""
    real = notes[~notes["grace"]]
    onsets = real[real["is_onset"]]
    if real.empty:
        return PartMeasureFeatures(0, 0.0, 0, float("nan"), 0.0, 0.0, 0.0, 0, 0.0)
    intervals = [(max(o, m_start), min(o + d, m_start + m_dur)) for o, d in zip(real["onset_qb"], real["dur_qb"])]
    sounding = _union_length([iv for iv in intervals if iv[1] > iv[0]]) / m_dur if m_dur > 0 else 0.0
    # Melodic line = highest note at each onset time (double stops count once).
    line = onsets.groupby("onset_qb")["midi"].max().sort_index()
    chord_sizes = onsets.groupby("onset_qb")["midi"].count()
    steps = np.diff(line.values) if len(line) > 1 else np.array([])
    absteps = np.abs(steps)
    n_int = max(len(absteps), 1)
    return PartMeasureFeatures(
        n_onsets=int(len(line)),
        sounding=float(min(sounding, 1.0)),
        n_pitches=int(real["midi"].nunique()),
        mean_pitch=float(real["midi"].mean()),
        repeat_ratio=float((absteps == 0).sum() / n_int) if len(absteps) else 0.0,
        stepwise_ratio=float(((absteps >= 1) & (absteps <= 2)).sum() / n_int) if len(absteps) else 0.0,
        leap_ratio=float((absteps >= 3).sum() / n_int) if len(absteps) else 0.0,
        rhythm_variety=int(onsets["dur_qb"].round(4).nunique()),
        double_stops=float((chord_sizes > 1).mean()) if len(chord_sizes) else 0.0,
    )


def measure_features(score: Score) -> pd.DataFrame:
    """One row per (mc, part) with the features above."""
    rows = []
    measures = score.measures.set_index("mc")
    grouped = {k: v for k, v in score.notes.groupby(["mc", "part"])}
    empty = score.notes.iloc[0:0]
    for mc in measures.index:
        m_start = float(measures.loc[mc, "start_qb"])
        m_dur = float(measures.loc[mc, "dur_qb"])
        for part in range(score.n_parts):
            f = part_measure_features(grouped.get((mc, part), empty), m_start, m_dur)
            rows.append({"mc": int(mc), "part": part, **f.__dict__})
    return pd.DataFrame(rows)


def _onset_sets(score: Score) -> dict[tuple[int, int], set[float]]:
    real = score.notes[score.notes["is_onset"] & ~score.notes["grace"]]
    return {k: set(np.round(v["onset_qb"].values, 4)) for k, v in real.groupby(["mc", "part"])}


def lead_scores(score: Score, features: pd.DataFrame,
                theme_parts: dict[int, set[int]] | None = None) -> pd.DataFrame:
    """Raw lead score per (mc, part) before smoothing."""
    theme_parts = theme_parts or {}
    onset_sets = _onset_sets(score)
    out = features.copy()
    out["score"] = 0.0
    for mc, grp in features.groupby("mc"):
        sounding = grp[grp["n_onsets"] > 0]
        if sounding.empty:
            continue
        top_part = int(sounding.loc[sounding["mean_pitch"].idxmax(), "part"])
        for idx, row in sounding.iterrows():
            part = int(row["part"])
            mine = onset_sets.get((mc, part), set())
            others = set().union(*[onset_sets.get((mc, p), set()) for p in sounding["part"] if p != part]) \
                if len(sounding) > 1 else set()
            independence = (len(mine - others) / len(mine)) if (mine and len(sounding) > 1) else 0.0
            s = (WEIGHTS["pitch_variety"] * min(row["n_pitches"] / 5.0, 1.0)
                 + WEIGHTS["not_repeated"] * (1.0 - row["repeat_ratio"])
                 + WEIGHTS["stepwise"] * row["stepwise_ratio"]
                 + WEIGHTS["rhythm_variety"] * min(row["rhythm_variety"] / 3.0, 1.0)
                 + WEIGHTS["independence"] * independence
                 + WEIGHTS["highest"] * (1.0 if part == top_part else 0.0))
            # Mostly double stops = harmonic support, rarely the tune.
            s -= 0.10 * row["double_stops"]
            if part in theme_parts.get(int(mc), set()):
                s += THEME_BONUS
            out.loc[idx, "score"] = max(s, 0.0)
    return out


def choose_lead(score: Score, scored: pd.DataFrame) -> pd.DataFrame:
    """Pick one lead part per measure with a switch penalty (Viterbi smoothing).

    Returns one row per mc: lead, co_lead (or -1), confidence (0..1).
    """
    mcs = list(score.measures["mc"].astype(int))
    n = score.n_parts
    table = np.zeros((len(mcs), n))
    pos = {mc: i for i, mc in enumerate(mcs)}
    for _, r in scored.iterrows():
        table[pos[int(r["mc"])], int(r["part"])] = r["score"]
    silent = table.sum(axis=1) == 0

    # Viterbi: best path that maximises total score minus switch penalties.
    best = np.zeros_like(table)
    back = np.zeros(table.shape, dtype=int)
    best[0] = table[0]
    for i in range(1, len(mcs)):
        if silent[i]:
            best[i] = best[i - 1]
            back[i] = np.arange(n)
            continue
        for p in range(n):
            cand = best[i - 1] - SWITCH_PENALTY
            cand[p] += SWITCH_PENALTY
            back[i, p] = int(np.argmax(cand))
            best[i, p] = cand[back[i, p]] + table[i, p]
    path = [int(np.argmax(best[-1]))]
    for i in range(len(mcs) - 1, 0, -1):
        path.append(int(back[i, path[-1]]))
    path.reverse()

    rows = []
    for i, mc in enumerate(mcs):
        scores = table[i]
        if silent[i]:
            rows.append({"mc": mc, "lead": -1, "co_lead": -1, "confidence": 0.0})
            continue
        lead = path[i]
        if scores[lead] == 0:          # smoothing kept a silent part: take the raw best
            lead = int(np.argmax(scores))
        order = [p for p in np.argsort(-scores) if p != lead]
        second = order[0] if order else -1
        co = second if (second >= 0 and scores[second] > 0 and scores[lead] - scores[second] <= CO_LEAD_MARGIN) else -1
        margin = scores[lead] - (scores[second] if second >= 0 else 0.0)
        conf = float(np.clip(margin / max(scores[lead], 1e-9) * 2.0, 0.0, 1.0))
        rows.append({"mc": mc, "lead": lead, "co_lead": co, "confidence": round(conf, 2)})
    return pd.DataFrame(rows)


def texture_type(score: Score, features: pd.DataFrame, lead: pd.DataFrame | None = None) -> pd.DataFrame:
    """Simple label per measure.

    tacet (silence), held (no new note, but notes held over still sound), solo,
    unison/octaves, homophonic (everyone moves together),
    melody + accompaniment (one part leads, the others move together),
    duet / trio (two or three independent parts), independent lines (four
    parts each doing something different; may be imitation, but not proven).
    """
    onset_sets = _onset_sets(score)
    held_bars = set(int(m) for m in score.notes["mc"])      # bars where any note sounds (also tied-over notes)
    pcs = {k: tuple((v.sort_values("onset_qb")["midi"] % 12).tolist())
           for k, v in score.notes[score.notes["is_onset"]].groupby(["mc", "part"])}
    lead_by_mc = dict(zip(lead["mc"], lead["lead"])) if lead is not None else {}

    def jaccard(parts: list[int], mc: int) -> float:
        sets = [onset_sets.get((mc, p), set()) for p in parts]
        pairs = [(a, b) for i, a in enumerate(sets) for b in sets[i + 1:]]
        return float(np.mean([len(a & b) / max(len(a | b), 1) for a, b in pairs])) if pairs else 1.0

    rows = []
    for mc, grp in features.groupby("mc"):
        active = [int(p) for p in grp.loc[grp["n_onsets"] > 0, "part"]]
        if not active:
            # no new note starts: notes held over from the bar before, or real silence
            kind = "held" if mc in held_bars else "tacet"
        elif len(active) == 1:
            kind = "solo"
        else:
            shared = jaccard(active, mc)
            same_pcs = len({pcs.get((mc, p)) for p in active}) == 1
            ld = lead_by_mc.get(mc, -1)
            others = [p for p in active if p != ld]
            lead_var = grp.loc[grp["part"] == ld, "n_pitches"].iloc[0] if ld in active else 0
            others_var = grp.loc[grp["part"].isin(others), "n_pitches"].mean() if others else 0
            if same_pcs and shared > 0.9:
                kind = "unison/octaves"
            elif ld in active and lead_var >= 4 and others_var <= 2:
                # one part moves through many pitches, the rest hold or repeat notes
                kind = "melody + accompaniment"
            elif shared >= 0.7:
                kind = "homophonic"
            elif ld in active and len(others) >= 2 and (
                    jaccard(others, mc) >= 0.5
                    or (grp.loc[grp["part"].isin(others), "n_pitches"].mean() <= 3
                        and grp.loc[grp["part"] == ld, "n_pitches"].iloc[0] >= 4)):
                kind = "melody + accompaniment"
            elif ld in active and len(others) == 1 and jaccard([ld] + others, mc) < 0.5 \
                    and grp.loc[grp["part"] == others[0], "n_pitches"].iloc[0] <= 2:
                kind = "melody + accompaniment"
            elif len(active) == 2:
                kind = "duet"
            elif len(active) == 3:
                kind = "trio"
            else:
                kind = "independent lines"
        rows.append({"mc": int(mc), "texture": kind, "active_parts": active})
    return pd.DataFrame(rows)


def analyse_texture(score: Score, theme_parts: dict[int, set[int]] | None = None) -> pd.DataFrame:
    """Full texture table: one row per measure."""
    feats = measure_features(score)
    scored = lead_scores(score, feats, theme_parts)
    lead = choose_lead(score, scored)
    tex = texture_type(score, feats, lead)
    density = feats.groupby("mc").agg(total_onsets=("n_onsets", "sum"),
                                      top_pitch=("mean_pitch", "max")).reset_index()
    out = lead.merge(tex, on="mc").merge(density, on="mc")
    return out
