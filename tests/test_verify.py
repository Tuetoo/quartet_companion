import pytest

from quartet_companion.facts import build_facts
from quartet_companion.guide.compact import compact_facts
from quartet_companion.guide.verify import Verifier, norm_key, verify_guide
from quartet_companion.io.abc import load_abc_movement


@pytest.fixture(scope="module")
def facts(abc_dir):
    return build_facts(load_abc_movement(abc_dir, "n05op18-5_03"))


def test_norm_key():
    assert norm_key("B minor") == norm_key("b min") == "b minor"
    assert norm_key("F♯ major") == "f# major"
    assert norm_key("Bb") == "bb major"


def test_true_claims_pass(facts):
    v = Verifier(facts)
    assert v.check({"type": "section", "measure": "16", "value": "Var. 1"}).status == "verified"
    assert v.check({"type": "key", "measure": "1", "value": "D major"}).status == "verified"
    assert v.check({"type": "variation_tune", "measure": "64", "value": "Violin 1"}).status == "verified"
    assert v.check({"type": "other", "measure": "1", "value": "anything"}).status == "unchecked"


def test_false_claims_fail(facts):
    v = Verifier(facts)
    assert v.check({"type": "key", "measure": "1", "value": "C minor"}).status == "failed"
    assert v.check({"type": "section", "measure": "1", "value": "Var. 4"}).status == "failed"
    assert v.check({"type": "key", "measure": "999", "value": "D major"}).status == "failed"
    assert v.check({"type": "dynamic", "measure": "1", "value": "fff"}).status == "failed"


def test_verify_guide_flags_bad_measure_tags(facts):
    guide = {"listening_points": [{"start_measure": "1", "end_measure": "8", "headline": "x",
                                   "text": "Listen at [m. 3] and [m. 777].", "focus_part": "Violin 1",
                                   "claims": [{"type": "key", "measure": "1", "value": "D major"}]}]}
    rep = verify_guide(guide, facts)
    assert rep.n_verified == 1
    assert "777" in rep.bad_labels


def test_compact_facts_is_reasonably_small(facts):
    text = compact_facts(facts)
    assert "MEASURE TABLE" in text and "Var. 1" in text
    assert len(text) < 60000
