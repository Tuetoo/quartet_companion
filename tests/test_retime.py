import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location("retime", Path(__file__).parents[1] / "scripts" / "retime.py")
retime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(retime)


def _bars(n=5, bar=2.0):
    return [{"label": str(i + 1), "start_sec": i * bar, "end_sec": (i + 1) * bar,
             "perf_start_qb": 4.0 * i, "perf_end_qb": 4.0 * (i + 1), "tempo_qpm": 120.0} for i in range(n)]


def test_set_moves_last_bars_and_keeps_bars_contiguous():
    ms = _bars()
    # the last bar comes later than the old end of the movement: must not be refused
    retime._apply_starts(ms, {3: 6.5, 4: 11.0}, end=13.0)
    assert [m["start_sec"] for m in ms] == [0.0, 2.0, 4.0, 6.5, 11.0]
    assert ms[2]["end_sec"] == 6.5 and ms[3]["end_sec"] == 11.0 and ms[4]["end_sec"] == 13.0
    assert ms[3]["tempo_qpm"] == pytest.approx(60 * 4 / 4.5, abs=0.1)


def test_set_refuses_bars_out_of_order():
    ms = _bars()
    with pytest.raises(SystemExit):
        retime._apply_starts(ms, {2: 9.0})          # bar 3 would start after bar 4


def test_index_takes_the_last_time_a_bar_is_played():
    ms = _bars(3) + _bars(3)
    assert retime._index(ms, "2") == 4
    with pytest.raises(SystemExit):
        retime._index(ms, "99")
