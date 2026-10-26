"""Dynamic time warping (DTW), in two passes.

DTW finds the best way to stretch one sequence in time so it matches
another. Here: the score (in beats) against the recording (in seconds).

Pass 1 (coarse): ~0.19 s frames over the whole piece. Cheap, robust.
Pass 2 (fine):   ~0.05 s frames, but only inside a narrow band around
                 the coarse path. Precise, and still cheap.

We also support "subsequence" DTW: find where a movement sits inside a
long recording (for example a CD track with all four movements).
"""
from __future__ import annotations

import numpy as np
from numba import njit

ONSET_WEIGHT = 0.3


def cost_matrix(sx: np.ndarray, ax: np.ndarray, so: np.ndarray | None = None,
                ao: np.ndarray | None = None) -> np.ndarray:
    """Cosine distance between chroma frames (+ onset difference). Rows = score, columns = audio."""
    c = 1.0 - sx.T @ ax
    if so is not None and ao is not None:
        c = c + ONSET_WEIGHT * np.abs(so[:, None] - ao[None, :])
    return c.astype(np.float64)


@njit(cache=True)
def _dtw_full(C: np.ndarray, subseq: bool, open_frames: int) -> np.ndarray:
    n, m = C.shape
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    if subseq:
        for j in range(m + 1):
            D[0, j] = 0.0
    else:
        # "open begin": the music may start a little after the recording starts
        for j in range(min(open_frames, m) + 1):
            D[0, j] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            c = C[i - 1, j - 1]
            best = D[i - 1, j - 1] + c            # diagonal counts once (symmetric-ish)
            v = D[i - 1, j] + c * 1.5             # mild penalty on non-diagonal moves
            if v < best:
                best = v
            h = D[i, j - 1] + c * 1.5
            if h < best:
                best = h
            D[i, j] = best
    return D


@njit(cache=True)
def _dtw_slope(C: np.ndarray, open_frames: int) -> np.ndarray:
    """DTW whose local tempo may change by at most a factor of 2 per step
    (steps (1,1), (1,2), (2,1)). Used to judge which repeat pattern fits:
    a wrong pattern needs impossible speed-ups and gets a high cost."""
    n, m = C.shape
    D = np.full((n + 2, m + 2), np.inf)
    for j in range(min(open_frames, m) + 1):
        D[1, j + 1] = C[0, j]
    for i in range(1, n):
        for j in range(1, m):
            c = C[i, j]
            best = D[i, j] + 2 * c                                     # (1,1)
            if i >= 2:
                v = D[i - 1, j] + 2 * C[i - 1, j] + c                     # (2,1)
                if v < best:
                    best = v
            if j >= 2:
                v = D[i, j - 1] + 2 * C[i, j - 1] + c                     # (1,2)
                if v < best:
                    best = v
            D[i + 1, j + 1] = best
    return D


def slope_cost(C: np.ndarray, open_frames: int = 0) -> float:
    """Cost (per score frame) of the best slope-constrained path; inf if none exists."""
    D = _dtw_slope(np.ascontiguousarray(C), open_frames)
    n, m = C.shape
    lo = max(1, m - open_frames) if open_frames else m
    end = D[n, lo:m + 1]
    best = float(np.min(end)) if end.size else np.inf
    return best / (3 * n)


@njit(cache=True)
def _backtrack(D: np.ndarray, end_j: int, subseq: bool) -> np.ndarray:
    i, j = D.shape[0] - 1, end_j
    path = np.zeros((D.shape[0] + D.shape[1], 2), dtype=np.int64)
    k = 0
    while i > 0 and (j > 0 or subseq):
        path[k, 0] = i - 1
        path[k, 1] = j - 1
        k += 1
        if subseq and i == 1:
            break
        a = D[i - 1, j - 1] if j > 0 else np.inf
        b = D[i - 1, j]
        c = D[i, j - 1] if j > 0 else np.inf
        if a <= b and a <= c:
            i, j = i - 1, j - 1
        elif b <= c:
            i = i - 1
        else:
            j = j - 1
    return path[:k][::-1]


def dtw(C: np.ndarray, subseq: bool = False, open_frames: int = 0) -> tuple[np.ndarray, float]:
    """Return (path as N x 2 [score_frame, audio_frame], cost per path step).

    open_frames: allow the match to start up to this many audio frames late and
    end up to this many frames early (silence, tuning, applause at the ends).
    """
    D = _dtw_full(np.ascontiguousarray(C), subseq, open_frames)
    m = C.shape[1]
    if subseq:
        end_j = int(np.argmin(D[-1, 1:]) + 1)
    elif open_frames:
        lo = max(1, m - open_frames)
        end_j = int(lo + np.argmin(D[-1, lo:]))
    else:
        end_j = m
    path = _backtrack(D, end_j, subseq or open_frames > 0)
    return path, float(D[-1, end_j] / max(len(path), 1))


@njit(cache=True)
def _dtw_band(C_band: np.ndarray, lo: np.ndarray) -> np.ndarray:
    """DTW on a band. C_band[i, k] is the cost of (i, lo[i] + k); inf outside.

    Row 0 may start at any column (open begin): the coarse pass already
    decided roughly where the music starts.
    """
    n, w = C_band.shape
    D = np.full((n, w), np.inf)
    for k in range(w):
        D[0, k] = C_band[0, k]
    for i in range(1, n):
        for k in range(w):
            c = C_band[i, k]
            if not np.isfinite(c):
                continue
            j = lo[i] + k
            best = np.inf
            kd = j - 1 - lo[i - 1]          # diagonal
            if 0 <= kd < w and D[i - 1, kd] + c < best:
                best = D[i - 1, kd] + c
            kv = j - lo[i - 1]              # vertical
            if 0 <= kv < w and D[i - 1, kv] + 1.5 * c < best:
                best = D[i - 1, kv] + 1.5 * c
            if k > 0 and D[i, k - 1] + 1.5 * c < best:
                best = D[i, k - 1] + 1.5 * c
            D[i, k] = best
    return D


def _band_limits(coarse_path: np.ndarray, n: int, m: int, factor_s: float, factor_a: float,
                 radius: int) -> tuple[np.ndarray, np.ndarray]:
    lo = np.full(n, m, dtype=np.int64)
    hi = np.full(n, -1, dtype=np.int64)
    for s_c, a_c in coarse_path:
        i0 = int(np.floor(s_c * factor_s))
        i1 = min(n, int(np.ceil((s_c + 1) * factor_s)))
        a0 = int(np.floor(a_c * factor_a)) - radius
        a1 = int(np.ceil((a_c + 1) * factor_a)) + radius
        for i in range(max(0, i0), i1):
            lo[i] = min(lo[i], a0)
            hi[i] = max(hi[i], a1)
    # rows the coarse path did not touch: copy neighbours
    for i in range(n):
        if hi[i] < 0:
            lo[i], hi[i] = (lo[i - 1], hi[i - 1]) if i > 0 else (0, radius)
    lo = np.clip(lo, 0, m - 1)
    hi = np.clip(hi, 0, m - 1)
    lo = np.minimum.accumulate(lo[::-1])[::-1]      # non-decreasing lower edge
    hi = np.maximum.accumulate(hi)                  # non-decreasing upper edge
    for i in range(1, n):                           # keep consecutive rows connected
        if lo[i] > hi[i - 1] + 1:
            hi[i - 1] = lo[i] - 1
    return lo, hi


def dtw_band(sx, ax, so, ao, coarse_path: np.ndarray, factor_s: float, factor_a: float,
             radius: int) -> tuple[np.ndarray, float]:
    """Refine a coarse path on finer frames inside a band of +/- radius frames."""
    n, m = sx.shape[1], ax.shape[1]
    lo, hi = _band_limits(coarse_path, n, m, factor_s, factor_a, radius)
    w = int((hi - lo).max()) + 1
    C_band = np.full((n, w), np.inf)
    for i in range(n):
        cols = np.arange(lo[i], hi[i] + 1)
        row = 1.0 - sx[:, i] @ ax[:, cols]
        row = row + ONSET_WEIGHT * np.abs(so[i] - ao[cols])
        C_band[i, : len(cols)] = row
    D = _dtw_band(C_band, lo)
    last = D[n - 1]
    if not np.isfinite(last).any():
        raise RuntimeError("fine alignment failed: no path through the band")
    k = int(np.argmin(np.where(np.isfinite(last), last, np.inf)))   # open end
    total = float(last[k])
    i = n - 1
    path = []
    while True:
        j = lo[i] + k
        path.append((i, j))
        if i == 0:
            break
        cands = []
        kd = j - 1 - lo[i - 1]
        kv = j - lo[i - 1]
        if 0 <= kd < w:
            cands.append((D[i - 1, kd], i - 1, kd))
        if 0 <= kv < w:
            cands.append((D[i - 1, kv], i - 1, kv))
        if k > 0:
            cands.append((D[i, k - 1], i, k - 1))
        cands = [c for c in cands if np.isfinite(c[0])]
        if not cands:
            break
        _, i, k = min(cands)
    path = np.array(path[::-1], dtype=np.int64)
    return path, total / max(len(path), 1)


def path_to_function(path: np.ndarray, how: str = "first") -> tuple[np.ndarray, np.ndarray]:
    """Monotone (score_frame -> audio_frame) samples from a DTW path.

    When one score frame is matched to several audio frames (the player held
    a note longer than written), "first" takes the earliest audio frame,
    which is when that score position was actually reached.
    """
    s = path[:, 0].astype(np.int64)
    a = path[:, 1].astype(float)
    if how == "mean":
        sums = np.bincount(s, weights=a)
        counts = np.bincount(s)
        uniq = np.nonzero(counts)[0]
        vals = sums[uniq] / counts[uniq]
    else:
        uniq, first_idx = np.unique(s, return_index=True)
        vals = a[first_idx]
    return uniq.astype(float), np.maximum.accumulate(vals)


@njit(cache=True)
def _dtw_slope_subseq(C: np.ndarray):
    """Slope-limited subsequence DTW: the whole score (rows) must match a
    stretch of the audio (columns) with local tempo changes of at most 2x.
    Returns accumulated costs and the start column of each cell's best path."""
    n, m = C.shape
    D = np.full((n, m), np.inf)
    S = np.zeros((n, m), dtype=np.int64)
    for j in range(m):
        D[0, j] = C[0, j]
        S[0, j] = j
    for i in range(1, n):
        for j in range(1, m):
            c = C[i, j]
            best = D[i - 1, j - 1] + 2 * c
            src = S[i - 1, j - 1]
            if i >= 2:
                v = D[i - 2, j - 1] + 2 * C[i - 1, j] + c
                if v < best:
                    best = v
                    src = S[i - 2, j - 1]
            if j >= 2:
                v = D[i - 1, j - 2] + 2 * C[i, j - 1] + c
                if v < best:
                    best = v
                    src = S[i - 1, j - 2]
            D[i, j] = best
            S[i, j] = src
    return D, S


def locate_subsequence(C: np.ndarray) -> tuple[int, int, float]:
    """(start_col, end_col, cost per score frame) of the best tempo-limited match."""
    D, S = _dtw_slope_subseq(np.ascontiguousarray(C))
    n = C.shape[0]
    end = int(np.argmin(D[-1]))
    cost = float(D[-1, end])
    if not np.isfinite(cost):
        return 0, C.shape[1] - 1, np.inf
    return int(S[-1, end]), end, cost / (3 * n)
