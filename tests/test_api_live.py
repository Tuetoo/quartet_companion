"""Live API smoke test. Runs only with:  pytest -m api  (costs a few cents)."""
import os

import pytest

from quartet_companion.facts import build_facts
from quartet_companion.guide.generate import generate_guide
from quartet_companion.io.abc import load_abc_movement

pytestmark = pytest.mark.api


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY") and not os.path.exists(".env"), reason="no API key")
def test_live_guide_is_verified(abc_dir):
    facts = build_facts(load_abc_movement(abc_dir, "n05op18-5_02"))
    res = generate_guide(facts, "en")
    assert res.guide["listening_points"], "guide is empty"
    assert res.report["failed"] == 0
    assert res.report["verified"] >= len(res.guide["listening_points"])
