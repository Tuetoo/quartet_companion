"""Check the model's claims against the fact sheet.

The model must attach a list of machine-readable claims to every
listening point, e.g. {"type": "lead", "measure": "27", "value": "Viola"}.
Each claim type has a simple rule. A claim passes if the fact sheet
supports it within a small window of measures (default +/- 1), because
musical events do not always start exactly on a bar line.

Claims we cannot check automatically (type "other") are reported as
"unchecked", never as "verified".
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

CLAIM_TYPES = ["section", "key", "modulation", "lead", "theme", "texture", "dynamic", "cadence",
               "variation_tune", "climax", "other"]

_PART_ALIASES = {
    "violin 1": "Violin 1", "first violin": "Violin 1", "vn1": "Violin 1", "violin i": "Violin 1",
    "violin 2": "Violin 2", "second violin": "Violin 2", "vn2": "Violin 2", "violin ii": "Violin 2",
    "viola": "Viola", "va": "Viola", "cello": "Cello", "vc": "Cello", "violoncello": "Cello",
    "violin": "Violin", "piano": "Piano", "pianoforte": "Piano", "pno": "Piano", "klavier": "Piano",
    "violine": "Violin", "violoncell": "Cello",
}
_TEXTURE_SYNONYMS = {
    "melody and accompaniment": "melody + accompaniment", "melody with accompaniment": "melody + accompaniment",
    "unison": "unison/octaves", "octaves": "unison/octaves", "polyphonic": "independent lines",
    "counterpoint": "independent lines", "imitation": "independent lines",
}
_CADENCE_SYNONYMS = {"perfect authentic": "PAC", "imperfect authentic": "IAC", "half": "HC",
                     "deceptive": "DC", "evaded": "EC", "authentic": "PAC|IAC", "plagal": "PC"}


def norm_part(text: str) -> str:
    """Part name from a claim value. Accepts extra words, e.g. "Viola (Var. 5, presence 0.63)"."""
    t = str(text).strip().lower()
    if t in _PART_ALIASES:
        return _PART_ALIASES[t]
    found = set()
    rest = t
    for alias in sorted(_PART_ALIASES, key=len, reverse=True):   # "violin 1" before "violin"
        if re.search(rf"\b{re.escape(alias)}\b", rest):
            found.add(_PART_ALIASES[alias])
            rest = re.sub(rf"\b{re.escape(alias)}\b", " ", rest)
    if len(found) == 1:
        return found.pop()
    return str(text).strip()


def norm_key(text: str) -> str:
    t = str(text).strip().replace("♭", "b").replace("♯", "#").replace("-", " ")
    t = re.sub(r"\s+", " ", t)
    m = re.match(r"^([A-Ga-g])([#b]?)\s*(major|minor|maj|min|m)?$", t, re.IGNORECASE)
    if not m:
        return t.lower()
    letter, acc, mode = m.groups()
    mode = (mode or "major").lower()
    mode = "minor" if mode in ("minor", "min", "m") else "major"
    return f"{letter.upper()}{acc} {mode}".lower()


@dataclass
class ClaimResult:
    claim: dict
    status: str              # verified | failed | unchecked
    reason: str = ""


@dataclass
class VerificationReport:
    results: list[ClaimResult] = field(default_factory=list)
    bad_labels: list[str] = field(default_factory=list)

    @property
    def n_failed(self) -> int:
        return sum(r.status == "failed" for r in self.results) + len(self.bad_labels)

    @property
    def n_verified(self) -> int:
        return sum(r.status == "verified" for r in self.results)

    @property
    def n_unchecked(self) -> int:
        return sum(r.status == "unchecked" for r in self.results)

    def summary(self) -> dict:
        return {"verified": self.n_verified, "failed": self.n_failed, "unchecked": self.n_unchecked,
                "failures": [{"claim": r.claim, "reason": r.reason} for r in self.results if r.status == "failed"]
                + [{"claim": {"label": b}, "reason": "measure label does not exist"} for b in self.bad_labels]}


class Verifier:
    def __init__(self, facts: dict, window: int = 1):
        self.facts = facts
        self.window = window
        self.measures = facts["measures"]
        self.labels = [m["label"] for m in self.measures]
        self.index_of: dict[str, list[int]] = {}
        for i, lb in enumerate(self.labels):
            self.index_of.setdefault(lb, []).append(i)
        self.parts = facts["piece"]["parts"]

    # --------------------------------------------------------------- helpers
    def _rows(self, label: str, window: int | None = None) -> list[dict]:
        w = self.window if window is None else window
        idx = self.index_of.get(str(label).strip())
        if not idx:
            return []
        lo, hi = max(0, min(idx) - w), min(len(self.measures) - 1, max(idx) + w)
        return self.measures[lo:hi + 1]

    def label_exists(self, label: str) -> bool:
        return str(label).strip() in self.index_of

    # ----------------------------------------------------------------- checks
    def check(self, claim: dict) -> ClaimResult:
        ctype = str(claim.get("type", "other")).lower()
        label = str(claim.get("measure", "")).strip()
        value = str(claim.get("value", "")).strip()
        if ctype not in CLAIM_TYPES or ctype == "other":
            return ClaimResult(claim, "unchecked", "free-form claim")
        if ctype != "climax" and not self.label_exists(label):
            return ClaimResult(claim, "failed", f"measure '{label}' does not exist")
        fn = getattr(self, f"_check_{ctype}")
        ok, reason = fn(label, value)
        return ClaimResult(claim, "verified" if ok else "failed", reason)

    def _check_section(self, label, value):
        rows = self._rows(label, 0)
        names = {r["section"].lower() for r in rows}
        v = value.lower().rstrip(".")
        ok = any(v == n.rstrip(".") or v in n or n in v for n in names)
        return ok, "" if ok else f"measure {label} is in section {sorted(names)}"

    def _check_key(self, label, value):
        rows = self._rows(label)
        keys = {norm_key(r["key"]) for r in rows}
        ok = norm_key(value) in keys
        return ok, "" if ok else f"key near {label} is {sorted(keys)}"

    def _check_modulation(self, label, value):
        rows = self._rows(label, max(2, self.window))
        target = norm_key(value)
        ok = any(norm_key(r["key"]) == target for r in rows) and \
            any(norm_key(r["key"]) != target for r in self._rows(label, 6))
        return ok, "" if ok else f"no change to {value} near {label}"

    def _check_lead(self, label, value):
        part = norm_part(value)
        rows = self._rows(label)
        leads = {r["lead"] for r in rows} | {r["co_lead"] for r in rows if r["co_lead"]}
        if part in leads:
            return True, ""
        # theme tune hidden in a part counts as "carrying the melody"
        for o in self.facts.get("theme_occurrences", []):
            if o["part"] == part and self._overlaps(o["start_label"], o["end_label"], label):
                return True, ""
        for v in self.facts.get("variations", []):
            if self._overlaps(v["start_label"], v["end_label"], label) and \
                    v["theme_tune_presence"].get(part, 0) >= 0.5:
                return True, ""
        return False, f"lead near {label} is {sorted(leads)}"

    def _check_theme(self, label, value):
        part = norm_part(value)
        for o in self.facts.get("theme_occurrences", []):
            if (part in ("", o["part"]) or value == "") and self._near(o["start_label"], label, 1):
                return True, ""
        for v in self.facts.get("variations", []):
            if self._overlaps(v["start_label"], v["end_label"], label) and \
                    v["theme_tune_presence"].get(part, 0) >= 0.5:
                return True, ""
        return False, f"no theme entry in {value} near {label}"

    def _check_variation_tune(self, label, value):
        part = norm_part(value)
        seen = []
        for v in self.facts.get("variations", []):
            if self._overlaps(v["start_label"], v["end_label"], label):
                share = v["theme_tune_presence"].get(part, 0)
                if share >= 0.5:
                    return True, ""
                seen.append(f"{v['name']}: {share}")
        if seen:
            return False, f"{part} does not carry the tune here ({'; '.join(seen)})"
        return False, f"{label} is not inside a variation"

    def _check_texture(self, label, value):
        v = _TEXTURE_SYNONYMS.get(value.lower(), value.lower())
        rows = self._rows(label)
        tex = {r["texture"] for r in rows}
        # facts made before "held" existed called held-over bars "tacet"; accept either word for them
        ok = v in tex or (v == "tacet" and "held" in tex) or (v in ("duet", "trio") and any(len(r["active_parts"]) == (2 if v == "duet" else 3) for r in rows))
        return ok, "" if ok else f"texture near {label} is {sorted(tex)}"

    def _check_dynamic(self, label, value):
        v = value.lower().replace(".", "").strip()
        rows = self._rows(label)
        found = set()
        for r in rows:
            found.add(r["dynamic"])
            found.update(m.lower() for m in r["markings"])
            found.update(h for h in r["hairpins"])
        if v in ("crescendo", "cresc"):
            v = "cresc"
        if v in ("diminuendo", "decrescendo", "dim", "decresc"):
            v = "dim"
        ok = v in found
        return ok, "" if ok else f"dynamics near {label}: {sorted(found)}"

    def _check_cadence(self, label, value):
        want = _CADENCE_SYNONYMS.get(value.lower().replace(" cadence", ""), value.upper())
        rows = self._rows(label)
        cads = {r["cadence"] for r in rows if r["cadence"]}
        ok = any(c in want.split("|") for c in cads)
        return ok, "" if ok else f"cadences near {label}: {sorted(cads) or 'none'}"

    def _check_climax(self, label, value):
        c = self.facts.get("climax")
        ok = bool(c) and self._near(c["label"], label, 2)
        return ok, "" if ok else f"computed climax is at {c['label'] if c else 'n/a'}"

    def _near(self, a: str, b: str, w: int) -> bool:
        ia, ib = self.index_of.get(str(a)), self.index_of.get(str(b))
        if not ia or not ib:
            return False
        return min(abs(x - y) for x in ia for y in ib) <= w

    def _overlaps(self, start: str, end: str, label: str) -> bool:
        s, e, x = self.index_of.get(str(start)), self.index_of.get(str(end)), self.index_of.get(str(label))
        if not s or not e or not x:
            return False
        return any(min(s) - self.window <= i <= max(e) + self.window for i in x)


LABEL_TAG = re.compile(r"\[m\.?\s*([0-9]+[a-h]?)\s*(?:[-–]\s*([0-9]+[a-h]?))?\]")


def verify_guide(guide: dict, facts: dict) -> VerificationReport:
    """Check all claims and all [m. N] tags in a guide."""
    v = Verifier(facts)
    report = VerificationReport()
    for point in guide.get("listening_points", []):
        for lb in (point.get("start_measure"), point.get("end_measure")):
            if lb is not None and not v.label_exists(str(lb)):
                report.bad_labels.append(str(lb))
        for m in LABEL_TAG.finditer(point.get("text", "")):
            for lb in m.groups():
                if lb and not v.label_exists(lb):
                    report.bad_labels.append(lb)
        for claim in point.get("claims", []):
            r = v.check(claim)
            r.claim = {**claim, "point": point.get("headline", "")}
            report.results.append(r)
    for claim in guide.get("overview_claims", []):
        report.results.append(v.check(claim))
    return report
