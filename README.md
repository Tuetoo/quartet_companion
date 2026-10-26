# Quartet Companion

Listen to string chamber music with the score's eyes.

You pick a movement and a recording. The program shows, while the music
plays, **who has the tune**, **which key you are in**, **which section you
are in**, and it gives you a **listening guide** written by Claude.
Every statement in the guide is **checked by code** against facts computed
from the score. Statements that cannot be backed are removed.

```
score (ABC / MusicXML / PDF via OMR) ──► analysis ──► facts.json ──► guide (Claude) ──► verifier
                                              │                                        │
recording (mp3 / wav) ──► alignment ──► alignment.json ─────────────────► web player ◄─┘
```

## What is in the box

| Folder / file | What it does |
|---|---|
| `src/quartet_companion/io/` | Load scores: ABC dataset (`abc.py`), MusicXML/MuseScore/MIDI (`musicxml.py`), PDF via Audiveris OMR (`omr.py`) |
| `src/quartet_companion/unfold.py` | Repeat signs, endings, Da Capo → possible playing orders |
| `src/quartet_companion/analysis/` | Lead part & texture, themes, sections, harmony, dynamics, variations |
| `src/quartet_companion/facts.py` | Runs all analyses → one fact sheet (`facts.json`) |
| `src/quartet_companion/align/` | Score-to-recording alignment (chroma + onset features, two-pass DTW) and its evaluation on MusicNet |
| `src/quartet_companion/guide/` | Prompt, Claude call, claim verifier, Q&A |
| `src/quartet_companion/site.py`, `web/` | Static web player |
| `src/quartet_companion/cli.py` | The `qc` command |
| `tests/` | Unit and integration tests (`pytest`) |
| `pieces/<id>/` | Results for each movement (config, facts, alignment, guides) |

## Setup (once)

```bash
cd ~/Documents/jiemin_zhang/common_core/quartet_companion
bash scripts/setup_mac.sh          # creates .venv, installs, downloads ABC, runs tests
source .venv/bin/activate          # every new terminal
```

Put your API key in `.env` (never commit it):
```
ANTHROPIC_API_KEY=sk-ant-...
```
Optional: `QC_MODEL=claude-sonnet-5-5` (default) or another Claude model.

## Everyday use

```bash
qc list                                   # pieces and which steps are done
qc studio                                 # add pieces in the browser: http://127.0.0.1:8765/studio.html
qc guide dvorak96 k465 --lang en zh       # write + verify guides (uses the API); prefixes = all movements
qc ask op18no5_3 "Where does the viola carry the tune?"
qc site && qc serve                       # open http://127.0.0.1:8765
```

`qc guide` skips guides that are already up to date, so an interrupted run can
just be started again (`--force` rewrites them). `qc site --only <prefix>` rebuilds
only some pieces (useful after adding one work to a big library).

The player's **Library** button (or the `/` key) searches every movement: composer,
title, nickname or key, also in Chinese (海顿, 死神与少女, 降E大调), with filters for
major/minor, length and "has a guide in this language".

### Add a quartet from the score library (easiest)

**In the browser:** run `qc studio`, open http://127.0.0.1:8765/studio.html,
search for the work, tick the recording(s) you put in `incoming/`, press *Add*.
The page shows the progress and a link to the new piece; then write the guides
with the `qc guide <short name>` command it shows.

**On the command line:** about 200 string quartets (Haydn, Mozart, Beethoven, Schubert, Mendelssohn, Brahms,
Dvořák, ...) are ready as checked, typeset scores in the OpenScore library (CC0).

```bash
qc library search schubert                  # list works
qc library add haydn 76 3 --prefix haydn76_3 \
  --audio incoming/mv1.mp3 incoming/mv2.mp3 incoming/mv3.mp3 incoming/mv4.mp3 \
  --audio-credit "Budapest String Quartet, LP"
qc guide haydn76_3_2 --lang en zh && qc site
```

`--audio` takes one file per movement, or one file with the whole work (it is
split at the pauses). `--movements 2` adds only some movements. The work is cut
into movements where the bar numbers start again; a few printed bars after a
movement's final barline that are not played there (e.g. Beethoven's motto before
the finale of Op. 135) are left out. Live recordings: applause at the ends is
trimmed automatically.

If an audio range you set by hand also holds part of the next (or previous)
movement, the aligner notices the gap between the movements and leaves the extra
audio out (it says so in the warnings).

### Add a new piece from IMSLP

1. Download a **score** (MusicXML is best; PDF works through OMR) and a
   **recording** (mp3/wav) into `incoming/`.
2. For PDF scores, install Audiveris once (see below).
3. Run:

```bash
qc new k525_1 \
  --score "incoming/IMSLP914586-PMLP5176-mozart_serenade_k.525_dover.pdf" --movement 1 \
  --audio "incoming/IMSLP324337-PMLP05176-mozart_kv525_afarcry.mp3" --search \
  --title "Mozart: Eine kleine Nachtmusik, K. 525 – I. Allegro" --composer "W. A. Mozart" \
  --parts "Violin 1,Violin 2,Viola,Cello" \
  --audio-credit "A Far Cry, IMSLP #324337 (CC BY-NC-ND 4.0)"
qc guide k525_1 --lang en zh
qc site
```

Useful options:
- `--search` – the recording holds several movements; find this one automatically.
  If the movement's end is found too late (a soft next movement follows), give `--end` (seconds).
  Or give `--start 0 --end 410` (seconds) yourself.
- `--movement 2` – which movement of a multi-movement PDF. OMR sometimes cuts one movement
  in two (it prints the pieces it found); join them with `--movement 1+2`.
- `--parts "Violin,Viola"` – OMR often calls parts "Voice 1/2"; name them. For a piano
  trio give `--parts "Violin,Cello,Piano"`: when OMR found more parts than that (a piano on
  two staves, an instrument split over several "Voice" parts), they are merged onto these
  instruments (by name, by when they play, and by register).
- `--period auto` (or `--period 4`) – passacaglia/chaconne: cut into variations of N measures.

After `qc new`, read `pieces/<id>/quality.json`. It lists measures whose notes do
not fill the bar, notes outside an instrument's range, and empty measures.
These are usually OMR mistakes. Fix them in MuseScore (free), export
MusicXML, and run `qc new` again with `--score your_fixed_file.mxl`.

### A whole work in one recording

When one file holds all movements (a CD track list joined, or an IMSLP "complete" file):

```bash
qc new-set k525 --score incoming/k525.pdf --audio incoming/k525_full.mp3 \
  --title "Mozart: Eine kleine Nachtmusik, K. 525" \
  --names "I. Allegro,II. Romanze,III. Menuetto,IV. Rondo" --parts "Violin 1,Violin 2,Viola,Cello"
```

The PDF is split into movements by OMR, and the recording is split at the
pauses between movements so that each part matches its score best. You can
also pass one MusicXML/MIDI file per movement: `--score mv1.mxl mv2.mid ...`.

### MIDI scores (e.g. Mutopia Project)

MIDI has exact rhythms but no repeat signs and no upbeat information. Tell the
program the upbeat length: `qc new id --score x.mid --pickup 2` (2 = a half-note upbeat).
Good for movements without repeats; sometimes better than OMR.

### Old recordings with hiss and crackle

```bash
qc clean-audio --test incoming/old.mp3 --start 30   # 40-second before/after samples to compare
qc clean-audio haydn76_3_2 --strength medium        # light / medium / strong
qc site
```

Only the player uses the cleaned file; analysis and alignment are unchanged.

### The score in the player

`qc site` shows every movement's score. While the music plays, the current
bar is highlighted and pages turn; click a bar to jump there.

* Scores read from a **PDF** show the **original printed pages**. OMR makes
  mistakes in the notes, but it finds bar lines reliably, so we keep its bar
  positions (`pieces/<id>/printed/`) and show the real scan. To see the
  recognised notes instead, set `"score_view": "redrawn"` in the config.
* Other scores (ABC, MusicXML, MIDI) are drawn with Verovio.
* For scores read by OMR, bars whose written notes fit the sound clearly worse
  than the bars around them get a red dotted frame and are listed above the score
  ("Bars to compare by ear", at most 12). They are hints that the scan may have
  been misread there, not verdicts.

### Compare recordings

```bash
qc add-recording haydn76_3_2 --name "Budapest Quartet" --main-name "Koeckert Quartet" \
  --audio "incoming/IMSLP722029-....mp3" --audio-credit "Budapest String Quartet, LP (IMSLP #722029)"
qc site
```

The player then shows a **Recording** menu (switching keeps your place: same bar,
same repeat) and a **Compare recordings** chart: the tempo of every bar in each
recording, the total lengths, which repeats each group took, and the sections where
the two differ most beyond one simply being faster. `qc align <id>` re-aligns all recordings.

### Practice mode

Under the timeline: **Speed** slows the recording down (50–100%) without changing
the pitch. **Choose bars to loop**, then click the first and the last bar in the
score: that passage repeats until you press *Stop looping*. **Count-in** plays one
bar of clicks (at the performers' tempo there, times your speed) before each start.

### If the repeats are wrong

The program chooses which repeats the performers took: it tries every mix of
taken and skipped repeats (up to 7 repeat signs), and when several fit almost
equally well it checks which one keeps every passage in the same relation to its
printed metronome mark (OMR reads these marks when OCR languages are installed,
see below). If it is still unsure, the player shows a note. You can fix it in `pieces/<id>/config.json`:
`"audio": {..., "order": "no_repeats"}` (names are in `alignment.json` →
`candidate_costs`), then `qc align <id> && qc site`. For OMR scores, repeat
signs may be misread; on a near tie the program takes fewer repeats. If you
know the metronome mark, `--tempo 66` helps it decide.

If OMR misread the repeat signs, write the repeats the performers play by hand
(measure labels), and take them all:

```json
"repeats": [["33", "36"], ["49", "52"]],
"audio": {..., "order": "all_repeats"}
```

`"repeats": []` removes every repeat sign. (First/second endings: fix the file in MuseScore.)

### Optical music recognition (Audiveris)

* Download the `.dmg` for Apple Silicon ("macosx-arm64") from
  https://github.com/Audiveris/audiveris/releases and drag it to Applications.
* The first time, macOS may block it: System Settings → Privacy & Security → "Open Anyway".
* `qc` finds it at `/Applications/Audiveris.app`. Elsewhere? `export QC_AUDIVERIS=/path/to/Audiveris`.
* Very large scans are re-rendered at 300 dpi automatically (Audiveris refuses pages above 20 MP).
* Text (tempo marks, "Allegro", "pizz.") is read only with OCR language files: put
  `eng.traineddata`, `ita.traineddata`, `deu.traineddata` (from github.com/tesseract-ocr/tessdata)
  in the `tessdata` folder inside Audiveris' user configuration folder (on Linux
  `~/.config/AudiverisLtd/audiveris/tessdata`; Audiveris' log names the folder it uses).
  Without them OMR still works, but cannot use the tempo marks.

### Piano trios and other piano music

The whole pipeline works with a piano (tested on Schubert's Trio D. 929, I). But
OMR reads piano staves much less reliably than string parts: in that test about
60% of the bars had rhythm errors. Following the music still works, because the
alignment needs only rough notes, and the player shows the printed page. The
analysis (keys, who leads) is rough. For piano music a MusicXML file is much better than a PDF.

## How it works (short)

**Analysis.** For each measure and part we compute simple numbers: how many
notes start, how many different pitches, how often the line moves by step,
whether its rhythm differs from the others, whether it is the top voice, and
whether it carries a known theme. A weighted score picks the *lead* part;
a Viterbi pass stops the lead from jumping every bar. Themes are matched by
melodic intervals (so transpositions count) and rhythm. In variation sets, the
theme's main notes are searched in every part of every variation. Harmony comes
from the expert ABC labels for Beethoven, or is estimated (Krumhansl key
profiles + chord templates) for new scores, and is marked as such.

**Alignment.** Score and audio are turned into chroma (12 pitch classes per
frame) plus an onset curve. The score is first warped by its written tempo
(Adagio sections take longer). Every repeat pattern (all, none, mixed, Da Capo)
is tried with a tempo-limited DTW; the best one wins. A fine DTW (46 ms frames)
in a band around the coarse path gives the start time of every measure.
Measures with a poor local match are flagged.

**Guide.** The fact sheet is compacted into text. Claude must return JSON
through a forced tool call; every listening point carries machine-readable
claims (`{"type": "lead", "measure": "27", "value": "Viola"}`). The verifier
checks each claim against the facts (±1 measure). Failures are sent back once
for repair; points that still fail are removed. The verification report is
saved with the guide and shown in the player.

## Accuracy so far

Alignment on 28 Beethoven quartet movements from MusicNet (ground truth from
MusicNet's note labels): see `docs/RESULTS.md`. Typical median error per
measure ≈ 0.1 s; the repeat pattern is right in 26 of 28 movements.

## Data and licences

* ABC – DCML Annotated Beethoven Corpus, CC BY (Neuwirth et al., 2018).
* MusicNet – Thickstun et al., CC BY 4.0. Recordings from Musopen, European Archive, Isabella Stewart Gardner Museum.
* IMSLP files keep their own licences (shown in each piece's credits). CC BY-NC-ND recordings: personal use only, do not redistribute.
* Audiveris – AGPL, used as an external program.

## Publishing

**The code** can go to a public GitHub repository as it is: `.gitignore` keeps out every
recording (`incoming/`, `pieces/*/audio*`), the built sites, MusicNet/ABC data and `.env`
(the API key). Code: MIT (see `LICENSE`); guides and analyses: CC BY 4.0.

**A public listening website** lives on the `gh-pages` branch of the same repository:

```bash
qc publish                # builds public_site/ and pushes it to the gh-pages branch
```

The first time, turn it on in GitHub: *Settings → Pages → Source: Deploy from a branch →
gh-pages / (root)*. The command prints the address (`https://<you>.github.io/<repo>/`).
Publishing again uploads only what changed. `qc site --public` builds the folder without
uploading; `qc publish --no-push` commits it locally only.

Each recording's licence decides what happens (the `"license"` field in the piece's
`config.json`, otherwise the licence written in its credit):

| Licence | Public site |
|---|---|
| CC0, CC BY, CC BY-SA, EFF Open Audio License | cut into movements, as on your own computer |
| CC BY-NC-ND, CC BY-ND (no changes allowed) | the original file, unchanged; each movement starts at its first bar |
| "public domain outside the US", unknown | left out |

Set `"public": false` in a piece's `config.json` to keep a whole piece private (it still
works on your computer). `public_site/credits.html` lists every score and recording with its
licence; the player links to it. Non-commercial (NC) licences: do not put the site behind
ads or a paywall.

## Checking the player

```bash
pip install playwright && python -m playwright install chromium   # once
python scripts/check_site.py site                                   # every piece, in a headless browser
```

If a score changes after a guide was written (for example a better score from
the library), the old guide is hidden and `qc site` prints the `qc guide` command
to write a new one.

## Tests

```bash
pytest -q            # fast, offline (fake API client)
pytest -q -m api     # one live API call (costs a few cents)
```
