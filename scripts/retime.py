"""Fix the timing of some bars of an alignment by hand, after listening.

The aligner is good in the middle of a movement but can be off at soft openings,
long final chords and fermatas. These commands change pieces/<id>/alignment.json
only (run `qc site --only <id>` afterwards). Without --write they only print what
would change. Each change adds a line to the alignment's warnings.

  python scripts/retime.py show    <id> [--last 12 | --first 12]
  python scripts/retime.py set     <id> 191=377.4 192=381.6 193=384.6 END=385.6 --write
  python scripts/retime.py refine  <id> <from-label> <to-label> --write
  python scripts/retime.py opening <id> --write
  python scripts/retime.py ending  <id> <from-label> <sound-end-sec> --write

  set      give bar starts (seconds in the recording) by bar label; the last time a bar
           is played is meant. END = when the last bar's sound stops.
  refine   align the bars between two bars you trust again, on their own.
  opening  the sound starts clearly before bar 1: align the first 10 bars again from there.
  ending   align the bars from <from-label> to the end again, up to where the sound ends.

To find seconds, play the movement in the player and read the time, or open the
recording in any audio editor and look at where the attacks are.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

from quartet_companion import pieces as P

ROOT = Path(".")


def _load(pid):
    path = ROOT / "pieces" / pid / "alignment.json"
    if not path.exists():
        sys.exit(f"no alignment for {pid}: run qc align {pid} first")
    return path, json.loads(path.read_text())


def _index(ms, label, last=True):
    hits = [i for i, m in enumerate(ms) if m["label"] == str(label)]
    if not hits:
        sys.exit(f"bar {label} not found (labels look like {ms[0]['label']}, {ms[1]['label']}, ...)")
    return hits[-1] if last else hits[0]


def _tempo(m):
    d = max(1e-6, m["end_sec"] - m["start_sec"])
    m["tempo_qpm"] = round(60 * (m["perf_end_qb"] - m["perf_start_qb"]) / d, 1)


def _apply_starts(ms, starts, end=None):
    """starts = {occurrence index: new start}. Each bar ends where the next one starts;
    `end` = new end of the last bar."""
    for i, t in starts.items():
        ms[i]["start_sec"] = round(float(t), 3)
    if end is not None:
        ms[-1]["end_sec"] = round(float(end), 3)
    touched = set()
    for i in starts:
        if i > 0:
            ms[i - 1]["end_sec"] = ms[i]["start_sec"]
            touched.add(i - 1)
        if i + 1 < len(ms):
            ms[i]["end_sec"] = ms[i + 1]["start_sec"]
        touched.add(i)
    if end is not None:
        touched.add(len(ms) - 1)
    for i in sorted(touched):
        if ms[i]["end_sec"] <= ms[i]["start_sec"]:
            sys.exit(f"bar {ms[i]['label']} would end before it starts: check the times")
        _tempo(ms[i])


def _apply(ms, i0, new, end=None):
    """new[k] = new start of occurrence i0+k."""
    _apply_starts(ms, {i0 + k: t for k, t in enumerate(new)}, end)


def _save(path, al, note, write):
    if not write:
        print("(dry run: add --write to save)")
        return
    al["warnings"] = al.get("warnings", []) + [note]
    path.write_text(json.dumps(al, indent=1))
    print("saved; now run: qc site --only", path.parent.name)


def _realign(pid, ms, i0, i1, t0, t1, end_qb=None):
    """DTW of score occurrences i0..i1-1 against audio t0..t1. Returns new starts."""
    from quartet_companion.align import dtw as dtw_mod
    from quartet_companion.align.features import FRAME_SEC, audio_chroma, audio_onset_curve, load_audio
    from quartet_companion.align.pipeline import FINE_POOL, _pool, _score_feats
    from quartet_companion.unfold import PlayingOrder, unfolded_notes

    cfg = P.load_config(pid, ROOT)
    score = P.load_piece_score(cfg, ROOT)
    notes = unfolded_notes(score, PlayingOrder("x", [m["mc"] for m in ms], ""))
    q0 = ms[i0]["perf_start_qb"]
    q1 = end_qb if end_qb is not None else ms[i1]["perf_start_qb"]
    sub = notes[(notes["perf_qb"] >= q0) & (notes["perf_qb"] < q1)].copy()
    sub["perf_qb"] -= q0
    y = load_audio(str(P._resolve(cfg["audio"]["path"], ROOT)), t0, t1 - t0)
    ax, ao = _pool(audio_chroma(y), FINE_POOL), _pool(audio_onset_curve(y), FINE_POOL)
    sx, so, fpq = _score_feats(sub, q1 - q0, ax.shape[1])
    path, _ = dtw_mod.dtw(dtw_mod.cost_matrix(sx, ax, so, ao))
    fsec = FRAME_SEC * FINE_POOL
    sfr, af = path[:, 0], path[:, 1]
    new = []
    for i in range(i0, i1):
        k = min(int(np.searchsorted(sfr, (ms[i]["perf_start_qb"] - q0) * fpq)), len(af) - 1)
        new.append(t0 + af[k] * fsec)
    new[0] = t0
    return new


def _sound_start(src, bar1, lo):
    """Last moment before bar 1 that follows 0.8 s of near silence (30 dB below the opening)."""
    import librosa
    lo = max(0.0, lo)
    if bar1 - lo < 0.5:
        return bar1
    y, sr = librosa.load(str(src), sr=11025, mono=True, offset=lo, duration=bar1 + 4 - lo)
    hop = sr // 10
    db = 20 * np.log10(np.maximum(librosa.feature.rms(y=y, frame_length=2 * hop, hop_length=hop)[0], 1e-10))
    k1 = int((bar1 - lo) * 10)
    ref = float(np.max(db[k1:k1 + 40])) if k1 < len(db) else float(db.max())
    k = k1
    while k > 8 and not np.all(db[k - 8:k] < ref - 30.0):
        k -= 1
    return lo + k / 10


def _print(ms, rows, old=None):
    for i in rows:
        m = ms[i]
        was = f"  (was {old[i]:.2f})" if old and abs(old[i] - m["start_sec"]) > 0.005 else ""
        print(f"  bar {m['label']:>6}  {m['start_sec']:9.2f} s{was}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["show", "set", "refine", "opening", "ending"])
    ap.add_argument("piece")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--first", type=int)
    ap.add_argument("--last", type=int)
    a = ap.parse_args(argv)
    path, al = _load(a.piece)
    ms = al["measures"]
    old = [m["start_sec"] for m in ms]

    if a.command == "show":
        n = len(ms)
        rows = range(0, min(n, a.first)) if a.first else range(max(0, n - (a.last or 12)), n)
        _print(ms, rows)
        print(f"  last bar ends {ms[-1]['end_sec']:.2f} s")
        return

    if a.command == "set":
        pairs = [x.split("=", 1) for x in a.args]
        if not pairs or any(len(p) != 2 for p in pairs):
            sys.exit("give label=seconds pairs, e.g. 191=377.4 END=385.6")
        end = next((float(s) for lab, s in pairs if lab.upper() == "END"), None)
        times = dict(sorted((_index(ms, lab), float(s)) for lab, s in pairs if lab.upper() != "END"))
        _apply_starts(ms, times, end)
        rows = sorted(set(times) | ({len(ms) - 1} if end is not None else set()))
        _print(ms, rows, old)
        _save(path, al, "Bars " + ", ".join(ms[i]["label"] for i in rows) + " timed by hand.", a.write)
        return

    if a.command == "refine":
        if len(a.args) != 2:
            sys.exit("give two bar labels: refine <id> <from> <to>")
        i0, i1 = _index(ms, a.args[0]), _index(ms, a.args[1])
        if i1 <= i0 + 1:
            sys.exit("the second bar must come at least two bars after the first")
        new = _realign(a.piece, ms, i0, i1, ms[i0]["start_sec"], ms[i1]["start_sec"])
        _apply(ms, i0, new)
        _print(ms, range(i0, i1), old)
        _save(path, al, f"Bars {a.args[0]}-{a.args[1]} aligned again on their own.", a.write)
        return

    if a.command == "opening":
        cfg = P.load_config(a.piece, ROOT)
        src = P._resolve(cfg["audio"]["path"], ROOT)
        s0 = _sound_start(src, ms[0]["start_sec"], float(cfg["audio"].get("start_sec") or 0.0))
        gap = ms[0]["start_sec"] - s0
        print(f"  sound starts {s0:.2f} s, bar 1 at {ms[0]['start_sec']:.2f} s (gap {gap:.2f} s)")
        if gap < 1.0:
            print("  nothing to do")
            return
        k = min(10, len(ms) - 1)
        new = _realign(a.piece, ms, 0, k, s0, ms[k]["start_sec"])
        new[0] = s0 + 0.05
        _apply(ms, 0, new)
        _print(ms, range(0, k), old)
        _save(path, al, f"Opening: the first {k} bars aligned again from where the sound starts ({s0:.1f} s).",
              a.write)
        return

    if a.command == "ending":
        if len(a.args) != 2:
            sys.exit("give a bar label and the end of the sound: ending <id> <from> <seconds>")
        i0, tend = _index(ms, a.args[0]), float(a.args[1])
        if tend <= ms[i0]["start_sec"]:
            sys.exit("the end of the sound must come after the start of that bar")
        new = _realign(a.piece, ms, i0, len(ms), ms[i0]["start_sec"], tend, ms[-1]["perf_end_qb"])
        _apply(ms, i0, new, tend)
        _print(ms, range(i0, len(ms)), old)
        _save(path, al, f"Bars {a.args[0]}-{ms[-1]['label']} aligned again up to the end of the sound ({tend:.1f} s).",
              a.write)
        return


if __name__ == "__main__":
    main()
