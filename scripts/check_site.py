"""Click through every piece of the built web player in a headless browser.

    python scripts/check_site.py [site_dir]        (needs: pip install playwright)

For each piece it checks: the page loads without script errors, the title is
right, the score shows and the right bar lights up on the right page, the
guide is shown when one exists, and (if there are several recordings) the
recording menu and comparison chart are there. Audio files are not needed.
Prints one line per piece and exits with code 1 if anything failed.
"""
from __future__ import annotations

import asyncio
import http.server
import io
import json
import os
import re
import sys
import threading
from pathlib import Path


class _Handler(http.server.SimpleHTTPRequestHandler):
    """Static files with HTTP range support (browsers need it to seek in audio)."""

    def send_head(self):
        rng, path = self.headers.get("Range"), self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        a, b = int(m.group(1) or 0), int(m.group(2) or size - 1)
        with open(path, "rb") as f:
            f.seek(a)
            data = f.read(b - a + 1)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {a}-{a + len(data) - 1}/{size}")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        return io.BytesIO(data)

    def log_message(self, *args):
        pass


def serve(site: Path, port: int = 8797) -> http.server.ThreadingHTTPServer:
    handler = lambda *a, **k: _Handler(*a, directory=str(site), **k)   # noqa: E731
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


async def check(site: Path, shots: Path | None = None) -> list[dict]:
    from playwright.async_api import async_playwright
    index = json.loads((site / "pieces" / "index.json").read_text())
    srv = serve(site)
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for entry in index:
            pid = entry["id"]
            data = json.loads((site / "pieces" / pid / "data.json").read_text())
            page = await browser.new_page(viewport={"width": 1200, "height": 1400})
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            problems: list[str] = []
            await page.goto(f"http://127.0.0.1:{srv.server_port}/#{pid}")
            await page.wait_for_timeout(1500)
            title = await page.inner_text("#title")
            if title.strip() != data["piece"]["title"].strip():
                problems.append(f"title shows {title!r}")
            info = {}
            if data.get("score"):
                sc = data["score"]
                mcs = [m["mc"] for m in data["measures"]]
                mapped = sum(1 for mc in mcs if str(mc) in sc["measures"])
                info["score_coverage"] = round(mapped / max(1, len(mcs)), 3)
                if info["score_coverage"] < 0.9:
                    problems.append(f"only {mapped}/{len(mcs)} bars found in the score")
                samples = [mc for mc in (mcs[0], mcs[len(mcs) // 2], mcs[-1]) if str(mc) in sc["measures"]]
                # no audio here: stop "follow the music" from turning back to the page at 0:00
                await page.evaluate("() => { document.querySelector('#follow').checked = false; }")
                for mc in samples:
                    want = sc["measures"][str(mc)]["page"]
                    await page.evaluate(f"() => window.qcDebug.showPage({want})")
                    await page.wait_for_timeout(400)
                    await page.evaluate(f"() => window.qcDebug.highlightMeasure({mc})")
                    await page.wait_for_timeout(200)
                    label = await page.inner_text("#page-label")
                    sel = ".qc-hl" if sc.get("kind") == "image" else ".qc-now"
                    lit = await page.evaluate(f"() => document.querySelectorAll('{sel}').length")
                    if not label.startswith(("page", "页")) or f" {want} /" not in f" {label.split(' ', 1)[-1]}":
                        problems.append(f"bar {mc}: page label {label!r}, expected page {want}")
                    if not lit:
                        problems.append(f"bar {mc}: nothing highlighted on page {want}")
            doubts = data.get("score_doubts") or []
            if doubts and data.get("score"):
                info["doubts"] = len(doubts)
                chips = await page.evaluate("() => document.querySelectorAll('#doubts-list .doubt-chip').length")
                if chips != len(doubts):
                    problems.append(f"{chips} doubt chips shown, expected {len(doubts)}")
                d0 = next((d for d in doubts if str(d["mc"]) in data["score"]["measures"]), None)
                if d0:
                    await page.evaluate("() => { document.querySelector('#follow').checked = false; }")
                    await page.evaluate(f"() => window.qcDebug.showPage({data['score']['measures'][str(d0['mc'])]['page']})")
                    await page.wait_for_timeout(500)
                    marks = await page.evaluate("() => document.querySelectorAll('.qc-doubtbox, .qc-doubt').length")
                    if not marks:
                        problems.append(f"bar {d0['label']}: no dotted mark on its page")
            n_points = await page.evaluate("() => document.querySelectorAll('.point').length")
            info["guide_points"] = n_points
            if data.get("guides") and not n_points:
                problems.append("guide exists but no listening points are shown")
            recs = data.get("recordings") or []
            if len(recs) > 1:
                opts = await page.evaluate("() => document.querySelectorAll('#rec-select option').length")
                lines = await page.evaluate("() => document.querySelectorAll('#compare-chart path').length")
                info["recordings"] = opts
                if opts != len(recs) or lines != len(recs):
                    problems.append(f"recordings menu {opts}, chart lines {lines}, expected {len(recs)}")
            await page.click(".lang button[data-lang=zh]")
            await page.wait_for_timeout(300)
            if shots:
                shots.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(shots / f"{pid}.png"))
            problems += [f"script error: {e}" for e in errors]
            results.append({"id": pid, "ok": not problems, "problems": problems, **info})
            print(("OK   " if not problems else "FAIL ") + pid + "  " + json.dumps(info) +
                  ("" if not problems else "  " + "; ".join(problems)), flush=True)
            await page.close()
        lib = await check_library(browser, srv.server_port, index, shots)
        results.append({"id": "(library)", "ok": not lib, "problems": lib})
        print(("OK   " if not lib else "FAIL ") + "(library search)" + ("" if not lib else "  " + "; ".join(lib)), flush=True)
        await browser.close()
    srv.shutdown()
    return results


async def check_library(browser, port: int, index: list[dict], shots: Path | None) -> list[str]:
    """The library panel lists every movement, search narrows it, and a click opens the piece."""
    problems: list[str] = []
    page = await browser.new_page(viewport={"width": 1200, "height": 1000})
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    await page.goto(f"http://127.0.0.1:{port}/")
    await page.wait_for_timeout(1200)
    await page.click("#lib-open")
    await page.wait_for_timeout(200)
    n_items = lambda: page.evaluate("() => document.querySelectorAll('#lib-list .lib-item').length")  # noqa: E731
    if await n_items() != len(index):
        problems.append(f"library lists {await n_items()} movements, index has {len(index)}")
    # search by the last word of a composer's name
    last = index[-1]["composer"].split()[-1]
    want = sum(1 for e in index if last.lower() in (e["composer"] + " " + e["title"]).lower())
    await page.fill("#lib-q", last)
    await page.wait_for_timeout(150)
    got = await n_items()
    if got < 1 or got > want:
        problems.append(f"search {last!r}: {got} results, expected 1..{want}")
    await page.fill("#lib-q", "zzzz-no-such-piece")
    await page.wait_for_timeout(150)
    if await n_items():
        problems.append("nonsense search still lists pieces")
    # Chinese key names are searchable, e.g. "G major" -> "G大调"
    zh = await page.evaluate("() => window.qcDebug.keyZh('E-flat major') + '|' + window.qcDebug.keyZh('D minor')")
    if zh != "降E大调|d小调":
        problems.append(f"Chinese key names wrong: {zh}")
    await page.fill("#lib-q", "")
    target = index[-1]
    await page.click(f"#lib-list .lib-item[data-id='{target['id']}']")
    await page.wait_for_timeout(1200)
    title = await page.inner_text("#title")
    if title.strip() != target["title"].strip():
        problems.append(f"clicking {target['id']} opened {title!r}")
    if await page.evaluate("() => document.getElementById('library').open"):
        problems.append("library stayed open after choosing a piece")
    await page.click(".lang button[data-lang=zh]")
    await page.click("#lib-open")
    await page.wait_for_timeout(200)
    count = await page.inner_text("#lib-count")
    if "部作品" not in count:
        problems.append(f"library count not in Chinese: {count!r}")
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(shots / "_library.png"))
    problems += [f"script error: {e}" for e in errors]
    await page.close()
    return problems


if __name__ == "__main__":
    site_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    res = asyncio.run(check(site_dir, Path(sys.argv[2]) if len(sys.argv) > 2 else None))
    print(f"{sum(r['ok'] for r in res)}/{len(res)} checks OK")
    sys.exit(0 if all(r["ok"] for r in res) else 1)
