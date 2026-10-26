"""Align a score with a recording: when does each measure start?

Usage
-----
>>> result = align_score_to_audio(score, "recording.mp3")
>>> result.measure_times.head()     # occurrence, mc, label, start_sec, end_sec, ...

Steps
-----
1. Load the audio (optionally only a time range), trim silence.
2. Build candidate playing orders (all repeats / no repeats / Da Capo ...).
3. Coarse DTW for each candidate; keep the one that fits best.
   If `search_long_recording` is set, we first search where the movement
   sits inside the recording (subsequence DTW over several tempos).
4. Fine DTW in a narrow band around the coarse path.
5. Read off the start time of every played measure; flag measures where
   the match is poor so a person can check them.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..score import Score
from ..unfold import PlayingOrder, measure_timeline, playing_orders, unfolded_notes
from . import dtw as dtw_mod
from .tempo import metronome_marks, tempo_by_measure, tempo_marking_kind, warp_function, warp_notes
from .features import FRAME_SEC, audio_chroma, audio_onset_curve, load_audio, score_chroma

FINE_POOL = 2          # 2 x 23 ms  = 46 ms
COARSE_POOL = 8        # 8 x 23 ms  = 186 ms
FINE_RADIUS_SEC = 2.5
# Measured on synthesized audio with exactly known timing: the chroma/onset
# features place note starts about 55 ms late. We subtract that constant.
LATENCY_CORRECTION_SEC = 0.055
OPEN_SEC = 4.0          # music may start/end up to 4 s inside the (trimmed) audio
MAX_TEMPO_CHECKS = 12   # tied repeat patterns checked against the tempo marks
NEAR_TIE = 0.01         # coarse costs this close count as a tie between repeat patterns
FINE_NEAR_TIE = 0.002   # fine-match costs this close count as a tie
COVER_TIE_SEC = 2.0     # patterns covering the audio within this many seconds of each other tie
EDGE_MARGIN_SEC = 2.0   # kept around the music when extra audio is cut off
EDGE_MIN_SHARE = 0.5    # the found music must cover at least this share of the audio
EDGE_MIN_GAIN = 0.015   # cutting must improve the match by at least 1.5 %
EDGE_OPEN_SEC = 6.0     # after such a cut both ends are known well: less freedom at the ends
EDGE_SNAP_SEC = 5.0     # search for the boundary pause near the found edge (3x this outward)


@dataclass
class AlignmentResult:
    audio_path: str
    order: str
    order_description: str
    segment_start_sec: float
    segment_end_sec: float
    cost: float
    candidate_costs: dict
    measure_times: pd.DataFrame
    warnings: list[str] = field(default_factory=list)
    trimmed_range: tuple[float, float] | None = None   # set when extra audio was cut off

    def to_dict(self) -> dict:
        extra = {"trimmed_range": list(self.trimmed_range)} if self.trimmed_range else {}
        return {**extra,
            "audio_path": self.audio_path, "order": self.order,
            "order_description": self.order_description,
            "segment_start_sec": round(self.segment_start_sec, 3),
            "segment_end_sec": round(self.segment_end_sec, 3),
            "cost": round(self.cost, 4), "candidate_costs": {k: round(v, 4) for k, v in self.candidate_costs.items()},
            "warnings": self.warnings,
            "measures": self.measure_times.to_dict("records"),
        }


def _pool(x: np.ndarray, k: int) -> np.ndarray:
    n = x.shape[-1] // k
    if n == 0:
        return x
    if x.ndim == 1:
        return x[: n * k].reshape(n, k).mean(axis=1)
    y = x[:, : n * k].reshape(x.shape[0], n, k).mean(axis=2)
    norm = np.linalg.norm(y, axis=0, keepdims=True)
    return y / np.maximum(norm, 1e-9)


def _score_feats(notes: pd.DataFrame, total_qb: float, n_frames: int):
    fpq = n_frames / total_qb
    sx, so = score_chroma(notes, total_qb, fpq)
    sx, so = sx[:, :n_frames], so[:n_frames]
    if sx.shape[1] < n_frames:   # rounding
        pad = n_frames - sx.shape[1]
        sx = np.pad(sx, ((0, 0), (0, pad)), mode="edge")
        so = np.pad(so, (0, pad))
    return sx, so, fpq


def _trim(y: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Cut quiet lead-in / tail. Threshold adapts to the recording's noise floor."""
    import librosa
    from .features import SR
    hop = 512
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    db = 20 * np.log10(np.maximum(rms, 1e-10))
    thr = min(max(np.percentile(db, 0.5) + 10, db.max() - 60), db.max() - 30)
    loud = db > thr
    # require ~0.3 s of sound so a click does not count as the start
    k = max(1, int(0.3 * SR / hop))
    run = np.convolve(loud.astype(int), np.ones(k, dtype=int), mode="valid")
    idx = np.nonzero(run == k)[0]
    if len(idx) == 0:
        return y, 0.0, len(y) / SR
    first = idx[0]
    last = idx[-1] + k
    a = max(0, first * hop - int(0.1 * SR))
    b = min(len(y), last * hop + 2048 + int(0.1 * SR))
    a, b = _trim_applause(y, a, b)
    return y[a:b], a / SR, b / SR


APPLAUSE_FLATNESS = 0.03   # applause measured ~0.09; string playing 0.0003-0.01 (tuning, room noise below 0.03)


def _trim_applause(y: np.ndarray, a: int, b: int) -> tuple[int, int]:
    """Move the ends inward past applause (noise-like sound) at the start or end of a
    live recording, one second at a time. Music never looks this noise-like."""
    import librosa
    from .features import SR
    sec = SR
    def noisy(i0: int) -> bool:
        seg = y[i0:i0 + sec]
        if len(seg) < sec // 2:
            return False
        return float(np.median(librosa.feature.spectral_flatness(y=seg, n_fft=2048, hop_length=512)[0])) > APPLAUSE_FLATNESS
    while b - a > 20 * sec and noisy(b - sec):
        b -= sec
    while b - a > 20 * sec and noisy(a):
        a += sec
    return a, b


def quiet_runs(y: np.ndarray, min_sec: float = 2.0) -> list[tuple[float, float]]:
    """Quiet stretches (pauses between movements are among them)."""
    import librosa
    from .features import SR
    hop = SR // 10
    rms = librosa.feature.rms(y=y, frame_length=4096, hop_length=hop)[0]
    db = 20 * np.log10(np.maximum(rms, 1e-10))
    sm = np.convolve(db, np.ones(10) / 10, mode="same")
    quiet = sm < np.percentile(sm, 2) + 12
    runs, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        if (not q or i == len(quiet) - 1) and start is not None:
            if (i - start) / 10 >= min_sec:
                runs.append((start / 10, i / 10))
            start = None
    return runs


def bar_note_similarity(score: Score, timeline: pd.DataFrame, chroma: np.ndarray, t0: float) -> np.ndarray:
    """For each played bar: how well the written notes (pitch classes with overtones,
    weighted by length) agree with the sound during that bar's aligned time span
    (cosine, 0..1). Unlike match_cost this is measured after alignment, so time
    warping cannot hide a misread bar. chroma frame 0 is at time t0 (seconds)."""
    from .features import OVERTONES, FRAME_SEC as FS
    notes = score.notes
    prof: dict[int, np.ndarray] = {}
    for mc, g in notes.groupby("mc"):
        h = np.zeros(12)
        for o, w in OVERTONES:
            np.add.at(h, (g["midi"].values.astype(int) + o) % 12, w * g["dur_qb"].values)
        prof[int(mc)] = h
    out = np.full(len(timeline), np.nan)
    for i, (mc, a_sec, b_sec) in enumerate(zip(timeline["mc"], timeline["start_sec"], timeline["end_sec"])):
        h = prof.get(int(mc))
        a, b = int((a_sec - t0) / FS), int(np.ceil((b_sec - t0) / FS))
        if h is None or not h.any() or b <= a or a < 0 or b > chroma.shape[1]:
            continue
        v = chroma[:, a:b].mean(axis=1)
        out[i] = float(h @ v / (np.linalg.norm(h) * np.linalg.norm(v) + 1e-9))
    return out


def movement_gaps(y: np.ndarray) -> list[tuple[float, float]]:
    """Near-silent gaps of the kind found between movements: at least 4 s more than
    25 dB below the music's loud level, with at least 2 s more than 30 dB below.
    Calibrated on real recordings: gaps between movements measured 4.7-6.3 s (2.4-5.2 s
    below -30 dB); pauses inside movements at most 3.6 s (1.5 s)."""
    import librosa
    from .features import SR
    hop = SR // 10
    rms = librosa.feature.rms(y=y, frame_length=2 * hop, hop_length=hop)[0]
    db = 20 * np.log10(np.maximum(rms, 1e-10))
    rel = db - np.percentile(db, 95)
    out, start = [], None
    for i, v in enumerate(np.append(rel, 0.0)):
        if v < -25 and start is None:
            start = i
        elif v >= -25 and start is not None:
            if (i - start) >= 40:
                deep = rel[start:i] < -30
                best = cur = 0
                for d in deep:
                    cur = cur + 1 if d else 0
                    best = max(best, cur)
                if best >= 20:
                    out.append((start / 10, i / 10))
            start = None
    return out


def _extra_audio(notes: pd.DataFrame, total_qb: float, ax_c: np.ndarray, ao_c: np.ndarray,
                 coarse_sec: float, y: np.ndarray, t_a: float, allowed_sec: float):
    """Is there other music before/after the movement inside the audio?

    Returns (lead_cut, tail_cut, new_start, new_end) in seconds from the trimmed audio
    start, or None. Both tests must agree: (1) matching the score with free ends
    finds it clearly inside the audio and cutting the rest makes the match clearly
    better (calibrated: well-cut movements gain <= 0.003, extra music >= 0.05);
    (2) there is a real gap where we cut (see movement_gaps). Test (1) alone is not
    enough: on complete one-movement recordings it sometimes "finds" a shorter match
    (MusicNet Op.127/IV, Op.130/III), so (2) carries most of the weight."""
    n = ax_c.shape[1]
    sx, so, _ = _score_feats(notes, total_qb, n)
    C = dtw_mod.cost_matrix(sx, ax_c, so, ao_c)
    a, b, _ = dtw_mod.locate_subsequence(C)
    lead, tail = a * coarse_sec, (n - 1 - b) * coarse_sec
    if (lead <= allowed_sec and tail <= allowed_sec) or (b - a + 1) < EDGE_MIN_SHARE * n:
        return None
    open_frames = int(OPEN_SEC / coarse_sec)
    full = dtw_mod.slope_cost(C, open_frames=open_frames)
    sx2, so2, _ = _score_feats(notes, total_qb, b - a + 1)
    part = dtw_mod.slope_cost(dtw_mod.cost_matrix(sx2, ax_c[:, a:b + 1], so2, ao_c[a:b + 1]),
                              open_frames=open_frames)
    if not np.isfinite(full) or (full - part) / max(full, 1e-9) < EDGE_MIN_GAIN:
        return None
    runs = [(q0 - t_a, q1 - t_a) for q0, q1 in movement_gaps(y)]
    new_a, new_b = 0.0, n * coarse_sec
    cut_lead = cut_tail = 0.0
    if tail > allowed_sec:
        b_sec = (b + 1) * coarse_sec
        # the free-end match tends to stop early (soft last chords match poorly),
        # so look further forward than back; the longest pause is the boundary
        near = [r for r in runs if b_sec - EDGE_SNAP_SEC <= r[0] <= b_sec + 3 * EDGE_SNAP_SEC]
        if near:
            r = max(near, key=lambda r: r[1] - r[0])
            new_b = min(r[1], r[0] + EDGE_MARGIN_SEC)
            cut_tail = n * coarse_sec - new_b
    if lead > allowed_sec:
        a_sec = a * coarse_sec
        near = [r for r in runs if a_sec - 3 * EDGE_SNAP_SEC <= r[1] <= a_sec + EDGE_SNAP_SEC]
        if near:
            r = max(near, key=lambda r: r[1] - r[0])
            new_a = max(r[0], r[1] - EDGE_MARGIN_SEC)
            cut_lead = new_a
    if cut_lead <= allowed_sec and cut_tail <= allowed_sec:
        return None
    return cut_lead, cut_tail, new_a, new_b


def candidate_segments(y: np.ndarray, expected_sec: float, lo: float = 0.4, hi: float = 2.5) -> list[tuple[float, float]]:
    """Stretches between pauses whose length could be this movement."""
    from .features import SR
    total = len(y) / SR
    runs = quiet_runs(y)
    starts = [0.0] + [b for _, b in runs]
    ends = [a for a, _ in runs] + [total]
    out = []
    for s0 in starts:
        for e0 in ends:
            if e0 > s0 and lo * expected_sec <= e0 - s0 <= hi * expected_sec:
                out.append((s0, e0))
    return out or [(0.0, total)]


def locate_in_long_recording(score: Score, ax_c: np.ndarray, ao_c: np.ndarray, order: PlayingOrder,
                             coarse_sec: float) -> tuple[int, int, float, float]:
    """Find (start_frame, end_frame, cost, speed factor) of the movement inside a long recording."""
    qb_pts, sec_pts = warp_function(score, order)
    notes = warp_notes(unfolded_notes(score, order), qb_pts, sec_pts)
    total = float(sec_pts[-1])
    best = (0, ax_c.shape[1], np.inf, 0.0)
    for factor in np.geomspace(0.5, 2.2, 14):        # performers are 0.5x - 2.2x the guessed speed
        dur_sec = total * factor
        n = int(dur_sec / coarse_sec)
        if n < 20 or n > ax_c.shape[1] * 1.1:
            continue
        sx, so, _ = _score_feats(notes, total, n)
        C = dtw_mod.cost_matrix(sx, ax_c, so, ao_c)
        a, b, cost = dtw_mod.locate_subsequence(C)
        if cost < best[2]:
            best = (a, b + 1, cost, float(factor))
    return best


def align_score_to_audio(score: Score, audio_path: str, start_sec: float | None = None,
                         end_sec: float | None = None, search_long_recording: bool = False,
                         orders: list[PlayingOrder] | None = None,
                         open_sec: float | None = None, tempo_hint_qpm: float | None = None,
                         repeats_uncertain: bool = False, check_edges: bool = True) -> AlignmentResult:
    """open_sec: how far inside the (trimmed) audio the music may start or end.
    Default 4 s; use more when the audio range is only roughly known.
    tempo_hint_qpm: rough written tempo when the score file has none (helps choose repeats).
    repeats_uncertain: the repeat signs themselves may be wrong (e.g. read by OMR): when two
    patterns fit almost equally, prefer the one with fewer repeats.
    check_edges: look for other music at the ends of the audio range and cut it off (for
    ranges set by hand). Ranges found by the movement splitter already sit at real
    pauses; there this check only adds risk (a quiet slow introduction can look like a
    gap), so the splitter's ranges are aligned without it."""
    offset = float(start_sec or 0.0)
    duration = (end_sec - offset) if end_sec is not None else None
    y = load_audio(audio_path, offset=offset, duration=duration)
    warnings: list[str] = []
    if len(y) < 22050:
        raise ValueError("audio is shorter than one second")

    orders = orders or playing_orders(score)
    base_chroma = audio_chroma(y)
    base_onset = audio_onset_curve(y)
    ax_c, ao_c = _pool(base_chroma, COARSE_POOL), _pool(base_onset, COARSE_POOL)
    coarse_sec = FRAME_SEC * COARSE_POOL

    seg_a, seg_b = 0.0, len(y) / 22050
    if search_long_recording:
        # Try every stretch between pauses that has a plausible length, with every
        # repeat pattern, and keep the one that matches best (tempo-limited DTW).
        cands = []
        for order in orders:
            qb_pts, sec_pts = warp_function(score, order)
            notes_w = warp_notes(unfolded_notes(score, order), qb_pts, sec_pts)
            expected = float(sec_pts[-1])
            for a_sec, b_sec in candidate_segments(y, expected):
                a, b = int(a_sec / coarse_sec), int(np.ceil(b_sec / coarse_sec))
                seg_c, seg_o = ax_c[:, a:b], ao_c[a:b]
                if seg_c.shape[1] < 20:
                    continue
                sx, so, _ = _score_feats(notes_w, expected, seg_c.shape[1])
                cost = dtw_mod.slope_cost(dtw_mod.cost_matrix(sx, seg_c, so, seg_o),
                                          open_frames=int(OPEN_SEC / coarse_sec))
                cands.append((cost, a_sec, b_sec, order.name))
        cands.sort()
        _, seg_a, seg_b, _ = cands[0]
        y = y[int(seg_a * 22050): int(seg_b * 22050)]
        base_chroma = audio_chroma(y)
        base_onset = audio_onset_curve(y)
    # Trim silence (applause, empty lead-in) so the ends line up.
    y_trim, t_a, t_b = _trim(y)
    if len(y_trim) < len(y):
        k0 = int(t_a / FRAME_SEC)
        k1 = int(np.ceil(t_b / FRAME_SEC))
        base_chroma, base_onset = base_chroma[:, k0:k1], base_onset[k0:k1]
    else:
        t_a = 0.0
    seg_start = offset + seg_a + t_a

    ax_c, ao_c = _pool(base_chroma, COARSE_POOL), _pool(base_onset, COARSE_POOL)
    ax_f, ao_f = _pool(base_chroma, FINE_POOL), _pool(base_onset, FINE_POOL)
    open_frames = int((open_sec if open_sec is not None else OPEN_SEC) / coarse_sec)

    # ------------------------------------------------ pick the playing order
    costs: dict[str, float] = {}
    coarse: dict[str, tuple] = {}
    for order in orders:
        # Score time may be warped by the written tempo (slow sections take longer).
        # Markings can mislead, so we also try an even (unwarped) time line.
        qb_w, sec_w = warp_function(score, order, tempo_hint_qpm)
        uniform = (qb_w, qb_w.copy())
        variants = [("tempo", (qb_w, sec_w))]
        if not np.allclose(np.diff(sec_w) / np.maximum(np.diff(qb_w), 1e-9),
                           (sec_w[-1] / max(qb_w[-1], 1e-9)), rtol=0.05):
            variants.append(("even", uniform))
        else:
            variants = [("even", uniform)]
        raw_notes = unfolded_notes(score, order)
        for vname, (qb_pts, sec_pts) in variants:
            notes = warp_notes(raw_notes, qb_pts, sec_pts)
            total_qb = float(sec_pts[-1])
            sx, so, _ = _score_feats(notes, total_qb, ax_c.shape[1])
            C = dtw_mod.cost_matrix(sx, ax_c, so, ao_c)
            # Judge the repeat pattern with tempo-limited DTW (see dtw.slope_cost).
            cost = dtw_mod.slope_cost(C, open_frames=open_frames)
            key = order.name if vname == variants[0][0] and len(variants) == 1 else f"{order.name}|{vname}"
            costs[key] = cost
            path, _ = dtw_mod.dtw(C, open_frames=open_frames)
            coarse[key] = (path, notes, total_qb, qb_pts, sec_pts, order)
    # 1) choose the repeat pattern using the first variant of each order
    #    (tempo-warped when the score has tempo changes): this was the most
    #    reliable choice on MusicNet;
    # 2) for that order, keep whichever time line (warped / even) fits better.
    by_order: dict[str, float] = {}
    for k, v in costs.items():
        o, _, vname = k.partition("|")
        if vname in ("", "tempo"):
            by_order[o] = v
    # The audio decides: first the coarse match over all patterns, then, among patterns
    # that nearly tie, the fine match. Only a near-exact fine tie is broken with outside
    # knowledge: metronome marks (tempo consistency), the user's --tempo, or (OMR scores,
    # whose repeat signs are unreliable) fewer repeats.
    order_name = min(by_order, key=by_order.get)
    tied = [o for o, v in by_order.items() if v - by_order[order_name] < NEAR_TIE]
    if len(tied) > 1:
        audio_sec = ax_c.shape[1] * coarse_sec
        lengths = {o.name: len(o) for o in orders}
        # 1) The detailed (fine) match separates near-tied patterns much better than the
        #    coarse one (e.g. it notices when the first pass of a repeat was skipped).
        fine, fine_paths = {}, {}
        for name in sorted(tied, key=by_order.get)[:MAX_TEMPO_CHECKS]:
            key = name if name in coarse else f"{name}|tempo"
            if key not in coarse:
                continue
            path_c, notes_c, total, qb_pts, sec_pts, o = coarse[key]
            path_f, n_f, fc = _fine_path(path_c, notes_c, total, ax_c, ax_f, ao_f, with_cost=True)
            fine[name], fine_paths[name] = fc, (path_f, n_f, total, qb_pts, sec_pts, o)
        best_f = min(fine.values())
        close = [o for o in fine if fine[o] - best_f < FINE_NEAR_TIE]
        order_name = min(close, key=fine.get)
        # 2) Among near-exact fine ties, prefer the pattern that covers more of the audio:
        #    skipping a poorly matching opening (often the first pass of a repeat) lowers
        #    the mean cost a little, and that is the usual way a wrong pattern wins.
        if len(close) > 1:
            fine_sec = FRAME_SEC * FINE_POOL
            cover = {o: float(fine_paths[o][0][-1, 1] - fine_paths[o][0][0, 1]) * fine_sec for o in close}
            most = max(cover.values())
            close = [o for o in close if cover[o] >= most - COVER_TIE_SEC]
            order_name = min(close, key=fine.get)
        # 3) Only what still ties is broken with outside knowledge:
        if len(close) > 1:
            spread = {}
            if tempo_marking_kind(score, tempo_hint_qpm) == "metronome":
                for name in close:
                    path_f, n_f, total, qb_pts, sec_pts, o = fine_paths[name]
                    spread[name] = tempo_consistency(score, o, path_f, total, qb_pts, sec_pts, n_f, tempo_hint_qpm)
            usable = {k: v for k, v in spread.items() if v is not None}
            if len(usable) >= 2 and len(usable) == len(close):
                # several metronome marks: the pattern whose passages keep the same relation to their marks
                best = min(usable.values())
                order_name = min((o for o in usable if usable[o] - best < 0.02), key=fine.get)
                warnings.append("Repeat pattern chosen with the help of the printed tempo marks.")
            elif tempo_hint_qpm:
                def misfit(name):
                    order = next(o for o in orders if o.name == name)
                    expected = float(warp_function(score, order, tempo_hint_qpm)[1][-1])
                    return abs(np.log(max(audio_sec, 1e-6) / max(expected, 1e-6)))
                order_name = min(close, key=misfit)
                warnings.append("Repeat pattern chosen with the help of the written tempo marking.")
            elif repeats_uncertain:
                order_name = min(close, key=lambda o: (lengths.get(o, 0), fine[o]))
                warnings.append("Repeat signs come from optical recognition; chose the pattern with fewer repeats.")
    keys = [k for k in costs if k.split("|")[0] == order_name]
    best_name = min(keys, key=costs.get)
    order = coarse[best_name][5]
    ranked = sorted(by_order.values())
    if len(ranked) > 1 and ranked[1] - ranked[0] < 0.01:
        warnings.append("Two repeat patterns fit almost equally well; check whether the performers "
                        "took the repeats.")

    # ------------------------------------- does the music fill the whole audio?
    # If the audio range also holds the end of the previous movement or the start of
    # the next one (or long applause), the alignment above was forced to stretch the
    # score over it. Look for the score inside the audio with free ends; when cutting
    # the extra audio clearly improves the match AND there is a pause at the cut,
    # cut it and align again.
    if check_edges and not search_long_recording:
        cut = _extra_audio(coarse[best_name][1], coarse[best_name][2], ax_c, ao_c, coarse_sec,
                           y, t_a, (open_sec if open_sec is not None else OPEN_SEC) + EDGE_MARGIN_SEC)
        if cut is not None:
            lead, tail, new_a, new_b = cut
            new_start, new_end = seg_start + new_a, seg_start + new_b
            res = align_score_to_audio(score, audio_path, start_sec=new_start, end_sec=new_end,
                                       orders=orders, open_sec=min(open_sec or OPEN_SEC, EDGE_OPEN_SEC),
                                       tempo_hint_qpm=tempo_hint_qpm,
                                       repeats_uncertain=repeats_uncertain, check_edges=False)
            parts = ([f"{lead:.0f} s before it"] if lead else []) + ([f"{tail:.0f} s after it"] if tail else [])
            res.warnings.insert(0, "The audio range held other sound besides this movement ("
                                + " and ".join(parts) + f"); it was left out. The movement now runs "
                                f"{new_start:.1f}-{new_end:.1f} s. Check by ear, and set start_sec/end_sec "
                                "in config.json if this is wrong.")
            res.trimmed_range = (round(new_start, 2), round(new_end, 2))
            return res

    # ------------------------------------------------------------ fine pass
    path_c, notes, total_qb, qb_pts, sec_pts, _ = coarse[best_name]
    n_fine = ax_f.shape[1]
    sx_f, so_f, fpq_f = _score_feats(notes, total_qb, n_fine)
    factor_s = n_fine / ax_c.shape[1]
    factor_a = ax_f.shape[1] / ax_c.shape[1]
    radius = int(FINE_RADIUS_SEC / (FRAME_SEC * FINE_POOL))
    path_f, cost_f = dtw_mod.dtw_band(sx_f, ax_f, so_f, ao_f, path_c, factor_s, factor_a, radius)
    s_frames, a_frames = dtw_mod.path_to_function(path_f)
    fine_sec = FRAME_SEC * FINE_POOL

    # local cost along the path, per score frame
    local = 1.0 - np.einsum("ij,ij->j", sx_f[:, path_f[:, 0]], ax_f[:, path_f[:, 1]])
    local_by_s = np.bincount(path_f[:, 0], weights=local, minlength=n_fine) / \
        np.maximum(np.bincount(path_f[:, 0], minlength=n_fine), 1)

    # ------------------------------------------------------ measure times
    timeline = measure_timeline(score, order)

    def warp(qb):
        return np.interp(np.asarray(qb, dtype=float), qb_pts, sec_pts)

    def qb_to_sec(qb: np.ndarray) -> np.ndarray:
        frames = warp(qb) * fpq_f
        t = np.interp(frames, s_frames, a_frames) * fine_sec + seg_start - LATENCY_CORRECTION_SEC
        return np.maximum(t, seg_start)

    timeline["start_sec"] = qb_to_sec(timeline["perf_start_qb"].values).round(3)
    timeline["end_sec"] = qb_to_sec(timeline["perf_end_qb"].values).round(3)
    lc = []
    for a_qb, b_qb in zip(timeline["perf_start_qb"], timeline["perf_end_qb"]):
        i0 = int(warp(a_qb) * fpq_f)
        i1 = max(i0 + 1, int(warp(b_qb) * fpq_f))
        lc.append(float(np.mean(local_by_s[i0:i1])) if i1 <= len(local_by_s) else float("nan"))
    timeline["match_cost"] = np.round(lc, 3)
    timeline["note_sim"] = np.round(bar_note_similarity(score, timeline, base_chroma, seg_start), 3)
    med = np.nanmedian(lc)
    mad = np.nanmedian(np.abs(np.array(lc) - med)) + 1e-6
    timeline["flagged"] = [bool(c > med + 4 * mad and c > 0.35) for c in lc]
    dur = (timeline["end_sec"] - timeline["start_sec"]).clip(lower=1e-3)
    timeline["tempo_qpm"] = ((timeline["perf_end_qb"] - timeline["perf_start_qb"]) / dur * 60).round(1)
    n_flag = int(timeline["flagged"].sum())
    if n_flag:
        labels = ", ".join(timeline.loc[timeline["flagged"], "label"].astype(str).head(12))
        warnings.append(f"{n_flag} measure(s) matched poorly and should be checked by ear: {labels}")
    if cost_f > 0.45:
        warnings.append("Overall match is weak. The score and the recording may not be the same piece/edition, "
                        "or the recording quality is poor.")

    return AlignmentResult(
        audio_path=str(audio_path), order=order.name, order_description=order.description,
        segment_start_sec=seg_start, segment_end_sec=float(timeline["end_sec"].iloc[-1]),
        cost=cost_f, candidate_costs=by_order, measure_times=timeline, warnings=warnings)


def tempo_consistency(score: Score, order: PlayingOrder, path: np.ndarray, total_sec: float,
                      qb_pts: np.ndarray, sec_pts: np.ndarray, n_frames: int,
                      hint_qpm: float | None = None, min_measures: int = 4) -> float | None:
    """How evenly the performance follows the written tempo marks (lower = better).

    For every passage with one tempo mark we compare the time the recording
    spends there with the time the mark predicts. Performers may play every
    section slower or faster, so only the *spread* of these ratios matters.
    A wrong repeat pattern pushes extra (or missing) music into a passage,
    which then looks much too slow (or fast). Returns None with fewer than
    two marked passages.
    """
    marks = metronome_marks(score)
    tl = measure_timeline(score, order)
    if not len(tl) or sum(1 for _, num in marks.values() if num) < 2:
        return None
    # Passages from one mark to the next (in playing order). Only passages that start
    # at a metronome *number* are judged: tempo words (Allegro...) are too vague.
    runs: list[tuple[float, float]] = []
    mcs = [int(mc) for mc in tl["mc"]]
    starts = [i for i, mc in enumerate(mcs) if i == 0 or mc in marks] + [len(mcs)]
    for s0, s1 in zip(starts, starts[1:]):
        mark = marks.get(mcs[s0])
        if mark and mark[1] and s1 - s0 >= min_measures:
            runs.append((float(tl["perf_start_qb"].iloc[s0]), float(tl["perf_end_qb"].iloc[s1 - 1])))
    if len(runs) < 2:
        return None
    s_frames, a_frames = dtw_mod.path_to_function(path)
    fpq = n_frames / total_sec

    def audio_at(qb: float) -> float:
        return float(np.interp(np.interp(qb, qb_pts, sec_pts) * fpq, s_frames, a_frames))

    logs = []
    for a, b in runs:
        expected = (np.interp(b, qb_pts, sec_pts) - np.interp(a, qb_pts, sec_pts)) * fpq
        actual = audio_at(b) - audio_at(a)
        if expected > 0 and actual > 0:
            logs.append(np.log(actual / expected))
    return float(np.std(logs)) if len(logs) >= 2 else None


def _fine_path(path_c: np.ndarray, notes: pd.DataFrame, total: float, ax_c, ax_f, ao_f,
               with_cost: bool = False):
    """Fine DTW in a band around a coarse path (same as the main fine pass).
    Returns (path, n_frames), plus the mean cost along the path when with_cost."""
    n_fine = ax_f.shape[1]
    sx_f, so_f, _ = _score_feats(notes, total, n_fine)
    factor = n_fine / ax_c.shape[1]
    radius = int(FINE_RADIUS_SEC / (FRAME_SEC * FINE_POOL))
    path_f, cost = dtw_mod.dtw_band(sx_f, ax_f, so_f, ao_f, path_c, factor, factor, radius)
    return (path_f, n_fine, float(cost)) if with_cost else (path_f, n_fine)
