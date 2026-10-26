"""Alignment on synthesized audio with a known, uneven tempo."""
import numpy as np
import soundfile as sf

from quartet_companion.align.pipeline import align_score_to_audio
from quartet_companion.align.synth import render, tempo_curve
from quartet_companion.io.abc import load_abc_movement
from quartet_companion.unfold import measure_timeline, playing_orders, unfolded_notes


def _run(abc_dir, tmp_path, piece, which, seed=3):
    s = load_abc_movement(abc_dir, piece)
    order = playing_orders(s)[which]
    tl = measure_timeline(s, order)
    f = tempo_curve(tl["perf_end_qb"].iloc[-1], base_qpm=100, wobble=0.2, seed=seed)
    y = render(unfolded_notes(s, order), f, lead_in=2.0)
    wav = tmp_path / "x.wav"
    sf.write(wav, y, 22050)
    r = align_score_to_audio(s, str(wav))
    return r, order, f(tl["perf_start_qb"].values) + 2.0


def test_variations_all_repeats(abc_dir, tmp_path):
    r, order, truth = _run(abc_dir, tmp_path, "n05op18-5_03", 0)
    assert r.order == order.name
    assert r.trimmed_range is None          # nothing extra in the audio: nothing cut
    err = np.abs(r.measure_times["start_sec"].values - truth)
    assert np.median(err) < 0.06 and np.percentile(err, 95) < 0.2


def test_menuetto_detects_skipped_repeats(abc_dir, tmp_path):
    s = load_abc_movement(abc_dir, "n05op18-5_02")
    idx = [o.name for o in playing_orders(s)].index("no_repeats+dc")
    r, order, truth = _run(abc_dir, tmp_path, "n05op18-5_02", idx, seed=5)
    assert r.order == "no_repeats+dc"
    err = np.abs(r.measure_times["start_sec"].values - truth)
    assert np.median(err) < 0.06


def test_extra_music_after_the_movement_is_cut(abc_dir, tmp_path):
    """Audio range that also holds the start of the next movement (after a pause)."""
    s = load_abc_movement(abc_dir, "n05op18-5_03")
    order = playing_orders(s)[0]
    tl = measure_timeline(s, order)
    f = tempo_curve(tl["perf_end_qb"].iloc[-1], base_qpm=100, wobble=0.2, seed=3)
    y = render(unfolded_notes(s, order), f, lead_in=2.0, tail=6.0)   # gap like between movements
    nxt = load_abc_movement(abc_dir, "n05op18-5_04")
    o2 = playing_orders(nxt)[0]
    g = tempo_curve(measure_timeline(nxt, o2)["perf_end_qb"].iloc[-1], base_qpm=120, seed=1)
    y2 = render(unfolded_notes(nxt, o2), g, lead_in=0.0)[: 22050 * 90]   # 90 s of the next movement
    wav = tmp_path / "x.wav"
    sf.write(wav, np.concatenate([y, y2]), 22050)
    r = align_score_to_audio(s, str(wav))
    assert r.trimmed_range is not None
    truth = f(tl["perf_start_qb"].values) + 2.0
    err = np.abs(r.measure_times["start_sec"].values - truth)
    assert np.median(err) < 0.06 and np.percentile(err, 95) < 0.2
    # the last bar must not spill into the next movement
    assert r.measure_times["end_sec"].values[-1] < len(y) / 22050
