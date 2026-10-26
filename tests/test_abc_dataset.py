"""Integration tests on the real ABC data (Beethoven Op. 18 No. 5)."""
import pytest

from quartet_companion.analysis.sections import find_sections
from quartet_companion.facts import build_facts
from quartet_companion.io.abc import load_abc_movement

PIECES = ["n05op18-5_01", "n05op18-5_02", "n05op18-5_03", "n05op18-5_04"]


@pytest.mark.parametrize("piece", PIECES)
def test_load_and_validate(abc_dir, piece):
    s = load_abc_movement(abc_dir, piece)
    assert s.validate() == []
    assert s.harmony is not None and len(s.harmony) > 50
    assert s.parts == ["Violin 1", "Violin 2", "Viola", "Cello"]


def test_variation_sections(abc_dir):
    s = load_abc_movement(abc_dir, "n05op18-5_03")
    names = find_sections(s)["name"].tolist()
    assert names[:6] == ["Theme", "Var. 1", "Var. 2", "Var. 3", "Var. 4", "Var. 5"]
    assert names[-1].startswith("Coda")


def test_home_keys(abc_dir):
    keys = {p: build_facts(load_abc_movement(abc_dir, p))["piece"]["home_key"] for p in PIECES}
    assert keys == {"n05op18-5_01": "A major", "n05op18-5_02": "A major",
                    "n05op18-5_03": "D major", "n05op18-5_04": "A major"}


def test_facts_are_self_consistent(abc_dir):
    f = build_facts(load_abc_movement(abc_dir, "n05op18-5_03"))
    labels = {m["label"] for m in f["measures"]}
    for occ in f["theme_occurrences"]:
        assert occ["start_label"] in labels
    for span in f["lead_spans"]:
        assert span["lead"] in f["piece"]["parts"] + ["none"]
    assert f["piece"]["harmony_source"] == "expert"
    assert len(f["variations"]) == 7
    assert f["variations"][0]["theme_tune_best_part"] == "Violin 1"
