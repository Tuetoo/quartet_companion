"""Turn the written score into the order a performance plays it.

A written score has repeat signs, first/second endings and "Da Capo"
instructions. A recording plays some measures twice. Alignment needs the
measures in *playing order*.

Performers do not always take every repeat. So we build several candidate
playing orders, and the aligner later picks the one that fits the
recording best.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

from .score import Score

_DC_RE = re.compile(r"(?:\bD\.\s?C\b\.?|\bda\s+capo)", re.IGNORECASE)   # "D.C.", "D. C", "Menuetto D.C"
_FINE_RE = re.compile(r"\bfine\b", re.IGNORECASE)
_TRIO_RE = re.compile(r"\btrio\b", re.IGNORECASE)


@dataclass
class PlayingOrder:
    name: str
    mcs: list[int]          # measure ids in playing order
    description: str

    def __len__(self) -> int:
        return len(self.mcs)


def repeat_groups(measures: pd.DataFrame) -> list[int]:
    """Measures that can jump backwards (the end of a repeated passage)."""
    groups = []
    for mc, nxt in zip(measures["mc"].astype(int), measures["next"]):
        if any(0 < int(t) <= mc for t in nxt):
            groups.append(int(mc))
    return groups


def _group_of_branch(nxt: dict, start: int, groups: set[int], limit: int = 200) -> int | None:
    """Follow the first option from a forward branch (first ending) to its repeat sign."""
    mc, steps = start, 0
    while mc in nxt and steps < limit:
        if mc in groups:
            return mc
        opts = nxt[mc]
        if not opts or opts[0] == -1:
            return None
        mc = int(opts[0])
        steps += 1
    return None


def _follow(measures: pd.DataFrame, take_repeats: bool | dict, max_steps: int = 20000) -> list[int]:
    """Walk the score. take_repeats: True/False for all repeats, or {repeat_end_mc: bool}."""
    nxt = {int(k): [int(x) for x in v] for k, v in zip(measures["mc"].astype(int), measures["next"])}
    groups = set(repeat_groups(measures))

    def wants(group: int | None) -> bool:
        if isinstance(take_repeats, dict):
            return bool(take_repeats.get(group, True)) if group is not None else True
        return bool(take_repeats)

    order: list[int] = []
    visits: dict[int, int] = {}
    mc = int(measures["mc"].iloc[0])
    while mc != -1 and mc in nxt and len(order) < max_steps:
        order.append(mc)
        options = nxt[mc] or [-1]
        if len(options) == 1:
            mc = options[0]
            continue
        k = visits.get(mc, 0)
        visits[mc] = k + 1
        if mc in groups:
            group = mc
        else:
            group = _group_of_branch(nxt, options[0], groups)
        if wants(group):
            mc = options[min(k, len(options) - 1)]
        else:
            mc = options[-1]          # skip the repeat (and its first ending)
    return order


def _find_dc(score: Score) -> tuple[int | None, int | None]:
    """Return (mc that carries a D.C. instruction, mc where the D.C. stops)."""
    ev = score.events
    if ev is None or ev.empty:
        return None, None
    texts = ev[ev["kind"].isin(["text", "tempo"])]
    dc_rows = texts[texts["value"].str.contains(_DC_RE)]
    if dc_rows.empty:
        return None, None
    dc_mc = int(dc_rows["mc"].iloc[0])
    fine_rows = texts[texts["value"].str.contains(_FINE_RE)]
    if not fine_rows.empty:
        return dc_mc, int(fine_rows["mc"].iloc[0])
    trio_rows = texts[texts["value"].str.contains(_TRIO_RE) & ~texts["value"].str.contains(_DC_RE)]
    mcs = list(score.measures["mc"].astype(int))
    if not trio_rows.empty:
        trio_mc = int(trio_rows["mc"].iloc[0])
        idx = mcs.index(trio_mc)
        return dc_mc, mcs[idx - 1] if idx > 0 else None
    # Fallback: the section ends where the key signature first changes.
    keys = list(score.measures["keysig"])
    for i in range(1, len(keys)):
        if keys[i] != keys[i - 1]:
            return dc_mc, mcs[i - 1]
    return dc_mc, None


def playing_orders(score: Score, max_groups_for_combinations: int = 7) -> list[PlayingOrder]:
    """Candidate playing orders, most likely first.

    Besides "all repeats" and "no repeats" we try every mix of taken and
    skipped repeats (e.g. exposition repeated, second half not) when there are
    up to 7 repeat signs (128 mixes); with more, we change one repeat at a time.
    """
    import itertools
    measures = score.measures
    orders: list[PlayingOrder] = []
    seen: set[tuple] = set()

    def add(name: str, mcs: list[int], desc: str) -> None:
        key = tuple(mcs)
        if key not in seen:
            seen.add(key)
            orders.append(PlayingOrder(name, mcs, desc))

    add("all_repeats", _follow(measures, True), "every repeat taken")
    add("no_repeats", _follow(measures, False), "no repeats taken")
    groups = repeat_groups(measures)
    labels = {int(mc): str(lb) for mc, lb in zip(measures["mc"], measures["label"])}
    if 1 < len(groups) <= max_groups_for_combinations:
        for combo in itertools.product([True, False], repeat=len(groups)):
            if all(combo) or not any(combo):
                continue
            policy = dict(zip(groups, combo))
            taken = [labels[g] for g, c in policy.items() if c]
            name = "repeats_at_" + "_".join(taken)
            add(name, _follow(measures, policy),
                "only the repeats ending at measure(s) " + ", ".join(taken) + " taken")
    elif len(groups) > max_groups_for_combinations:
        # Too many repeat signs to try every mix: try leaving out (or taking) one at a time.
        for g in groups:
            for base in (True, False):
                policy = {x: (base if x != g else not base) for x in groups}
                taken = [labels[x] for x, c in policy.items() if c]
                name = "repeats_at_" + "_".join(taken) if taken else "no_repeats"
                add(name, _follow(measures, policy),
                    "only the repeats ending at measure(s) " + ", ".join(taken) + " taken")

    dc_mc, fine_mc = _find_dc(score)
    if dc_mc is not None and fine_mc is not None:
        # The return after D.C. is traditionally played without repeats.
        mcs = list(measures["mc"].astype(int))
        da_capo = mcs[: mcs.index(fine_mc) + 1]
        da_capo = [m for m in da_capo if _not_first_ending(measures, m)]
        orders = [PlayingOrder(o.name + "+dc", o.mcs + da_capo, o.description + ", then Da Capo without repeats")
                  for o in orders] + orders
    return orders


def _not_first_ending(measures: pd.DataFrame, mc: int) -> bool:
    row = measures.loc[measures["mc"] == mc].iloc[0]
    return int(row["volta"]) in (0, 2) or int(row["volta"]) > 2


def unfolded_notes(score: Score, order: PlayingOrder) -> pd.DataFrame:
    """Notes in playing order, with `perf_qb` = position in the performance."""
    measures = score.measures.set_index("mc")
    parts = []
    perf_start = 0.0
    by_mc = {mc: df for mc, df in score.notes.groupby("mc")}
    for occurrence, mc in enumerate(order.mcs):
        m = measures.loc[mc]
        notes = by_mc.get(mc)
        if notes is not None and len(notes):
            n = notes.copy()
            n["perf_qb"] = perf_start + (n["onset_qb"] - m["start_qb"])
            n["occurrence"] = occurrence
            parts.append(n)
        perf_start += float(m["dur_qb"])
    if not parts:
        return score.notes.iloc[0:0].assign(perf_qb=[], occurrence=[])
    return pd.concat(parts, ignore_index=True)


def measure_timeline(score: Score, order: PlayingOrder) -> pd.DataFrame:
    """One row per played measure: occurrence index, mc, label, perf start/end in qb."""
    measures = score.measures.set_index("mc")
    rows = []
    pos = 0.0
    for occurrence, mc in enumerate(order.mcs):
        dur = float(measures.loc[mc, "dur_qb"])
        rows.append({"occurrence": occurrence, "mc": mc, "label": measures.loc[mc, "label"],
                     "perf_start_qb": pos, "perf_end_qb": pos + dur})
        pos += dur
    return pd.DataFrame(rows)
