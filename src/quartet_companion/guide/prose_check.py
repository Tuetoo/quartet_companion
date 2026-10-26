"""Checks on the guide's PROSE (the verifier checks only the structured claims).

These rules come from a line-by-line human-style review of the first 28
guides (24 Oct 2026). The most common problems were: a key named in the text
that is not there, "alone" for a passage where others play, a sudden change
described as gradual ("swells", 渐强) with no crescendo marked, the estimated
"loudest point" stated as plain fact, and a low-confidence lead stated
without "probably". Each problem found is sent back to the model once, like a
failed claim.
"""
from __future__ import annotations

import re

HEDGE = re.compile(r"probab|perhaps|may |might|seems|likely|shared|unclear|uncertain|not sure|"
                   r"可能|大概|似乎|也许|分担|共同|不太确定|把握不大|不确定", re.I)
ESTIMATE = re.compile(r"estimat|software|computer|analysis|heuristic|估计|估算|按分析|程序|软件|电脑", re.I)
LOUDEST = re.compile(r"loudest|最响|最高点|高潮|climax", re.I)
GRADUAL = re.compile(r"\bswell|\bgrows? (louder|soft)|\bbuilds? (up|to)|\bbuilding\b|\bfades?\b|\bfading\b|"
                     r"渐强|渐弱|逐渐|慢慢变", re.I)
ALONE = re.compile(r"\balone\b|\bby itself\b|\bsolo\b|独奏|独自|单独", re.I)
OUTSIDE = re.compile(r"\b1[6-9]\d\d\b|Vienna|dedicat|premiere|deaf|维也纳|献给|首演|耳聋|创作于|\d{4}\s*年")
KEY_EN = re.compile(r"\b([A-G])(-flat|-sharp| flat| sharp|♭|♯|b|#)?\s(major|minor)\b")
KEY_ZH = re.compile(r"(升|降)?([A-G])(大调|小调)")
REF = re.compile(r"\[m\.\s*([0-9]+[a-z]?)(?:\s*[-–]\s*([0-9]+[a-z]?))?\]")


def _key(letter: str, acc: str | None, mode: str) -> str:
    acc = (acc or "").strip().lower()
    a = "b" if acc in ("-flat", "flat", "♭", "b", "降") else "#" if acc in ("-sharp", "sharp", "♯", "#", "升") else ""
    return f"{letter}{a} {'major' if mode in ('major', '大调') else 'minor'}"


def _fact_key(k: str) -> str:
    m = re.match(r"([A-G])([b#-]?)\s*(major|minor)", str(k or ""))
    return _key(m.group(1), m.group(2).replace("-", "b"), m.group(3)) if m else str(k)


def prose_issues(guide: dict, facts: dict, language: str = "en", whole_piece: bool = False) -> list[dict]:
    ms = facts["measures"]
    pos: dict[str, int] = {}
    last: dict[str, int] = {}               # a label can occur twice (a bar split at a repeat sign)
    for i, m in enumerate(ms):
        pos.setdefault(str(m["label"]), i)
        last[str(m["label"])] = i
    # where the theme (or a variation's tune) is known to be in a part, naming that part needs no hedge
    tune_in: dict[str, set[str]] = {}
    for o in facts.get("theme_occurrences", []):
        a0, b0 = pos.get(str(o.get("start_label"))), last.get(str(o.get("end_label")))
        if a0 is not None and b0 is not None:
            for i in range(a0, b0 + 1):
                tune_in.setdefault(str(ms[i]["label"]), set()).add(o.get("part"))
    for v in facts.get("variations", []):
        a0, b0 = pos.get(str(v.get("start_label"))), last.get(str(v.get("end_label")))
        best = [pt for pt, x in (v.get("theme_tune_presence") or {}).items() if x >= 0.5]
        if a0 is not None and b0 is not None:
            for i in range(a0, b0 + 1):
                tune_in.setdefault(str(ms[i]["label"]), set()).update(best)
    out: list[dict] = []

    def add(point: str, problem: str) -> None:
        out.append({"point": point, "problem": problem})

    for k, p in enumerate(guide.get("listening_points", []), 1):
        name = f"point {k} ({p.get('headline', '')})"
        a, b = pos.get(str(p.get("start_measure"))), last.get(str(p.get("end_measure")))
        if a is None or b is None:
            continue
        a, b = min(a, b), max(a, b)
        text = f"{p.get('headline', '')} {p.get('text', '')}"
        win = ms[max(0, a - 2): b + 3]
        rng = ms[a: b + 1]
        # keys named in the text must occur near the point
        keys_here = {_fact_key(m.get("key")) for m in win}
        named = [_key(*m.groups()) for m in KEY_EN.finditer(text)] + \
                [_key(m.group(2), m.group(1), m.group(3)) for m in KEY_ZH.finditer(text)]
        for key in named:
            if key not in keys_here and not re.search(r"\bA minor key\b", text):
                add(name, f"the text names {key}, but the facts show {sorted(keys_here)} here")
        # "alone/solo" only where the texture is solo somewhere in the range
        if ALONE.search(text) and not any(m.get("texture") == "solo" for m in rng):
            add(name, "the text says a part plays alone, but no measure in this range is solo")
        # gradual change words need a cresc/dim marking
        if GRADUAL.search(text) and not any(re.search(r"cresc|dim", " ".join(m.get("hairpins") or []) + " " +
                                                      " ".join(m.get("markings") or []), re.I) for m in win):
            add(name, "the text describes a gradual change (swell/fade/渐强/渐弱), but no crescendo or "
                      "diminuendo is marked here; say the change is sudden")
        # the loudest point is an estimate
        if LOUDEST.search(text) and not ESTIMATE.search(text):
            add(name, "the 'loudest point' is a computer estimate; say so")
        # low-confidence lead stated without a hedge
        lows = [c for c in p.get("claims", []) if c.get("type") == "lead" and str(c.get("measure")) in pos
                and max(ms[i].get("lead_confidence") or 0 for i in (pos[str(c["measure"])], last[str(c["measure"])])) < 0.4
                and c.get("value") not in tune_in.get(str(c["measure"]), set())]
        if lows and not HEDGE.search(text):
            add(name, f"who leads at m. {lows[0]['measure']} is uncertain (confidence below 0.4); say 'probably'")
        # measure references far outside the point, without saying so
        for r in REF.finditer(p.get("text", "")):
            for lb in filter(None, r.groups()):
                i = pos.get(lb)
                if i is not None and not (a - 3 <= i <= b + 3) and not re.search(
                        r"earlier|before|as in|like|again|前面|之前|开头|第一部分|如同|和.*一样", p.get("text", "")):
                    add(name, f"[m. {lb}] is outside this point's range; move it or say it refers back")
        if OUTSIDE.search(text):
            add(name, "outside knowledge (dates, places, history) is not allowed")
    if language == "zh" and not whole_piece:
        all_text = guide.get("overview", "") + " ".join(p.get("headline", "") + p.get("text", "")
                                                        for p in guide.get("listening_points", []))
        if "全曲" in all_text:
            add("overview/points", "this guide is about one movement: write 本乐章, not 全曲")
        if re.search(r"齐奏[^/]{0,4}(homophonic)|同步和声|齐步和声", all_text + str(guide.get("glossary", ""))):
            add("glossary", "homophonic is 主调织体 in Chinese; 齐奏 means unison")
    return out
