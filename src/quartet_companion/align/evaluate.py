"""Measure how accurate the alignment is, using MusicNet as ground truth.

MusicNet gives, for every note in a recording, its time in the audio
(start_time, in samples at 44.1 kHz) and its position in the score
(start_beat, in quarter-note beats counted along the performance). So we
know the true time of any score position. We run our aligner without
looking at those labels, then compare.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..io.abc import load_abc_movement
from ..unfold import measure_timeline, playing_orders, unfolded_notes
from . import dtw as dtw_mod
from .features import score_chroma
from .pipeline import align_score_to_audio

MUSICNET_SR = 44100

# MusicNet recording id -> ABC movement id (Beethoven string quartets in both datasets)
MUSICNET_TO_ABC = {
    2313: "n15op132_01", 2314: "n15op132_02", 2315: "n15op132_03",
    2365: "n12op127_01", 2366: "n12op127_02", 2368: "n12op127_04",
    2376: "n08op59-2_01", 2377: "n08op59-2_02", 2379: "n08op59-2_04",
    2381: "n13op130_01", 2382: "n13op130_02", 2383: "n13op130_03", 2384: "n13op130_04",
    2403: "n01op18-1_04", 2431: "n16op135_01", 2432: "n16op135_02", 2433: "n16op135_03",
    2451: "n06op18-6_02", 2480: "n05op18-5_01", 2481: "n05op18-5_02", 2482: "n05op18-5_03",
    2483: "n05op18-5_04", 2494: "n11op95_01", 2497: "n11op95_04",
    2560: "n02op18-2_02", 2562: "n02op18-2_04", 2621: "n07op59-1_01", 2622: "n07op59-1_02",
}


def read_musicnet_notes(path: str | Path) -> pd.DataFrame:
    rows = []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            rows.append({"perf_qb": float(row["start_beat"]), "dur_qb": float(row["end_beat"]),
                         "midi": int(row["note"]), "sec": int(row["start_time"]) / MUSICNET_SR})
    return pd.DataFrame(rows).sort_values("perf_qb").reset_index(drop=True)


def symbolic_map(ours: pd.DataFrame, theirs: pd.DataFrame, fpq: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """Map our performance beats to MusicNet's beats by aligning the two note lists.

    MusicNet's reference MIDI sometimes counts beats differently (e.g. a pickup
    padded to a full bar), so we align the two scores with DTW on chroma.
    """
    t_ours = float((ours["perf_qb"] + ours["dur_qb"]).max())
    t_theirs = float((theirs["perf_qb"] + theirs["dur_qb"]).max())
    a, ao = score_chroma(ours, t_ours, fpq)
    b, bo = score_chroma(theirs, t_theirs, fpq)
    path, _ = dtw_mod.dtw(dtw_mod.cost_matrix(a, b, ao, bo))
    s, t = dtw_mod.path_to_function(path)
    return s / fpq, t / fpq


def read_musicnet_labels(path: str | Path) -> tuple[np.ndarray, np.ndarray, float]:
    """Return (beats, seconds) for note starts, sorted, plus total beats."""
    beats, secs, ends = [], [], []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            b = float(row["start_beat"])
            beats.append(b)
            secs.append(int(row["start_time"]) / MUSICNET_SR)
            ends.append(b + float(row["end_beat"]))       # 'end_beat' is a duration in MusicNet
    beats, secs = np.array(beats), np.array(secs)
    order = np.argsort(beats, kind="stable")
    beats, secs = beats[order], secs[order]
    # one time per distinct beat (median over simultaneous notes)
    ub = np.unique(beats)
    us = np.array([np.median(secs[beats == b]) for b in ub])
    return ub, np.maximum.accumulate(us), float(max(ends))


@dataclass
class EvalResult:
    musicnet_id: int
    piece: str
    chosen_order: str
    truth_order: str
    median_err: float
    p90_err: float
    max_err: float
    within_250ms: float
    n_measures: int
    mean_signed: float = float("nan")

    def row(self) -> dict:
        return self.__dict__


def evaluate_one(musicnet_id: int, abc_dir: str | Path, musicnet_dir: str | Path, score=None) -> EvalResult:
    """score: judge another score of the same movement (e.g. from OpenScore) instead of the ABC one."""
    root = Path(musicnet_dir)
    piece = MUSICNET_TO_ABC[musicnet_id]
    split = "train" if (root / "train_data" / f"{musicnet_id}.wav").exists() else "test"
    wav = root / f"{split}_data" / f"{musicnet_id}.wav"
    labels = root / f"{split}_labels" / f"{musicnet_id}.csv"
    score = score if score is not None else load_abc_movement(abc_dir, piece)
    gt_beats, gt_secs, total_beats = read_musicnet_labels(labels)

    # Which of our playing orders matches the performance? Compare each order's notes
    # with MusicNet's note list (symbolic DTW) and keep the best match.
    orders = playing_orders(score)
    theirs = read_musicnet_notes(labels)
    tb, to = None, None
    costs = {}
    for o in orders:
        ours = unfolded_notes(score, o)
        a, ao = score_chroma(ours, float((ours["perf_qb"] + ours["dur_qb"]).max()), 2)
        if tb is None:
            tb, to = score_chroma(theirs, float((theirs["perf_qb"] + theirs["dur_qb"]).max()), 2)
        _, costs[o.name] = dtw_mod.dtw(dtw_mod.cost_matrix(a, tb, ao, to))
    # Plain DTW can "skip" a repeated passage at little cost, so first keep only the
    # orders whose length matches MusicNet's (within 3%), then take the best match.
    length = {o.name: float(measure_timeline(score, o)["perf_end_qb"].max()) for o in orders}
    close = [n for n in costs if abs(length[n] - total_beats) <= 0.03 * total_beats]
    truth_order = min(close or costs, key=costs.get)

    result = align_score_to_audio(score, str(wav))
    if result.order != truth_order:
        return EvalResult(musicnet_id, piece, result.order, truth_order, float("nan"), float("nan"),
                          float("nan"), 0.0, len(result.measure_times))
    tl = result.measure_times
    notes = unfolded_notes(score, next(o for o in orders if o.name == truth_order))
    ours_q, their_q = symbolic_map(notes, read_musicnet_notes(labels))
    their_beat = np.interp(tl["perf_start_qb"].values, ours_q, their_q)
    truth = np.interp(their_beat, gt_beats, gt_secs)
    # Only judge measures inside the labelled range (no extrapolation)
    inside = (their_beat >= gt_beats[0]) & (their_beat <= gt_beats[-1])
    signed = (tl["start_sec"].values - truth)[inside]
    err = np.abs(signed)
    return EvalResult(musicnet_id, piece, result.order, truth_order, float(np.median(err)),
                      float(np.percentile(err, 90)), float(err.max()), float(np.mean(err <= 0.25)),
                      int(inside.sum()), float(np.mean(signed)))


def main(argv: list[str] | None = None) -> None:
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Evaluate alignment on MusicNet recordings")
    ap.add_argument("--abc", required=True)
    ap.add_argument("--musicnet", required=True, help="folder that contains train_data/ train_labels/ ...")
    ap.add_argument("--ids", nargs="*", type=int, default=list(MUSICNET_TO_ABC))
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    rows = []
    for mid in args.ids:
        try:
            r = evaluate_one(mid, args.abc, args.musicnet)
            rows.append(r.row())
            print(json.dumps(r.row()), flush=True)
        except Exception as exc:   # keep going; report the failure
            rows.append({"musicnet_id": mid, "error": f"{type(exc).__name__}: {exc}"})
            print(json.dumps(rows[-1]), flush=True)
    if args.out:
        Path(args.out).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
