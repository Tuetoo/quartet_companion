"""Gentle clean-up of old recordings (hiss, crackle, rumble).

Old recordings on IMSLP (1930s-1950s) often have three kinds of noise:
* rumble  - very low frequencies from the turntable/microphone   -> high-pass filter
* crackle - short clicks from the disc surface                    -> detect and repair
* hiss    - steady broadband noise, strongest in the high treble  -> spectral gating

Strength "light" changes the sound very little; "strong" removes more noise
but can make the strings sound slightly dull or "watery". The cleaned file
is used only for listening; alignment works on either version.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import scipy.signal as sg

STRENGTHS = {
    #          prop_decrease, lowpass_hz, click_threshold
    "light":  (0.55, 9000, 8.0),
    "medium": (0.75, 8000, 6.0),
    "strong": (0.90, 7000, 5.0),
}


def remove_clicks(y: np.ndarray, sr: int, threshold: float = 6.0, max_ms: float = 3.0) -> tuple[np.ndarray, int]:
    """Find short spikes in the high-frequency part and replace them by interpolation."""
    hp = sg.sosfiltfilt(sg.butter(4, 3000, "hp", fs=sr, output="sos"), y)
    env = np.abs(hp)
    # local level: median over ~20 ms, so loud music is not mistaken for clicks
    win = max(3, int(0.02 * sr) | 1)
    k = max(1, win // 16)
    local = sg.medfilt(env[::k], kernel_size=max(3, (win // k) | 1))
    local = np.repeat(local, k)[: len(env)] + 1e-6
    bad = env > threshold * local
    y = y.copy()
    n_fixed = 0
    max_len = int(max_ms / 1000 * sr)
    idx = np.flatnonzero(bad)
    if len(idx) == 0:
        return y, 0
    # group into runs
    splits = np.flatnonzero(np.diff(idx) > int(0.001 * sr)) + 1
    for run in np.split(idx, splits):
        a, b = run[0] - int(0.0005 * sr), run[-1] + int(0.0005 * sr)
        if b - a > max_len or a < 1 or b >= len(y) - 1:
            continue
        y[a:b] = np.linspace(y[a - 1], y[b], b - a, endpoint=False)
        n_fixed += 1
    return y, n_fixed


def clean_audio(y: np.ndarray, sr: int, strength: str = "medium") -> tuple[np.ndarray, dict]:
    import noisereduce as nr
    prop, lowpass, click_thr = STRENGTHS[strength]
    # 1) rumble and very high hiss
    y = sg.sosfiltfilt(sg.butter(2, 60, "hp", fs=sr, output="sos"), y)
    if lowpass < sr / 2:
        y = sg.sosfiltfilt(sg.butter(4, lowpass, "lp", fs=sr, output="sos"), y)
    # 2) crackle
    y, n_clicks = remove_clicks(y, sr, threshold=click_thr)
    # 3) hiss: learn the noise from the quietest 3% of the recording
    frame = int(0.05 * sr)
    n = len(y) // frame
    rms = np.sqrt(np.mean(y[: n * frame].reshape(n, frame) ** 2, axis=1))
    quiet = np.argsort(rms)[: max(10, n * 3 // 100)]
    noise = np.concatenate([y[i * frame:(i + 1) * frame] for i in sorted(quiet)])
    y = nr.reduce_noise(y=y, sr=sr, y_noise=noise, stationary=True, prop_decrease=prop, n_fft=2048)
    peak = np.abs(y).max()
    if peak > 0.99:
        y = y / peak * 0.99
    return y.astype(np.float32), {"strength": strength, "clicks_repaired": int(n_clicks)}


def clean_file(src: str | Path, dst: str | Path, strength: str = "medium",
               start_sec: float | None = None, end_sec: float | None = None) -> dict:
    import soundfile as sf
    info = sf.info(str(src))
    start = int((start_sec or 0) * info.samplerate)
    stop = int(end_sec * info.samplerate) if end_sec else None
    y, sr = sf.read(str(src), start=start, stop=stop, always_2d=True)
    y = y.mean(axis=1)                       # old recordings are mono anyway
    out, report = clean_audio(y, sr, strength)
    fmt = "MP3" if str(dst).lower().endswith(".mp3") else None
    sf.write(str(dst), out, sr, format=fmt)
    return report
