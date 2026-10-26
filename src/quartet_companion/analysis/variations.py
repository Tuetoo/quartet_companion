"""Compare each variation with its theme.

Two questions a listener asks in a set of variations:
1. "Is the theme still there, and who plays it now?"
   We sample the theme's tune at its main notes and check, for each part
   of the variation, whether that pitch is sounding at the same moment.
2. "How is this variation different?"
   We compare harmony (same chords at the same place?), rhythmic density
   (more or fewer notes?), loudness and key.

This also works for a passacaglia / chaconne: there the "variations" are
equal-length repetitions of the bass and harmony pattern.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..score import Score
from .themes import melodic_line


def _section_notes(score: Score, start_mc: int, end_mc: int) -> pd.DataFrame:
    n = score.notes
    return n[(n["mc"] >= start_mc) & (n["mc"] <= end_mc) & ~n["grace"]]


def _section_start_qb(score: Score, start_mc: int) -> float:
    return float(score.measures.loc[score.measures["mc"] == start_mc, "start_qb"].iloc[0])


def _section_len_qb(score: Score, start_mc: int, end_mc: int) -> float:
    m = score.measures
    sel = m[(m["mc"] >= start_mc) & (m["mc"] <= end_mc)]
    return float(sel["dur_qb"].sum())


def theme_skeleton(score: Score, part: int, start_mc: int, end_mc: int,
                   min_dur: float = 0.5) -> list[tuple[float, int]]:
    """Main notes of the theme tune: (position from section start in qb, pitch class)."""
    line = melodic_line(score, part)
    line = line[(line["mc"] >= start_mc) & (line["mc"] <= end_mc)]
    t0 = _section_start_qb(score, start_mc)
    notes = score.notes
    out = []
    for onset, midi in zip(line["onset_qb"], line["midi"]):
        dur = notes[(notes["part"] == part) & (notes["onset_qb"] == onset)]["dur_qb"].max()
        if dur >= min_dur:
            out.append((float(onset - t0), int(midi) % 12))
    return out


def _sounding_pcs(notes: pd.DataFrame, t: float) -> set[int]:
    s = notes[(notes["onset_qb"] <= t + 1e-6) & (notes["onset_qb"] + notes["dur_qb"] > t + 1e-6)]
    return set((s["midi"] % 12).astype(int))


def tune_presence(score: Score, skeleton: list[tuple[float, int]], start_mc: int, end_mc: int,
                  transpose: int = 0) -> dict[int, float]:
    """Share of the theme's main notes heard in each part of a section."""
    t0 = _section_start_qb(score, start_mc)
    length = _section_len_qb(score, start_mc, end_mc)
    notes = _section_notes(score, start_mc, end_mc)
    usable = [(pos, pc) for pos, pc in skeleton if pos < length]
    out = {}
    for part in range(score.n_parts):
        pn = notes[notes["part"] == part]
        if pn.empty or not usable:
            out[part] = 0.0
            continue
        hits = sum(1 for pos, pc in usable
                   if (pc + transpose) % 12 in _sounding_pcs(pn, t0 + pos)
                   # allow the tune to be ornamented: check slightly later too
                   or (pc + transpose) % 12 in _sounding_pcs(pn, t0 + pos + 0.25))
        out[part] = round(hits / len(usable), 2)
    return out


def _numerals_by_offset(score: Score, start_mc: int, end_mc: int) -> list[tuple[float, str]]:
    h = score.harmony
    if h is None or h.empty or "numeral" not in h.columns:
        return []
    t0 = _section_start_qb(score, start_mc)
    sel = h[(h["mc"] >= start_mc) & (h["mc"] <= end_mc)]
    out = [(float(o - t0), str(nm)) for o, nm in zip(sel["onset_qb"], sel["numeral"]) if str(nm)]
    if not out and "chord" in sel.columns:      # estimated harmony has chord names, not numerals
        out = [(float(o - t0), str(c)) for o, c in zip(sel["onset_qb"], sel["chord"]) if str(c)]
    return out


def harmonic_similarity(score: Score, theme: tuple[int, int], var: tuple[int, int], step: float = 1.0) -> float | None:
    """Share of beats where the variation has the same Roman numeral as the theme (expert labels only)."""
    a = _numerals_by_offset(score, *theme)
    b = _numerals_by_offset(score, *var)
    if not a or not b:
        return None
    length = min(_section_len_qb(score, *theme), _section_len_qb(score, *var))

    def at(seq, t):
        cur = None
        for pos, nm in seq:
            if pos <= t + 1e-6:
                cur = nm
            else:
                break
        return cur
    grid = np.arange(0, length, step)
    same = [at(a, t) == at(b, t) for t in grid if at(a, t) is not None]
    return round(float(np.mean(same)), 2) if same else None


def compare_variations(score: Score, sections: pd.DataFrame, texture: pd.DataFrame | None = None,
                       dynamics: pd.DataFrame | None = None, theme_part: int | None = None) -> list[dict]:
    """One summary per section, compared with the first section (the theme)."""
    if sections.empty or len(sections) < 2:
        return []
    theme = sections.iloc[0]
    th = (int(theme["start_mc"]), int(theme["end_mc"]))
    if theme_part is None:
        if texture is not None and not texture.empty:
            sel = texture[(texture["mc"] >= th[0]) & (texture["mc"] <= th[1]) & (texture["lead"] >= 0)]
            theme_part = int(sel["lead"].mode().iloc[0]) if not sel.empty else 0
        else:
            theme_part = 0
    skeleton = theme_skeleton(score, theme_part, *th)
    theme_len = _section_len_qb(score, *th)
    theme_density = len(_section_notes(score, *th)) / max(theme_len, 1e-9)
    out = []
    for _, sec in sections.iterrows():
        rng = (int(sec["start_mc"]), int(sec["end_mc"]))
        length = _section_len_qb(score, *rng)
        presence = tune_presence(score, skeleton, *rng)
        best_part = max(presence, key=presence.get)
        density = len(_section_notes(score, *rng)) / max(length, 1e-9)
        info = {
            "name": sec["name"], "start_label": sec["start_label"], "end_label": sec["end_label"],
            "is_theme": rng == th,
            "length_ratio_to_theme": round(length / theme_len, 2) if theme_len else None,
            "theme_tune_presence": {score.parts[p]: v for p, v in presence.items()},
            "theme_tune_best_part": score.parts[best_part] if presence[best_part] >= 0.5 else "",
            "harmonic_similarity_to_theme": harmonic_similarity(score, th, rng),
            "note_density_vs_theme": round(density / theme_density, 2) if theme_density else None,
        }
        if texture is not None and not texture.empty:
            sel = texture[(texture["mc"] >= rng[0]) & (texture["mc"] <= rng[1])]
            leads = sel[sel["lead"] >= 0]["lead"].value_counts(normalize=True)
            info["lead_share"] = {score.parts[int(p)]: round(float(v), 2) for p, v in leads.items()}
            info["main_texture"] = sel["texture"].mode().iloc[0] if not sel.empty else ""
        if dynamics is not None and not dynamics.empty:
            sel = dynamics[(dynamics["mc"] >= rng[0]) & (dynamics["mc"] <= rng[1])]
            levels = sel[sel["level_name"] != "unmarked"]["level_name"].tolist()
            info["dynamics_used"] = sorted(set(levels), key=levels.index)
        out.append(info)
    return out


def periodic_sections(score: Score, period_measures: int, first_mc: int | None = None,
                      name: str = "Variation") -> pd.DataFrame:
    """Cut a passacaglia/chaconne into equal units of `period_measures` measures."""
    from fractions import Fraction
    m = score.measures.reset_index(drop=True)
    mcs = list(m["mc"].astype(int))
    try:
        num, den = str(m.loc[0, "timesig"]).split("/")
        expected = float(Fraction(int(num) * 4, int(den)))
    except ValueError:
        expected = float(m["dur_qb"].median())
    if len(mcs) > 1 and float(m.loc[0, "dur_qb"]) < 0.75 * expected:
        mcs = mcs[1:]                                           # skip a pickup measure
    if first_mc is not None:
        mcs = [mc for mc in mcs if mc >= first_mc]
    rows = []
    for k in range(0, len(mcs), period_measures):
        chunk = mcs[k:k + period_measures]
        if len(chunk) < period_measures // 2:
            break
        rows.append({"section": len(rows) + 1,
                     "name": "Theme" if not rows else f"{name} {len(rows)}",
                     "start_mc": chunk[0], "end_mc": chunk[-1],
                     "start_label": score.measure_label(chunk[0]), "end_label": score.measure_label(chunk[-1]),
                     "n_measures": len(chunk), "repeated": False, "named_in_score": False})
    return pd.DataFrame(rows)


def tune_parts_by_measure(score: Score, sections: pd.DataFrame, theme_part: int,
                          threshold: float = 0.6) -> dict[int, set[int]]:
    """mc -> parts that play most of the theme's main notes in that measure (per variation)."""
    if sections.empty:
        return {}
    theme = sections.iloc[0]
    th = (int(theme["start_mc"]), int(theme["end_mc"]))
    skeleton = theme_skeleton(score, theme_part, *th)
    out: dict[int, set[int]] = {}
    m = score.measures.set_index("mc")
    for _, sec in sections.iterrows():
        rng = (int(sec["start_mc"]), int(sec["end_mc"]))
        t0 = _section_start_qb(score, rng[0])
        notes = _section_notes(score, *rng)
        for mc in [mc for mc in m.index if rng[0] <= mc <= rng[1]]:
            ms = float(m.loc[mc, "start_qb"]) - t0
            me = ms + float(m.loc[mc, "dur_qb"])
            points = [(pos, pc) for pos, pc in skeleton if ms <= pos < me]
            if not points:
                continue
            for part in range(score.n_parts):
                pn = notes[notes["part"] == part]
                if pn.empty:
                    continue
                hits = sum(1 for pos, pc in points
                           if pc in _sounding_pcs(pn, t0 + pos) or pc in _sounding_pcs(pn, t0 + pos + 0.25))
                if hits / len(points) >= threshold and len(points) >= 1:
                    out.setdefault(int(mc), set()).add(part)
    return out


def detect_period(score: Score, candidates=(2, 4, 8, 16)) -> tuple[int, float]:
    """Guess how many measures one variation lasts (passacaglia / chaconne).

    For each candidate length L we check how often measure m and measure m+L
    have the same bass note (lowest pitch class at the downbeat) and the same
    chord root. The best L wins. Returns (L, agreement 0..1).
    """
    from .harmony import auto_harmony
    h = score.harmony if score.harmony is not None and not score.harmony.empty else auto_harmony(score)
    first_chord = h.sort_values("onset_qb").groupby("mc")["chord"].first().to_dict()
    notes = score.notes[~score.notes["grace"]]
    bass = {}
    for mc, grp in notes.groupby("mc"):
        start = grp["onset_qb"].min()
        bass[int(mc)] = int(grp[grp["onset_qb"] <= start + 1e-6]["midi"].min()) % 12
    mcs = list(score.measures["mc"].astype(int))
    best = (candidates[0], 0.0)
    for L in candidates:
        pairs = [(mcs[i], mcs[i + L]) for i in range(len(mcs) - L)]
        if len(pairs) < 2 * L:
            continue
        agree = np.mean([(bass.get(a) == bass.get(b)) * 0.5 + (first_chord.get(a) == first_chord.get(b)) * 0.5
                         for a, b in pairs])
        # small preference for shorter periods when scores tie
        if agree > best[1] + 0.03:
            best = (L, float(agree))
    return best
