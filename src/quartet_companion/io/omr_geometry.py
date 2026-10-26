"""Where every measure sits on the printed page, read from an Audiveris book (.omr).

OMR makes mistakes in the *notes*, but it finds staff lines and bar lines
very reliably. So for scores that came from a PDF we can show the original
printed page (no OMR errors) and still know which rectangle is "measure 27".

An .omr file is a zip. Each sheet (= one PDF page) has sheet#N/sheet#N.xml with
<system> elements; each system has <stack left= right=> elements (one per
measure, across all staves) and <staff> elements with the five staff lines.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def _sheet_numbers(z: zipfile.ZipFile) -> list[int]:
    nums = {int(m.group(1)) for n in z.namelist() if (m := re.match(r"sheet#(\d+)/sheet#\1\.xml$", n))}
    return sorted(nums)


def book_measure_boxes(omr_path: str | Path, pad: int = 6) -> list[dict]:
    """All measures of the book in reading order.

    Each item: {"sheet": n (1-based PDF page), "movement_start": bool,
    "x0", "x1", "y0", "y1" (pixels), "w", "h" (sheet size in pixels)}.
    """
    out: list[dict] = []
    with zipfile.ZipFile(omr_path) as z:
        # movement starts are recorded in book.xml: <sheet number=n><page id=k movement-start="true">
        starts = set()
        book = ET.fromstring(z.read("book.xml"))
        for sh in book.iter("sheet"):
            for pg in sh.findall(".//page"):
                if pg.get("movement-start") == "true":
                    starts.add((int(sh.get("number")), pg.get("id")))
        for sn in _sheet_numbers(z):
            root = ET.fromstring(z.read(f"sheet#{sn}/sheet#{sn}.xml"))
            pic = root.find("picture")
            w, h = int(pic.get("width")), int(pic.get("height"))
            interline = 18
            il = root.find("scale/interline")
            if il is not None:
                interline = int(il.get("main"))
            for page in root.findall("page"):
                first_in_page = True
                movement_start = (sn, page.get("id")) in starts
                for system in page.findall("system"):
                    ys: list[float] = []
                    for staff in system.iter("staff"):
                        for line in staff.findall("lines/line"):
                            ys += [float(p.get("y")) for p in line.findall("point")]
                    if not ys:
                        continue
                    y0 = max(0, int(min(ys) - 3 * interline))
                    y1 = min(h, int(max(ys) + 3 * interline))
                    for stack in system.findall("stack"):
                        out.append({"sheet": sn, "movement_start": movement_start and first_in_page,
                                    "x0": max(0, int(stack.get("left")) - pad), "x1": min(w, int(stack.get("right")) + pad),
                                    "y0": y0, "y1": y1, "w": w, "h": h})
                        first_in_page = False
    return out


def movements(boxes: list[dict]) -> list[list[dict]]:
    """Split the book's measures where Audiveris saw a new movement."""
    groups: list[list[dict]] = []
    for b in boxes:
        if b["movement_start"] or not groups:
            groups.append([])
        groups[-1].append(b)
    return groups


def merge_split_measures(boxes: list[dict], omr_path: str | Path) -> list[list[dict]]:
    """Audiveris repeats a stack id when one measure continues on the next system
    (marked special="CAUTIONARY"). Join those into one measure with several boxes."""
    out: list[list[dict]] = []
    with zipfile.ZipFile(omr_path) as z:
        flags = []
        for sn in _sheet_numbers(z):
            root = ET.fromstring(z.read(f"sheet#{sn}/sheet#{sn}.xml"))
            for page in root.findall("page"):
                for system in page.findall("system"):
                    has_lines = any(True for _ in system.iter("line"))
                    if not has_lines:
                        continue
                    for stack in system.findall("stack"):
                        flags.append((sn, page.get("id"), stack.get("id"), stack.get("special") == "CAUTIONARY"))
    prev_key = None
    for b, (sn, pid, sid, caut) in zip(boxes, flags):
        key = (sn, pid, sid)
        if out and (caut or key == prev_key):
            out[-1].append(b)
        else:
            out.append([b])
        prev_key = key
    return out


def _mxl_measure_numbers(mxl: str | Path) -> list[str]:
    from ..score_render import read_musicxml_text
    text = read_musicxml_text(mxl)
    part = re.search(r"<part\b.*?</part>", text, flags=re.S)
    return re.findall(r'<measure\b[^>]*?\bnumber="([^"]*)"', part.group(0)) if part else []


def save_printed_pages(omr_book: str | Path, mxl_files: list[str | Path], dest_dirs: list[str | Path | None],
                       page_width: int = 1240) -> list[bool]:
    """For each movement, write <dest>/printed/page-N.png and geometry.json.

    geometry.json: {"pages": [{"file", "w", "h"}], "measures": [{"number", "boxes": [{"page", "x0","y0","x1","y1"}]}]}
    Box coordinates are fractions of the page size (0..1). Returns, per movement, whether it worked.
    """
    import json
    from PIL import Image

    omr_book = Path(omr_book)
    boxes = book_measure_boxes(omr_book)

    def split(measures):
        """Into movements (a measure starts a movement if its first box does)."""
        groups: list[list[list[dict]]] = []
        for m in measures:
            if m[0]["movement_start"] or not groups:
                groups.append([])
            groups[-1].append(m)
        if len(groups) != len(mxl_files) and len(mxl_files) == 1:
            groups = [[m for g in groups for m in g]]
        return groups

    # Two readings: split measures joined (usual), or one box per stack (when the
    # exported file also kept the halves as separate measures).
    readings = [split(merge_split_measures(boxes, omr_book)), split([[b] for b in boxes])]
    ok = []
    with zipfile.ZipFile(omr_book) as z:
        wanted: dict[str, list[tuple[list, list[str]]]] = {}      # dest -> [(measures, numbers)]
        for i, (mxl, dest) in enumerate(zip(mxl_files, dest_dirs)):
            if dest is None:                     # this movement is not wanted
                ok.append(False)
                continue
            numbers = _mxl_measure_numbers(mxl)
            groups = next((g for g in readings if i < len(g) and len(g[i]) == len(numbers)), None)
            if groups is None:
                # A bar split around a repeat sign appears twice in the file (same number)
                # but once on the page: let both halves share the page box.
                uniq = [n for k, n in enumerate(numbers) if k == 0 or n != numbers[k - 1]]
                g = next((g for g in readings if i < len(g) and len(g[i]) == len(uniq)), None)
                if g is not None:
                    it, expanded = iter(g[i]), []
                    for k, n in enumerate(numbers):
                        expanded.append(next(it) if k == 0 or n != numbers[k - 1] else expanded[-1])
                    groups = [None] * i + [expanded]
            if groups is None:
                found = len(readings[0][i]) if i < len(readings[0]) else 0
                print(f"  [printed] movement {i + 1}: {found} measures on the page vs {len(numbers)} in the file; "
                      "the printed page view is skipped")
                ok.append(False)
                continue
            wanted.setdefault(str(dest), []).append((groups[i], numbers))
            ok.append(True)
        # Several OMR "movements" may be one real movement (same destination): join them,
        # numbering later pieces on from the earlier ones (as concat_scores does).
        for dest, items in wanted.items():
            out = Path(dest) / "printed"
            out.mkdir(parents=True, exist_ok=True)
            sheets = sorted({b["sheet"] for meas, _ in items for m in meas for b in m})
            page_of = {sn: k + 1 for k, sn in enumerate(sheets)}
            pages = []
            for sn in sheets:
                with z.open(f"sheet#{sn}/BINARY.png") as fh:
                    im = Image.open(fh).convert("L")
                    h = round(im.height * page_width / im.width)
                    im = im.resize((page_width, h), Image.LANCZOS)
                    name = f"page-{page_of[sn]}.png"
                    im.save(out / name, optimize=True)
                    pages.append({"file": name, "w": page_width, "h": h})
            geo, offset = [], 0
            for meas, numbers in items:
                top = 0
                for num, m in zip(numbers, meas):
                    shown = str(int(num) + offset) if num.lstrip("-").isdigit() else num
                    top = max(top, int(shown)) if shown.lstrip("-").isdigit() else top
                    geo.append({"number": shown, "boxes": [
                        {"page": page_of[b["sheet"]], "x0": round(b["x0"] / b["w"], 4),
                         "x1": round(b["x1"] / b["w"], 4), "y0": round(b["y0"] / b["h"], 4),
                         "y1": round(b["y1"] / b["h"], 4)} for b in m]})
                offset = top
            (out / "geometry.json").write_text(json.dumps({"source": omr_book.name, "pages": pages, "measures": geo}))
    return ok


def printed_measure_map(score, geometry: dict) -> dict[int, dict]:
    """mc -> {"page", "boxes"} for the printed-page view.

    Same count: match in order. Otherwise match by printed number (k-th
    measure with number n in the score <-> k-th on the page)."""
    mcs = list(score.measures["mc"].astype(int))
    geo = geometry["measures"]
    if len(geo) == len(mcs):
        pairs = list(zip(mcs, geo))
    else:
        by_num: dict[str, list[dict]] = {}
        for g in geo:
            by_num.setdefault(str(g["number"]), []).append(g)
        seen: dict[str, int] = {}
        pairs = []
        for mc, mn in zip(mcs, score.measures["mn"].astype(int)):
            lst = by_num.get(str(mn))
            if not lst:
                continue
            k = seen.get(str(mn), 0)
            seen[str(mn)] = k + 1
            pairs.append((mc, lst[min(k, len(lst) - 1)]))
    return {mc: {"page": g["boxes"][0]["page"], "id": f"m{mc}", "boxes": g["boxes"]} for mc, g in pairs}


def save_printed_pages_safe(omr_dir: str | Path, mxl_files, dest_dirs) -> None:
    """Find the Audiveris book in omr_dir and save printed pages; never fail the caller."""
    books = sorted(Path(omr_dir).glob("*.omr"))
    if not books:
        print("  [printed] no Audiveris book (.omr) found; the player will redraw the recognised notes")
        return
    try:
        res = save_printed_pages(books[0], mxl_files, dest_dirs)
        if any(res):
            print("  [printed] the player will show the original printed pages")
    except Exception as exc:                     # a nice-to-have: never break `qc new`
        print(f"  [printed] could not prepare the printed pages ({type(exc).__name__}: {exc})")
