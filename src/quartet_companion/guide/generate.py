"""Write a listening guide with Claude, then check it.

Flow
----
1. Compact the fact sheet into text (compact.py).
2. Ask the model for a guide in a fixed JSON shape (via a forced tool
   call). Every listening point carries machine-checkable claims.
3. Verify every claim (verify.py).
4. If some claims fail, send the failures back once and ask for a fix.
5. Drop points that still fail, and save the verification report.

The API key is read from the environment or from a `.env` file
(ANTHROPIC_API_KEY=...). It is never printed or saved.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from .compact import compact_facts
from .prose_check import prose_issues
from .verify import CLAIM_TYPES, verify_guide

DEFAULT_MODEL = os.environ.get("QC_MODEL", "claude-sonnet-5-5")
MAX_TOKENS = 8000

LANGUAGE_NAMES = {"en": "English", "zh": "Simplified Chinese (简体中文)"}

GUIDE_TOOL = {
    "name": "write_listening_guide",
    "description": "Return the listening guide in a fixed structure.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "overview": {"type": "string", "description": "3-5 short sentences: what this movement is and what to listen for overall."},
            "overview_claims": {"type": "array", "items": {"$ref": "#/$defs/claim"}},
            "listening_points": {
                "type": "array",
                "description": "8-16 points in time order.",
                "items": {
                    "type": "object",
                    "properties": {
                        "start_measure": {"type": "string", "description": "measure label exactly as in the facts"},
                        "end_measure": {"type": "string"},
                        "headline": {"type": "string", "description": "max 10 words"},
                        "text": {"type": "string", "description": "2-4 short sentences. Mention measures as [m. 12] or [m. 12-16]."},
                        "focus_part": {"type": "string", "description": "a part name from the facts, or 'all'"},
                        "claims": {"type": "array", "items": {"$ref": "#/$defs/claim"}},
                    },
                    "required": ["start_measure", "end_measure", "headline", "text", "focus_part", "claims"],
                },
            },
            "glossary": {
                "type": "array",
                "items": {"type": "object", "properties": {"term": {"type": "string"}, "explanation": {"type": "string"}},
                          "required": ["term", "explanation"]},
            },
        },
        "required": ["title", "overview", "listening_points", "glossary"],
        "$defs": {
            "claim": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": CLAIM_TYPES},
                    "measure": {"type": "string", "description": "measure label exactly as in the facts"},
                    "value": {"type": "string", "description": "key name ('B minor'), part name ('Viola'), "
                              "texture label, dynamic ('pp', 'cresc'), cadence code ('PAC'), or section name"},
                },
                "required": ["type", "measure", "value"],
            }
        },
    },
}

SYSTEM_PROMPT = """You write listening guides for classical chamber music.
Your reader loves listening but has little music theory. Your job is to tell them what to listen for, and where.

Hard rules:
1. Use ONLY the facts provided. Never use outside knowledge about this piece (no history, dates, anecdotes, recordings).
2. Every musical statement must be backed by a claim object whose type, measure and value match the facts exactly.
   Use claim types: section, key, modulation, lead, theme, texture, dynamic, cadence, variation_tune, climax.
   Use "other" only for statements that cannot be checked (avoid them).
3. Measure labels must be copied exactly from the facts (e.g. "64b"). Refer to measures in the text as [m. 12] or [m. 12-16].
4. The lead part is a heuristic. If lead confidence is below 0.4, say "probably" or describe it as shared.
5. If harmony_source is "auto", say keys and chords are estimated.
   If the method notes say the score came from optical recognition with errors, prefer the big picture
   (sections, keys, who leads, loud/soft) over small rhythmic details, and say once that details may be imprecise.
6. Write in short, simple sentences. One idea per sentence. Explain any technical word in plain language the first time,
   and add it to the glossary.
7. Always return the result by calling the write_listening_guide tool, never as plain text.
8. Prefer what a listener can actually hear: who has the tune, louder/softer, busier/calmer, a change of key that
   brightens or darkens the mood, a return of the opening tune.
9. Say exactly what the facts say, no more:
   - "alone"/"solo"/独奏 only for measures whose texture is solo; otherwise say the others accompany.
   - A change is gradual ("swells", "fades", 渐强, 渐弱) only if a cresc/dim marking is there; otherwise it is sudden.
   - The loudest/busiest point is a computer estimate: say so ("the analysis marks ...").
   - A theme return "transposed 0 semitones" is at the same pitch as the opening, whatever the local key label says.
   - Do not add general knowledge about forms or genres ("a trio is usually calmer"), melodic direction, or how many
     notes or chords are played, unless the facts give it.
   - Empty measures in a score read by optical recognition may be recognition errors: do not present them as rests.
   - Texture "held" means no new note starts but earlier notes still sound: it is not silence. Only "tacet" is silence.
10. In Chinese use standard terms: 主调织体 (homophonic), 齐奏 only for unison/octaves, 强/弱 for f/p, 很强/很弱 for ff/pp,
    and 本乐章 (not 全曲) when the guide is about one movement.
"""


@dataclass
class GuideResult:
    guide: dict
    report: dict
    language: str
    model: str
    usage: list[dict] = field(default_factory=list)


def _client():
    try:
        from dotenv import load_dotenv
        for cand in [Path.cwd() / ".env", Path(__file__).resolve().parents[3] / ".env"]:
            if cand.exists():
                load_dotenv(cand, override=False)
                break
    except ImportError:
        pass
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Put it in a .env file in the project folder.")
    import anthropic
    return anthropic.Anthropic()


def _replay_content(content) -> list[dict]:
    """An assistant turn ready to send back in a later request.

    Thinking blocks are dropped: their signature is bound to the exact
    conversation they came from, and our retries change that conversation
    (the API then answers 400 "Invalid signature in thinking block")."""
    out = []
    for b in content:
        d = b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else dict(getattr(b, "__dict__", b))
        if d.get("type") in ("thinking", "redacted_thinking"):
            continue
        out.append(d)
    return out or [{"type": "text", "text": "(no answer)"}]


def create_with_tool(client, tool: dict, retries_without_tool: int = 2, validate=None, **kwargs):
    """Call the API and return (tool_use block, response).

    Some models do not accept a forced tool_choice. We ask with
    tool_choice "auto" and a clear instruction. If the model answers in plain
    text, or `validate(input)` returns an error message (e.g. an empty list),
    we tell it what is wrong and ask again.
    """
    messages = list(kwargs.pop("messages"))
    for attempt in range(retries_without_tool + 1):
        resp = _create_with_retries(client, tools=[tool], tool_choice={"type": "auto"}, messages=messages, **kwargs)
        block = next((b for b in resp.content if b.type == "tool_use" and b.name == tool["name"]), None)
        problem = None
        if block is None:
            problem = f"Please return your answer by calling the {tool['name']} tool."
        elif validate is not None:
            problem = validate(block.input)
        if problem is None:
            return block, resp
        if attempt == retries_without_tool:
            break
        content = _replay_content(resp.content)
        follow = ([{"type": "tool_result", "tool_use_id": block.id, "is_error": True, "content": problem}]
                  if block is not None else [{"type": "text", "text": problem}])
        messages = messages + [{"role": "assistant", "content": content}, {"role": "user", "content": follow}]
    if block is None:
        raise RuntimeError(f"the model did not call {tool['name']}")
    return block, resp


def _guide_problem(raw: dict) -> str | None:
    g = normalize_guide(raw)
    n = len(g["listening_points"])
    if n < 4:
        return (f"listening_points has {n} items. It must be a JSON array (not a string) of 8-16 objects, "
                "each with start_measure, end_measure, headline, text, focus_part and claims. "
                "Call the tool again with the complete guide.")
    return None


def _create_with_retries(client, **kwargs):
    for attempt in range(4):
        try:
            return client.messages.create(**kwargs)
        except Exception as exc:  # retry transient errors (overloaded, rate limits)
            name = type(exc).__name__
            if attempt == 3 or name not in ("RateLimitError", "InternalServerError", "APIConnectionError",
                                             "OverloadedError", "APITimeoutError"):
                raise
            time.sleep(5 * (attempt + 1))


def _call(client, model: str, facts_text: str, user_text: str, history: list | None = None):
    messages = [{"role": "user", "content": [
        {"type": "text", "text": "FACTS:\n" + facts_text, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": user_text},
    ]}]
    if history:
        messages += history
    block, resp = create_with_tool(client, GUIDE_TOOL, model=model, max_tokens=MAX_TOKENS,
                                   system=SYSTEM_PROMPT, messages=messages, validate=_guide_problem)
    # keep the assistant turn (without thinking blocks) for a repair round
    full = _replay_content(resp.content)
    usage = {"input": resp.usage.input_tokens, "output": resp.usage.output_tokens,
             "cache_read": getattr(resp.usage, "cache_read_input_tokens", 0) or 0,
             "cache_write": getattr(resp.usage, "cache_creation_input_tokens", 0) or 0}
    return block, usage, full


def normalize_guide(guide: dict) -> dict:
    """Models sometimes return a list as a JSON string; turn it back into a list."""
    guide = dict(guide)
    for key in ("listening_points", "glossary", "overview_claims"):
        val = guide.get(key)
        if isinstance(val, str):
            try:
                val = json.loads(val)
            except json.JSONDecodeError:
                val = []
        guide[key] = [x for x in (val or []) if isinstance(x, dict)]
    for p in guide["listening_points"]:
        if isinstance(p.get("claims"), str):
            try:
                p["claims"] = json.loads(p["claims"])
            except json.JSONDecodeError:
                p["claims"] = []
        p["claims"] = [c for c in (p.get("claims") or []) if isinstance(c, dict)]
        for k in ("start_measure", "end_measure"):
            if k in p:
                p[k] = str(p[k])
    return guide


def generate_guide(facts: dict, language: str = "en", model: str | None = None,
                   repair_rounds: int = 1, client=None) -> GuideResult:
    model = model or DEFAULT_MODEL
    client = client or _client()
    facts_text = compact_facts(facts)
    lang = LANGUAGE_NAMES.get(language, language)
    ask = (f"Write the listening guide in {lang}. Keep measure labels, part names in claims, and claim values in "
           f"English exactly as in the facts (only the prose is in {lang}). Return it with the tool.")
    block, usage, full = _call(client, model, facts_text, ask)
    usages = [usage]
    guide = normalize_guide(block.input)
    report = verify_guide(guide, facts)
    whole_piece = " – " not in str(facts.get("piece", {}).get("title", ""))
    prose = prose_issues(guide, facts, language, whole_piece)

    for _ in range(repair_rounds):
        if report.n_failed == 0 and not prose:
            break
        msg = []
        if report.n_failed:
            msg.append("These claims do not match the facts:\n" +
                       json.dumps(report.summary()["failures"], ensure_ascii=False, indent=1))
        if prose:
            msg.append("These sentences say more than the facts (fix the wording):\n" +
                       json.dumps(prose, ensure_ascii=False, indent=1))
        history = [
            {"role": "assistant", "content": full},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": block.id, "is_error": True,
                 "content": "\n\n".join(msg)},
                {"type": "text", "text": "Fix or remove the wrong statements (text AND claims). "
                                         "Return the complete corrected guide with the tool."}]},
        ]
        block, usage, full = _call(client, model, facts_text, ask, history)
        usages.append(usage)
        guide = normalize_guide(block.input)
        report = verify_guide(guide, facts)
        prose = prose_issues(guide, facts, language, whole_piece)

    # Remove points that still contain failed claims, so nothing wrong reaches the reader.
    failed_points = {r.claim.get("point") for r in report.results if r.status == "failed"}
    if failed_points or report.bad_labels:
        bad = set(report.bad_labels)
        kept = [p for p in guide.get("listening_points", [])
                if p.get("headline") not in failed_points
                and str(p.get("start_measure")) not in bad and str(p.get("end_measure")) not in bad]
        removed = len(guide.get("listening_points", [])) - len(kept)
        guide["listening_points"] = kept
        summary = report.summary()
        summary["removed_points"] = removed
    else:
        summary = report.summary()
        summary["removed_points"] = 0
    final = verify_guide(guide, facts).summary()
    final["removed_points"] = summary["removed_points"]
    final["before_removal"] = {k: summary[k] for k in ("verified", "failed", "unchecked")}
    # prose problems left after the repair round are reported (shown by `qc guide`), not hidden
    final["prose_issues"] = prose_issues(guide, facts, language, whole_piece)
    return GuideResult(guide=guide, report=final, language=language, model=model, usage=usages)


def facts_fingerprint(facts: dict) -> str:
    """Short id of the facts a guide was checked against (measure labels, sections, keys).
    If the score changes, the old guide no longer fits and the player hides it."""
    import hashlib
    core = {"labels": [m.get("label") for m in facts.get("measures", [])],
            "sections": [(s.get("name"), s.get("start_label")) for s in facts.get("sections", [])],
            "keys": [(k.get("key_name"), k.get("start_label")) for k in facts.get("key_plan", [])]}
    return hashlib.sha1(json.dumps(core, sort_keys=True).encode()).hexdigest()[:12]


def save_guide(result: GuideResult, path: str | Path, facts: dict | None = None) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    data = {"language": result.language, "model": result.model, "verification": result.report,
            "usage": result.usage, "guide": result.guide}
    if facts is not None:
        data["facts_fingerprint"] = facts_fingerprint(facts)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=1))
