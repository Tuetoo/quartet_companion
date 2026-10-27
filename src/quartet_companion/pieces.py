"""A "piece" folder holds everything about one movement.

pieces/<piece_id>/
    config.json        what the piece is and where its score and audio are
    score.mxl          the score (if it came from MusicXML / OMR)
    quality.json       OMR / score problems to check
    facts.json         the analysis (single source of truth)
    alignment.json     when each measure starts in the recording
    guide_en.json      listening guide in English (verified)
    guide_zh.json      listening guide in Chinese (verified)

The functions here run each step and save its result, so steps can be
re-run one at a time.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .score import Score

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_root() -> Path:
    return PROJECT_ROOT


def piece_dir(piece_id: str, root: Path | None = None) -> Path:
    return (root or PROJECT_ROOT) / "pieces" / piece_id


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def write_json(path: Path, data) -> None:
    from .facts import _json_default
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=_json_default))


def load_config(piece_id: str, root: Path | None = None) -> dict:
    return read_json(piece_dir(piece_id, root) / "config.json")


def save_config(piece_id: str, cfg: dict, root: Path | None = None) -> None:
    write_json(piece_dir(piece_id, root) / "config.json", cfg)


def _resolve(path: str, root: Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else root / p


def load_piece_score(cfg: dict, root: Path | None = None) -> Score:
    """Load the score described by a config (ABC dataset or a music file)."""
    root = root or PROJECT_ROOT
    src = cfg["score"]
    if src["type"] == "abc":
        from .io.abc import load_abc_movement
        score = load_abc_movement(_resolve(src["abc_dir"], root), src["piece"])
    elif isinstance(src["path"], str) and src["path"].lower().endswith((".mid", ".midi")):
        from .io.midi import load_midi
        score = load_midi(_resolve(src["path"], root), piece_id=cfg["id"], title=cfg.get("title"),
                          composer=cfg.get("composer", ""), pickup_qb=cfg.get("pickup_qb"))
        if cfg.get("parts") and len(cfg["parts"]) == len(score.parts):   # MIDI tracks are often unnamed
            score.parts = list(cfg["parts"])
    else:
        from .io.musicxml import load_music_file
        from .io.omr import concat_scores, consolidate_parts, rename_parts
        paths = src["path"] if isinstance(src["path"], list) else [src["path"]]
        pieces = []
        for pth in paths:                 # OMR may cut one movement in two: join the pieces
            sc = load_music_file(_resolve(pth, root), piece_id=cfg["id"],
                                 title=cfg.get("title"), composer=cfg.get("composer", ""))
            if cfg.get("parts"):
                if len(cfg["parts"]) == len(sc.parts):
                    rename_parts(sc, cfg["parts"])
                else:                     # OMR split or mislabelled parts: map them onto the instruments
                    consolidate_parts(sc, cfg["parts"])
            pieces.append(sc)
        score = concat_scores(pieces) if len(pieces) > 1 else pieces[0]
    if cfg.get("repeats") is not None:
        set_repeats(score, cfg["repeats"])
    if cfg.get("structure"):
        set_structure(score, cfg["structure"])
    if cfg.get("title"):
        score.title = cfg["title"]
    if cfg.get("composer"):
        score.meta["composer"] = cfg["composer"]
    score.piece_id = cfg["id"]
    return score


def copy_into_piece(src: Path, piece_id: str, name: str, root: Path | None = None) -> str:
    d = piece_dir(piece_id, root)
    d.mkdir(parents=True, exist_ok=True)
    dst = d / name
    if Path(src).resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return str(dst.relative_to(root or PROJECT_ROOT))


def set_structure(score: Score, structure: dict) -> None:
    """Repeat signs, first/second endings and D.C. texts for scores that have none (MIDI).

    structure = {"marks": {"2": "start", "9": "end"},     # by measure id (mc)
                 "volta": {"9": 1, "10": 2},
                 "texts": {"18": "Trio", "37": "Menuetto D.C."}}
    """
    from .io.musicxml import _next_pointers
    from .score import make_labels
    m = score.measures
    marks = {int(k): v for k, v in (structure.get("marks") or {}).items()}
    volta = {int(k): int(v) for k, v in (structure.get("volta") or {}).items()}
    m["repeats"] = [marks.get(int(mc), "") for mc in m["mc"]]
    m["volta"] = [volta.get(int(mc), 0) for mc in m["mc"]]
    m["label"] = make_labels(m)
    m["next"] = _next_pointers(m)
    texts = structure.get("texts") or {}
    if texts:
        import pandas as pd
        from .score import EVENT_COLUMNS
        rows = []
        for k, v in texts.items():
            row = m[m["mc"] == int(k)].iloc[0]
            rows.append({"mc": int(k), "mn": int(row["mn"]), "onset_qb": float(row["start_qb"]), "part": 0,
                         "kind": "text", "value": str(v)})
        new = pd.DataFrame(rows, columns=EVENT_COLUMNS)
        ev = score.events
        score.events = new if ev is None or ev.empty else pd.concat([ev, new], ignore_index=True)
    # notes carry no labels, but keep mn consistent with the measures
    score.measures = m


def set_repeats(score: Score, spans: list) -> None:
    """Replace the score's repeat signs (OMR often misreads them).

    spans: [["25", "28"], ["33", "36"], ...] = measure labels where a repeated
    passage starts and ends. An empty list means: no repeat signs at all.
    First/second endings are not supported here (edit the file in MuseScore).
    """
    from .score import default_next
    m = score.measures
    if "volta" in m.columns and (m["volta"].astype(int) > 0).any():
        raise ValueError('"repeats" cannot describe first/second endings; use "structure" '
                         '(marks and volta) instead, or fix the file in MuseScore')
    mcs = list(m["mc"].astype(int))
    label_to_mc = {str(lb): int(mc) for lb, mc in zip(m["label"], m["mc"])}
    nxt = default_next(m)
    marks = [""] * len(mcs)
    for span in spans:
        a, b = (label_to_mc.get(str(x)) for x in span)
        if a is None or b is None or a > b:
            raise ValueError(f"repeat {span}: unknown measure label (labels: {', '.join(list(label_to_mc)[:8])} ...)")
        i, j = mcs.index(a), mcs.index(b)
        nxt[j] = [a] + nxt[j]
        marks[i] = (marks[i] + " start").strip()
        marks[j] = (marks[j] + " end").strip()
    m["next"] = nxt
    m["repeats"] = marks
    if "volta" in m.columns:
        m["volta"] = 0
