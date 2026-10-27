"""Build the web player: a static site in ./site (local, everything) or ./public_site
(public=True: only what the licences allow, see audio_policy).

For each piece that has facts.json, we write site/pieces/<id>/data.json (facts, alignment,
guides, score pages) and its audio: this movement's part of the recording as a
constant-bitrate MP3 clip, or, when the licence forbids changes, the original file
(shared by all movements, in site/audio/). Open the local site with `qc serve`.
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


def ffmpeg_exe() -> str | None:
    """ffmpeg on the PATH (brew install ffmpeg), else the copy that the Python package
    imageio-ffmpeg brings along inside .venv (pip install imageio-ffmpeg)."""
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _audio_clip_for_site(src: Path, dst_dir: Path, start_sec: float, end_sec: float,
                         name: str = "audio.mp3") -> tuple[str, float]:
    """Write just this movement's part of the recording as MP3.

    A recording file may hold a whole work (all movements). Cutting it means
    each movement in the player starts at its own first measure.
    Returns (file name, offset in seconds that was cut from the start).
    """
    import subprocess
    import soundfile as sf
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / name
    info = sf.info(str(src))
    clip_start = round(max(0.0, start_sec - 1.5), 1)      # cut exactly where the cache key says
    clip_end = round(min(info.duration, end_sec + 3.0), 1)
    meta = dst_dir / (Path(name).stem + ".clip.json")
    # Re-cut only when the source or the cut points change (not after every re-alignment).
    # Constant bitrate: browsers can only jump to an exact time in a constant-bitrate MP3
    # (in a variable-bitrate one, Safari's jumps can land seconds away from the bar).
    # The source is recorded by name and size only: this file is published, and a full
    # path would show the folders on the owner's computer.
    want = {"src": src.name, "src_size": src.stat().st_size, "src_mtime": src.stat().st_mtime,
            "start": clip_start, "end": clip_end, "encoding": "cbr192"}
    if dst.exists() and meta.exists() and json.loads(meta.read_text()) == want:
        return dst.name, clip_start
    ffmpeg = ffmpeg_exe()
    done = False
    if ffmpeg:          # fast: seeks straight to the start instead of decoding from the beginning
        r = subprocess.run([ffmpeg, "-v", "error", "-y", "-ss", f"{clip_start:.3f}", "-to", f"{clip_end:.3f}",
                            "-i", str(src), "-vn", "-c:a", "libmp3lame", "-b:a", "192k", str(dst)],
                           capture_output=True)
        done = r.returncode == 0 and dst.exists() and dst.stat().st_size > 0
    if not done:
        data, sr = sf.read(str(src), start=int(clip_start * info.samplerate),
                           stop=int(clip_end * info.samplerate), always_2d=False)
        sf.write(str(dst), data, sr, format="MP3")
    meta.write_text(json.dumps(want))
    return dst.name, clip_start


def _sound_end(src: Path, last_bar_end: float, limit: float) -> float:
    """When the last chord has really died away (the alignment ends where the last bar
    starts to decay; a long final chord or fermata goes on after that). Stops at silence or
    applause, and never after `limit` (the end of this movement's part of the recording)."""
    import librosa
    import numpy as np
    hi = min(limit, last_bar_end + 20.0)
    if hi <= last_bar_end + 0.5:
        return max(last_bar_end, min(limit, last_bar_end + 0.5))
    lo = max(0.0, last_bar_end - 3.0)
    try:
        y, sr = librosa.load(str(src), sr=11025, mono=True, offset=lo, duration=hi - lo)
    except Exception:
        return last_bar_end + 2.5
    hop = sr // 10
    rms = librosa.feature.rms(y=y, frame_length=2 * hop, hop_length=hop)[0]
    db = 20 * np.log10(np.maximum(rms, 1e-10))
    flat = librosa.feature.spectral_flatness(y=y, n_fft=2 * hop, hop_length=hop)[0][:len(db)]
    k0 = int((last_bar_end - lo) * 10)
    ref = float(np.max(db[max(0, k0 - 30):k0 + 1])) if k0 > 0 else float(db.max())
    quiet = ref - 30.0              # 30 dB below the last bars: the chord has died away
    for k in range(k0, len(db) - 8):
        silent = np.all(db[k:k + 8] < quiet)                               # 0.8 s of near silence
        clapping = np.all((flat[k:k + 8] > 0.05) & (db[k:k + 8] > ref - 15))   # applause
        if silent or clapping:
            return lo + k / 10
    return hi


def _stretch_ending(rows: list[dict], sound_end: float) -> None:
    """Keep the last bar highlighted until its chord has died away. (Moving the earlier
    bars automatically was tried and made them late as often as it made them right:
    every ending slows down differently, so those are corrected by ear when needed.)"""
    if rows and sound_end > rows[-1]["end_sec"]:
        rows[-1]["end_sec"] = round(sound_end - 0.2, 3)


_MP3_RATES = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]


def is_vbr_mp3(path: Path, n_frames: int = 2000) -> bool:
    """True if the MP3's first frames use more than one bitrate (variable bitrate)."""
    if path.suffix.lower() != ".mp3":
        return False
    b = path.read_bytes()[:4_000_000]
    i = 0
    if b[:3] == b"ID3":
        i = 10 + ((b[6] << 21) | (b[7] << 14) | (b[8] << 7) | b[9])
    rates, frames = set(), 0
    while i < len(b) - 4 and frames < n_frames:
        if b[i] == 0xFF and (b[i + 1] & 0xE0) == 0xE0:
            bri, sri, pad = b[i + 2] >> 4, (b[i + 2] >> 2) & 3, (b[i + 2] >> 1) & 1
            if bri in (0, 15) or sri == 3:
                i += 1
                continue
            rate = _MP3_RATES[bri]
            rates.add(rate)
            i += 144000 * rate // [44100, 48000, 32000][sri] + pad
            frames += 1
        else:
            i += 1
    return len(rates) > 1


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
            if is_vbr_mp3(audio_src):
                # Same recording, converted to constant bitrate so that jumping to a bar is exact.
                # A format change only (CC licences allow technical changes needed for other formats).
                marker = dst.with_suffix(".cbr.json")
                want = {"src_size": audio_src.stat().st_size, "src_mtime": audio_src.stat().st_mtime}
                if not (dst.exists() and marker.exists() and json.loads(marker.read_text()) == want):
                    import subprocess
                    ffmpeg = ffmpeg_exe()
                    if not ffmpeg:
                        raise SystemExit("ffmpeg is needed to convert variable-bitrate MP3 files for the "
                                         "public site: pip install imageio-ffmpeg (or brew install ffmpeg)")
                    subprocess.run([ffmpeg, "-v", "error", "-y", "-i", str(audio_src), "-vn", "-c:a", "libmp3lame",
                                    "-b:a", "256k", str(dst)], check=True)
                    marker.write_text(json.dumps(want))
            elif not dst.exists() or dst.stat().st_size != audio_src.stat().st_size:
                shutil.copy2(audio_src, dst)
            audio_name = f"../../audio/{dst.name}"
    sound_end = None
    if audio_src.exists():
        last = max(m["end_sec"] for m in al["measures"])
        import soundfile as sf
        limit = float(audio_cfg.get("end_sec") or sf.info(str(audio_src)).duration)
        sound_end = _sound_end(audio_src, last, limit)
    if whole_file_dir is None and audio_src.exists():
        first = min(m["start_sec"] for m in al["measures"])
        audio_name, offset = _audio_clip_for_site(audio_src, out_dir, first, sound_end - 2.0, clip_name)
    measures = []
    for m in al["measures"]:
        row = {k: m[k] for k in ("occurrence", "mc", "label", "start_sec", "end_sec", "flagged", "tempo_qpm")}
        row["start_sec"] = round(row["start_sec"] - offset, 3)     # times inside the clip
        row["end_sec"] = round(row["end_sec"] - offset, 3)
        measures.append(row)
    if sound_end:
        _stretch_ending(measures, sound_end - offset)
    return {"audio": audio_name, "order": al["order"], "order_description": al["order_description"],
            "sound_end_sec": round(sound_end - offset, 3) if sound_end else None,
            "warnings": al["warnings"], "clip_offset_sec": round(offset, 3), "measures": measures,
            "credit": audio_cfg.get("credit", "")}


_SCORE_CACHE: dict = {}


def _load_score(cfg: dict, root: Path):
    """The piece's score, read once per build (reading a long MusicXML file takes seconds)."""
    key = (str(root), json.dumps(cfg, sort_keys=True))
    if key not in _SCORE_CACHE:
        _SCORE_CACHE.clear()                  # one piece at a time: keep memory small
        _SCORE_CACHE[key] = P.load_piece_score(cfg, root)
    return _SCORE_CACHE[key]


def _printed_pages(piece_id: str, cfg: dict, root: Path, out: Path) -> dict | None:
    """Scores read from a PDF: show the original printed pages (no OMR mistakes),
    with measure boxes found by Audiveris. Set "score_view": "redrawn" in the
    config to draw the recognised notes instead."""
    geo_path = P.piece_dir(piece_id, root) / "printed" / "geometry.json"
    if cfg.get("score_view") == "redrawn" or not geo_path.exists():
        return None
    from .io.omr_geometry import printed_measure_map
    geometry = json.loads(geo_path.read_text())
    score = _load_score(cfg, root)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for pg in geometry["pages"]:
        shutil.copy2(geo_path.parent / pg["file"], out / pg["file"])
    if cfg.get("printed_map"):          # score from another source (MIDI): which page boxes are measure mc
        geo = geometry["measures"]
        measures = {}
        for mc, idxs in cfg["printed_map"].items():
            boxes = [b for i in idxs if 0 <= int(i) < len(geo) for b in geo[int(i)]["boxes"]]
            if boxes:
                measures[int(mc)] = {"page": boxes[0]["page"], "id": f"m{mc}", "boxes": boxes}
    else:
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
    try:
        printed = _printed_pages(piece_id, cfg, root, out)
    except Exception as exc:              # a bad page set must not stop the whole build
        print(f"  [score] {piece_id}: could not show the printed pages ({type(exc).__name__}: {exc})")
        printed = None
    if printed is not None:
        return printed
    stamp_file = out / "stamp.json"
    facts_mtime = (d / "facts.json").stat().st_mtime
    score = _load_score(cfg, root)
    if stamp_file.exists() and json.loads(stamp_file.read_text()).get("facts_mtime") == facts_mtime \
            and (out / "score.json").exists():
        info = json.loads((out / "score.json").read_text())
    else:
        try:
            if cfg["score"]["type"] == "abc" or isinstance(cfg["score"].get("path"), list) \
                    or str(cfg["score"].get("path", "")).lower().endswith((".mid", ".midi")):
                # MIDI, ABC, or one movement joined from several OMR files: draw our own reading
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


def _score_credit(cfg: dict, facts: dict) -> str:
    """Where the score comes from, for people (not a file name)."""
    if (cfg.get("score") or {}).get("credit"):
        return str(cfg["score"]["credit"])
    orig = str((cfg.get("score") or {}).get("original", ""))
    if "OpenScore" in orig:
        return "OpenScore String Quartets (CC0)"
    m = re.search(r"\(([^()]*(?:IMSLP|Mutopia|public domain)[^()]*)\)", orig, re.I)
    if m:
        return m.group(1)
    m = re.search(r"IMSLP(\d+)", orig)
    if m:
        return f"IMSLP #{m.group(1)} (public domain edition)"
    if re.match(r"n\d\dop", str(facts["piece"].get("id", ""))) or "ABC" in orig:
        return "DCML Annotated Beethoven Corpus (CC BY)"
    src = str(facts["piece"].get("score_source", ""))
    if re.search(r"\.(mxl|musicxml|xml|mid|midi|mscz|abc|krn)$", src, re.I):
        return ""                         # a bare file name says nothing about where the score is from
    return src


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
        "piece": {k: v for k, v in facts["piece"].items() if k != "audio"},   # no local file paths
        "sections": [{k: s[k] for k in ("name", "start_mc", "end_mc", "start_label", "end_label")} for s in facts["sections"]],
        "key_plan": facts["key_plan"],
        "themes": facts["themes"],
        "theme_occurrences": facts["theme_occurrences"],
        "variations": facts.get("variations", []),
        "measures": [{k: m[k] for k in MEASURE_KEYS} for m in facts["measures"]],
        "method_notes": facts.get("method_notes", {}),
        "credits": {"score": _score_credit(cfg, facts), "audio": cfg.get("audio", {}).get("credit", "")},
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
        if public and not P._resolve(audio_cfg.get("path", ""), root).exists():
            # stop instead of publishing the piece without sound (and deleting the
            # audio that is online now): e.g. a fresh clone, where incoming/ is empty
            raise SystemExit(f"{piece_id}: recording not found ({Path(audio_cfg.get('path', '')).name}). "
                             "Put it back in incoming/ or set \"public\": false before publishing.")
        rec = _recording_bundle(d / fname, audio_cfg, root, site_dir / "pieces" / piece_id,
                                "audio.mp3" if rid == "main" else f"audio_{rid}.mp3",
                                whole_file_dir=(site_dir / "audio") if policy == "whole" else None)
        rec["license"] = audio_license(audio_cfg)
        rec["id"] = rid
        rec["name"] = audio_cfg.get("name") or _short_credit(audio_cfg.get("credit", "")) or rid
        recs.append(rec)
    if public and not recs:
        return None                    # no recording may be published: leave the piece out
    if public and not bundle["credits"]["score"]:
        print(f"  [credits] {piece_id}: no score source to credit; add \"credit\" under \"score\" in its config")
    if recs:
        bundle["alignment"] = recs[0]
        bundle["credits"]["audio"] = recs[0].get("credit", "")      # the recording that actually plays
    if len(recs) > 1:
        bundle["recordings"] = recs
    sp = _score_pages(piece_id, cfg, root, site_dir)
    if sp:
        # a version tag for the page files: a new score keeps the file names (page-1.png ...),
        # and without it browsers keep showing the old pages from their cache
        import hashlib
        sp["v"] = hashlib.sha1(json.dumps(sp, sort_keys=True).encode()).hexdigest()[:10]
        bundle["score"] = sp
    # time signature of every measure (practice mode: count-in clicks)
    try:
        sc = _load_score(cfg, root)
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
    if lic.startswith(("CC BY", "CC0", "EFF OPEN AUDIO")):
        return "clip"
    # public domain only when it is public domain everywhere; "public domain in the EU",
    # "(non-US)" and similar wordings stay private (GitHub Pages is a US service)
    if lic.rstrip(".") in ("PUBLIC DOMAIN", "PUBLIC DOMAIN (WORLDWIDE)", "PUBLIC DOMAIN WORLDWIDE"):
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
<p>Scores and recordings: as listed below, each under its own licence; recordings whose licence forbids changes are played from the original file, unchanged (a variable-bitrate
file is converted to constant bitrate so that the player can jump to an exact bar; the recording itself is not changed). Listening guides and
analyses: CC BY 4.0. Code: MIT.</p>
<p>乐谱与录音：见下表，各自遵守其授权；不允许修改的录音直接播放原始文件（可变码率的文件只转换为固定码率，以便准确跳转，录音内容不变）。
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
        # A public build always checks every piece again: a piece or recording that became
        # private must not survive from an earlier build.
        if only and not public and not any(pid.startswith(o) for o in only) and built.exists():
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
    # folders of pieces that are gone (deleted, or no longer built) must not stay on the site
    listed = {e["id"] for e in index}
    for old in (site_dir / "pieces").iterdir():
        if old.is_dir() and old.name not in listed and not (only and not public):
            shutil.rmtree(old)
            print(f"[site] removed {old.name} (no longer in the library)", flush=True)
    bundles = [json.loads((site_dir / "pieces" / e["id"] / "data.json").read_text()) for e in index]
    write_credits_page(site_dir, bundles)
    _remove_unused_audio(site_dir, bundles, index)
    return site_dir


def _remove_unused_audio(site_dir: Path, bundles: list[dict], index: list[dict]) -> None:
    """Delete audio files no piece uses any more (a recording that became private, or one
    that is now played from its whole original file), so they do not stay on the website."""
    used: set[Path] = set()
    for e, b in zip(index, bundles):
        piece_dir = site_dir / "pieces" / e["id"]
        for rec in [b.get("alignment") or {}] + list(b.get("recordings") or []):
            if rec.get("audio"):
                used.add((piece_dir / rec["audio"]).resolve())
    for f in list((site_dir / "pieces").glob("*/audio*")) + list((site_dir / "audio").glob("*")):
        if not f.is_file():
            continue
        target = f
        if f.name.endswith(".clip.json"):
            target = f.parent / (f.name[: -len(".clip.json")] + ".mp3")
        elif f.name.endswith(".cbr.json"):
            target = f.parent / (f.name[: -len(".cbr.json")] + ".mp3")
        if target.resolve() not in used:
            f.unlink()
            print(f"[site] removed unused {f.relative_to(site_dir)}", flush=True)
