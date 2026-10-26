"""Split one recording that holds several movements.

Idea: movements are separated by pauses. We list the longest pauses, then
choose N-1 of them (for N movements, in order) so that each piece of audio
matches its movement's score as well as possible. Matching uses the same
chroma features and tempo-limited DTW as the aligner, on coarse frames.
This joint choice is much more reliable than searching for each movement
alone, because quiet passages inside a slow movement also look like pauses.
"""
from __future__ import annotations

import numpy as np

from ..score import Score
from ..unfold import playing_orders, unfolded_notes
from . import dtw as dtw_mod
from .features import FRAME_SEC, SR, audio_chroma, audio_onset_curve, load_audio
from .tempo import warp_function, warp_notes

SEARCH_POOL = 16                 # ~0.37 s frames


def _pool(x, k):
    from .pipeline import _pool as p
    return p(x, k)


def pause_list(y: np.ndarray, max_pauses: int = 14) -> list[tuple[float, float]]:
    from .pipeline import quiet_runs
    runs = quiet_runs(y, min_sec=1.5)
    # merge pauses that are almost touching
    merged: list[list[float]] = []
    for a, b in runs:
        if merged and a - merged[-1][1] < 2.0:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    merged.sort(key=lambda r: r[1] - r[0], reverse=True)
    return sorted((a, b) for a, b in merged[:max_pauses])


def split_recording(scores: list[Score], audio_path: str) -> list[tuple[float, float]]:
    """Return (start_sec, end_sec) for each score, in order."""
    y = load_audio(audio_path)
    total = len(y) / SR
    chroma = _pool(audio_chroma(y), SEARCH_POOL)
    onset = _pool(audio_onset_curve(y), SEARCH_POOL)
    step = FRAME_SEC * SEARCH_POOL
    pauses = pause_list(y)
    # boundary points: start, the middle of every pause, end
    starts = [0.0] + [b for _, b in pauses]
    ends = [a for a, _ in pauses] + [total]
    n = len(scores)
    k = len(pauses)
    # feats per score: (notes warped, expected length) for two repeat options
    feats = []
    for sc in scores:
        opts = []
        for order in playing_orders(sc)[:2]:
            qb, sec = warp_function(sc, order)
            opts.append((warp_notes(unfolded_notes(sc, order), qb, sec), float(sec[-1])))
        feats.append(opts)

    from .pipeline import _score_feats
    cache: dict[tuple[int, int, int], float] = {}

    def seg_cost(m: int, i: int, j: int) -> float:
        """Cost of movement m on audio from starts[i] to ends[j]."""
        key = (m, i, j)
        if key in cache:
            return cache[key]
        a_sec, b_sec = starts[i], ends[j]
        cost = np.inf
        if b_sec - a_sec > 10:
            a, b = int(a_sec / step), int(np.ceil(b_sec / step))
            seg_c, seg_o = chroma[:, a:b], onset[a:b]
            for notes, expected in feats[m]:
                ratio = (b_sec - a_sec) / max(expected, 1e-6)
                if not (0.33 <= ratio <= 3.0):
                    continue
                sx, so, _ = _score_feats(notes, expected, seg_c.shape[1])
                c = dtw_mod.slope_cost(dtw_mod.cost_matrix(sx, seg_c, so, seg_o), open_frames=int(4 / step))
                cost = min(cost, c)
        cache[key] = cost
        return cost

    # Dynamic programming: movement m uses audio from boundary i (start index)
    # to boundary j (end index, j >= i); the next movement starts at j + 1.
    INF = np.inf
    best = np.full((n + 1, k + 2), INF)      # best[m][i]: movements < m placed, next starts at starts[i]
    back = np.full((n + 1, k + 2), -1, dtype=int)
    best[0][0] = 0.0
    for m in range(n):
        for i in range(k + 1):
            if not np.isfinite(best[m][i]):
                continue
            last_needed = k if m == n - 1 else k - (n - 1 - m)
            j_range = [k] if m == n - 1 else range(i, max(i, last_needed) + 1)
            for j in j_range:
                if j > k:
                    continue
                c = seg_cost(m, i, j)
                if best[m][i] + c < best[m + 1][j + 1]:
                    best[m + 1][j + 1] = best[m][i] + c
                    back[m + 1][j + 1] = i
    if not np.isfinite(best[n][k + 1]):
        # fall back: equal parts
        edges = np.linspace(0, total, n + 1)
        return [(float(edges[i]), float(edges[i + 1])) for i in range(n)]
    out = []
    j = k + 1
    for m in range(n, 0, -1):
        i = back[m][j]
        out.append((starts[i], ends[j - 1]))
        j = i
    return list(reversed(out))
