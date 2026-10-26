"""Static file server with HTTP range support (browsers need it to jump around in audio)."""
from __future__ import annotations

import http.server
import io
import os
import re


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        rng, path = self.headers.get("Range"), self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        if not m:
            return super().send_head()
        a = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2) or 0))
        b = int(m.group(2)) if (m.group(1) and m.group(2)) else size - 1
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
