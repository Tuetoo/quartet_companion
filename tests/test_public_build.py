"""The public website build: what may and may not be published."""
import json

import numpy as np
import pytest


def _make_piece(root, pid, licence, public=None):
    mido = pytest.importorskip("mido")
    sf = pytest.importorskip("soundfile")
    from quartet_companion.cli import step_analyze
    d = root / "pieces" / pid
    d.mkdir(parents=True)
    mf = mido.MidiFile(ticks_per_beat=480)
    for name, base in (("violinI", 72), ("violinII", 67), ("viola", 60), ("cello", 48)):
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name=name))
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
        for k in range(16):
            tr.append(mido.Message("note_on", note=base + (k % 5), velocity=64, time=0))
            tr.append(mido.Message("note_off", note=base + (k % 5), velocity=0, time=480))
        mf.tracks.append(tr)
    mf.save(d / "score.mid")
    audio = root / "incoming" / f"{pid}.wav"
    audio.parent.mkdir(exist_ok=True)
    sr = 22050
    sf.write(audio, (0.1 * np.sin(2 * np.pi * 440 * np.arange(sr * 12) / sr)).astype(np.float32), sr)
    cfg = {"id": pid, "title": f"Test: Quartet – {pid}", "composer": "Test",
           "score": {"type": "file", "path": f"pieces/{pid}/score.mid", "credit": "Test score (CC0)"},
           "parts": ["Violin 1", "Violin 2", "Viola", "Cello"],
           "audio": {"path": str(audio), "credit": "Test players", "license": licence}}  # absolute on purpose
    if public is not None:
        cfg["public"] = public
    (d / "config.json").write_text(json.dumps(cfg))
    step_analyze(pid, root)
    ms = [{"occurrence": i, "mc": i + 1, "label": str(i + 1), "perf_start_qb": 4 * i, "perf_end_qb": 4 * i + 4,
           "start_sec": 1.0 + 2 * i, "end_sec": 3.0 + 2 * i, "match_cost": 0.1, "note_sim": 0.9, "flagged": False,
           "tempo_qpm": 120.0} for i in range(4)]
    (d / "alignment.json").write_text(json.dumps({"audio_path": str(audio), "order": "all_repeats",
                                                  "order_description": "", "warnings": [], "cost": 0.2,
                                                  "measures": ms}))


def test_public_build_leaves_out_private_material(tmp_path):
    from quartet_companion.site import build_site
    _make_piece(tmp_path, "open_1", "CC BY 4.0")
    _make_piece(tmp_path, "later_1", "CC BY 4.0")
    site = build_site(tmp_path, public=True)
    assert (site / "pieces" / "later_1" / "audio.mp3").exists()

    # the second piece becomes private; a quick rebuild of another piece must still remove it
    cfg_path = tmp_path / "pieces" / "later_1" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["public"] = False
    cfg_path.write_text(json.dumps(cfg))
    build_site(tmp_path, public=True, only=["open_1"])
    assert not (site / "pieces" / "later_1").exists()
    ids = [e["id"] for e in json.loads((site / "pieces" / "index.json").read_text())]
    assert ids == ["open_1"]
    assert "later_1" not in (site / "credits.html").read_text()

    # no file of the public site may reveal folders on the owner's computer
    for f in site.rglob("*"):
        if f.is_file() and f.suffix in (".json", ".html", ".js"):
            assert str(tmp_path) not in f.read_text(errors="ignore"), f

    # a recording that may no longer be published disappears from the site
    cfg_path = tmp_path / "pieces" / "open_1" / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["audio"]["license"] = "All rights reserved"
    cfg_path.write_text(json.dumps(cfg))
    build_site(tmp_path, public=True)
    assert not list(site.rglob("*.mp3"))

    # a piece deleted from the library disappears from the site too
    import shutil
    cfg["audio"]["license"] = "CC BY 4.0"
    cfg_path.write_text(json.dumps(cfg))
    build_site(tmp_path, public=True)
    assert (site / "pieces" / "open_1" / "data.json").exists()
    shutil.rmtree(tmp_path / "pieces" / "open_1")
    build_site(tmp_path, public=True)
    assert not (site / "pieces" / "open_1").exists()


def test_only_worldwide_public_domain_is_published():
    from quartet_companion.site import audio_policy
    assert audio_policy({"license": "Public domain"}) == "clip"
    assert audio_policy({"license": "CC BY 4.0"}) == "clip"
    assert audio_policy({"license": "CC BY-NC-ND 3.0"}) == "whole"
    for lic in ("Public domain outside the US (not in the US)", "Public domain (non-US)",
                "public domain in the EU only", "", "All rights reserved"):
        assert audio_policy({"license": lic}) == "private", lic


def test_public_build_stops_when_a_recording_is_missing(tmp_path):
    from quartet_companion.site import build_site
    _make_piece(tmp_path, "open_1", "CC BY 4.0")
    build_site(tmp_path, public=True)
    (tmp_path / "incoming" / "open_1.wav").unlink()        # e.g. a fresh clone: incoming/ is empty
    with pytest.raises(SystemExit, match="recording not found"):
        build_site(tmp_path, public=True)
    assert list((tmp_path / "public_site" / "pieces" / "open_1").glob("audio*.mp3"))   # online audio kept


def test_local_server_refuses_other_host_names(tmp_path):
    import functools
    import threading
    import urllib.error
    import urllib.request
    from quartet_companion.httpserve import QuietServer, RangeHandler
    (tmp_path / "a.txt").write_text("private")
    srv = QuietServer(("127.0.0.1", 0), functools.partial(RangeHandler, directory=str(tmp_path)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/a.txt"
    try:
        assert urllib.request.urlopen(url).read() == b"private"
        req = urllib.request.Request(url, headers={"Host": "evil.example:80"})
        with pytest.raises(urllib.error.HTTPError) as e:
            urllib.request.urlopen(req)
        assert e.value.code == 403
    finally:
        srv.shutdown()
