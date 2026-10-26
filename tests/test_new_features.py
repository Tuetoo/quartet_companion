"""Tests for: repeat tie-breaking, MIDI loading, recording split, score drawing, audio clean-up."""
import json

import numpy as np
import pandas as pd
import pytest
import soundfile as sf

from conftest import make_score
from quartet_companion.align.split import split_recording
from quartet_companion.align.synth import render, tempo_curve
from quartet_companion.unfold import measure_timeline, playing_orders, unfolded_notes


def _two_movements():
    """Two short, clearly different 'movements' (C major scale tune / A minor arpeggios)."""
    tune1 = [60, 62, 64, 65, 67, 69, 71, 72] * 4
    tune2 = [57, 60, 64, 69, 64, 60] * 5
    s1 = make_score([(1 + i // 4, i % 4, 1.0, 0, p) for i, p in enumerate(tune1)] +
                    [(m, 0, 4.0, 3, 48) for m in range(1, 9)], 8)
    s2 = make_score([(1 + i // 3, i % 3, 1.0, 0, p) for i, p in enumerate(tune2)] +
                    [(m, 0, 3.0, 3, 45) for m in range(1, 11)], 10, beats_per_measure=3.0)
    return s1, s2


def test_split_recording_finds_both_movements(tmp_path):
    s1, s2 = _two_movements()
    ys, bounds, t = [], [], 0.0
    for s, qpm in [(s1, 90), (s2, 120)]:
        o = playing_orders(s)[0]
        f = tempo_curve(measure_timeline(s, o)["perf_end_qb"].iloc[-1], base_qpm=qpm, wobble=0.05)
        y = render(unfolded_notes(s, o), f, lead_in=1.0, tail=1.0)
        ys.append(y)
        ys.append(np.zeros(int(4 * 22050), dtype=np.float32))     # a 4 s pause
        bounds.append((t, t + len(y) / 22050))
        t += len(y) / 22050 + 4
    wav = tmp_path / "both.wav"
    sf.write(wav, np.concatenate(ys), 22050)
    spans = split_recording([s1, s2], str(wav))
    assert spans[0][0] < 2.0
    assert abs(spans[1][0] - bounds[1][0]) < 3.0


def test_midi_loader_with_pickup(tmp_path):
    mido = pytest.importorskip("mido")
    from quartet_companion.io.midi import load_midi
    mf = mido.MidiFile(ticks_per_beat=480)
    for name, pitches in [("violinI", [67, 69, 71, 72, 74]), ("cello", [43, 43, 43, 43, 43])]:
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name=name))
        tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4))
        tr.append(mido.MetaMessage("key_signature", key="G"))
        for p in pitches:
            tr.append(mido.Message("note_on", note=p, velocity=64, time=0))
            tr.append(mido.Message("note_off", note=p, velocity=0, time=480))
        mf.tracks.append(tr)
    path = tmp_path / "x.mid"
    mf.save(path)
    s = load_midi(path, pickup_qb=1.0)
    assert s.parts == ["Violin 1", "Cello"]
    assert s.measures["dur_qb"].tolist()[:2] == [1.0, 4.0]
    assert s.measures["mn"].tolist()[:2] == [0, 1]
    assert int(s.measures["keysig"].iloc[0]) == 1
    assert s.validate() == []


def test_score_drawing_maps_every_measure(tmp_path, melody_in_viola_score):
    pytest.importorskip("verovio")
    from quartet_companion.score_render import measure_map, render_pages, score_to_musicxml
    s = melody_in_viola_score
    xml = score_to_musicxml(s, tmp_path / "s.musicxml")
    info = render_pages(xml, tmp_path / "pages", len(s.measures))
    assert info["pages"] >= 1 and info["matches_score"]
    m = measure_map(s, info)
    assert sorted(m) == [1, 2, 3, 4]
    svg = (tmp_path / "pages" / "page-1.svg").read_text()
    assert all(v["id"] in svg for v in m.values())


def test_with_part_names(tmp_path):
    from quartet_companion.score_render import with_part_names
    xml = tmp_path / "a.musicxml"
    xml.write_text('<score-partwise><part-list><score-part id="P1"><part-name>Voice 1</part-name></score-part>'
                   '<score-part id="P2"><part-name>Voice 2</part-name></score-part></part-list></score-partwise>')
    out = with_part_names(xml, ["Violin", "Viola"], tmp_path / "b.musicxml").read_text()
    assert "Voice" not in out and "<part-name>Viola</part-name>" in out


def test_clean_audio_reduces_noise_keeps_music():
    pytest.importorskip("noisereduce")
    from quartet_companion.audio_clean import clean_audio
    sr = 22050
    t = np.arange(sr * 4) / sr
    music = 0.3 * np.sin(2 * np.pi * 440 * t) * (t > 1)            # 1 s of silence, then a tone
    rng = np.random.default_rng(0)
    noisy = music + 0.01 * rng.standard_normal(len(t))
    clicks = rng.choice(len(t), 40, replace=False)
    noisy[clicks] += 0.5
    out, rep = clean_audio(noisy.astype(np.float32), sr, "medium")
    quiet_before = np.sqrt(np.mean(noisy[: sr // 2] ** 2))
    quiet_after = np.sqrt(np.mean(out[: sr // 2] ** 2))
    assert quiet_after < quiet_before / 3                            # noise floor clearly lower
    tone = slice(int(1.5 * sr), int(3.5 * sr))
    assert np.sqrt(np.mean(out[tone] ** 2)) > 0.7 * np.sqrt(np.mean(music[tone] ** 2))
    assert rep["clicks_repaired"] > 0


def test_score_doubts_marks_outliers_but_not_repeat_jumps():
    from quartet_companion.site import score_doubts
    # 40 bars played straight, then a repeat of 1-8; bar 20 fits the sound badly,
    # bar 8 (just before the jump back) too, but repeat jumps are left out.
    order = list(range(1, 41)) + list(range(1, 9))
    sims = {mc: 0.8 + 0.01 * ((mc * 7) % 5) for mc in range(1, 41)}
    sims[20], sims[8] = 0.4, 0.4
    al = {"measures": [{"mc": mc, "label": str(mc), "note_sim": sims[mc]} for mc in order]}
    q = {"measures_with_wrong_length": [{"label": "20"}]}
    got = score_doubts(al, q)
    assert [d["mc"] for d in got] == [20]
    assert got[0]["reasons"] == ["notes", "length"]
    assert score_doubts({"measures": []}, None) == []


def test_guide_command_selects_missing_and_outdated(tmp_path, monkeypatch, capsys):
    import json
    from quartet_companion import cli
    from quartet_companion.guide.generate import facts_fingerprint
    facts = {"measures": [{"label": "1"}], "sections": [], "key_plan": []}
    for pid in ("w_1", "w_2", "w_3", "other_1"):
        d = tmp_path / "pieces" / pid
        d.mkdir(parents=True)
        (d / "config.json").write_text("{}")
        (d / "facts.json").write_text(json.dumps(facts))
    fp = facts_fingerprint(facts)
    (tmp_path / "pieces" / "w_1" / "guide_en.json").write_text(json.dumps({"facts_fingerprint": fp}))
    (tmp_path / "pieces" / "w_1" / "guide_zh.json").write_text(json.dumps({"facts_fingerprint": fp}))
    (tmp_path / "pieces" / "w_2" / "guide_en.json").write_text(json.dumps({"facts_fingerprint": "old"}))
    calls = []
    monkeypatch.setattr(cli, "step_guide", lambda pid, root, langs, model: calls.append((pid, langs)))
    cli.main(["--root", str(tmp_path), "guide", "w"])
    assert calls == [("w_2", ["en", "zh"]), ("w_3", ["en", "zh"])]


def test_audio_policy_for_public_site():
    from quartet_companion.site import audio_license, audio_policy
    assert audio_policy({"credit": "Musopen String Quartet, 2012 (IMSLP, CC BY 3.0)"}) == "clip"
    assert audio_policy({"credit": "MusicNet #2480, Pascal String Quartet (CC BY 4.0)"}) == "clip"
    assert audio_policy({"credit": "Goldstein, IMSLP #72056 (EFF Open Audio License)"}) == "clip"
    assert audio_policy({"credit": "Borromeo String Quartet (IMSLP #76160, CC BY-NC-ND 3.0)"}) == "whole"
    assert audio_license({"credit": "A Far Cry, IMSLP #324337 (CC BY-NC-ND 4.0)"}) == "CC BY-NC-ND 4.0"
    # unknown or not public domain in the US: never published
    assert audio_policy({"credit": "Budapest String Quartet, LP (IMSLP #722028, via archive.org)"}) == "private"
    assert audio_policy({"credit": "Koeckert", "license": "Public domain outside the US"}) == "private"
    assert audio_policy({"credit": "x (CC BY 3.0)", "public": False}) == "private"


def test_publish_to_gh_pages(tmp_path):
    import subprocess
    from quartet_companion.publish import pages_url, publish
    assert pages_url("https://github.com/JennyZ/quartet-companion.git") == "https://jennyz.github.io/quartet-companion/"
    assert pages_url("git@github.com:JennyZ/quartet-companion.git") == "https://jennyz.github.io/quartet-companion/"
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    proj = tmp_path / "proj"
    (proj / "public_site").mkdir(parents=True)
    (proj / "public_site" / "index.html").write_text("<html>v1</html>")
    git = lambda *a, cwd=proj: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)  # noqa: E731
    git("init", "-q"); git("config", "user.name", "T"); git("config", "user.email", "t@x")
    (proj / ".gitignore").write_text("public_site/\n"); git("add", "-A"); git("commit", "-q", "-m", "code")
    git("remote", "add", "origin", str(remote))
    assert publish(proj, build=False).startswith("Publish listening site")
    assert publish(proj, build=False) == "nothing changed since the last publish"
    (proj / "public_site" / "index.html").write_text("<html>v2</html>")
    publish(proj, build=False)
    log = subprocess.run(["git", "log", "--oneline", "gh-pages"], cwd=remote, capture_output=True, text=True).stdout
    assert len(log.strip().splitlines()) == 2
    files = subprocess.run(["git", "ls-tree", "--name-only", "gh-pages"], cwd=remote, capture_output=True, text=True).stdout.split()
    assert sorted(files) == [".nojekyll", "index.html"]
    # the main branch never gets the site
    assert "public_site" not in subprocess.run(["git", "ls-files"], cwd=proj, capture_output=True, text=True).stdout
