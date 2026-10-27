"""Load MusicXML / MuseScore / MIDI files (via music21) into a Score.

This is the loader for new pieces: files from IMSLP, MuseScore, or the
output of optical music recognition (OMR). Such files have no expert
harmony labels, so harmony is estimated later (marked "auto").
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from ..score import EVENT_COLUMNS, Score, make_labels

_QUARTET_ORDER = ["violin 1", "violin 2", "viola", "cello"]


def _part_name(part, index: int) -> str:
    name = (part.partName or "").strip()
    if not name:
        inst = part.getInstrument(returnDefault=False)
        name = (inst.instrumentName or inst.partName or "") if inst else ""
    name = name.strip() or f"Part {index + 1}"
    low = name.lower().replace("violoncello", "cello").replace("violoncell", "cello").replace("violino", "violin")
    low = low.replace("violine", "violin").replace("vla", "viola")
    if re.match(r"(piano|pianoforte|klavier|pf\b|pno\b|clavier)", low):
        return "Piano"
    low = re.sub(r"\s+", " ", low)
    is_violin = re.search(r"\b(violin|vn|vl|vln)\b", low) is not None
    if is_violin and re.search(r"\b(1|i|1st|first|primo|prima)\b", low):
        return "Violin 1"
    if is_violin and re.search(r"\b(2|ii|2nd|second|secondo|seconda)\b", low):
        return "Violin 2"
    if low.startswith("viola"):
        return "Viola"
    if low.startswith("cello") or low.startswith("vc") or "basso" in low or "bass" in low:
        return "Cello" if "contrabass" not in low or "cello" in low else "Double bass"
    if low.startswith("violin"):
        return "Violin"
    return name


def _unique_names(names: list[str]) -> list[str]:
    out, seen = [], {}
    for n in names:
        if names.count(n) > 1:
            seen[n] = seen.get(n, 0) + 1
            out.append(f"{n} {seen[n]}" if n != "Violin" else f"Violin {seen[n]}")
        else:
            out.append(n)
    return out


def load_music_file(path: str | Path, piece_id: str | None = None, title: str | None = None,
                    composer: str = "", drop_empty_parts: bool = True) -> Score:
    from music21 import bar, converter, dynamics, expressions, spanner, stream, tempo
    path = Path(path)
    sc = converter.parse(str(path))
    if isinstance(sc, stream.Opus):
        sc = sc.scores[0] if len(sc.scores) == 1 else _concat_opus(sc)
    parts = list(sc.parts)
    if not parts:
        raise ValueError(f"no parts found in {path}")

    # ------------------------------------------------------------- measures
    ref = parts[0].getElementsByClass(stream.Measure)
    mrows = []
    for i, m in enumerate(ref):
        mrows.append({"mc": i + 1, "mn": int(m.number) if m.number is not None else i + 1,
                      "start_qb": float(m.offset), "dur_qb": float(m.duration.quarterLength) or float(m.barDuration.quarterLength),
                      "timesig": "", "keysig": 0, "volta": 0, "repeats": "", "_m": m})
    measures = pd.DataFrame(mrows)
    # time and key signatures carried forward
    ts, ks = "4/4", 0
    for idx, m in enumerate(ref):
        t = m.timeSignature or (m.getContextByClass("TimeSignature") if idx == 0 else None)
        if t is not None:
            ts = t.ratioString
        k = m.keySignature or (m.getContextByClass("KeySignature") if idx == 0 else None)
        if k is not None:
            ks = int(k.sharps)
        measures.loc[idx, "timesig"] = ts
        measures.loc[idx, "keysig"] = ks
    # repeat barlines and endings
    mc_of = {id(m): i + 1 for i, m in enumerate(ref)}
    for idx, m in enumerate(ref):
        rep = []
        if isinstance(m.leftBarline, bar.Repeat):
            rep.append("start")
        if isinstance(m.rightBarline, bar.Repeat):
            rep.append("end")
        measures.loc[idx, "repeats"] = ",".join(rep)
    for rb in sc.recurse().getElementsByClass(spanner.RepeatBracket):
        if hasattr(rb, "numberRange"):          # music21 9+ (getNumberList is deprecated)
            nums = [n for n in rb.numberRange if n > 0] or [1]
        elif hasattr(rb, "getNumberList"):
            nums = rb.getNumberList() or [1]
        else:
            nums = [int(x) for x in re.findall(r"\d+", str(getattr(rb, "number", "1") or "1"))] or [1]
        spanned = []
        for m in rb.getSpannedElements():
            mc = mc_of.get(id(m))
            if mc is None:
                # bracket may point at a measure of another part with the same offset
                same = measures[(measures["start_qb"] - float(m.offset)).abs() < 1e-6]
                mc = int(same["mc"].iloc[0]) if len(same) else None
            if mc is not None:
                spanned.append(mc)
        if spanned:
            # An ending over several bars may list only its first and last bar: fill the gap.
            lo, hi = min(spanned), max(spanned)
            measures.loc[(measures["mc"] >= lo) & (measures["mc"] <= hi), "volta"] = int(nums[0])
    measures["next"] = _next_pointers(measures)
    # Fix printed numbers: endings share a number in print but OMR often numbers them on.
    measures["label"] = make_labels(measures)
    measures = measures.drop(columns=["_m"])

    # ----------------------------------------------------------------- notes
    names = _unique_names([_part_name(p, i) for i, p in enumerate(parts)])
    note_rows, events = [], []
    starts = measures.set_index("mc")["start_qb"].to_dict()
    for pi, part in enumerate(parts):
        pms = part.getElementsByClass(stream.Measure)
        for mi, m in enumerate(pms):
            mc = mi + 1
            if mc not in starts:
                continue
            m_off = starts[mc]
            for el in m.recurse().notes:
                off = m_off + float(el.getOffsetInHierarchy(m))
                pitches = el.pitches
                tie = getattr(el, "tie", None)
                is_onset = not (tie is not None and tie.type in ("stop", "continue"))
                grace = el.duration.isGrace
                for p in pitches:
                    note_rows.append({"mc": mc, "mn": int(measures.loc[mi, "mn"]), "onset_qb": off,
                                      "dur_qb": 0.0 if grace else float(el.duration.quarterLength),
                                      "part": pi, "midi": int(p.midi), "is_onset": is_onset, "grace": grace})
            for d in m.recurse().getElementsByClass(dynamics.Dynamic):
                events.append({"mc": mc, "mn": int(measures.loc[mi, "mn"]), "onset_qb": m_off + float(d.getOffsetInHierarchy(m)),
                               "part": pi, "kind": "dynamic", "value": str(d.value)})
            for t in m.recurse().getElementsByClass(expressions.TextExpression):
                txt = (t.content or "").strip()
                if txt:
                    kind = "hairpin" if txt.lower().startswith(("cresc", "dim", "decresc")) else "text"
                    val = ("cresc" if txt.lower().startswith("cresc") else "dim") if kind == "hairpin" else txt
                    events.append({"mc": mc, "mn": int(measures.loc[mi, "mn"]),
                                   "onset_qb": m_off + float(t.getOffsetInHierarchy(m)), "part": pi, "kind": kind, "value": val})
            # "Da Capo al Fine", "Fine", "D.S."...: music21 reads these as repeat expressions,
            # not as text, but the playing order needs them (unfold._find_dc)
            from music21 import repeat as m21repeat
            for t in m.recurse().getElementsByClass(m21repeat.RepeatExpression):
                txt = (t.getText() or "").strip() if hasattr(t, "getText") else ""
                if txt:
                    events.append({"mc": mc, "mn": int(measures.loc[mi, "mn"]),
                                   "onset_qb": m_off + float(t.getOffsetInHierarchy(m)), "part": pi,
                                   "kind": "text", "value": txt})
            for t in m.recurse().getElementsByClass(tempo.TempoIndication):
                txt = ""
                if isinstance(t, tempo.MetronomeMark):
                    if t.text:
                        events.append({"mc": mc, "mn": int(measures.loc[mi, "mn"]),
                                       "onset_qb": m_off + float(t.getOffsetInHierarchy(m)), "part": pi,
                                       "kind": "text", "value": str(t.text)})
                    if t.number:
                        txt = f"♩={int(t.number * (t.referent.quarterLength if t.referent else 1))}"
                else:
                    txt = getattr(t, "text", "") or ""
                if txt:
                    events.append({"mc": mc, "mn": int(measures.loc[mi, "mn"]),
                                   "onset_qb": m_off + float(t.getOffsetInHierarchy(m)), "part": pi, "kind": "tempo", "value": txt})
        for sp in part.recurse().getElementsByClass(dynamics.DynamicWedge):
            first = sp.getFirst()
            if first is None:
                continue
            mm = first.getContextByClass(stream.Measure)
            mc = mc_of.get(id(mm)) or (pms.index(mm) + 1 if mm in pms else None)
            if mc:
                events.append({"mc": mc, "mn": int(measures.loc[mc - 1, "mn"]), "onset_qb": float(starts[mc]),
                               "part": pi, "kind": "hairpin",
                               "value": "cresc" if isinstance(sp, dynamics.Crescendo) else "dim"})

    notes = pd.DataFrame(note_rows)
    if notes.empty:
        raise ValueError(f"no notes found in {path}")
    notes = notes.sort_values(["onset_qb", "part", "midi"]).reset_index(drop=True)
    ev = pd.DataFrame(events, columns=EVENT_COLUMNS)
    if not ev.empty:
        ev = ev.drop_duplicates(["mc", "onset_qb", "kind", "value"]).sort_values(["onset_qb", "part"]).reset_index(drop=True)

    # drop parts without notes (e.g. an empty staff created by OMR)
    if drop_empty_parts:
        used = sorted(notes["part"].unique())
        if len(used) < len(names):
            remap = {old: new for new, old in enumerate(used)}
            notes["part"] = notes["part"].map(remap)
            if not ev.empty:
                ev = ev[ev["part"].isin(used)].copy()
                ev["part"] = ev["part"].map(remap)
            names = [names[i] for i in used]

    md = sc.metadata
    score = Score(
        piece_id=piece_id or path.stem,
        title=title or (md.title if md and md.title else path.stem),
        parts=names,
        measures=measures[["mc", "mn", "label", "start_qb", "dur_qb", "timesig", "keysig", "volta", "repeats", "next"]],
        notes=notes, harmony=None, events=ev,
        meta={"source": str(path.name), "composer": composer or (md.composer if md and md.composer else ""),
              "harmony_source": "auto"},
    )
    texts = ev[(ev["kind"].isin(["text", "tempo"])) & (ev["mc"] <= 2)]["value"].tolist() if not ev.empty else []
    words = [t for t in texts if "=" not in t]
    if words or texts:
        score.meta["tempo_marking"] = (words or texts)[0]
    return score


def _next_pointers(measures: pd.DataFrame) -> list[list[int]]:
    """Build 'next' lists (like the ABC data) from repeat signs and endings."""
    mcs = list(measures["mc"].astype(int))
    reps = list(measures["repeats"])
    volta = list(measures["volta"].astype(int))
    n = len(mcs)
    nxt = [[mcs[i + 1]] if i + 1 < n else [-1] for i in range(n)]

    def section_start(i_end: int) -> int:
        j = i_end
        while j > 0:
            if "start" in reps[j] and volta[j] == 0:
                return j
            if j < i_end and "end" in reps[j - 1] and volta[j] == 0 and "start" not in reps[j]:
                return j
            if j < i_end and volta[j - 1] >= 2 and volta[j] == 0:
                return j          # first bar after a second ending: a new section starts here
            j -= 1
        return 0

    i = 0
    while i < n:
        if volta[i] == 1 and (i == 0 or volta[i - 1] != 1):
            # first ending: find its last measure and the start of the second ending
            j = i
            while j + 1 < n and volta[j + 1] == 1:
                j += 1
            k = j + 1 if j + 1 < n and volta[j + 1] >= 2 else None
            start = section_start(i - 1) if i > 0 else 0
            if i > 0 and k is not None:
                nxt[i - 1] = [mcs[i], mcs[k]]
            nxt[j] = [mcs[start]]
            i = j + 1
            continue
        if "end" in reps[i] and volta[i] == 0:
            start = section_start(i)
            nxt[i] = [mcs[start], mcs[i + 1] if i + 1 < n else -1]
        i += 1
    return nxt


def _concat_opus(opus):
    from music21 import stream
    out = stream.Score()
    for i, s in enumerate(opus.scores):
        if i == 0:
            out = s
            continue
        for p_out, p_in in zip(out.parts, s.parts):
            for m in p_in.getElementsByClass(stream.Measure):
                p_out.append(m)
    return out
