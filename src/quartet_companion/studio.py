"""`qc studio`: add pieces from the browser instead of the command line.

A small local web server (only reachable from this computer):

    /                 the player (the built site/ folder)
    /studio.html      the add-a-piece page
    /api/search?q=    search the OpenScore string quartet library
    /api/incoming     recordings (and scores) waiting in incoming/
    /api/pieces       pieces already in the project
    /api/add          POST: add a work (runs `qc library add` in a separate process)
    /api/jobs/<n>     progress of a running job (log lines, done/failed)

Each job runs the normal command line in a child process, so a crash cannot take the
server down, and the log the page shows is exactly what the command prints. After a
successful add, the new pieces are built into the player (`qc site --only <prefix>`).
Guides are not written here (they use the API): the page shows the command to run.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path

from . import pieces as P
from .httpserve import QuietServer, RangeHandler

STUDIO_DIR = Path(__file__).resolve().parent / "studio_web"
AUDIO_EXT = {".mp3", ".wav", ".flac", ".ogg", ".aiff", ".aif"}   # what the audio reader can open

_jobs: dict[int, dict] = {}
_lock = threading.Lock()


def suggest_prefix(row: dict, existing: set[str]) -> str:
    """A short id for a work: composer + catalogue number ('mozart_k458', 'haydn_op76_4')."""
    comp = re.sub(r"[^a-z]", "", row["composer"].split(",")[0].lower())[:12] or "work"
    name = row["name"]
    m = (re.search(r"\b([KD])\.?\s?(\d+)", name) or re.search(r"Op\.?\s?(\d+)(?:,?\s*No\.?\s?(\d+))?", name, re.I)
         or re.search(r"No\.?\s?(\d+)", name, re.I))
    if m and m.re.pattern.startswith(r"\b([KD])"):
        tag = f"{m.group(1).lower()}{m.group(2)}"
    elif m and "Op" in m.re.pattern:
        tag = f"op{m.group(1)}" + (f"_{m.group(2)}" if m.group(2) else "")
    elif m:
        tag = f"no{m.group(1)}"
    else:
        tag = row["id"]
    base = f"{comp}_{tag}"
    prefix, n = base, 2
    while any(e == prefix or e.startswith(prefix + "_") for e in existing):
        prefix, n = f"{base}_{n}", n + 1
    return prefix


def _run_job(job_id: int, root: Path, cmds: list[list[str]]) -> None:
    job = _jobs[job_id]
    for cmd in cmds:
        job["log"].append("$ qc " + " ".join(cmd[3:]))
        try:
            proc = subprocess.Popen(cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                    bufsize=1, env={**__import__("os").environ, "PYTHONUNBUFFERED": "1"})
        except OSError as exc:
            job["log"].append(f"(could not start: {exc})")
            job["status"] = "failed"
            return
        for line in proc.stdout:
            line = line.rstrip()
            if line and not re.search(r"Warning|warnings.warn|getNumberList", line):
                with _lock:
                    job["log"].append(line)
        proc.wait()
        if proc.returncode != 0:
            job["status"] = "failed"
            job["log"].append(f"(stopped: the command ended with code {proc.returncode})")
            return
    job["status"] = "done"


class _Handler(RangeHandler):
    root: Path = Path(".")

    def _json(self, data, code: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def translate_path(self, path: str) -> str:
        p = urllib.parse.urlparse(path).path
        if p in ("/studio", "/studio.html"):
            return str(STUDIO_DIR / "studio.html")
        return str(Path(super().translate_path(path)))

    def _local_request(self) -> bool:
        """Only this computer's own pages may use the API (not another web site open in the
        browser, and not a DNS-rebinding trick that points a strange name at 127.0.0.1)."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        origin = self.headers.get("Origin")
        local = re.compile(r"https?://(127\.0\.0\.1|localhost)(:\d+)?")
        return host in ("127.0.0.1", "localhost") and (origin is None or bool(local.fullmatch(origin)))

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        if u.path.startswith("/api/") and not self._local_request():
            return self._json({"error": "forbidden"}, 403)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/api/search":
            from .io import library as L
            rows = L.catalogue(self.root / "data" / "openscore")
            words = (q.get("q", [""])[0]).split()
            hits = L.search(rows, words) if words else []
            existing = set(_piece_ids(self.root))
            have = {P.read_json(P.piece_dir(pid, self.root) / "config.json").get("score", {}).get("openscore_id")
                    for pid in existing}
            return self._json([{"id": r["id"], "composer": r["composer"], "name": r["name"],
                                "in_library": r["id"] in have,
                                "prefix": suggest_prefix(r, existing)} for r in hits[:40]])
        if u.path == "/api/incoming":
            inc = self.root / "incoming"
            files = sorted(f for f in inc.rglob("*") if f.is_file() and f.suffix.lower() in AUDIO_EXT
                           and "clean_test" not in f.relative_to(inc).parts) if inc.exists() else []   # skip before/after samples
            used = set()
            for pid in _piece_ids(self.root):
                cfg = P.read_json(P.piece_dir(pid, self.root) / "config.json")
                for a in [cfg.get("audio") or {}] + list((cfg.get("recordings") or {}).values()):
                    if a.get("path"):
                        used.add(Path(a["path"]).name)
            return self._json([{"path": str(f.relative_to(self.root)), "name": f.name,
                                "mb": round(f.stat().st_size / 1e6, 1), "used": f.name in used} for f in files])
        if u.path == "/api/pieces":
            return self._json(_piece_ids(self.root))
        m = re.fullmatch(r"/api/jobs/(\d+)", u.path)
        if m:
            job = _jobs.get(int(m.group(1)))
            if not job:
                return self._json({"error": "no such job"}, 404)
            try:
                since = max(0, int(q.get("since", ["0"])[0]))
            except ValueError:
                return self._json({"error": "since must be a number"}, 400)
            with _lock:
                return self._json({"status": job["status"], "log": job["log"][since:], "next": len(job["log"]),
                                   "prefix": job["prefix"]})
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        if urllib.parse.urlparse(self.path).path != "/api/add":
            return self._json({"error": "unknown"}, 404)
        if not self._local_request():
            return self._json({"error": "forbidden"}, 403)
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            work, prefix = str(body["id"]), str(body["prefix"])
            audio = [str(a) for a in body.get("audio", [])]
            credit = str(body.get("credit", "")).strip()
        except (KeyError, ValueError, TypeError):
            return self._json({"error": "need id, prefix and audio", "code": "bad_request"}, 400)
        if not re.fullmatch(r"[A-Za-z0-9]{1,20}", work):
            return self._json({"error": "unknown work", "code": "bad_request"}, 400)
        if not re.fullmatch(r"[a-z0-9][a-z0-9_]{1,40}", prefix):
            return self._json({"error": "the short name may use only a-z, 0-9 and _", "code": "bad_name"}, 400)
        if any(pid == prefix or pid.startswith(prefix + "_") for pid in _piece_ids(self.root)):
            return self._json({"error": f"'{prefix}' is already used; choose another short name", "code": "name_taken"}, 400)
        for a in audio:                  # only files inside incoming/
            if not (self.root / a).resolve().is_relative_to((self.root / "incoming").resolve()) or not (self.root / a).is_file():
                return self._json({"error": f"not a file in incoming/: {a}", "code": "bad_file"}, 400)
        base = [sys.executable, "-m", "quartet_companion.cli", "--root", str(self.root)]
        add = base + ["library", "add", work, "--prefix", prefix] + (["--audio", *audio] if audio else []) + \
            (["--audio-credit", credit] if credit else [])
        site = base + ["site", "--only", prefix]
        with _lock:
            job_id = len(_jobs) + 1
            _jobs[job_id] = {"status": "running", "log": [], "prefix": prefix}
        threading.Thread(target=_run_job, args=(job_id, self.root, [add, site]), daemon=True).start()
        return self._json({"job": job_id})


def _piece_ids(root: Path) -> list[str]:
    return sorted(p.parent.name for p in (root / "pieces").glob("*/config.json"))


def serve(root: Path, port: int = 8765) -> None:
    site = root / "site"
    if not (site / "index.html").exists():
        from .site import build_site
        build_site(root)

    class Handler(_Handler):
        pass
    Handler.root = root

    def make(*a, **k):
        return Handler(*a, directory=str(site), **k)
    try:
        srv = QuietServer(("127.0.0.1", port), make)
    except OSError:
        raise SystemExit(f"Port {port} is already in use (is `qc serve` or `qc studio` running in another "
                         f"terminal window?). Use another port: qc studio --port {port + 1}")
    print(f"Open http://127.0.0.1:{port}/studio.html to add pieces, http://127.0.0.1:{port}/ for the player "
          "(Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
