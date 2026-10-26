"""Guide generation with a fake API client (no network, no cost)."""
from types import SimpleNamespace

import pytest

from quartet_companion.facts import build_facts
from quartet_companion.guide.generate import generate_guide
from quartet_companion.io.abc import load_abc_movement


class FakeClient:
    """Returns one wrong guide first, then a corrected one."""

    def __init__(self, guides):
        self.guides = list(guides)
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        guide = self.guides.pop(0)
        block = SimpleNamespace(type="tool_use", id=f"tu_{len(self.calls)}", name="write_listening_guide", input=guide)
        usage = SimpleNamespace(input_tokens=1000, output_tokens=500, cache_read_input_tokens=0,
                                cache_creation_input_tokens=0)
        return SimpleNamespace(content=[block], usage=usage)


def _pad(points, n=4):
    """Guides need at least 4 points; pad with simple true points."""
    filler = {"start_measure": "1", "end_measure": "8", "headline": "", "text": "x", "focus_part": "Violin 1",
              "claims": [{"type": "key", "measure": "1", "value": "D major"}]}
    return points + [dict(filler, headline=f"filler {i}") for i in range(max(0, n - len(points)))]


def _point(headline, claims, start="1", end="8"):
    return {"start_measure": start, "end_measure": end, "headline": headline, "text": "Listen [m. 1].",
            "focus_part": "Violin 1", "claims": claims}


@pytest.fixture(scope="module")
def facts(abc_dir):
    return build_facts(load_abc_movement(abc_dir, "n05op18-5_03"))


def test_repair_loop_and_removal(facts):
    good = _point("Theme", [{"type": "key", "measure": "1", "value": "D major"}])
    bad = _point("Wrong", [{"type": "key", "measure": "1", "value": "C minor"}])
    first = {"title": "t", "overview": "o", "listening_points": _pad([good, bad]), "glossary": []}
    second = {"title": "t", "overview": "o", "listening_points": _pad([good, bad]), "glossary": []}   # still wrong
    client = FakeClient([first, second])
    res = generate_guide(facts, "en", model="fake", client=client)
    assert len(client.calls) == 2                       # one repair round
    assert "do not match" in str(client.calls[1]["messages"][-1]["content"][0]["content"])
    assert "Wrong" not in [p["headline"] for p in res.guide["listening_points"]]   # wrong point removed
    assert res.guide["listening_points"][0]["headline"] == "Theme"
    assert res.report["failed"] == 0 and res.report["removed_points"] == 1


def test_no_repair_when_all_claims_pass(facts):
    good = _point("Theme", [{"type": "section", "measure": "16", "value": "Var. 1"}], start="16", end="31")
    good["text"] = "Listen [m. 16]."
    client = FakeClient([{"title": "t", "overview": "o", "listening_points": _pad([good]), "glossary": []}])
    res = generate_guide(facts, "zh", model="fake", client=client)
    assert len(client.calls) == 1
    assert res.report["verified"] == 4
    # the facts block is marked for prompt caching
    assert client.calls[0]["messages"][0]["content"][0]["cache_control"] == {"type": "ephemeral"}


def test_list_returned_as_json_string_is_repaired(facts):
    import json
    good = _point("Theme", [{"type": "key", "measure": "1", "value": "D major"}])
    client = FakeClient([{"title": "t", "overview": "o", "listening_points": json.dumps(_pad([good])), "glossary": "[]"}])
    res = generate_guide(facts, "zh", model="fake", client=client)
    assert res.guide["listening_points"][0]["headline"] == "Theme"
    assert res.report["verified"] == 4


def test_empty_guide_is_retried(facts):
    good = _point("Theme", [{"type": "key", "measure": "1", "value": "D major"}])
    pts = [dict(good, headline=f"P{i}") for i in range(5)]
    empty = {"title": "t", "overview": "o", "listening_points": [], "glossary": []}
    full = {"title": "t", "overview": "o", "listening_points": pts, "glossary": []}
    client = FakeClient([empty, full])
    res = generate_guide(facts, "zh", model="fake", client=client)
    assert len(client.calls) == 2
    assert len(res.guide["listening_points"]) == 5


def test_thinking_blocks_are_not_sent_back(facts):
    """Thinking signatures are bound to one conversation; a repair round must not resend them."""
    good = _point("Theme", [{"type": "key", "measure": "1", "value": "D major"}])
    bad = _point("Wrong", [{"type": "key", "measure": "1", "value": "C minor"}])
    guide = {"title": "t", "overview": "o", "listening_points": _pad([good, bad]), "glossary": []}

    class ThinkingClient(FakeClient):
        def _create(self, **kw):
            resp = super()._create(**kw)
            thinking = SimpleNamespace(type="thinking", thinking="...", signature="sig")
            return SimpleNamespace(content=[thinking] + resp.content, usage=resp.usage)

    client = ThinkingClient([guide, dict(guide)])
    generate_guide(facts, "en", model="fake", client=client)
    assistant = client.calls[1]["messages"][1]
    assert assistant["role"] == "assistant"
    assert all(b["type"] != "thinking" for b in assistant["content"])


def test_prose_problems_are_sent_back(facts):
    """A point that calls a non-solo passage 'alone' is sent back once with the reason."""
    good = _point("Theme", [{"type": "key", "measure": "1", "value": "D major"}])
    loud = dict(good, headline="Alone", text="Violin 2 plays alone here [m. 20-24].", start="20", end="24")
    first = {"title": "t", "overview": "o", "listening_points": _pad([good, loud]), "glossary": []}
    fixed = {"title": "t", "overview": "o", "listening_points": _pad([good]), "glossary": []}
    client = FakeClient([first, fixed])
    res = generate_guide(facts, "en", model="fake", client=client)
    assert len(client.calls) == 2
    sent = str(client.calls[1]["messages"][-1]["content"][0]["content"])
    assert "alone" in sent and "say more than the facts" in sent
    assert res.report["prose_issues"] == []


def test_prose_check_rules():
    from quartet_companion.guide.prose_check import prose_issues
    ms = [{"label": str(i), "key": "C major", "texture": "melody + accompaniment", "lead_confidence": 1.0,
           "markings": [], "hairpins": []} for i in range(1, 11)]
    facts = {"measures": ms}
    pt = lambda text, claims=(): {"start_measure": "2", "end_measure": "6", "headline": "h", "text": text,
                                  "claims": list(claims)}
    issue = lambda text, lang="en", whole=False: prose_issues({"listening_points": [pt(text)]}, facts, lang, whole)
    assert issue("The key turns to F minor [m. 3].")              # key not in the facts
    assert not issue("It stays in C major [m. 3].")
    assert issue("The cello plays alone [m. 4].")                  # not solo
    assert issue("The music swells to loud [m. 5].")               # no crescendo marked
    assert issue("This is the loudest point [m. 5].")
    assert not issue("The analysis marks [m. 5] as the loudest point.")
    assert issue("全曲最安静的地方 [m. 5]。", "zh")
    assert not issue("全曲最安静的地方 [m. 5]。", "zh", True)
