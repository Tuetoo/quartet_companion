"""Split a movement into sections (e.g. 'Theme', 'Var. 1', 'Trio', 'Coda').

We only use signs that are written in the score: text such as "Var. 2"
or "Trio", tempo changes, key-signature and time-signature changes, and
repeat signs. This keeps every section boundary checkable.
"""
from __future__ import annotations

import re

import pandas as pd

from ..score import Score

TEMPO_WORDS = re.compile(
    r"\b(adagio|allegro|allegretto|andante|andantino|presto|prestissimo|largo|larghetto|lento|"
    r"moderato|vivace|grave|maestoso|tempo\s+i|a\s+tempo)\b", re.IGNORECASE)

SECTION_WORDS = re.compile(
    r"^(var(\.|iation)?\s*\w+\.?|thema|theme|trio|coda|menuetto|minuetto|scherzo|minore|maggiore|"
    r"tema|finale|introduction|introduzione)\b", re.IGNORECASE)


def _boundaries(score: Score) -> dict[int, str]:
    """mc -> reason/name for every measure that starts a new section."""
    m = score.measures.reset_index(drop=True)
    mcs = list(m["mc"].astype(int))
    starts: dict[int, str] = {mcs[0]: ""}
    ev = score.events
    if ev is not None and not ev.empty:
        texts = ev[ev["kind"].isin(["text", "tempo"])].drop_duplicates(["mc", "value"])
        for _, r in texts.iterrows():
            value = str(r["value"]).strip()
            if SECTION_WORDS.match(value) and not re.search(r"D\.\s?C\.|da capo", value, re.IGNORECASE):
                starts[int(r["mc"])] = value.rstrip(".")
            elif int(r["mc"]) != mcs[0] and "=" not in value and TEMPO_WORDS.search(value):
                # A new tempo word later in the movement (e.g. "Poco Adagio") starts a section.
                starts.setdefault(int(r["mc"]), value)
    named = any(SECTION_WORDS.match(v or "") for v in starts.values())
    if not named:
        # No written section names (typical in sonata movements): use repeat signs.
        for i in range(len(m)):
            rep = str(m.loc[i, "repeats"])
            if "start" in rep and i > 0:
                starts.setdefault(mcs[i], "repeat")
            if "end" in rep and i + 1 < len(m):
                # skip a following second ending: it belongs to the same section
                j = i + 1
                while j < len(m) and int(m.loc[j, "volta"]) > 1:
                    j += 1
                if j < len(m):
                    starts.setdefault(mcs[j], "repeat")
    for i in range(1, len(m)):
        mc = mcs[i]
        if m.loc[i, "keysig"] != m.loc[i - 1, "keysig"]:
            starts.setdefault(mc, "new key signature")
        if m.loc[i, "timesig"] != m.loc[i - 1, "timesig"]:
            starts.setdefault(mc, "new time signature")
    return starts


def find_sections(score: Score) -> pd.DataFrame:
    """Sections with start/end measure ids and labels.

    Columns: section, name, start_mc, end_mc, start_label, end_label, n_measures, named_in_score
    """
    m = score.measures.reset_index(drop=True)
    mcs = list(m["mc"].astype(int))
    starts = _boundaries(score)
    ordered = sorted(starts)
    # Merge very short unnamed pieces (a pickup, or a bar or two between two repeat signs).
    pos = {mc: i for i, mc in enumerate(mcs)}
    changed = True
    while changed and len(ordered) > 1:
        changed = False
        for i, st in enumerate(ordered):
            nxt = ordered[i + 1] if i + 1 < len(ordered) else None
            length = (pos[nxt] - pos[st]) if nxt is not None else len(mcs) - pos[st]
            if length >= 4 or nxt is None:
                continue
            if i == 0:
                if SECTION_WORDS.match(starts[nxt] or ""):
                    continue
                starts[st] = starts[st] or starts[nxt]
                del starts[nxt]                     # the first section absorbs the next one
            else:
                if SECTION_WORDS.match(starts[st] or ""):
                    continue
                del starts[st]                      # this short piece joins the previous section
            ordered = sorted(starts)
            changed = True
            break
    rows = []
    for i, start in enumerate(ordered):
        end = mcs[mcs.index(ordered[i + 1]) - 1] if i + 1 < len(ordered) else mcs[-1]
        name = starts[start]
        named = bool(name) and SECTION_WORDS.match(name) is not None
        rows.append({"start_mc": start, "end_mc": end, "raw_name": name, "named_in_score": named})
    # If the first section has no name but later ones are variations, it is the theme.
    has_vars = any(re.match(r"var", r["raw_name"], re.IGNORECASE) for r in rows)
    out = []
    for i, r in enumerate(rows):
        name = r["raw_name"]
        if not r["named_in_score"]:
            if i == 0 and has_vars:
                name = "Theme"
            elif has_vars and i == len(rows) - 1 and TEMPO_WORDS.search(name or ""):
                name = f"Coda ({name})"
            elif name == "repeat" or (i == 0 and not name):
                name = f"Part {i + 1}"
            else:
                name = f"Section {i + 1} ({name})" if name else f"Section {i + 1}"
        repeated = _is_repeated(score, r["start_mc"], r["end_mc"])
        n_meas = int(m[(m["mc"] >= r["start_mc"]) & (m["mc"] <= r["end_mc"])]["mn"].nunique())
        out.append({"section": i + 1, "name": name, "start_mc": r["start_mc"], "end_mc": r["end_mc"],
                    "start_label": score.measure_label(r["start_mc"]),
                    "end_label": score.measure_label(r["end_mc"]),
                    "n_measures": n_meas, "repeated": repeated, "named_in_score": r["named_in_score"] or (i == 0 and has_vars)})
    return pd.DataFrame(out)


def _is_repeated(score: Score, start_mc: int, end_mc: int) -> bool:
    """True if a repeat sign sends the music back to the start of this span."""
    m = score.measures
    inside = m[(m["mc"] >= start_mc) & (m["mc"] <= end_mc)]
    for nxt in inside["next"]:
        if any(start_mc <= int(t) <= end_mc and int(t) != -1 for t in nxt[:1]) and len(nxt) > 1:
            return True
    return False


def section_of(sections: pd.DataFrame, mc: int) -> str:
    row = sections[(sections["start_mc"] <= mc) & (sections["end_mc"] >= mc)]
    return str(row["name"].iloc[0]) if len(row) else ""
