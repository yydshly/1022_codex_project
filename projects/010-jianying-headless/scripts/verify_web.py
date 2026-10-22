"""Check research identity, generated artifacts and the page's publishing boundary."""
from __future__ import annotations

import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("src", "href"):
            if key in attrs:
                self.references.append(attrs[key])
        if tag == "img":
            assert attrs.get("alt"), "Every research image needs alternative text"


def main() -> None:
    data = json.loads((ROOT / "research.json").read_text(encoding="utf-8"))
    backup = json.loads((ROOT / "backup-record.json").read_text(encoding="utf-8"))
    assert len(data["modes"]) == 3 and len(data["steps"]) == 6
    assert len(data["projects"]) == 4 and len(data["extensions"]) == 8
    assert len(data["questions"]) == 6 and len(data["sources"]) == 9
    assert sum(item["ref_count"] for item in backup["repositories"]) == 67
    assert sum(item["source_file_count"] for item in backup["repositories"]) == 357
    assert sum(item["reachable_commits"] for item in backup["repositories"]) == 187
    assert data["projects"][0]["revision"] == backup["repositories"][0]["head_commit"][:7]
    assert data["projects"][1]["revision"] == backup["repositories"][1]["head_commit"][:7]
    for source in data["sources"]:
        parts = urlsplit(source["url"])
        assert parts.scheme == "https" and parts.netloc == "github.com"
        assert len(parts.path.split("/blob/", 1)[1].split("/", 1)[0]) == 40
    source_ids = {"source-" + source["id"] for source in data["sources"]}
    parser = Document()
    parser.feed((WEB / "index.html").read_text(encoding="utf-8"))
    assert len(parser.ids) == len(set(parser.ids)), "Duplicate DOM IDs"
    for reference in parser.references:
        if reference.startswith("#"):
            assert reference[1:] in set(parser.ids) | source_ids, reference
        elif reference.startswith("./"):
            assert (WEB / reference.split("#", 1)[0]).is_file(), reference
    for forbidden in ("_upstream", "backups", ".git"):
        assert not (WEB / forbidden).exists(), f"Private data entered web/: {forbidden}"
    assert not list(WEB.rglob("*.bundle")) and not list(WEB.rglob("*.zip"))
    ET.parse(ROOT / "assets/research-overview.svg")
    spec = importlib.util.spec_from_file_location("package_research_web", ROOT / "scripts/package_web.py")
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)
    for path, content in package.outputs().items():
        assert path.read_bytes() == content, f"Generated file is stale: {path}"
    standalone = (WEB / "standalone.html").read_text(encoding="utf-8")
    assert '<script src=' not in standalone and '<link rel="stylesheet"' not in standalone
    assert 'src="./assets/research-overview.svg"' not in standalone
    print("Research page verified: 3 modes, 6 steps, 4 projects, 8 proposals, 6 FAQs, 9 pinned sources; offline assets and private-backup boundary OK")


if __name__ == "__main__":
    main()
