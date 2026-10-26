"""Ready-made scores from the OpenScore String Quartets corpus (CC0).

OpenScore (https://musescore.com/openscore-string-quartets) has typeset,
checked scores of about 200 string quartets of the "long 19th century"
(Haydn, Mozart, Beethoven, Schubert, Mendelssohn, Brahms, Dvořák ...).
They are much more accurate than a PDF read by OMR.

* `catalogue()`   - the list of works (downloaded once, kept in data/openscore/)
* `search(words)` - works whose composer/name/path contain all the words
* `download(row)` - the work's MusicXML file
* `split_movements(path, out_dir)` - one file per movement. A whole work is one
  file; MuseScore restarts the measure numbers at every movement, which is how
  we find the movements.
"""
from __future__ import annotations

import copy
import csv
import io
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RAW = "https://raw.githubusercontent.com/OpenScore/StringQuartets/main/"
ATTR_ORDER = ["divisions", "key", "time", "staves", "part-symbol", "instruments", "clef", "staff-details",
              "transpose", "for-part", "directive", "measure-style"]


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "quartet-companion"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _url(path: str) -> str:
    return RAW + urllib.parse.quote(path)


def catalogue(cache_dir: str | Path) -> list[dict]:
    cache = Path(cache_dir) / "scores.tsv"
    if not cache.exists():
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(_get(_url("data/scores.tsv")))
    rows = list(csv.DictReader(io.StringIO(cache.read_text(encoding="utf-8")), delimiter="\t"))
    for r in rows:
        r["composer"] = r["path"].split("/")[0].replace("_", " ")
    return rows


def _norm(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s)


def search(rows: list[dict], words: list[str]) -> list[dict]:
    """Rows that contain every word (accents and punctuation ignored): 'haydn 76 3', 'schubert maiden'."""
    ws = [_norm(w).strip() for w in words if _norm(w).strip()]
    out = []
    for r in rows:
        hay = " " + _norm(r["path"] + " " + r["name"] + " " + r["composer"]) + " "
        if all((f" {w} " in hay) if w.isdigit() else (w in hay) for w in ws):
            out.append(r)
    return out


def download(row: dict, cache_dir: str | Path) -> Path:
    dst = Path(cache_dir) / "files" / f"sq{row['id']}.mxl"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(_get(_url(f"scores/{row['path']}/sq{row['id']}.mxl"), timeout=120))
    return dst


# ----------------------------------------------------------------- movements
def _movement_starts(numbers: list[str]) -> list[int]:
    """Indices where a new movement begins: the measure number drops back to 0 or 1.
    Unnumbered measures (MuseScore writes e.g. "X4" for a bar outside the count, often
    the last bar before the next movement) are skipped when comparing."""
    starts = [0]
    prev = None
    for i, n in enumerate(numbers):
        m = re.fullmatch(r"-?\d+[a-z]?", n or "")
        if not m:
            continue
        cur = int(re.match(r"-?\d+", n).group())
        if prev is not None and cur <= 1 and prev > 4:
            starts.append(i)
        prev = cur
    return starts


def _attributes_before(measures: list[ET.Element], idx: int) -> dict[str, list[ET.Element]]:
    """The divisions/key/time/clef... in force when measure idx starts."""
    state: dict[str, list[ET.Element]] = {}
    for m in measures[:idx]:
        for attrs in m.findall("attributes"):
            for child in attrs:
                if child.tag == "clef":                  # one per staff
                    num = child.get("number", "1")
                    state["clef"] = [c for c in state.get("clef", []) if c.get("number", "1") != num] + [child]
                else:
                    state[child.tag] = [child]
    return state


def _played_end(measures: list[ET.Element], a: int, b: int, max_extra: int = 8) -> int:
    """End (exclusive) of the played part of a movement spanning measures[a:b].

    Some editions print a few bars after a movement's final barline that are not played
    there, e.g. the motto "Der schwer gefaßte Entschluß" Beethoven placed before the
    finale of Op.135 (OpenScore puts it at the end of the third movement). Up to
    max_extra such bars after a final barline are dropped, unless they hold a Trio or a
    da capo (then they belong to the movement)."""
    last_final = None
    for i in range(a, b - 1):
        for bl in measures[i].findall("barline"):
            if bl.findtext("bar-style") == "light-heavy" and bl.find("repeat") is None:
                last_final = i
    if last_final is None or b - (last_final + 1) > max_extra:
        return b
    words = " ".join(w.text or "" for m in measures[last_final + 1:b] for w in m.iter("words"))
    if re.search(r"\btrio\b|\bD\.\s?C\b|da\s+capo|\bfine\b", words, re.IGNORECASE):
        return b
    return last_final + 1


def split_movements(path: str | Path, out_dir: str | Path, stem: str = "mv") -> list[Path]:
    """Write one MusicXML file per movement. Returns the files in order."""
    from ..score_render import read_musicxml_text
    root = ET.fromstring(read_musicxml_text(path))
    parts = root.findall("part")
    numbers = [m.get("number", "") for m in parts[0].findall("measure")]
    starts = _movement_starts(numbers)
    bounds = [(a, _played_end(parts[0].findall("measure"), a, b)) for a, b in zip(starts, starts[1:] + [len(numbers)])]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for k, (a, b) in enumerate(bounds):
        doc = copy.deepcopy(root)
        for part in doc.findall("part"):
            ms = part.findall("measure")
            state = _attributes_before(ms, a)
            for m in ms[:a] + ms[b:]:
                part.remove(m)
            first = ms[a]
            attrs = first.find("attributes")
            if attrs is None:
                attrs = ET.Element("attributes")
                first.insert(0, attrs)
            have = {c.tag for c in attrs}
            for tag, elems in state.items():
                if tag not in have:
                    for e in elems:
                        attrs.append(copy.deepcopy(e))
            attrs[:] = sorted(list(attrs), key=lambda c: ATTR_ORDER.index(c.tag) if c.tag in ATTR_ORDER else 99)
        f = out_dir / f"{stem}{k + 1}.musicxml"
        ET.ElementTree(doc).write(f, encoding="utf-8", xml_declaration=True)
        files.append(f)
    return files


_PLAYING_WORDS = re.compile(
    r"^(arco|pizz\.?|pizzicato|col legno|sul .*|con sord.*|senza sord.*|sord\.?|solo|tutti|unis\.?|div\.?|"
    r"dolce|espr\.?|espressivo|cantabile|sotto voce|legato|stacc\.?|staccato|ten\.?|marc\.?|cresc\.?|dim\.?|"
    r"decresc\.?|rit\.?|riten\.?|rall\.?|a tempo|tr|sf|sfz|fp|pp+|p|mp|mf|f+|simile|sempre.*|poco a poco.*)$",
    re.IGNORECASE)
_TEMPO_WORDS = re.compile(r"(allegr|adagi|andant|largo|larghetto|lento|presto|vivace|moderato|menuet|minuet|scherzo|"
                          r"rondo|finale|grave|tempo|tema|variation|andantino|allegretto|maestoso|sostenuto|"
                          # French and German tempo words (Debussy, Ravel, Schumann...)
                          r"anim[eé]|vif|vite|mod[eé]r[eé]|lent|doucement|rythm[eé]|d[eé]cid[eé]|calme|"
                          r"schnell|langsam|lebhaft|ruhig|m[aä](ss|ß)ig|bewegt|kr[aä]ftig)", re.IGNORECASE)
_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def movement_titles(files: list[Path]) -> list[str]:
    """A short name for each movement from the words at its start ('II. Poco adagio; cantabile').
    Playing instructions (arco, pizz., dolce...) are skipped."""
    names = []
    for i, f in enumerate(files):
        root = ET.parse(f).getroot()
        words: list[str] = []
        for part in root.findall("part"):
            for m in part.findall("measure")[:2]:            # only the start of the movement
                words += [w.text.strip() for w in m.iter("words") if w.text and w.text.strip()]
        words = [re.sub(r"\s+", " ", w) for w in words if not _PLAYING_WORDS.match(w.strip())]
        head = next((w for w in words if re.match(r"^[IVX]+\.", w)), "")
        tempo = next((w for w in words if w != head and _TEMPO_WORDS.search(w)), "")
        if head and tempo and tempo.lower() in head.lower():
            tempo = ""
        if not head:
            head = (_ROMAN[i] + ".") if len(files) > 1 and i < len(_ROMAN) else ""
        names.append(" ".join(x for x in (head, tempo) if x).strip() or f.stem)
    return names
