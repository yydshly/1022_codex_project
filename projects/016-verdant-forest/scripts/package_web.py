"""Package the attributed forest evidence and verify the numbered static site."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
from urllib.parse import unquote, urlsplit

PROJECT = Path(__file__).resolve().parents[1]
WEB = PROJECT / "web"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.fragments: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            identity = values["id"]
            if identity in self.ids:
                raise ValueError(f"Duplicate HTML id: {identity}")
            self.ids.add(identity)
        if tag == "img" and values.get("src") and not values.get("alt"):
            raise ValueError("Every image needs descriptive alt text.")
        for name in ("href", "src"):
            value = values.get(name)
            if not value:
                continue
            if value.startswith("#"):
                self.fragments.append(value[1:])
            else:
                self.refs.append(value)


def package(check: bool = False) -> None:
    manifest = json.loads((PROJECT / "assets/source-manifest.json").read_text(encoding="utf-8"))
    files = [(PROJECT / item["path"], WEB / item["path"], item["sha256"]) for item in manifest["files"]]
    for source, target in ((PROJECT / "assets/source-manifest.json", WEB / "assets/source-manifest.json"),
                           (PROJECT / "assets/understanding-overview.png", WEB / "assets/understanding-overview.png"),
                           (PROJECT / "assets/overview-prompt.txt", WEB / "assets/overview-prompt.txt"),
                           (PROJECT / "assets/overview.json", WEB / "assets/overview.json"),
                           (PROJECT / "THIRD_PARTY_NOTICES.md", WEB / "assets/THIRD_PARTY_NOTICES.md")):
        files.append((source, target, digest(source)))
    for source, target, expected in files:
        if not source.is_file() or digest(source) != expected:
            raise ValueError(f"Canonical source hash mismatch: {source}")
        if not check:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        if not target.is_file() or digest(target) != expected:
            raise ValueError(f"Published asset missing or modified: {target}")

    capture = json.loads((PROJECT / "assets/evidence/browser-capture.json").read_text())
    for filename, frame in (("forest-floor.png", 240), ("canopy-start.png", 750), ("canopy.png", 840)):
        record = next(item for item in capture["timings"] if item["frame"] == frame)
        if digest(PROJECT / "assets/upstream" / filename) != record["sha256"]:
            raise ValueError(f"Image does not match upstream browser capture ledger: {filename}")
    if capture["info"]["objects"]["trees"] != 7155:
        raise ValueError("Review the documented forest statistics against upstream evidence.")
    film = json.loads((PROJECT / "assets/evidence/film-capture.json").read_text())
    if film["laptopCapture"]["frames"] != 720 or film["laptopCapture"]["wallSeconds"] != 405.08:
        raise ValueError("Review the documented film capture evidence.")
    overview = json.loads((PROJECT / "assets/overview.json").read_text(encoding="utf-8"))
    if digest(PROJECT / overview["image"]["path"]) != overview["image"]["sha256"]:
        raise ValueError("Summary image does not match its generation record.")
    for reference in overview["references"]:
        if digest(PROJECT / reference["path"]) != reference["sha256"]:
            raise ValueError(f"Summary image reference changed: {reference['path']}")

    parser = References()
    parser.feed((WEB / "index.html").read_text(encoding="utf-8"))
    for fragment in parser.fragments:
        if fragment not in parser.ids:
            raise ValueError(f"Unresolved section link: #{fragment}")
    for reference in parser.refs:
        parts = urlsplit(reference)
        if parts.scheme or parts.netloc or reference == "../":
            continue
        target = (WEB / unquote(parts.path)).resolve()
        if not target.is_relative_to(WEB.resolve()) or not target.is_file():
            raise ValueError(f"Local resource escapes the publish directory or is missing: {reference}")
    for script in ("app.js", "data.js"):
        if not (WEB / script).is_file():
            raise ValueError(f"Missing script: {script}")
    print(f"{'Verified' if check else 'Packaged'} {len(files)} source/credit files; image ledgers, claims and local references passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        package(args.check)
    except (ValueError, OSError, KeyError, StopIteration) as exc:
        parser.exit(1, f"Forest packaging failed: {exc}\n")
