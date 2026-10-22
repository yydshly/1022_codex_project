"""Check release assets, licenses, upstream identity and teaching evidence."""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            assert attributes["id"] not in self.ids, f"duplicate ID: {attributes['id']}"
            self.ids.add(attributes["id"])
        for key in ("href", "src"):
            if key in attributes:
                self.refs.append(attributes[key])

def main():
    page = Page()
    page.feed((WEB / "index.html").read_text(encoding="utf-8"))
    for ref in page.refs:
        parts = urlsplit(ref)
        assert parts.scheme != "javascript", ref
        if parts.scheme or parts.netloc:
            continue
        if parts.path:
            file = (WEB / unquote(parts.path)).resolve()
            assert file.is_relative_to(WEB.resolve()) and file.is_file(), ref
        elif parts.fragment:
            assert parts.fragment in page.ids, ref
    manifest = json.loads((ROOT / "SOURCE.json").read_text(encoding="utf-8"))
    sources = {item["path"]: item for item in json.loads((WEB / "assets/sources.json").read_text(encoding="utf-8"))}
    for item in manifest["files"]:
        raw = (ROOT / "upstream" / item["path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"], item["path"]
        assert sources[item["path"]]["text"] == raw.decode("utf-8"), item["path"]
        assert manifest["commit"] in sources[item["path"]]["url"]
    assert len(sources) == len(manifest["files"]) == 31
    assert (WEB / "assets/LICENSE.upstream.txt").read_bytes() == (ROOT / "upstream/LICENSE").read_bytes()
    for name in ("upstream-reproduction.json", "lab-verification.json"):
        assert (WEB / "assets" / name).read_bytes() == (ROOT / "results" / name).read_bytes(), name
    lab = json.loads((ROOT / "results/lab-verification.json").read_text(encoding="utf-8"))
    assert lab["engineSHA256"] == hashlib.sha256((WEB / "lab-engine.js").read_bytes()).hexdigest()
    assert len(lab["checks"]) == 16 and all(item["status"] == "pass" for item in lab["checks"])
    assert (ROOT / "assets/cover.jpg").read_bytes() == (WEB / "assets/cover.jpg").read_bytes()
    overview = json.loads((ROOT / "assets/overview-generation.json").read_text(encoding="utf-8"))
    for item in overview["files"]:
        raw = (ROOT / "assets" / item["name"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == item["sha256"], item["name"]
        assert raw == (WEB / "assets" / item["name"]).read_bytes(), item["name"]
    assert overview["dimensions"] == [1800, 2600]
    assert (ROOT / "assets/overview-generation.json").read_bytes() == (WEB / "assets/overview-generation.json").read_bytes()
    print(f"OK: {len(page.refs)} HTML references; 31 upstream files; license, current engine and evidence identities match.")

if __name__ == "__main__":
    main()
