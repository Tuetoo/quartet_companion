# Alignment accuracy (MusicNet ground truth)

Run on 24 Oct 2026 with `qc eval`. Raw numbers: `eval/alignment_eval_2026-10-24.jsonl`
(the 23 Oct run, before the changes below, is in `eval/alignment_eval_2026-10-23.jsonl`).

## How we measure

MusicNet gives the true time of every note in each recording, aligned to
a reference MIDI file. We run our aligner **without** looking at those
labels, then compare the predicted start time of every measure with the
true time. Because MusicNet's MIDI sometimes counts beats differently
(e.g. a pickup padded to a full bar), we first align our score to MusicNet's
note list symbolically, then read off the true times.

Note: MusicNet's own labels were also made by alignment, with an estimated
4% label error rate. Some large errors below may be label errors.

## Summary

- Movements tested: **28** (all Beethoven quartet movements that are in both MusicNet and ABC).
- Repeat pattern (which repeats the players took) chosen correctly: **26 / 28** (25 / 28 on 23 Oct).
- Median of the per-movement median errors: **0.10 s**.
- On average **80%** of measure starts are within 0.25 s of the truth
  (movements with the right repeat pattern).

## Per movement

| MusicNet id | Movement | Repeats right? | Median error (s) | 90% of measures within (s) | Share within 0.25 s |
|---|---|---|---|---|---|
| 2313 | Op. 132, mvt 1 | yes | 0.09 | 0.24 | 0.91 |
| 2314 | Op. 132, mvt 2 | yes | 0.09 | 0.17 | 0.98 |
| 2315 | Op. 132, mvt 3 | yes | 0.24 | 0.89 | 0.51 |
| 2365 | Op. 127, mvt 1 | yes | 0.10 | 0.25 | 0.91 |
| 2366 | Op. 127, mvt 2 | yes | 0.46 | 25.83 | 0.42 |
| 2368 | Op. 127, mvt 4 | yes | 0.14 | 0.68 | 0.76 |
| 2376 | Op. 59 No. 2, mvt 1 | yes | 0.10 | 0.29 | 0.87 |
| 2377 | Op. 59 No. 2, mvt 2 | yes | 0.13 | 0.37 | 0.81 |
| 2379 | Op. 59 No. 2, mvt 4 | yes | 0.05 | 0.20 | 0.92 |
| 2381 | Op. 130, mvt 1 | yes | 0.13 | 1.38 | 0.74 |
| 2382 | Op. 130, mvt 2 | no | – | – | – |
| 2383 | Op. 130, mvt 3 | yes | 0.12 | 8.24 | 0.69 |
| 2384 | Op. 130, mvt 4 | yes | 0.18 | 0.38 | 0.67 |
| 2403 | Op. 18 No. 1, mvt 4 | yes | 0.08 | 0.17 | 0.97 |
| 2431 | Op. 135, mvt 1 | yes | 0.10 | 0.28 | 0.88 |
| 2432 | Op. 135, mvt 2 | yes | 0.07 | 0.21 | 0.92 |
| 2433 | Op. 135, mvt 3 | yes | 0.62 | 1.08 | 0.11 |
| 2451 | Op. 18 No. 6, mvt 2 | yes | 0.39 | 0.82 | 0.38 |
| 2480 | I. Allegro | yes | 0.07 | 0.16 | 0.99 |
| 2481 | II. Menuetto | yes | 0.08 | 0.20 | 0.95 |
| 2483 | IV. Allegro | yes | 0.07 | 0.17 | 0.94 |
| 2482 | III. Andante cantabile | yes | 0.10 | 0.37 | 0.79 |
| 2494 | Op. 95, mvt 1 | yes | 0.08 | 0.19 | 0.96 |
| 2497 | Op. 95, mvt 4 | yes | 0.10 | 0.36 | 0.82 |
| 2560 | Op. 18 No. 2, mvt 2 | no | – | – | – |
| 2562 | Op. 18 No. 2, mvt 4 | yes | 0.07 | 0.14 | 0.98 |
| 2621 | Op. 59 No. 1, mvt 1 | yes | 0.09 | 0.19 | 0.96 |
| 2622 | Op. 59 No. 1, mvt 2 | yes | 0.14 | 0.30 | 0.83 |

## Changes on 24 Oct 2026 (and how each was tested)

* **Near-tied repeat patterns are decided by the fine match.** The coarse match
  picks the candidates; when several nearly tie, the detailed (fine) alignment
  decides. Among patterns that still tie, the one that covers more of the audio
  wins (a wrong pattern usually "wins" by skipping a poorly matching opening, e.g.
  the first pass of a repeat). Printed tempo marks, `--tempo` and the
  "fewer repeats" rule for OMR scores now only break what is left.
  MusicNet: 26/28 repeat patterns right (was 25; Op. 130 mvt 4 fixed); no movement
  got worse. In the project: Schubert D.810/III no longer skips its first 16 s;
  Haydn Op. 76/3 III no longer skips 21 s; K525 II now fills its recording.
* **Extra music in the audio range is cut off** (ranges set by hand): if the
  score fits clearly better inside the range *and* there is a real gap between
  movements at that point (≥ 4 s more than 25 dB below the music, ≥ 2 s below
  −30 dB), the extra audio is left out and the alignment is redone. Tested on
  D929 and K525 with 30–175 s of the next movement added (all cut correctly) and
  on all 28 MusicNet movements (no change). Ranges found by the movement splitter
  skip this check (they already sit at real pauses; a quiet slow introduction
  can look like a gap — Debussy IV).
* **Applause is trimmed** at the ends of live recordings (noise-like sound,
  spectral flatness > 0.03; applause measured ~0.09, string playing < 0.02),
  and ranges from the splitter get only 6 s of freedom at the ends (was up to 30 s).
* **Bars to compare by ear** (OMR scores only): after alignment, the written
  notes of each bar are compared with the sound in that bar's time span. Tested by
  changing 10 bars of a clean score aligned with its real recording: about half
  were found; bars at repeat jumps are left out because they stand out even in a
  clean score. Shown as hints (at most 12 per movement), not as errors.

## Listening check of every published movement (25–27 Oct 2026)

The numbers above measure the aligner on MusicNet. For the movements on the website
there is no ground truth. Every movement was checked by measurement (sound before bar 1,
sound after the last bar, bars that fit the sound poorly), the openings, endings and
flagged passages were checked by ear, and the problems found were fixed by hand (`scripts/retime.py`; each fix is
listed in that movement's `alignment.json` → `warnings`).

* **Openings.** In seven live recordings the first bar was placed after the music had
  already started (soft or slow openings: Op. 135 I, D. 810 I, Debussy IV, K. 465 I,
  Mendelssohn Op. 13 I, III and IV). The first ten bars were aligned again from where
  the sound starts. Every other movement was checked by measuring the gap between the
  first sound and bar 1 (none above 1 s).
* **Endings.** Where a long final chord, a fermata or a pause before the last chord
  came at the end, the last bars were squeezed and, in whole-work recordings, the
  movement's audio range sometimes stopped before the last chord (Op. 135 I, K. 465 I,
  Debussy III). The ranges were widened and the last bars timed from the attacks in the
  recording. The player now also keeps playing until the last chord has died away.
* **Op. 18 No. 5 (MusicNet recordings).** The website alignment was compared with
  MusicNet's own note labels for these recordings: within 0.1 s for every bar except
  the last four bars of the finale, which were then fixed.
* **Still approximate** (marked in the player): Haydn Op. 64 No. 5 (Lark) IV opening,
  Schubert D. 929 bars 114–153, Mendelssohn Op. 13 III bars 27–40, and the free-tempo
  middle of the Passacaglia.

## What is hard, and why

* **Slow movements** (Op. 135 mvt 3 Lento, Op. 18 No. 6 Adagio, Op. 132 mvt 3):
  notes are long and change slowly, so the exact start of a measure is
  blurry. Errors of 0.3–0.7 s are still under a quarter of a measure there.
* **Movements with many short repeats** (Op. 130 mvt 2, Op. 18 No. 2
  mvt 2): several repeat patterns fit almost equally well. The program
  then shows a warning, and you can fix the pattern with
  `"order": "<name>"` in the piece's `config.json` (names are listed in
  `alignment.json` → `candidate_costs`).
* **Op. 127 mvt 2**: one stretch (about measures 50–90) is off by up to
  30 s, then the alignment catches up again. Either the performance
  differs from the score there, or MusicNet's labels are wrong. The
  measures are flagged in the player.

## Synthetic test

`tests/test_align_synth.py` renders a score with a known, uneven tempo and align it:
median error ≈ 0.015 s, 95% within ≈ 0.05 s.

## Scores from the OpenScore library (24 Oct 2026)

The same four MusicNet recordings of Op. 18 No. 5, aligned with the OpenScore
score (`qc library add beethoven 18 5 ...`) instead of the expert ABC score:

| MusicNet id | Movement | Repeats right | Median error (s) | Within 0.25 s | ABC score, for comparison |
|---|---|---|---|---|---|
| 2480 | I. Allegro | yes | 0.07 | 0.99 | 0.07 / 0.99 |
| 2481 | II. Menuetto | yes | 0.09 | 0.89 | 0.08 / 0.95 |
| 2482 | III. Andante cantabile | yes | 0.10 | 0.84 | 0.10 / 0.79 |
| 2483 | IV. Allegro | yes | 0.06 | 0.97 | 0.07 / 0.96 |

So a library score is as good for following the music as the hand-checked
research data. (The expert harmony labels are what the ABC data adds.)

## Other checks

* Changes of 24 Oct (trying up to 128 repeat mixes, tempo-mark tie-break, the
  evaluation's length check): re-run on the five MusicNet movements they can
  affect (Op. 18/5 mvt 3, Op. 127 mvt 1–2, Op. 132 mvt 1 and 3): identical results.
* `scripts/check_site.py` opens every piece of the built player in a headless
  browser and checks title, score pages, bar highlighting, guide and recordings:
  14/14 pieces OK.
