"""Static file server with HTTP range support (browsers need it to jump around in audio)."""
from __future__ import annotations

import http.server
import io
import os
import re


CHUNK = 4 * 1024 * 1024        # bytes per open-ended range answer (a whole-work file is 30-60 MB)


LOCAL_HOSTS = ("127.0.0.1", "localhost")


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        # Only pages opened as 127.0.0.1/localhost may read the files: a strange web site can
        # point its own name at 127.0.0.1 (DNS rebinding) and read the private recordings.
        host = (self.headers.get("Host") or "127.0.0.1").rsplit(":", 1)[0]
        if host not in LOCAL_HOSTS:
            self.send_error(403)
            return None
        rng, path = self.headers.get("Range"), self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        if not m:
            return super().send_head()
        a = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2) or 0))
        b = int(m.group(2)) if (m.group(1) and m.group(2)) else size - 1
        if m.group(1) and not m.group(2):
            b = a + CHUNK - 1        # "from here to the end": send a part; the browser asks for more
        b = min(b, size - 1)
        if a > b:
            self.send_error(416)
            return None
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


class QuietServer(http.server.ThreadingHTTPServer):
    """When the browser stops a download halfway (it does this all the time with audio:
    after a jump it asks for another part of the file), the connection closes early.
    That is normal, so do not print an error for it."""
    daemon_threads = True

    def handle_error(self, request, client_address):
        import sys
        if isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError)):
            return
        super().handle_error(request, client_address)
