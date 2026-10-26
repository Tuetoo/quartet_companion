"""Turn the full fact sheet into a compact text the model can read cheaply.

The full JSON is large (one record per measure with many fields). For the
prompt we keep every fact, but write the per-measure table as short
'|'-separated lines.
"""
from __future__ import annotations

import json

PART_ABBR = {"Violin 1": "Vn1", "Violin 2": "Vn2", "Viola": "Va", "Cello": "Vc", "Violin": "Vn"}


def abbr(part: str) -> str:
    return PART_ABBR.get(part, part)


def compact_facts(facts: dict, max_cadences: int = 60) -> str:
    p = facts["piece"]
    out = []
    out.append("## PIECE")
    out.append(json.dumps({k: p[k] for k in ["title", "composer", "tempo_marking", "parts", "home_key",
                                             "time_signature", "n_measures", "first_label", "last_label",
                                             "harmony_source", "score_quality"] if k in p}, ensure_ascii=False))
    out.append("Part abbreviations: " + ", ".join(f"{abbr(x)}={x}" for x in p["parts"]))

    out.append("\n## SECTIONS (start-end measure labels)")
    for s in facts["sections"]:
        out.append(f"- {s['name']}: {s['start_label']}-{s['end_label']} ({s['n_measures']} measures"
                   f"{', repeated' if s.get('repeated') else ''})")

    out.append("\n## KEY PLAN (local keys in order)")
    for r in facts["key_plan"]:
        out.append(f"- {r['key_name']}: {r['start_label']}-{r['end_label']}")

    if facts.get("cadences"):
        out.append("\n## CADENCES (measure: type)")
        cads = facts["cadences"][:max_cadences]
        out.append("; ".join(f"{c['label']}: {c['cadence']} in {c['key_name']}" for c in cads))
        out.append("Cadence codes: PAC=strong final close, IAC=weaker close, HC=half cadence (pause on dominant), "
                   "EC=evaded, DC=deceptive (surprise chord).")

    out.append("\n## THEMES")
    for t in facts["themes"]:
        out.append(f"- '{t['name']}': first played by {t['part']} at {t['start_label']}; notes {' '.join(t['notes'])}")
    if facts["theme_occurrences"]:
        out.append("Theme returns (exact interval match unless noted):")
        for o in facts["theme_occurrences"]:
            out.append(f"- {o['theme']}: {o['part']} {o['start_label']}-{o['end_label']}, {o['kind']}, "
                       f"transposed {o['transposition_semitones']} semitones, key {o['key_at_start']}")

    if facts.get("variations"):
        out.append("\n## VARIATIONS COMPARED WITH THE THEME")
        out.append("theme_tune_presence = share of the theme's main notes heard in that part (0-1).")
        for v in facts["variations"]:
            pres = ", ".join(f"{abbr(k)} {val}" for k, val in v["theme_tune_presence"].items())
            leads = ", ".join(f"{abbr(k)} {val}" for k, val in v.get("lead_share", {}).items())
            out.append(f"- {v['name']} ({v['start_label']}-{v['end_label']}): tune presence [{pres}]; "
                       f"tune mostly in: {v['theme_tune_best_part'] or 'not clearly in one part'}; "
                       f"same harmony as theme: {v['harmonic_similarity_to_theme']}; "
                       f"note density vs theme: {v['note_density_vs_theme']}x; lead share [{leads}]; "
                       f"main texture: {v.get('main_texture')}; dynamics: {', '.join(v.get('dynamics_used', []))}")

    out.append("\n## LEAD PART SPANS (heuristic; conf = mean confidence 0-1)")
    out.append("; ".join(f"{s['start_label']}-{s['end_label']} {abbr(s['lead'])} (conf {s['mean_confidence']})"
                         for s in facts["lead_spans"]))

    out.append("\n## TEXTURE SPANS")
    out.append("; ".join(f"{s['start_label']}-{s['end_label']} {s['texture']}" for s in facts["texture_spans"]))

    if facts.get("climax"):
        c = facts["climax"]
        out.append(f"\n## LOUDEST/BUSIEST POINT (heuristic): measure {c['label']} ({c['dynamic']}, {c['section']})")

    out.append("\n## MEASURE TABLE")
    out.append("label|section|key|lead(+co-lead)|lead_conf|texture|dynamic in force|new markings|cadence|chords")
    for m in facts["measures"]:
        lead = abbr(m["lead"]) + (f"+{abbr(m['co_lead'])}" if m["co_lead"] else "")
        marks = ",".join(m["markings"] + [f"<{h}>" for h in m["hairpins"]])
        out.append("|".join([m["label"], m["section"], m["key"], lead, str(m["lead_confidence"]), m["texture"],
                             m["dynamic"], marks, m["cadence"], " ".join(m["chords"][:4])]))
    out.append("\n## METHOD NOTES")
    for k, v in facts.get("method_notes", {}).items():
        out.append(f"- {k}: {v}")
    return "\n".join(out)
