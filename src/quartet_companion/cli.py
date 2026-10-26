"""Command line: `qc <command>` (or `python -m quartet_companion.cli <command>`).

Typical use
-----------
New piece from IMSLP (PDF score + recording):
    qc new k525_1 --score incoming/k525.pdf --audio incoming/k525.mp3 \\
        --title "Mozart: Eine kleine Nachtmusik, I. Allegro" --composer Mozart --movement 1 --search
    qc guide k525_1 --lang en zh
    qc site && qc serve

Beethoven movement from the ABC dataset + a MusicNet recording:
    qc abc op18no5_3 --piece n05op18-5_03 --audio data/musicnet/musicnet/train_data/2482.wav

Each step can be re-run alone: analyze, align, guide, site.
"""
from __future__ import annotations

import argparse
import re
import json
import sys
from pathlib import Path

from . import pieces as P


def _root(args) -> Path:
    return Path(args.root).resolve() if getattr(args, "root", None) else P.project_root()


# ------------------------------------------------------------------ steps
def step_analyze(piece_id: str, root: Path) -> dict:
    from .facts import build_facts
    from .io.omr import quality_report
    cfg = P.load_config(piece_id, root)
    score = P.load_piece_score(cfg, root)
    quality = quality_report(score)
    P.write_json(P.piece_dir(piece_id, root) / "quality.json", quality)
    period = cfg.get("period_measures")
    if period == "auto":
        from .analysis.variations import detect_period
        period, agree = detect_period(score)
        print(f"[analyze] variation length detected: {period} measures (agreement {agree:.2f})")
    facts = build_facts(score, theme_specs=cfg.get("themes"), period_measures=period)
    facts["piece"]["audio"] = cfg.get("audio", {}).get("path", "")
    if cfg["score"]["type"] != "abc":
        facts["piece"]["score_quality"] = quality["verdict"]
        facts["method_notes"]["score"] = (
            f"Score file: {Path(cfg['score'].get('original', '')).name or 'user file'}. "
            f"{round(100 * quality['share_wrong_length'])}% of measures have notes that do not fill the bar "
            f"(often optical-recognition errors); {len(quality.get('empty_measures', []))} measure(s) have no notes. "
            "Rhythm and texture details may be wrong; sections, keys and the overall shape are more reliable.")
    P.write_json(P.piece_dir(piece_id, root) / "facts.json", facts)
    print(f"[analyze] {piece_id}: {facts['piece']['n_measures']} measures, {len(facts['sections'])} sections, "
          f"harmony={facts['piece']['harmony_source']}, score quality: {quality['verdict']}")
    return facts


def step_align(piece_id: str, root: Path, rec_id: str | None = None) -> dict:
    """Align the main recording, or another one (cfg["recordings"][rec_id])."""
    from .align.pipeline import align_score_to_audio
    cfg = P.load_config(piece_id, root)
    audio = (cfg.get("audio") or {}) if rec_id is None else cfg["recordings"][rec_id]
    if not audio.get("path"):
        raise SystemExit(f"{piece_id}: no audio in config")
    score = P.load_piece_score(cfg, root)
    orders = None
    if audio.get("order"):
        # the user knows which repeats the performers took (see alignment.json "candidate_costs")
        from .unfold import playing_orders
        orders = [o for o in playing_orders(score) if o.name == audio["order"]]
        if not orders:
            names = ", ".join(o.name for o in playing_orders(score))
            raise SystemExit(f"unknown repeat pattern {audio['order']!r}; choose one of: {names}")
    res = align_score_to_audio(score, str(P._resolve(audio["path"], root)), start_sec=audio.get("start_sec"),
                               end_sec=audio.get("end_sec"), search_long_recording=bool(audio.get("search")),
                               orders=orders, open_sec=audio.get("open_sec"),
                               tempo_hint_qpm=cfg.get("tempo_qpm"),
                               repeats_uncertain=bool(cfg.get("omr")) or "omr" in str(cfg["score"].get("path", "")).lower()
                               or "omr" in str(cfg["score"].get("original", "")).lower(),
                               check_edges=audio.get("range_from") != "split")
    data = res.to_dict()
    data["audio_path"] = audio["path"]
    out_name = "alignment.json" if rec_id is None else f"alignment_{rec_id}.json"
    P.write_json(P.piece_dir(piece_id, root) / out_name, data)
    print(f"[align] {piece_id}{'' if rec_id is None else ' (' + rec_id + ')'}: order={res.order}, {res.segment_start_sec:.1f}-{res.segment_end_sec:.1f}s, "
          f"cost={res.cost:.3f}")
    for w in res.warnings:
        print("  warning:", w)
    return data


def step_guide(piece_id: str, root: Path, langs: list[str], model: str | None) -> None:
    from .guide.generate import generate_guide, save_guide
    facts = P.read_json(P.piece_dir(piece_id, root) / "facts.json")
    for lang in langs:
        res = generate_guide(facts, language=lang, model=model)
        save_guide(res, P.piece_dir(piece_id, root) / f"guide_{lang}.json", facts)
        r = res.report
        tokens = sum(u["input"] + u["output"] for u in res.usage)
        print(f"[guide] {piece_id} {lang}: {len(res.guide['listening_points'])} points, verified={r['verified']}, "
              f"failed={r['failed']}, unchecked={r['unchecked']}, removed={r['removed_points']}, "
              f"prose_issues={len(r.get('prose_issues', []))}, tokens={tokens}")


# --------------------------------------------------------------- commands
def cmd_abc(args) -> None:
    root = _root(args)
    cfg = {"id": args.id, "title": args.title, "composer": "Ludwig van Beethoven",
           "score": {"type": "abc", "abc_dir": args.abc, "piece": args.piece},
           "audio": {"path": args.audio} if args.audio else {}}
    if args.audio_credit:
        cfg["audio"]["credit"] = args.audio_credit
    P.save_config(args.id, cfg, root)
    step_analyze(args.id, root)
    if args.audio:
        step_align(args.id, root)


def cmd_new(args) -> None:
    root = _root(args)
    d = P.piece_dir(args.id, root)
    d.mkdir(parents=True, exist_ok=True)
    score_path = Path(args.score)
    rel_score: str | list[str] | None = None
    if score_path.suffix.lower() in (".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"):
        from .io.omr import run_omr
        from .io.omr_geometry import save_printed_pages_safe
        print(f"[omr] running Audiveris on {score_path.name} (this can take a few minutes)...")
        files = run_omr(score_path, d / "omr")
        print("[omr] movements found:", ", ".join(f.name for f in files))
        idxs = [int(x) - 1 for x in str(args.movement or "1").split("+")]
        if max(idxs) >= len(files) or min(idxs) < 0:
            raise SystemExit(f"only {len(files)} movement file(s) found; choose --movement 1..{len(files)}")
        save_printed_pages_safe(d / "omr", files, [d if i in idxs else None for i in range(len(files))])
        if len(idxs) > 1:                      # one movement that OMR cut into pieces
            rel_score = [P.copy_into_piece(files[i], args.id, f"score_part{k + 1}{files[i].suffix.lower()}", root)
                         for k, i in enumerate(idxs)]
        score_path = files[idxs[0]]
    if rel_score is None:
        rel_score = P.copy_into_piece(score_path, args.id, "score" + score_path.suffix.lower(), root)
    cfg = {"id": args.id, "title": args.title or args.id, "composer": args.composer or "",
           "score": {"type": "file", "path": rel_score, "original": str(args.score)},
           "audio": {"path": str(args.audio)} if args.audio else {}}
    if args.parts:
        cfg["parts"] = [p.strip() for p in args.parts.split(",")]
    if args.period:
        cfg["period_measures"] = "auto" if args.period == "auto" else int(args.period)
    if args.pickup:
        cfg["pickup_qb"] = args.pickup
    if args.tempo:
        cfg["tempo_qpm"] = args.tempo
    if score_path != Path(args.score):
        cfg["omr"] = True                      # the score was read from a PDF
    if args.audio:
        if args.start is not None:
            cfg["audio"]["start_sec"] = args.start
        if args.end is not None:
            cfg["audio"]["end_sec"] = args.end
        if args.search:
            cfg["audio"]["search"] = True
        if args.audio_credit:
            cfg["audio"]["credit"] = args.audio_credit
    P.save_config(args.id, cfg, root)
    # show part names so the user can fix them
    score = P.load_piece_score(cfg, root)
    print(f"[score] parts: {score.parts}  (rename with --parts \"Violin 1,Violin 2,Viola,Cello\")")
    step_analyze(args.id, root)
    q = P.read_json(d / "quality.json")
    if q["measures_with_wrong_length"]:
        bad = ", ".join(x["label"] for x in q["measures_with_wrong_length"][:15])
        print(f"  check in MuseScore: measures whose notes do not fill the bar: {bad}"
              f"{' ...' if len(q['measures_with_wrong_length']) > 15 else ''}")
    if args.audio:
        step_align(args.id, root)


SPLIT_OPEN_SEC = 6.0


def cmd_new_set(args) -> None:
    """A whole work: one PDF (several movements) + one recording (all movements)."""
    root = _root(args)
    from .align.split import split_recording
    from .io.omr import run_omr
    work = P.piece_dir(args.prefix, root).parent / f"_{args.prefix}_omr"
    paths = [Path(p) for p in args.score]
    from_pdf = len(paths) == 1 and paths[0].suffix.lower() in (".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff")
    if from_pdf:
        print(f"[omr] running Audiveris on {paths[0].name} (a 12-page score takes about 10 minutes)...")
        files = run_omr(paths[0], work)
    else:
        files = paths                     # one MusicXML/MuseScore file per movement, in order
    print(f"[omr] {len(files)} movement(s): " + ", ".join(f.name for f in files))
    if from_pdf:
        from .io.omr_geometry import save_printed_pages_safe
        save_printed_pages_safe(work, files, [P.piece_dir(f"{args.prefix}_{i + 1}", root) for i in range(len(files))])
    if isinstance(args.names, list):
        names = [n.strip() for n in args.names]
    else:
        names = [n.strip() for n in args.names.split(",")] if args.names else [f"movement {i + 1}" for i in range(len(files))]
    if len(names) != len(files):
        print(f"  note: {len(names)} names for {len(files)} movements; extra names are ignored")
    ids = []
    for i, f in enumerate(files):
        pid = f"{args.prefix}_{i + 1}"
        rel = P.copy_into_piece(f, pid, "score" + f.suffix.lower(), root)
        title = f"{args.title}" + (f" – {names[i]}" if i < len(names) else f" – movement {i + 1}")
        cfg = {"id": pid, "title": title, "composer": args.composer or "",
               "score": {"type": "file", "path": rel,
                         "original": str(args.score[0]) if len(args.score) == 1 else str(f)},
               "audio": {"path": str(args.audio)} if args.audio else {}}
        if args.parts:
            cfg["parts"] = [p.strip() for p in args.parts.split(",")]
        if from_pdf:
            cfg["omr"] = True
        if args.audio_credit and args.audio:
            cfg["audio"]["credit"] = args.audio_credit
        P.save_config(pid, cfg, root)
        ids.append(pid)
    if args.audio and len(ids) > 1:
        print("[split] finding where each movement starts in the recording ...")
        scores = [P.load_piece_score(P.load_config(pid, root), root) for pid in ids]
        spans = split_recording(scores, str(P._resolve(args.audio, root)))
        for pid, (a, b) in zip(ids, spans):
            cfg = P.load_config(pid, root)
            cfg["audio"].update({"start_sec": round(a, 2), "end_sec": round(b, 2), "range_from": "split",
                                 # the splitter cuts at real pauses: little freedom at the ends, so that
                                 # the first pass of a repeat cannot be skipped (applause is trimmed
                                 # separately, see pipeline._trim_applause)
                                 "open_sec": SPLIT_OPEN_SEC})
            P.save_config(pid, cfg, root)
            print(f"  {pid}: {int(a // 60)}:{a % 60:04.1f} - {int(b // 60)}:{b % 60:04.1f}")
    for pid in ids:
        step_analyze(pid, root)
        if args.audio:
            step_align(pid, root)


def cmd_clean_audio(args) -> None:
    """Reduce hiss/crackle of an old recording, for listening in the player."""
    from .audio_clean import clean_file
    root = _root(args)
    if args.test:
        src = Path(args.test)
        out = root / "incoming" / "clean_test"
        out.mkdir(parents=True, exist_ok=True)
        start = args.start or 0.0
        from .audio_clean import STRENGTHS
        import soundfile as sf
        info = sf.info(str(src))
        y, sr = sf.read(str(src), start=int(start * info.samplerate), stop=int((start + 40) * info.samplerate),
                        always_2d=True)
        sf.write(str(out / "0_original.mp3"), y.mean(axis=1), sr, format="MP3")
        for i, st in enumerate(STRENGTHS, 1):
            rep = clean_file(src, out / f"{i}_{st}.mp3", st, start, start + 40)
            print(f"[clean] {st}: {rep['clicks_repaired']} clicks repaired")
        print(f"[clean] listen and compare: {out}")
        return
    for pid in args.ids:
        cfg = P.load_config(pid, root)
        src = P._resolve(cfg["audio"]["path"], root)
        dst = P.piece_dir(pid, root) / f"audio_clean_{args.strength}.mp3"
        rep = clean_file(src, dst, args.strength)
        cfg["audio"]["playback"] = str(dst.relative_to(root))
        cfg["audio"]["cleaned"] = rep
        P.save_config(pid, cfg, root)
        print(f"[clean] {pid}: {args.strength}, {rep['clicks_repaired']} clicks repaired -> {dst.name}")
    print("Run `qc site` to use the cleaned audio in the player.")


def cmd_analyze(args) -> None:
    step_analyze(args.id, _root(args))


def cmd_align(args) -> None:
    root = _root(args)
    step_align(args.id, root)
    for rid in (P.load_config(args.id, root).get("recordings") or {}):
        step_align(args.id, root, rid)


def cmd_add_recording(args) -> None:
    """Add another recording of a piece (to compare performances in the player)."""
    root = _root(args)
    cfg = P.load_config(args.id, root)
    rid = re.sub(r"[^a-z0-9]+", "_", (args.name or "rec").lower()).strip("_") or "rec"
    rec = {"name": args.name, "path": str(args.audio)}
    for k, v in (("start_sec", args.start), ("end_sec", args.end)):
        if v is not None:
            rec[k] = v
    if args.search:
        rec["search"] = True
    if args.audio_credit:
        rec["credit"] = args.audio_credit
    cfg.setdefault("recordings", {})[rid] = rec
    if args.main_name:
        cfg.setdefault("audio", {})["name"] = args.main_name
    P.save_config(args.id, cfg, root)
    step_align(args.id, root, rid)
    print("Run `qc site` to compare the recordings in the player.")


def cmd_guide(args) -> None:
    """One or more pieces (ids or prefixes, e.g. "dvorak96" for all four movements).
    Guides that already exist for the current facts are skipped (--force to redo),
    so an interrupted run can simply be started again."""
    from .guide.generate import facts_fingerprint
    root = _root(args)
    all_ids = sorted(p.parent.name for p in (root / "pieces").glob("*/config.json"))
    ids = [i for i in all_ids if any(i == w or i.startswith(w + "_") or (w.endswith("_") and i.startswith(w))
                                      for w in args.id)]
    if not ids:
        raise SystemExit(f"no pieces match {args.id}")
    todo = []
    for pid in ids:
        d = P.piece_dir(pid, root)
        if not (d / "facts.json").exists():
            print(f"[guide] {pid}: no facts yet (run qc analyze {pid}); skipped")
            continue
        fp = facts_fingerprint(P.read_json(d / "facts.json"))
        langs = [l for l in args.lang if args.force or not (d / f"guide_{l}.json").exists()
                 or P.read_json(d / f"guide_{l}.json").get("facts_fingerprint") != fp]
        if langs:
            todo.append((pid, langs))
    print(f"[guide] {len(todo)} piece(s) to write: " + ", ".join(f"{p} ({' '.join(l)})" for p, l in todo))
    for n, (pid, langs) in enumerate(todo, 1):
        print(f"[guide] {n}/{len(todo)} {pid}", flush=True)
        step_guide(pid, root, langs, args.model)


def cmd_ask(args) -> None:
    from .guide.ask import ask
    facts = P.read_json(P.piece_dir(args.id, _root(args)) / "facts.json")
    a = ask(facts, args.question, model=args.model)
    print(a.answer)
    for v in a.verification:
        print(f"  [{v['status']}] {v['claim']}" + (f" - {v['reason']}" if v["reason"] else ""))


def cmd_site(args) -> None:
    from .site import build_site
    out = build_site(_root(args), Path(args.out) if args.out else None, only=args.only, public=args.public)
    print(f"[site] built {out}")


def cmd_publish(args) -> None:
    from .publish import pages_url, publish, _git
    root = _root(args)
    msg = publish(root, build=not args.no_build, push=not args.no_push, force=args.force)
    print(f"[publish] {msg}")
    remote = _git(["remote", "get-url", "origin"], root, check=False).stdout.strip()
    url = pages_url(remote) if remote else None
    if url and not args.no_push:
        print(f"[publish] the site will be at {url} (first time: GitHub > Settings > Pages > "
              "Source: Deploy from a branch, Branch: gh-pages / root; it takes a minute or two)")


def cmd_studio(args) -> None:
    from .studio import serve
    serve(_root(args), args.port)


def cmd_serve(args) -> None:
    import functools
    import http.server
    import socketserver
    site = (_root(args) / "site")
    from .httpserve import RangeHandler        # range requests: lets the player jump around in the audio
    handler = functools.partial(RangeHandler, directory=str(site))
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        print(f"Open http://127.0.0.1:{args.port}/  (Ctrl+C to stop)")
        httpd.serve_forever()


def cmd_list(args) -> None:
    root = _root(args)
    for d in sorted((root / "pieces").glob("*/config.json")):
        cfg = json.loads(d.read_text())
        have = [f.stem for f in d.parent.glob("*.json") if f.stem != "config" and "." not in f.stem]
        print(f"{cfg['id']:<24} {cfg.get('title', '')[:50]:<52} {', '.join(sorted(have))}")


def cmd_eval(args) -> None:
    from .align.evaluate import main as eval_main
    eval_main(["--abc", args.abc, "--musicnet", args.musicnet, "--out", args.out] +
              (["--ids", *map(str, args.ids)] if args.ids else []))


def cmd_library(args) -> None:
    """Find a quartet in the OpenScore library and add it (all movements)."""
    from .io import library as L
    root = _root(args)
    cache = root / "data" / "openscore"
    rows = L.catalogue(cache)
    if args.action == "search":
        hits = L.search(rows, args.words)
        for r in hits[:40]:
            print(f"{r['id']:>10}  {r['composer']:<28} {r['name']}")
        print(f"{len(hits)} work(s). Add one with: qc library add <id or words> --prefix NAME --audio FILE")
        return
    if not args.prefix:
        raise SystemExit("add: give --prefix, e.g. --prefix haydn76_3")
    hits = [r for r in rows if r["id"] in args.words] or L.search(rows, args.words)
    if len(hits) != 1:
        for r in hits[:20]:
            print(f"{r['id']:>10}  {r['composer']:<28} {r['name']}")
        raise SystemExit(f"{len(hits)} works match; give more words or the id")
    row = hits[0]
    print(f"[library] {row['composer']}: {row['name']}")
    mxl = L.download(row, cache)
    files = L.split_movements(mxl, cache / row["id"], "mv")
    names = L.movement_titles(files)
    if args.movements:
        keep = [int(x) - 1 for x in args.movements.split(",")]
        files, names = [files[i] for i in keep], [names[i] for i in keep]
    print(f"[library] {len(files)} movement(s): " + " | ".join(names))
    composer = row["composer"].split(",")
    composer = " ".join(reversed([c.strip() for c in composer])) if len(composer) == 2 else row["composer"]
    audios = args.audio or []
    ns = argparse.Namespace(root=args.root, prefix=args.prefix, score=[str(f) for f in files],
                            audio=audios[0] if len(audios) == 1 else None,
                            title=f"{composer.split()[-1]}: {row['name']}", names=names,   # a list: titles may contain commas
                            composer=composer, parts=None, audio_credit=args.audio_credit)
    cmd_new_set(ns)
    ids = [f"{args.prefix}_{i + 1}" for i in range(len(files))]
    for pid in ids:                       # remember where the score came from
        cfg = P.load_config(pid, root)
        cfg["score"]["original"] = f"OpenScore String Quartets (CC0): {row['link']}"
        cfg["score"]["openscore_id"] = row["id"]
        P.save_config(pid, cfg, root)
    if len(audios) > 1:                   # one recording file per movement
        if len(audios) != len(ids):
            raise SystemExit(f"{len(audios)} recordings for {len(ids)} movements")
        for pid, a in zip(ids, audios):
            cfg = P.load_config(pid, root)
            cfg["audio"] = {"path": a, **({"credit": args.audio_credit} if args.audio_credit else {})}
            P.save_config(pid, cfg, root)
            step_align(pid, root)
    print("Next: qc guide <id> --lang en zh  (uses the API), then qc site")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="qc", description="Quartet Companion")
    ap.add_argument("--root", help="project folder (default: this project)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="new piece from a score file (PDF via OMR, MusicXML, MuseScore, MIDI)")
    s.add_argument("id")
    s.add_argument("--score", required=True)
    s.add_argument("--audio")
    s.add_argument("--title")
    s.add_argument("--composer")
    s.add_argument("--parts", help='comma-separated part names, e.g. "Violin,Viola"')
    s.add_argument("--movement", default="1", help="which movement of a multi-movement PDF; \'1+2\' joins pieces that OMR cut apart")
    s.add_argument("--start", type=float, help="movement start in the recording (seconds)")
    s.add_argument("--end", type=float, help="movement end in the recording (seconds)")
    s.add_argument("--search", action="store_true", help="find the movement inside a long recording")
    s.add_argument("--period", help="passacaglia/chaconne: measures per variation, or 'auto'")
    s.add_argument("--pickup", type=float, help="MIDI scores: length of the upbeat in quarter notes (e.g. 2)")
    s.add_argument("--tempo", type=float, help="written metronome mark in quarter notes per minute, if the file lacks it")
    s.add_argument("--audio-credit")
    s.set_defaults(func=cmd_new)

    s = sub.add_parser("new-set", help="a whole work: multi-movement score + one recording")
    s.add_argument("prefix", help="e.g. k525 -> pieces k525_1, k525_2, ...")
    s.add_argument("--score", required=True, nargs="+", help="one PDF, or one music file per movement")
    s.add_argument("--audio")
    s.add_argument("--title", required=True)
    s.add_argument("--names", help='movement names, comma-separated: "I. Allegro,II. Romanze,..."')
    s.add_argument("--composer")
    s.add_argument("--parts")
    s.add_argument("--audio-credit")
    s.set_defaults(func=cmd_new_set)

    s = sub.add_parser("library", help="ready-made quartet scores from OpenScore (search / add)")
    s.add_argument("action", choices=["search", "add"])
    s.add_argument("words", nargs="+", help='e.g. haydn 76 3, or an OpenScore id')
    s.add_argument("--prefix", help="add: piece ids become PREFIX_1, PREFIX_2, ...")
    s.add_argument("--audio", nargs="*", help="add: one recording of the whole work, or one file per movement")
    s.add_argument("--movements", help='add: only some movements, e.g. "2" or "1,3"')
    s.add_argument("--audio-credit")
    s.set_defaults(func=cmd_library)

    s = sub.add_parser("abc", help="piece from the ABC dataset (expert harmony)")
    s.add_argument("id")
    s.add_argument("--piece", required=True, help="e.g. n05op18-5_03")
    s.add_argument("--abc", default="data/ABC")
    s.add_argument("--audio")
    s.add_argument("--title")
    s.add_argument("--audio-credit")
    s.set_defaults(func=cmd_abc)

    s = sub.add_parser("clean-audio", help="reduce hiss/crackle of old recordings for listening")
    s.add_argument("ids", nargs="*", help="pieces whose recording to clean")
    s.add_argument("--strength", choices=["light", "medium", "strong"], default="medium")
    s.add_argument("--test", help="audio file: write 40 s before/after samples to compare by ear")
    s.add_argument("--start", type=float, help="with --test: where the sample starts (seconds)")
    s.set_defaults(func=cmd_clean_audio)

    for name, fn in [("analyze", cmd_analyze), ("align", cmd_align)]:
        s = sub.add_parser(name)
        s.add_argument("id")
        s.set_defaults(func=fn)

    s = sub.add_parser("add-recording", help="add another recording of a piece, to compare performances")
    s.add_argument("id")
    s.add_argument("--name", required=True, help='short name shown in the player, e.g. "Budapest Quartet 1940"')
    s.add_argument("--audio", required=True)
    s.add_argument("--start", type=float)
    s.add_argument("--end", type=float)
    s.add_argument("--search", action="store_true")
    s.add_argument("--audio-credit")
    s.add_argument("--main-name", help="short name for the piece's first recording")
    s.set_defaults(func=cmd_add_recording)

    s = sub.add_parser("guide", help="write and verify listening guides (uses the API)")
    s.add_argument("id", nargs="+", help="piece ids or prefixes (dvorak96 = all its movements)")
    s.add_argument("--force", action="store_true", help="rewrite guides that are already up to date")
    s.add_argument("--lang", nargs="+", default=["en", "zh"])
    s.add_argument("--model")
    s.set_defaults(func=cmd_guide)

    s = sub.add_parser("ask", help="ask a question about a piece (uses the API)")
    s.add_argument("id")
    s.add_argument("question")
    s.add_argument("--model")
    s.set_defaults(func=cmd_ask)

    s = sub.add_parser("publish", help="build the public site and push it to the gh-pages branch")
    s.add_argument("--no-build", action="store_true", help="publish public_site/ as it is")
    s.add_argument("--no-push", action="store_true", help="commit locally, do not upload")
    s.add_argument("--force", action="store_true", help="replace gh-pages on GitHub with this build")
    s.set_defaults(func=cmd_publish)

    s = sub.add_parser("studio", help="add pieces from the browser (search the library, pick recordings)")
    s.add_argument("--port", type=int, default=8765)
    s.set_defaults(func=cmd_studio)

    s = sub.add_parser("site", help="build the web player into site/")
    s.add_argument("--out")
    s.add_argument("--public", action="store_true", help="build the public version into public_site/ (only "
                   "recordings whose licence allows it; see README 'Publishing')")
    s.add_argument("--only", nargs="*", help="rebuild only pieces whose id starts with one of these "
                   "(others keep their last build; the library list still shows all)")
    s.set_defaults(func=cmd_site)

    s = sub.add_parser("serve", help="open the web player locally")
    s.add_argument("--port", type=int, default=8765)
    s.set_defaults(func=cmd_serve)

    s = sub.add_parser("list", help="list pieces")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("eval", help="measure alignment accuracy on MusicNet")
    s.add_argument("--abc", default="data/ABC")
    s.add_argument("--musicnet", default="data/musicnet/musicnet")
    s.add_argument("--out", default="eval/alignment_eval.json")
    s.add_argument("--ids", nargs="*", type=int)
    s.set_defaults(func=cmd_eval)
    return ap


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
