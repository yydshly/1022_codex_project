"""Verify gallery integrity, prompt assembly and local HTTP resources (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import urlopen

PROJECT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"src", "href"} and value and not value.startswith(("#", "../")) and not urlsplit(value).scheme:
                self.links.add(unquote(urlsplit(value).path))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Published local HTTP project URL, including trailing slash")
    args = parser.parse_args()
    manifest = json.loads((PROJECT / "media.json").read_text(encoding="utf-8"))
    assert len(manifest["upstream_samples"]) == 8
    assert len(manifest["demo_outputs"]) == 7
    assert len(manifest["rejected_outputs"]) == 3
    assert len(manifest["study_guides"]) == 1
    original = (PROJECT / "prompts/original.zh-CN.md").read_text(encoding="utf-8").strip()
    prompts = sorted((PROJECT / "prompts").glob("*.txt"))
    assert len(prompts) == 10
    for prompt in prompts:
        text = prompt.read_text(encoding="utf-8")
        assert text.startswith(original), f"Source brief changed in {prompt.name}"
        assert text.count("OUTPUT MODE:") == 1, f"Mode alternatives leaked into {prompt.name}"
    packed_js = (PROJECT / "web/media.js").read_text(encoding="utf-8")
    prompt_entries = json.loads(packed_js.split("\nwindow.PANEL_PROMPTS = ", 1)[1].strip().removesuffix(";"))
    assert len(prompt_entries) == 11
    expected_paths = {path.relative_to(PROJECT).as_posix() for path in prompts} | {"prompts/original.zh-CN.md"}
    assert {entry["path"] for entry in prompt_entries} == expected_paths
    for entry in prompt_entries:
        assert entry["text"] == (PROJECT / entry["path"]).read_text(encoding="utf-8"), entry["path"]
        if entry["addition"]:
            assert entry["addition"] == entry["text"][len(original):].lstrip("\n"), entry["path"]
    records = [manifest["source"], *manifest["upstream_samples"], *manifest["demo_outputs"], *manifest["rejected_outputs"], *manifest["study_guides"]]
    links = Links()
    links.feed((PROJECT / "web/index.html").read_text(encoding="utf-8"))
    resources = links.links | {record["path"] for record in records}
    resources |= {item.relative_to(PROJECT).as_posix() for item in prompts}
    resources |= {"media.json", "assets/NOTICE.md", "assets/README.md", "assets/upstream/LICENSE.txt", "prompts/original.zh-CN.md"}
    resources |= {guide["prompt"] for guide in manifest["study_guides"]}
    hashes = {record["path"]: record["sha256"] for record in records}
    for resource in sorted(resources):
        path = (PROJECT / "web" / resource).resolve()
        assert path.is_relative_to((PROJECT / "web").resolve()) and path.is_file(), f"Invalid resource {resource}"
        data = path.read_bytes()
        if resource in hashes:
            assert hashlib.sha256(data).hexdigest() == hashes[resource], resource
        if args.base_url:
            with urlopen(urljoin(args.base_url, resource), timeout=15) as response:
                assert response.status == 200, resource
                assert response.read() == data, f"HTTP bytes differ: {resource}"
    print(f"OK: 8 upstream + 7 final + 3 rejected + 1 source + 1 guide; 11 prompt entries match source files; {len(resources)} local resources" + (" and HTTP byte checks." if args.base_url else "."))


if __name__ == "__main__":
    main()
