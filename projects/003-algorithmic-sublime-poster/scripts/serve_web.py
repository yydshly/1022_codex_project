"""Serve the static research site with HTTP byte ranges for seekable video."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import shutil


class RangeHandler(SimpleHTTPRequestHandler):
    """Single byte ranges, including suffix ranges; all other routing is stdlib."""

    def send_head(self):
        self.byte_range = None
        path = Path(self.translate_path(self.path))
        requested = self.headers.get("Range")
        if not requested or not path.is_file():
            return super().send_head()
        size = path.stat().st_size
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested.strip())
        if not match or not any(match.groups()) or size == 0:
            return self.invalid_range(size)
        start_text, end_text = match.groups()
        if not start_text:
            suffix = int(end_text)
            if suffix == 0:
                return self.invalid_range(size)
            start, end = max(0, size - suffix), size - 1
        else:
            start = int(start_text)
            end = min(int(end_text), size - 1) if end_text else size - 1
        if start >= size or end < start:
            return self.invalid_range(size)
        try:
            stream = path.open("rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        self.byte_range = (start, end)
        stream.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(path)))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(path.stat().st_mtime))
        self.end_headers()
        return stream

    def invalid_range(self, size):
        self.send_response(416)
        self.send_header("Content-Range", f"bytes */{size}")
        self.send_header("Content-Length", "0")
        self.end_headers()
        return None

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def copyfile(self, source, outputfile):
        if self.byte_range is None:
            return shutil.copyfileobj(source, outputfile)
        remaining = self.byte_range[1] - self.byte_range[0] + 1
        while remaining:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--port", type=int, default=8033)
    parser.add_argument("--bind", default="127.0.0.1")
    args = parser.parse_args()
    directory = Path(args.directory).resolve(strict=True)
    if not directory.is_dir():
        parser.error("--directory must be a folder")
    server = ThreadingHTTPServer((args.bind, args.port), partial(RangeHandler, directory=str(directory)))
    print(f"Serving {directory} at http://{args.bind}:{args.port}/ (video byte ranges enabled)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
