"""Answer a listener's question about one movement, using only the facts."""
from __future__ import annotations

from dataclasses import dataclass

from .compact import compact_facts
from .generate import DEFAULT_MODEL, GUIDE_TOOL, _client, create_with_tool
from .verify import Verifier

ANSWER_TOOL = {
    "name": "answer_question",
    "description": "Answer the listener's question.",
    "input_schema": {
        "type": "object",
        "properties": {
            "answer": {"type": "string", "description": "Short, simple sentences. Mention measures as [m. 12]."},
            "claims": {"type": "array", "items": GUIDE_TOOL["input_schema"]["$defs"]["claim"]},
            "cannot_answer_from_facts": {"type": "boolean",
                                         "description": "true if the facts do not contain what is needed"},
        },
        "required": ["answer", "claims", "cannot_answer_from_facts"],
    },
}

ASK_SYSTEM = """You answer questions about one movement of chamber music for a curious listener.
Use ONLY the facts provided. If the facts cannot answer the question (for example history, the composer's life,
or emotions that the facts do not support), say so honestly and set cannot_answer_from_facts=true.
Back every musical statement with a claim (type, measure label exactly as in the facts, value).
Keep claim values short: for lead, theme and variation_tune claims the value is only the part name (e.g. "Viola").
Write short, simple sentences. Answer in the same language as the question.
Always answer by calling the answer_question tool."""


@dataclass
class Answer:
    answer: str
    claims: list[dict]
    verification: list[dict]
    cannot_answer: bool


def ask(facts: dict, question: str, model: str | None = None, client=None) -> Answer:
    client = client or _client()
    block, _ = create_with_tool(
        client, ANSWER_TOOL, model=model or DEFAULT_MODEL, max_tokens=2000, system=ASK_SYSTEM,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": "FACTS:\n" + compact_facts(facts), "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": "QUESTION: " + question}]}])
    data = dict(block.input)
    if isinstance(data.get("claims"), str):
        import json
        try:
            data["claims"] = json.loads(data["claims"])
        except json.JSONDecodeError:
            data["claims"] = []
    data["claims"] = [c for c in data.get("claims") or [] if isinstance(c, dict)]
    v = Verifier(facts)
    checks = [{"claim": c, "status": r.status, "reason": r.reason}
              for c in data.get("claims", []) for r in [v.check(c)]]
    return Answer(answer=data.get("answer", ""), claims=data.get("claims", []), verification=checks,
                  cannot_answer=bool(data.get("cannot_answer_from_facts")))
