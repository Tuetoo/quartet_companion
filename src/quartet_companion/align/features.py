"""Features that make a score and a recording comparable.

We describe both the score and the audio as a "chroma" sequence: for each
short time frame, how strong each of the 12 pitch classes (C, C#, ... B)
is. Chroma ignores octave and instrument colour, so a score and a real
recording look similar even though one is symbols and the other sound.

* Audio chroma: from the constant-Q spectrum (librosa).
* Score chroma: from the notes. We add a little weight for the strongest
  overtones (octave, twelfth, ...), because real strings have overtones.

We also compute an "onset" curve (where new notes start). Adding it to
chroma sharpens the alignment at note starts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SR = 22050
HOP = 512                      # ~23 ms per frame
FRAME_SEC = HOP / SR

# Overtones that matter for chroma: (semitones above the note, weight)
OVERTONES = [(0, 1.0), (12, 0.5), (19, 0.33), (24, 0.25), (28, 0.2)]


def load_audio(path: str, offset: float = 0.0, duration: float | None = None) -> np.ndarray:
    import librosa
    y, _ = librosa.load(path, sr=SR, mono=True, offset=offset, duration=duration)
    return y


def audio_chroma(y: np.ndarray) -> np.ndarray:
    """12 x T chroma, smoothed and normalised (CENS-like)."""
    import librosa
    c = librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=HOP, bins_per_octave=36, n_chroma=12)
    return _normalise(c)


def audio_onset_curve(y: np.ndarray) -> np.ndarray:
    import librosa
    o = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    return _scale01(o)


def score_chroma(notes: pd.DataFrame, total_qb: float, frames_per_qb: float) -> tuple[np.ndarray, np.ndarray]:
    """Chroma (12 x T) and onset curve (T) from notes with a `perf_qb` column."""
    n_frames = max(1, int(np.ceil(total_qb * frames_per_qb)))
    chroma = np.zeros((12, n_frames))
    onset = np.zeros(n_frames)
    for start, dur, midi in zip(notes["perf_qb"].values, notes["dur_qb"].values, notes["midi"].values):
        a = int(start * frames_per_qb)
        b = max(a + 1, int((start + max(dur, 0.05)) * frames_per_qb))
        a, b = min(a, n_frames - 1), min(b, n_frames)
        # Notes decay: weight the start of the note more than its end.
        length = b - a
        env = np.linspace(1.0, 0.5, length) if length > 1 else np.ones(1)
        for semis, w in OVERTONES:
            chroma[(int(midi) + semis) % 12, a:b] += w * env
        onset[a] += 1.0
    onset = np.convolve(onset, np.hanning(5), mode="same")
    return _normalise(chroma), _scale01(onset)


def _normalise(c: np.ndarray) -> np.ndarray:
    """Log-compress, smooth over ~10 frames, then unit-normalise each frame."""
    c = np.log1p(10 * np.maximum(c, 0))
    k = np.hanning(9)
    k /= k.sum()
    c = np.vstack([np.convolve(row, k, mode="same") for row in c])
    norm = np.linalg.norm(c, axis=0, keepdims=True)
    out = np.where(norm > 1e-9, c / np.maximum(norm, 1e-9), 1 / np.sqrt(12))
    return out


def _scale01(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    hi = np.percentile(x, 99) if x.size else 0
    return np.clip(x / hi, 0, 1) if hi > 0 else np.zeros_like(x)


def resample_frames(x: np.ndarray, n_out: int) -> np.ndarray:
    """Linearly stretch a feature sequence (last axis) to n_out frames."""
    n_in = x.shape[-1]
    if n_in == n_out:
        return x
    src = np.linspace(0, n_in - 1, n_out)
    if x.ndim == 1:
        return np.interp(src, np.arange(n_in), x)
    return np.vstack([np.interp(src, np.arange(n_in), row) for row in x])
