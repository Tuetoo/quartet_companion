"""Written dynamics: which loudness marking is in force in each measure."""
from __future__ import annotations

import pandas as pd

from ..score import Score

LEVELS = {"ppp": 0, "pp": 1, "p": 2, "mp": 3, "mf": 4, "f": 5, "ff": 6, "fff": 7}
ACCENTS = {"sf", "sfz", "fz", "sfp", "fp", "rf", "rfz", "sffz"}


def normalise_marking(value: str) -> str:
    return str(value).strip().lower().replace(".", "")


def dynamics_by_measure(score: Score) -> pd.DataFrame:
    """One row per measure: level (0-7, carried forward), level_name, markings, accents, hairpins."""
    ev = score.events
    rows = []
    level, level_name = 2, "p"      # unmarked openings: assume piano-ish, flagged below
    marked_yet = False
    by_mc = {mc: grp for mc, grp in ev.groupby("mc")} if ev is not None and not ev.empty else {}
    for mc in score.measures["mc"].astype(int):
        grp = by_mc.get(mc)
        markings, accents, hairpins = [], [], []
        if grp is not None:
            for _, r in grp.sort_values("onset_qb").iterrows():
                v = normalise_marking(r["value"])
                if r["kind"] == "dynamic":
                    if v in LEVELS:
                        level, level_name = LEVELS[v], v
                        marked_yet = True
                        if v not in markings:
                            markings.append(v)
                    elif v in ACCENTS:
                        if v not in accents:
                            accents.append(v)
                        if v in ("fp", "sfp"):
                            level, level_name = LEVELS["p"], "p"
                    else:
                        if v and v not in markings:
                            markings.append(v)
                elif r["kind"] == "hairpin" and v not in hairpins:
                    hairpins.append(v)
        rows.append({"mc": mc, "level": level, "level_name": level_name if marked_yet else "unmarked",
                     "markings": markings, "accents": accents, "hairpins": hairpins})
    return pd.DataFrame(rows)
