"""Build the local web player (a static site in ./site).

For each piece that has facts.json, we write site/pieces/<id>/data.json
(facts + alignment + guides) and copy the recording next to it (WAV files
are converted to MP3 to keep the folder small). Open it with `qc serve`.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from . import pieces as P

WEB_DIR = Path(__file__).resolve().parent / "web"

MEASURE_KEYS = ["mc", "label", "section", "key", "lead", "co_lead", "lead_confidence", "texture",
                "dynamic", "active_parts", "cadence", "markings"]


def _audio_clip_for_site(src: Path, dst_dir: Path, start_sec: float, end_sec: float,
                         stamp: float, name: str = "audio.mp3") -> tuple[str, float]:
    """Write just this movement's part of the recording as MP3.

    A recording file may hold a whole work (all movements). Cutting it means
    each movement in the player starts at its own first measure.
    Returns (file name, offset in seconds that was cut from the start).
    """
    import shutil
    import subprocess
    import soundfile as sf
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / name
    info = sf.info(str(src))
    clip_start = max(0.0, start_sec - 1.5)
    clip_end = min(info.duration, end_sec + 3.0)
    meta = dst_dir / (Path(name).stem + ".clip.json")
    # Re-cut only when the source or the cut points change (not after every re-alignment).
    want = {"src": str(src), "src_mtime": src.stat().st_mtime, "start": round(clip_start, 1), "end": round(clip_end, 1)}
    if dst.exists() and meta.exists() and json.loads(meta.read_text()) == want:
        return dst.name, clip_start
    ffmpeg = shutil.which("ffmpeg")
    done = False
    if ffmpeg:          # fast: seeks straight to the start instead of decoding from the beginning
        r = subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", f"{clip_start:.3f}", "-to", f"{clip_end:.3f}",
                            "-i", str(src), "-vn", "-c:a", "libmp3lame", "-q:a", "2", str(dst)],
                           capture_output=True)
        done = r.returncode == 0 and dst.exists() and dst.stat().st_size > 0
    if not done:
        data, sr = sf.read(str(src), start=int(clip_start * info.samplerate),
                           stop=int(clip_end * info.samplerate), always_2d=False)
        sf.write(str(dst), data, sr, format="MP3")
    meta.write_text(json.dumps(want))
    return dst.name, clip_start
    data, sr = sf.read(str(src), start=int(clip_start * info.samplerate),
                       stop=int(clip_end * info.samplerate), always_2d=False)
    sf.write(str(dst), data, sr, format="MP3")
    meta.write_text(json.dumps(want))
    return dst.name, clip_start


def _short_credit(credit: str) -> str:
    """'Koeckert Quartet, IMSLP #502448 (...)' -> 'Koeckert Quartet'."""
    return re.split(r"[,(]", credit or "")[0].strip()


def _recording_bundle(al_path: Path, audio_cfg: dict, root: Path, out_dir: Path, clip_name: str,
                      whole_file_dir: Path | None = None) -> dict:
    """One recording for the player: its audio clip and the time of every measure inside it.

    whole_file_dir: do not cut or re-encode the recording (licences that forbid changes,
    e.g. CC BY-NC-ND): copy the original file once into that folder, unchanged, and let the
    player start at the movement's first bar (it already stops at the movement's end)."""
    al = P.read_json(al_path)
    # play the cleaned version if one was made (same timing as the original)
    audio_src = P._resolve(audio_cfg.get("playback") or audio_cfg["path"], root)
    audio_name, offset = "", 0.0
    if whole_file_dir is not None:
        audio_src = P._resolve(audio_cfg["path"], root)          # never the cleaned (changed) copy
        if audio_src.exists():
            whole_file_dir.mkdir(parents=True, exist_ok=True)
            dst = whole_file_dir / re.sub(r"[^A-Za-z0-9._-]+", "_", audio_src.name)
            if not dst.exists() or dst.stat().st_size != audio_src.stat().st_size:
                shutil.copy2(audio_src, dst)
            audio_name = f"../../audio/{dst.name}"
    elif audio_src.exists():
        first = min(m["start_sec"] for m in al["measures"])
        last = max(m["end_sec"] for m in al["measures"])
        audio_name, offset = _audio_clip_for_site(audio_src, out_dir, first, last, al_path.stat().st_mtime,
                                                  clip_name)
    measures = []
    for m in al["measures"]:
        row = {k: m[k] for k in ("occurrence", "mc", "label", "start_sec", "end_sec", "flagged", "tempo_qpm")}
        row["start_sec"] = round(row["start_sec"] - offset, 3)     # times inside the clip
        row["end_sec"] = round(row["end_sec"] - offset, 3)
        measures.append(row)
    return {"audio": audio_name, "order": al["order"], "order_description": al["order_description"],
            "warnings": al["warnings"], "clip_offset_sec": round(offset, 3), "measures": measures,
            "credit": audio_cfg.get("credit", "")}


def _printed_pages(piece_id: str, cfg: dict, root: Path, out: Path) -> dict | None:
    """Scores read from a PDF: show the original printed pages (no OMR mistakes),
    with measure boxes found by Audiveris. Set "score_view": "redrawn" in the
    config to draw the recognised notes instead."""
    geo_path = P.piece_dir(piece_id, root) / "printed" / "geometry.json"
    if cfg.get("score_view") == "redrawn" or not geo_path.exists():
        return None
    from .io.omr_geometry import printed_measure_map
    geometry = json.loads(geo_path.read_text())
    score = P.load_piece_score(cfg, root)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for pg in geometry["pages"]:
        shutil.copy2(geo_path.parent / pg["file"], out / pg["file"])
    measures = printed_measure_map(score, geometry)
    if len(measures) < 0.8 * len(score.measures):
        print(f"  [score] {piece_id}: printed pages match only {len(measures)} of {len(score.measures)} measures")
    return {"kind": "image", "pages": len(geometry["pages"]),
            "page_files": [pg["file"] for pg in geometry["pages"]],
            "page_sizes": [[pg["w"], pg["h"]] for pg in geometry["pages"]],
            "measures": {str(k): v for k, v in measures.items()}}


def _score_pages(piece_id: str, cfg: dict, root: Path, site_dir: Path) -> dict | None:
    """Render the score to SVG pages (cached). Returns {"pages": n, "measures": {mc: {page, id}}}."""
    try:
        from .score_render import measure_map, render_pages, score_to_musicxml, with_part_names
    except ImportError:
        return None
    d = P.piece_dir(piece_id, root)
    out = site_dir / "pieces" / piece_id / "score"
    printed = _printed_pages(piece_id, cfg, root, out)
    if printed is not None:
        return printed
    stamp_file = out / "stamp.json"
    facts_mtime = (d / "facts.json").stat().st_mtime
    score = P.load_piece_score(cfg, root)
    if stamp_file.exists() and json.loads(stamp_file.read_text()).get("facts_mtime") == facts_mtime \
            and (out / "score.json").exists():
        info = json.loads((out / "score.json").read_text())
    else:
        try:
            if cfg["score"]["type"] == "abc" or str(cfg["score"].get("path", "")).lower().endswith((".mid", ".midi")):
                src = score_to_musicxml(score, d / "score_for_display.musicxml")
            else:
                src = P._resolve(cfg["score"]["path"], root)
                # show our part names (OMR files say "Voice 1", "Voice 2" ...)
                src = with_part_names(src, score.parts, d / "score_for_display.musicxml")
            if out.exists():
                shutil.rmtree(out)
            try:
                info = render_pages(src, out, len(score.measures))
            except Exception:
                if cfg["score"]["type"] == "abc":
                    raise
                # the original file could not be drawn: draw our own reading of it instead
                print(f"  [score] {piece_id}: drawing from the analysed notes instead of the original file")
                src = score_to_musicxml(score, d / "score_for_display.musicxml")
                if out.exists():
                    shutil.rmtree(out)
                info = render_pages(src, out, len(score.measures))
            stamp_file.write_text(json.dumps({"facts_mtime": facts_mtime}))
        except Exception as exc:          # a drawing problem must not break the player
            print(f"  [score] {piece_id}: could not draw the score ({type(exc).__name__}: {exc})")
            return None
    return {"pages": info["pages"], "measures": {str(k): v for k, v in measure_map(score, info).items()}}


def piece_bundle(piece_id: str, root: Path, site_dir: Path, public: bool = False) -> dict | None:
    """Everything the player needs for one piece. public=True: only recordings whose
    licence allows a public website (see audio_policy); None if the piece must stay private."""
    d = P.piece_dir(piece_id, root)
    if not (d / "facts.json").exists():
        return None
    cfg = P.load_config(piece_id, root)
    if public and cfg.get("public") is False:
        return None
    facts = P.read_json(d / "facts.json")
    bundle = {
        "id": piece_id,
        "piece": facts["piece"],
        "sections": [{k: s[k] for k in ("name", "start_mc", "end_mc", "start_label", "end_label")} for s in facts["sections"]],
        "key_plan": facts["key_plan"],
        "themes": facts["themes"],
        "theme_occurrences": facts["theme_occurrences"],
        "variations": facts.get("variations", []),
        "measures": [{k: m[k] for k in MEASURE_KEYS} for m in facts["measures"]],
        "method_notes": facts.get("method_notes", {}),
        "credits": {"score": facts["piece"].get("score_source", ""), "audio": cfg.get("audio", {}).get("credit", "")},
        "guides": {}, "verification": {},
    }
    q = P.read_json(d / "quality.json") if (d / "quality.json").exists() else None
    if q:
        bundle["score_quality"] = {"verdict": q["verdict"], "share_wrong_length": q["share_wrong_length"]}
    if _is_omr(cfg) and (d / "alignment.json").exists():
        doubts = score_doubts(P.read_json(d / "alignment.json"), q)
        if doubts:
            bundle["score_doubts"] = doubts
    recs = []
    for rid, audio_cfg, fname in [("main", cfg.get("audio") or {}, "alignment.json")] + \
            [(rid, r, f"alignment_{rid}.json") for rid, r in (cfg.get("recordings") or {}).items()]:
        if not (d / fname).exists():
            continue
        policy = audio_policy(audio_cfg) if public else "clip"
        if policy == "private":
            continue
        rec = _recording_bundle(d / fname, audio_cfg, root, site_dir / "pieces" / piece_id,
                                "audio.mp3" if rid == "main" else f"audio_{rid}.mp3",
                                whole_file_dir=(site_dir / "audio") if policy == "whole" else None)
        rec["license"] = audio_license(audio_cfg)
        rec["id"] = rid
        rec["name"] = audio_cfg.get("name") or _short_credit(audio_cfg.get("credit", "")) or rid
        recs.append(rec)
    if public and not recs:
        return None                    # no recording may be published: leave the piece out
    if recs:
        bundle["alignment"] = recs[0]
        bundle["credits"]["audio"] = recs[0].get("credit", "")      # the recording that actually plays
    if len(recs) > 1:
        bundle["recordings"] = recs
    sp = _score_pages(piece_id, cfg, root, site_dir)
    if sp:
        bundle["score"] = sp
    # time signature of every measure (practice mode: count-in clicks)
    try:
        sc = P.load_piece_score(cfg, root)
        bundle["timesig"] = {str(int(mc)): str(ts) for mc, ts in zip(sc.measures["mc"], sc.measures["timesig"])}
    except Exception:              # never break the site for this
        bundle["timesig"] = {}
    from .guide.generate import facts_fingerprint
    fp = facts_fingerprint(facts)
    for f in sorted(d.glob("guide_*.json")):
        if not re.fullmatch(r"guide_[a-z]{2}(-[A-Za-z]+)?\.json", f.name):
            continue                       # backups such as guide_en.before_x.json
        g = P.read_json(f)
        if g.get("facts_fingerprint") not in (None, fp):
            print(f"  [guide] {piece_id} {g['language']}: written for an older version of the facts; "
                  f"not shown. Run: qc guide {piece_id} --lang {g['language']}")
            continue
        bundle["guides"][g["language"]] = g["guide"]
        bundle["verification"][g["language"]] = g["verification"]
    return bundle


# ----------------------------------------------------------------- publishing
# What a public website may do with a recording, by licence:
#   "clip"    open licences (CC0, CC BY, CC BY-SA, EFF Open Audio, public domain everywhere):
#             cut into movements as usual;
#   "whole"   no-derivatives licences (CC BY-NC-ND, CC BY-ND): play the original file unchanged;
#   "private" anything else, including "public domain outside the US" and unknown licences.
LICENSE_URLS = {
    "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC BY-NC-ND 3.0": "https://creativecommons.org/licenses/by-nc-nd/3.0/",
    "CC BY-NC-ND 4.0": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "EFF Open Audio License": "https://web.archive.org/web/2005/http://www.eff.org/IP/Open_licenses/eff_oal.php",
}


def audio_license(audio_cfg: dict) -> str:
    """The recording's licence: the config's "license" field, else read from the credit text."""
    if audio_cfg.get("license"):
        return str(audio_cfg["license"])
    credit = audio_cfg.get("credit", "")
    m = re.search(r"CC[ -]BY(?:-[A-Z]{2})*(?:-[A-Z]{2})?\s*\d\.\d|CC0|EFF Open Audio License", credit)
    return m.group(0).replace("CC-BY", "CC BY") if m else ""


def audio_policy(audio_cfg: dict) -> str:
    if audio_cfg.get("public") is False:
        return "private"
    lic = audio_license(audio_cfg).upper()
    if not lic or "OUTSIDE THE US" in lic or "NON-PD" in lic:
        return "private"
    if "-ND" in lic:
        return "whole"
    if lic.startswith(("CC BY", "CC0", "EFF OPEN AUDIO", "PUBLIC DOMAIN")):
        return "clip"
    return "private"


def write_credits_page(site_dir: Path, bundles: list[dict]) -> None:
    """credits.html: where every score and recording comes from, and under which licence."""
    import html
    rows = []
    for b in bundles:
        recs = b.get("recordings") or ([b["alignment"]] if b.get("alignment") else [])
        rec_txt = "<br>".join(
            html.escape(r.get("credit") or r.get("name", "")) +
            (f' · <a href="{LICENSE_URLS[r["license"]]}">{html.escape(r["license"])}</a>' if r.get("license") in LICENSE_URLS
             else (f" · {html.escape(r['license'])}" if r.get("license") else ""))
            for r in recs) or "–"
        rows.append(f"<tr><td>{html.escape(b['piece']['title'])}</td><td>{html.escape(str(b['credits'].get('score', '')))}</td>"
                    f"<td>{rec_txt}</td></tr>")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Quartet Companion · Credits</title>
<link rel="stylesheet" href="style.css"><style>main{{max-width:1100px}} table{{border-collapse:collapse;width:100%;font-size:14px}}
td,th{{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}} a{{color:var(--accent)}}</style></head>
<body><main><p><a href="./">← Quartet Companion</a></p><h1 style="font-family:var(--serif)">Credits and licences</h1>
<p>Scores: OpenScore String Quartets (CC0) or public-domain editions from IMSLP. Recordings: as listed, under their own
licences; recordings whose licence forbids changes are played from the original, unchanged file. Listening guides and
analyses: CC BY 4.0. Code: MIT.</p>
<p>乐谱：OpenScore 弦乐四重奏曲库（CC0）或 IMSLP 上的公版乐谱。录音：见下表，各自遵守其授权；不允许修改的录音直接播放原始文件。
导读与分析：CC BY 4.0。代码：MIT。</p>
<table><tr><th>Piece</th><th>Score</th><th>Recording</th></tr>{''.join(rows)}</table></main></body></html>"""
    (site_dir / "credits.html").write_text(page, encoding="utf-8")


DOUBT_Z = 4.0      # how far below its neighbours a bar's note match must fall
MAX_DOUBTS = 12    # show at most this many bars per movement


def _is_omr(cfg: dict) -> bool:
    sc = cfg.get("score") or {}
    return bool(cfg.get("omr")) or "omr" in str(sc.get("path", "")).lower() or "omr" in str(sc.get("original", "")).lower()


def score_doubts(al: dict, quality: dict | None) -> list[dict]:
    """Bars whose written notes fit the sound much worse than the bars around them
    (scores read by OMR: likely misread notes, worth comparing by ear).

    Tested by corrupting 10 bars of a clean score aligned with its real recording:
    at this threshold about half of the changed bars were found, plus 5-6 bars that
    stand out even in the clean score (mostly at repeat jumps, now left out). So these
    are hints, not verdicts."""
    import numpy as np
    by: dict[int, list[float]] = {}
    labels: dict[int, str] = {}
    for m in al.get("measures", []):
        v = m.get("note_sim")
        if v is None or (isinstance(v, float) and np.isnan(v)):
            continue
        by.setdefault(int(m["mc"]), []).append(float(v))
        labels[int(m["mc"])] = str(m["label"])
    if len(by) < 12:
        return []
    # Bars next to a jump in the playing order (repeat signs, endings, da capo) and the
    # first/last bar are left out: timing there is less exact, so they look worse in
    # every score, misread or not (seen in the test above).
    order = [int(m["mc"]) for m in al.get("measures", [])]
    edge = {order[0], order[-1]} if order else set()
    for a, b in zip(order, order[1:]):
        if b != a + 1:
            edge.update((a, b))
    by = {k: v for k, v in by.items() if k not in edge} if len(by) - len(edge) >= 12 else by
    mcs = sorted(by)
    sim = np.array([np.mean(by[k]) for k in mcs])
    local = np.array([np.median(sim[max(0, i - 6): i + 7]) for i in range(len(sim))])
    d = local - sim
    mad = np.median(np.abs(d - np.median(d))) + 1e-6
    wrong = {str(w["label"]) for w in (quality or {}).get("measures_with_wrong_length", [])}
    out = []
    for mc, z, sv in zip(mcs, d / mad, sim):
        if z >= DOUBT_Z:
            reasons = ["notes"] + (["length"] if labels[mc] in wrong else [])
            out.append({"mc": mc, "label": labels[mc], "reasons": reasons, "match": round(float(sv), 2),
                        "z": round(float(z), 1)})
    # a long list is no help to a listener: keep the clearest ones, in score order
    out = sorted(sorted(out, key=lambda x: -x["z"])[:MAX_DOUBTS], key=lambda x: x["mc"])
    return out


def _index_entry(pid: str, work: str, b: dict) -> dict:
    """What the player's library list needs to search and filter (no per-bar data)."""
    pc = b["piece"]
    al = b.get("alignment") or {}
    ms = al.get("measures") or []
    dur = (float(ms[-1]["end_sec"]) - float(ms[0]["start_sec"])) if ms else None
    key = pc.get("home_key") or ""
    return {"id": pid, "work": work, "title": pc["title"], "composer": pc.get("composer", ""),
            "has_audio": "alignment" in b, "languages": sorted(b["guides"]),
            "key": key, "mode": key.split()[-1] if key else "",
            "time_signature": pc.get("time_signature", ""), "tempo": pc.get("tempo_marking", ""),
            "n_measures": pc.get("n_measures"), "duration_sec": round(dur, 1) if dur else None,
            "n_recordings": max(len(b.get("recordings") or []), 1 if ms else 0),
            "ensemble": {3: "trio", 4: "quartet", 5: "quintet"}.get(len(pc.get("parts") or []), "other")}


def build_site(root: Path | None = None, out: Path | None = None, only: list[str] | None = None,
               public: bool = False) -> Path:
    """public=True builds the version for a public website (default folder public_site/):
    pieces marked "public": false and recordings that may not be published are left out,
    and no-derivatives recordings are played from their original files."""
    root = root or P.project_root()
    site_dir = out or (root / ("public_site" if public else "site"))
    site_dir.mkdir(parents=True, exist_ok=True)
    for f in WEB_DIR.iterdir():
        if f.is_file():
            shutil.copy2(f, site_dir / f.name)
    index = []
    for cfg_path in sorted((root / "pieces").glob("*/config.json")):
        pid = cfg_path.parent.name
        built = site_dir / "pieces" / pid / "data.json"
        if only and not any(pid.startswith(o) for o in only) and built.exists():
            b = json.loads(built.read_text())          # keep the last build of this piece
        else:
            b = piece_bundle(pid, root, site_dir, public=public)
            if b is None:
                if public and (site_dir / "pieces" / pid).exists():
                    shutil.rmtree(site_dir / "pieces" / pid)      # was public before, not any more
                if public and (P.piece_dir(pid, root) / "facts.json").exists():
                    print(f"[site] {pid}: left out (its recordings may not be published)", flush=True)
                continue
            built.parent.mkdir(parents=True, exist_ok=True)
            built.write_text(json.dumps(b, ensure_ascii=False))
            print(f"[site] {pid}", flush=True)
        work = pid.rsplit("_", 1)[0] if re.search(r"_\d+$", pid) else pid
        index.append(_index_entry(pid, work, b))
    (site_dir / "pieces" / "index.json").parent.mkdir(parents=True, exist_ok=True)
    (site_dir / "pieces" / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1))
    write_credits_page(site_dir, [json.loads((site_dir / "pieces" / e["id"] / "data.json").read_text()) for e in index])
    return site_dir
