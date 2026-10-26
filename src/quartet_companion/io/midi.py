"""Load a MIDI file (e.g. from the Mutopia Project) as a Score.

MIDI has exact note timing but no repeat signs, and it does not say
whether the music starts with an upbeat (pickup). Give `pickup_qb` (in
quarter notes) when the piece starts with an upbeat, so measure numbers
match the printed score.

Use MIDI when the piece has no repeats (or the MIDI already plays them
out), or when OMR / MusicXML conversion gave poor rhythms.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..score import EVENT_COLUMNS, Score, default_next, make_labels
from .musicxml import _part_name, _unique_names

_KEY_FIFTHS = {"C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5, "F#": 6, "C#": 7, "F": -1, "Bb": -2, "Eb": -3,
               "Ab": -4, "Db": -5, "Gb": -6, "Cb": -7}
_MINOR_FIFTHS = {"A": 0, "E": 1, "B": 2, "F#": 3, "C#": 4, "G#": 5, "D#": 6, "A#": 7, "D": -1, "G": -2,
                 "C": -3, "F": -4, "Bb": -5, "Eb": -6, "Ab": -7}


def _fifths(key: str) -> int:
    if key.endswith("m"):
        return _MINOR_FIFTHS.get(key[:-1], 0)
    return _KEY_FIFTHS.get(key, 0)


def load_midi(path: str | Path, piece_id: str | None = None, title: str | None = None, composer: str = "",
              pickup_qb: float | None = None) -> Score:
    import mido
    path = Path(path)
    mf = mido.MidiFile(str(path))
    tpb = mf.ticks_per_beat
    tracks, names = [], []
    time_sigs: list[tuple[float, int, int]] = []
    key_sigs: list[tuple[float, int]] = []
    for tr in mf.tracks:
        tick, name = 0, ""
        on: dict[tuple[int, int], list[int]] = {}
        notes = []
        for msg in tr:
            tick += msg.time
            if msg.type == "track_name":
                name = msg.name.strip().rstrip(":")
            elif msg.type == "time_signature":
                time_sigs.append((tick / tpb, msg.numerator, msg.denominator))
            elif msg.type == "key_signature":
                key_sigs.append((tick / tpb, _fifths(msg.key)))
            elif msg.type == "note_on" and msg.velocity > 0:
                on.setdefault((msg.channel, msg.note), []).append(tick)
            elif msg.type in ("note_off", "note_on"):
                starts = on.get((msg.channel, msg.note))
                if starts:
                    s = starts.pop(0)
                    notes.append((s / tpb, (tick - s) / tpb, msg.note))
        if notes:
            tracks.append(notes)
            names.append(name)
    if not tracks:
        raise ValueError(f"no notes in {path}")
    end = max(o + d for tr in tracks for o, d, _ in tr)

    # ---- measures from time signatures (+ optional pickup)
    time_sigs = sorted(set(time_sigs)) or [(0.0, 4, 4)]
    key_sigs = sorted(set(key_sigs)) or [(0.0, 0)]

    def ts_at(q):
        cur = time_sigs[0]
        for t in time_sigs:
            if t[0] <= q + 1e-6:
                cur = t
        return cur

    def ks_at(q):
        cur = key_sigs[0][1]
        for t, f in key_sigs:
            if t <= q + 1e-6:
                cur = f
        return cur

    rows, pos, mn = [], 0.0, 0 if pickup_qb else 1
    while pos < end - 1e-6:
        _, num, den = ts_at(pos)
        bar = num * 4.0 / den
        dur = pickup_qb if (pickup_qb and not rows) else bar
        rows.append({"mc": len(rows) + 1, "mn": mn, "start_qb": pos, "dur_qb": dur, "timesig": f"{num}/{den}",
                     "keysig": ks_at(pos), "volta": 0, "repeats": ""})
        pos += dur
        mn += 1
    measures = pd.DataFrame(rows)
    measures["next"] = default_next(measures)
    measures["label"] = make_labels(measures)
    starts = measures["start_qb"].values

    import numpy as np
    note_rows = []
    for pi, tr in enumerate(tracks):
        for o, d, midi in tr:
            i = int(np.searchsorted(starts, o + 1e-6, side="right") - 1)
            i = max(0, min(i, len(measures) - 1))
            note_rows.append({"mc": int(measures.loc[i, "mc"]), "mn": int(measures.loc[i, "mn"]), "onset_qb": o,
                              "dur_qb": d, "part": pi, "midi": int(midi), "is_onset": True, "grace": False})
    notes = pd.DataFrame(note_rows).sort_values(["onset_qb", "part", "midi"]).reset_index(drop=True)
    parts = _unique_names([_part_name(_Named(n), i) for i, n in enumerate(names)])
    return Score(piece_id=piece_id or path.stem, title=title or path.stem, parts=parts,
                 measures=measures[["mc", "mn", "label", "start_qb", "dur_qb", "timesig", "keysig", "volta",
                                    "repeats", "next"]],
                 notes=notes, harmony=None, events=pd.DataFrame(columns=EVENT_COLUMNS),
                 meta={"source": path.name, "composer": composer, "harmony_source": "auto"})


class _Named:
    """Tiny adapter so MIDI track names can reuse the MusicXML part-name rules."""

    def __init__(self, name: str):
        n = name.replace("violinII", "Violin II")
        self.partName = n if n != name else name.replace("violinI", "Violin I")

    def getInstrument(self, returnDefault=False):
        return None
