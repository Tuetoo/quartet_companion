"""Small music-theory helpers: key names, pitch names, Roman numerals.

We count pitches on the "line of fifths" (tpc = tonal pitch class):
C = 0, G = 1, D = 2, ..., F = -1, Bb = -2 ... This keeps the spelling
right (Ab and G# are different keys on paper).
"""
from __future__ import annotations

import re

LETTERS_BY_FIFTHS = "FCGDAEB"  # tpc -1 .. 5
_LETTER_TPC = {ch: i - 1 for i, ch in enumerate(LETTERS_BY_FIFTHS)}

# Scale-degree offsets on the line of fifths, relative to the tonic.
_MAJOR_DEGREE_FIFTHS = [0, 2, 4, -1, 1, 3, 5]
# DCML convention: in a minor key, numerals refer to the natural minor scale.
_MINOR_DEGREE_FIFTHS = [0, 2, -3, -1, 1, -4, -2]
_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]

PITCH_NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def tpc_to_name(tpc: int) -> str:
    """Line-of-fifths position -> note name, e.g. 0 -> 'C', -4 -> 'Ab', 6 -> 'F#'."""
    letter = LETTERS_BY_FIFTHS[(tpc + 1) % 7]
    shift = (tpc + 1) // 7
    return letter + ("#" * shift if shift > 0 else "b" * (-shift))


def name_to_tpc(name: str) -> int:
    """'Eb' -> -3, 'f#' -> 6. Case is ignored."""
    name = name.strip()
    letter = name[0].upper()
    if letter not in _LETTER_TPC:
        raise ValueError(f"not a note name: {name!r}")
    tpc = _LETTER_TPC[letter]
    for ch in name[1:]:
        if ch == "#":
            tpc += 7
        elif ch == "b":
            tpc -= 7
        else:
            raise ValueError(f"not a note name: {name!r}")
    return tpc


def tpc_to_pc(tpc: int) -> int:
    """Line-of-fifths position -> pitch class 0..11."""
    return (tpc * 7) % 12


def midi_to_name(midi: int) -> str:
    """60 -> 'C4' (sharp spelling; only for display of single notes)."""
    return f"{PITCH_NAMES_SHARP[midi % 12]}{midi // 12 - 1}"


def key_label(tonic_tpc: int, minor: bool) -> str:
    """Human key name: 'D major', 'B minor'."""
    return f"{tpc_to_name(tonic_tpc)} {'minor' if minor else 'major'}"


def parse_dcml_key(globalkey: str) -> tuple[int, bool]:
    """DCML global key ('D' = D major, 'b' = B minor) -> (tonic tpc, is_minor)."""
    globalkey = globalkey.strip()
    minor = globalkey[0].islower()
    return name_to_tpc(globalkey), minor


_NUMERAL_RE = re.compile(r"^(?P<acc>[#b]*)(?P<num>(?:VII|VI|V|IV|III|II|I|vii|vi|v|iv|iii|ii|i))$")


def resolve_numeral_key(numeral: str, tonic_tpc: int, minor: bool) -> tuple[int, bool]:
    """Resolve a key written as a Roman numeral relative to (tonic, mode).

    Supports accidentals and chains such as 'V/V' (read right to left).
    """
    numeral = numeral.strip()
    if "/" in numeral:
        head, tail = numeral.split("/", 1)
        base_tpc, base_minor = resolve_numeral_key(tail, tonic_tpc, minor)
        return resolve_numeral_key(head, base_tpc, base_minor)
    m = _NUMERAL_RE.match(numeral)
    if not m:
        raise ValueError(f"cannot read numeral {numeral!r}")
    num = m.group("num")
    degree = _ROMAN.index(num.upper())
    offsets = _MINOR_DEGREE_FIFTHS if minor else _MAJOR_DEGREE_FIFTHS
    tpc = tonic_tpc + offsets[degree]
    for ch in m.group("acc"):
        tpc += 7 if ch == "#" else -7
    return tpc, num.islower()


def dcml_local_key_name(globalkey: str, localkey: str) -> str:
    """('D', 'vi') -> 'B minor'. Falls back to the raw text if it cannot be read."""
    try:
        g_tpc, g_minor = parse_dcml_key(globalkey)
        tpc, minor = resolve_numeral_key(localkey, g_tpc, g_minor)
        return key_label(tpc, minor)
    except (ValueError, IndexError):
        return f"{localkey} of {globalkey}"


def keysig_to_major_tonic(fifths: int) -> str:
    """Key signature in sharps (+) / flats (-) -> name of the major key."""
    return tpc_to_name(fifths)
