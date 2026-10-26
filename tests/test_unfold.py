from quartet_companion.unfold import measure_timeline, playing_orders, unfolded_notes
from conftest import make_score


def _volta_score():
    # m1 m2 |: m3 m4 [1. m5 :| [2. m6 ] m7
    nxt = [[2], [3], [4], [5, 6], [3], [7], [-1]]
    volta = [0, 0, 0, 0, 1, 2, 0]
    rows = [(m, 0, 4.0, 0, 60 + m) for m in range(1, 8)]
    s = make_score(rows, 7, next_=nxt, volta=volta)
    return s


def test_labels_for_endings():
    s = _volta_score()
    # endings share a printed number in real scores; here mn differ but volta marks them
    assert s.measures["label"].tolist()[4] == "5a"


def test_all_and_no_repeats():
    s = _volta_score()
    orders = {o.name: o.mcs for o in playing_orders(s)}
    assert orders["all_repeats"] == [1, 2, 3, 4, 5, 3, 4, 6, 7]
    assert orders["no_repeats"] == [1, 2, 3, 4, 6, 7]


def test_unfolded_positions_are_continuous():
    s = _volta_score()
    order = playing_orders(s)[0]
    tl = measure_timeline(s, order)
    assert (tl["perf_start_qb"].diff().dropna() == 4.0).all()
    notes = unfolded_notes(s, order)
    assert len(notes) == len(order.mcs)
    assert notes["perf_qb"].is_monotonic_increasing


def test_da_capo_order():
    nxt = [[2], [3], [4], [-1]]
    events = [{"mc": 3, "mn": 3, "onset_qb": 8.0, "part": 0, "kind": "text", "value": "Trio"},
              {"mc": 4, "mn": 4, "onset_qb": 12.0, "part": 0, "kind": "text", "value": "Menuetto D.C."}]
    s = make_score([(m, 0, 4.0, 0, 60) for m in range(1, 5)], 4, next_=nxt, events=events)
    names = [o.name for o in playing_orders(s)]
    assert names[0].endswith("+dc")
    assert playing_orders(s)[0].mcs == [1, 2, 3, 4, 1, 2]


def test_mixed_repeat_combinations():
    # |: m1 :| |: m2 :| m3
    nxt = [[1, 2], [2, 3], [-1]]
    s = make_score([(m, 0, 4.0, 0, 60) for m in range(1, 4)], 3, next_=nxt)
    orders = {o.name: o.mcs for o in playing_orders(s)}
    assert orders["all_repeats"] == [1, 1, 2, 2, 3]
    assert orders["no_repeats"] == [1, 2, 3]
    assert [1, 1, 2, 3] in orders.values()
    assert [1, 2, 2, 3] in orders.values()
