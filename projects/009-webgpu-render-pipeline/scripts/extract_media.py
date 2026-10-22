"""Re-extract the two original figures by their documented IDs and verify exact bytes."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
COMMIT = "ca576b601bf84527102f1768372aa8cd96a3c55a"
API = "https://api.github.com/repos/vibegameengine/web-starter-kit-webgpu-pipline"


def read(url, accept="application/vnd.github+json"):
    request = urllib.request.Request(url, headers={"User-Agent": "Codex-project-research", "Accept": accept})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def main():
    tree = json.loads(read(f"{API}/git/trees/{COMMIT}?recursive=1"))
    blob = next(item for item in tree["tree"] if item["path"] == "public/lighting-look-development.html")
    text = read(f"{API}/git/blobs/{blob['sha']}", "application/vnd.github.raw+json").decode("utf-8")
    tags = re.findall(r"<img\b[^>]*>", text, re.IGNORECASE)
    records = json.loads((PROJECT / "media.json").read_text(encoding="utf-8"))
    for record in records:
        tag = next(tag for tag in tags if f'id="{record["html_id"]}"' in tag)
        match = re.search(r'src="data:image/[^;]+;base64,([^\"]+)"', tag)
        data = base64.b64decode(match[1])
        assert hashlib.sha256(data).hexdigest() == record["sha256"], record["path"]
        target = PROJECT / record["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"Verified and extracted {len(records)} unchanged upstream figures.")


if __name__ == "__main__":
    main()
