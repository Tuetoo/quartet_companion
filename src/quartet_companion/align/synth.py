"""A tiny synthesizer, used only for tests.

It turns a score into audio with a known (and deliberately uneven) tempo,
so we know the true time of every measure and can measure alignment error
without a real recording.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .features import SR


def tempo_curve(total_qb: float, base_qpm: float = 90.0, wobble: float = 0.15, seed: int = 0):
    """Return a function qb -> seconds with smoothly varying tempo (+/- wobble)."""
    rng = np.random.default_rng(seed)
    grid = np.linspace(0, total_qb, max(4, int(total_qb / 4)) + 1)
    factors = 1 + wobble * np.sin(np.linspace(0, 3 * np.pi, len(grid)) + rng.uniform(0, 3))
    factors *= 1 + 0.05 * rng.standard_normal(len(grid))
    sec_per_qb = 60.0 / (base_qpm * factors)
    seconds = np.concatenate([[0], np.cumsum(np.diff(grid) * (sec_per_qb[:-1] + sec_per_qb[1:]) / 2)])
    return lambda qb: np.interp(qb, grid, seconds)


def render(notes: pd.DataFrame, qb_to_sec, lead_in: float = 1.0, tail: float = 1.5,
           seed: int = 0) -> np.ndarray:
    """Additive synthesis (6 harmonics, decaying envelope) of notes with `perf_qb`."""
    rng = np.random.default_rng(seed)
    end_sec = float(qb_to_sec((notes["perf_qb"] + notes["dur_qb"]).max())) + lead_in + tail
    y = np.zeros(int(end_sec * SR) + 1)
    for qb, dur, midi in zip(notes["perf_qb"], notes["dur_qb"], notes["midi"]):
        t0 = float(qb_to_sec(qb)) + lead_in
        t1 = float(qb_to_sec(qb + max(dur, 0.1))) + lead_in
        n = max(int((t1 - t0) * SR), 64)
        a = int(t0 * SR)
        t = np.arange(n) / SR
        f0 = 440.0 * 2 ** ((midi - 69) / 12)
        env = np.minimum(1.0, t / 0.02) * np.exp(-t * 1.5)
        env[-min(len(env), 256):] *= np.linspace(1, 0, min(len(env), 256))
        tone = sum((0.7 ** h) * np.sin(2 * np.pi * f0 * (h + 1) * t + rng.uniform(0, 6.28)) for h in range(6))
        seg = y[a:a + n]
        seg += 0.08 * env[: len(seg)] * tone[: len(seg)]
    y += 0.002 * rng.standard_normal(len(y))       # a little noise
    return (y / max(1e-9, np.abs(y).max()) * 0.8).astype(np.float32)
