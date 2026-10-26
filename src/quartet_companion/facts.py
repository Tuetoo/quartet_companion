"""Build the "fact sheet" for one movement.

The fact sheet is the single source of truth. The language model only
reads this sheet, and the verifier checks every claim against it.
Everything here is computed by code, never written by the model.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .analysis import dynamics as dyn_mod
from .analysis import harmony as harm_mod
from .analysis import sections as sec_mod
from .analysis import texture as tex_mod
from .analysis import themes as theme_mod
from .analysis import variations as var_mod
from .keys import midi_to_name
from .score import Score

FACTS_VERSION = 1


def _spans(rows: list[dict], key_fields: list[str], score: Score) -> list[dict]:
    """Merge consecutive measures that share the same values in key_fields."""
    spans: list[dict] = []
    for r in rows:
        if spans and all(spans[-1][k] == r[k] for k in key_fields):
            spans[-1]["end_mc"] = r["mc"]
            spans[-1]["_conf"].append(r.get("confidence", 1.0))
        else:
            spans.append({**{k: r[k] for k in key_fields}, "start_mc": r["mc"], "end_mc": r["mc"],
                          "_conf": [r.get("confidence", 1.0)]})
    for s in spans:
        s["start_label"] = score.measure_label(s["start_mc"])
        s["end_label"] = score.measure_label(s["end_mc"])
        s["mean_confidence"] = round(float(sum(s["_conf"]) / len(s["_conf"])), 2)
        del s["_conf"]
    return spans


_MAJ = ["Cb", "Gb", "Db", "Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#"]
_MIN = ["Ab", "Eb", "Bb", "F", "C", "G", "D", "A", "E", "B", "F#", "C#", "G#", "D#", "A#"]


_PC_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def _final_chord_key(score, end_mc: int) -> tuple[int | None, str | None]:
    """(tonic pitch class, "major"/"minor"/None) from the last chord: the bass of the
    final bar is the tonic; its third decides the mode (None if there is no third)."""
    notes = score.notes
    mcs = sorted(int(m) for m in score.measures["mc"] if int(m) <= end_mc)
    for mc in reversed(mcs[-3:]):          # skip a final bar of rests
        last = notes[notes["mc"] == mc]
        if len(last):
            break
    else:
        return None, None
    tonic = int(last["midi"].min()) % 12
    pcs = set(int(x) % 12 for x in last["midi"])
    major, minor = (tonic + 4) % 12 in pcs, (tonic + 3) % 12 in pcs
    return tonic, ("major" if major and not minor else "minor" if minor and not major else None)


def home_key(score, regions: pd.DataFrame, first_key: str) -> str:
    """The movement's home key.

    Movements may open away from home (a slow introduction, an ambiguous opening),
    but they end at home. The last chord gives the tonic (its bass) and the mode (its
    third). With a da capo the music ends at the Fine. If the last chord has no third
    (bare octaves), the key signature at the end decides between its major and minor
    key, preferring the first bar's key when it is one of them.
    Checked on 46 movements (e.g. Op.135/I is F major, not the B-flat minor of its
    ambiguous first bars; introductions in other keys: Borodin II/4, Op.135/4; Dvorak
    III ends in F major although the signature still has four flats; Schubert D.810/II
    is in G minor although its last chord is G major)."""
    from .unfold import _find_dc
    ms = score.measures
    if not len(ms):
        return first_key
    dc_mc, fine_mc = _find_dc(score)
    end_mc = int(fine_mc) if (dc_mc is not None and fine_mc) else int(ms["mc"].iloc[-1])
    tonic, chord_mode = _final_chord_key(score, end_mc)
    ks = int(ms.loc[ms["mc"].astype(int) <= end_mc, "keysig"].iloc[-1])
    cands = [f"{_MAJ[ks + 7]} major", f"{_MIN[ks + 7]} minor"] if -7 <= ks <= 7 else []
    if tonic is None:
        return first_key if (first_key in cands or not cands) else cands[0]
    pc = lambda key: _PC_NAMES.index(_norm(key.split()[0]))           # noqa: E731
    sig_key = next((c for c in cands if pc(c) == tonic), None)
    # The mode is voted on by three clues; ties go to the signature:
    #  - the signature at the end (if it has a key on this tonic),
    #  - the opening (if it is on the same tonic: a minor movement often ends on a
    #    major chord, e.g. Schubert D.810/II),
    #  - the third of the final chord.
    votes = []
    if sig_key:
        votes.append(sig_key.split()[1])
    if first_key and " " in first_key and pc(first_key) == tonic:
        votes.append(first_key.split()[1])
    if chord_mode:
        votes.append(chord_mode)
    if not votes:
        return first_key if (first_key in cands or not cands) else cands[0]
    n_major, n_minor = votes.count("major"), votes.count("minor")
    mode = "major" if n_major > n_minor else "minor" if n_minor > n_major else (sig_key or "x " + votes[0]).split()[1]
    name = f"{_PC_NAMES[tonic]} {mode}"
    for c in [sig_key, first_key]:        # keep the spelling used by the signature (D-flat, not C#)
        if c and pc(c) == tonic and c.endswith(mode):
            return c
    return name


def _norm(name: str) -> str:
    """Spell a note name the way _PC_NAMES does (C# -> Db, Gb -> F#, Cb -> B ...)."""
    pc = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[name[0]] + name[1:].count("#") - name[1:].count("b")
    return _PC_NAMES[pc % 12]


def build_facts(score: Score, theme_specs: list[dict] | None = None,
                period_measures: int | None = None) -> dict:
    """Run every analysis and return a JSON-ready dict.

    theme_specs: optional list of {"name", "part", "start_label", "end_label"} to
    define themes by hand. Without it, the opening melody is used.
    period_measures: for a passacaglia/chaconne without written variation
    names, cut the piece into units of this many measures.
    """
    problems = score.validate()
    if problems:
        raise ValueError("score is not valid: " + "; ".join(problems))
    parts = score.parts

    # Harmony: expert labels if present, otherwise estimated.
    harmony = score.harmony
    harmony_source = "expert"
    if harmony is None or harmony.empty:
        harmony = harm_mod.auto_harmony(score)
        harmony_source = "auto"
    keys = harm_mod.key_by_measure(harmony, score)
    chords = harm_mod.chords_by_measure(harmony)
    regions = harm_mod.key_regions(harmony, score)
    cads = harm_mod.cadences(harmony, score)

    # First pass of texture (no theme info) to find the opening melody.
    texture0 = tex_mod.analyse_texture(score)
    themes: list[theme_mod.Theme] = []
    label_map = score.label_to_mcs()
    for spec in theme_specs or []:
        start = label_map.get(str(spec["start_label"]), [None])[0]
        end = label_map.get(str(spec.get("end_label", "")), [None])[-1]
        part = parts.index(spec["part"]) if isinstance(spec["part"], str) else int(spec["part"])
        t = theme_mod.extract_theme(score, part, start, name=spec.get("name", "theme"), end_mc=end) if start else None
        if t:
            themes.append(t)
    if not themes:
        t = theme_mod.auto_main_theme(score, texture0)
        if t:
            themes.append(t)
    matches: list[theme_mod.ThemeMatch] = []
    for t in themes:
        matches += theme_mod.find_matches(score, t)
    theme_parts = theme_mod.theme_parts_by_measure(matches)

    sections = sec_mod.find_sections(score)
    if period_measures:
        sections = var_mod.periodic_sections(score, period_measures)
    dyn = dyn_mod.dynamics_by_measure(score)
    is_variation_set = bool(period_measures) or sections["name"].astype(str).str.match(r"(?i)var").any()
    variations: list[dict] = []
    if is_variation_set:
        th = sections.iloc[0]
        sel = texture0[(texture0["mc"] >= th["start_mc"]) & (texture0["mc"] <= th["end_mc"]) & (texture0["lead"] >= 0)]
        theme_part = int(sel["lead"].mode().iloc[0]) if not sel.empty else 0
        for mc, ps in var_mod.tune_parts_by_measure(score, sections, theme_part).items():
            theme_parts.setdefault(mc, set()).update(ps)
    texture = tex_mod.analyse_texture(score, theme_parts) if theme_parts else texture0
    if is_variation_set:
        import dataclasses
        # use the same harmony as the rest of the sheet (expert or estimated)
        variations = var_mod.compare_variations(dataclasses.replace(score, harmony=harmony), sections, texture, dyn)
    cad_by_mc = {int(r["mc"]): r["cadence"] for _, r in cads.iterrows()}

    # ------------------------------------------------------- per-measure table
    tex_by_mc = texture.set_index("mc")
    dyn_by_mc = dyn.set_index("mc")
    measures = []
    for _, m in score.measures.iterrows():
        mc = int(m["mc"])
        t = tex_by_mc.loc[mc]
        d = dyn_by_mc.loc[mc]
        measures.append({
            "mc": mc,
            "label": str(m["label"]),
            "section": sec_mod.section_of(sections, mc),
            "key": keys.get(mc, ""),
            "chords": chords.get(mc, []),
            "cadence": cad_by_mc.get(mc, ""),
            "lead": parts[int(t["lead"])] if int(t["lead"]) >= 0 else "none",
            "co_lead": parts[int(t["co_lead"])] if int(t["co_lead"]) >= 0 else "",
            "lead_confidence": float(t["confidence"]),
            "texture": t["texture"],
            "active_parts": [parts[p] for p in t["active_parts"]],
            "dynamic": d["level_name"],
            "dynamic_level": int(d["level"]),
            "markings": list(d["markings"]) + list(d["accents"]),
            "hairpins": list(d["hairpins"]),
            "onsets": int(t["total_onsets"]),
        })

    lead_rows = [{"mc": r["mc"], "lead": r["lead"], "co_lead": r["co_lead"], "confidence": r["lead_confidence"]}
                 for r in measures]
    texture_rows = [{"mc": r["mc"], "texture": r["texture"]} for r in measures]

    # --------------------------------------------------------- climax (heuristic)
    def climax_score(r: dict) -> float:
        return r["dynamic_level"] * 2 + r["onsets"] / max(1, max(x["onsets"] for x in measures)) * 3
    climax = max(measures, key=climax_score) if measures else None

    modulations = []
    for i in range(1, len(regions)):
        modulations.append({"label": regions.iloc[i]["start_label"], "mc": int(regions.iloc[i]["start_mc"]),
                            "from_key": regions.iloc[i - 1]["key_name"], "to_key": regions.iloc[i]["key_name"]})

    first = score.measures.iloc[0]
    facts = {
        "facts_version": FACTS_VERSION,
        "piece": {
            "id": score.piece_id,
            "title": score.title,
            "composer": score.meta.get("composer", ""),
            "tempo_marking": score.meta.get("tempo_marking", ""),
            "parts": parts,
            "home_key": home_key(score, regions, keys.get(int(first["mc"]), "")),
            "time_signature": str(first["timesig"]),
            "n_measures": int(score.measures["mn"].nunique()),
            "first_label": str(first["label"]),
            "last_label": str(score.measures.iloc[-1]["label"]),
            "harmony_source": harmony_source,
            "score_source": score.meta.get("source", ""),
        },
        "sections": sections.to_dict("records"),
        "key_plan": regions.to_dict("records"),
        "modulations": modulations,
        "cadences": cads.to_dict("records"),
        "themes": [{"name": t.name, "part": parts[t.part], "start_label": score.measure_label(t.start_mc),
                    "notes": [midi_to_name(p) for p in t.pitches], "intervals": t.intervals} for t in themes],
        "theme_occurrences": [{"theme": mt.theme, "part": parts[mt.part],
                               "start_label": score.measure_label(mt.start_mc),
                               "end_label": score.measure_label(mt.end_mc),
                               "start_mc": mt.start_mc, "end_mc": mt.end_mc, "kind": mt.kind,
                               "transposition_semitones": mt.transposition,
                               "rhythm_similarity": mt.rhythm_similarity,
                               "key_at_start": keys.get(mt.start_mc, "")} for mt in matches],
        "variations": variations,
        "lead_spans": _spans(lead_rows, ["lead"], score),
        "texture_spans": _spans(texture_rows, ["texture"], score),
        "climax": {"label": climax["label"], "mc": climax["mc"], "dynamic": climax["dynamic"],
                   "section": climax["section"]} if climax else None,
        "measures": measures,
        "method_notes": {
            "lead": "Lead part is a heuristic (pitch variety, stepwise motion, rhythmic independence, "
                    "register, theme presence). Treat low-confidence spans as uncertain.",
            "harmony": "Expert Roman-numeral labels (DCML ABC)." if harmony_source == "expert"
                       else "Estimated automatically (key profiles + chord templates); may contain errors.",
        },
    }
    return facts


def save_facts(facts: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(facts, ensure_ascii=False, indent=1, default=_json_default))


def _json_default(o):
    if hasattr(o, "item"):
        return o.item()
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, pd.Timestamp):
        return str(o)
    raise TypeError(f"cannot serialise {type(o)}")
