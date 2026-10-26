from quartet_companion.analysis.texture import analyse_texture
from quartet_companion.analysis.themes import extract_theme, find_matches, is_distinctive
from conftest import make_score


def test_lead_is_the_moving_part_not_the_highest(melody_in_viola_score):
    t = analyse_texture(melody_in_viola_score)
    assert (t["lead"] == 2).all(), t
    assert set(t["texture"]) == {"melody + accompaniment"}


def test_silent_measure_has_no_lead():
    rows = [(1, b, 1.0, 0, 60 + b) for b in range(4)]
    s = make_score(rows, 2)
    t = analyse_texture(s)
    assert t.loc[t["mc"] == 2, "lead"].iloc[0] == -1
    assert t.loc[t["mc"] == 2, "texture"].iloc[0] == "tacet"
    assert t.loc[t["mc"] == 1, "texture"].iloc[0] == "solo"


def test_theme_found_transposed_in_other_part():
    tune = [60, 64, 67, 65, 64, 62, 60, 67, 72]
    rows = [(1 + i // 4, (i % 4) * 1.0, 1.0, 0, p) for i, p in enumerate(tune)]
    # cello plays it a fifth lower (-7) starting in measure 4
    rows += [(4 + i // 4, (i % 4) * 1.0, 1.0, 3, p - 7 - 12) for i, p in enumerate(tune)]
    s = make_score(rows, 7)
    theme = extract_theme(s, 0, 1)
    assert is_distinctive(theme)
    ms = find_matches(s, theme)
    kinds = {(m.part, m.kind, m.transposition) for m in ms}
    assert (0, "original", 0) in kinds
    assert (3, "exact", -19) in kinds


def test_inverted_theme():
    tune = [60, 62, 64, 65, 67, 65, 64, 62, 60]
    inv = [72 - (p - 60) for p in tune]
    rows = [(1 + i // 4, (i % 4) * 1.0, 1.0, 0, p) for i, p in enumerate(tune)]
    rows += [(4 + i // 4, (i % 4) * 1.0, 1.0, 1, p) for i, p in enumerate(inv)]
    s = make_score(rows, 7)
    ms = find_matches(s, extract_theme(s, 0, 1))
    assert any(m.kind == "inverted" and m.part == 1 for m in ms)


def test_repeated_note_theme_is_not_distinctive():
    rows = [(1, b, 1.0, 0, 60) for b in range(4)] + [(2, b, 1.0, 0, 60) for b in range(4)]
    s = make_score(rows, 2)
    assert not is_distinctive(extract_theme(s, 0, 1))
