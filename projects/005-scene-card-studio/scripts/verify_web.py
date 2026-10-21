"""Verify static page links, packaged bytes and optional HTTP resources."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.resources: set[str] = set()
        self.ids: set[str] = set()
        self.fragments: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                assert value not in self.ids, f"Duplicate id: {value}"
                self.ids.add(value)
            if key in {"href", "src", "data-image"} and value:
                if value.startswith("#"):
                    self.fragments.add(value[1:])
                elif not urlsplit(value).scheme and not value.startswith("../"):
                    self.resources.add(unquote(urlsplit(value).path).removeprefix("./"))


def verify(base_url: str | None = None, report: bool = False) -> dict:
    web = ROOT / "web"
    links = PageLinks()
    links.feed((web / "index.html").read_text(encoding="utf-8"))
    assert links.fragments <= links.ids, links.fragments - links.ids
    script = (web / "data.js").read_text(encoding="utf-8")
    payload = json.loads(script.removeprefix("window.SCENE_CARD = ").strip().removesuffix(";"))
    rules = json.loads((ROOT / "rules/upstream-rules.json").read_text(encoding="utf-8"))
    assert len(payload["systems"]) == 11 and len(payload["profiles"]) == 24
    for system in payload["systems"]:
        assert system["profiles"] == list(rules["expression_profiles_by_system"][system["id"]])
    for prompt in payload["prompts"]:
        relative = prompt["url"].removeprefix("./")
        links.resources.add(relative)
        assert prompt["text"] == (ROOT / relative).read_text(encoding="utf-8"), relative
    media = json.loads((ROOT / "media.json").read_text(encoding="utf-8"))
    assert len(media["assets"]) == 6
    for record in media["assets"]:
        links.resources.add(record["path"])
        assert hashlib.sha256((web / record["path"]).read_bytes()).hexdigest() == record["sha256"]
    study_guide = json.loads((ROOT / "study-guide.json").read_text(encoding="utf-8"))
    links.resources.add("study-guide.json")
    for key in ("image", "prompt"):
        record = study_guide[key]
        links.resources.add(record["path"])
        assert hashlib.sha256((web / record["path"]).read_bytes()).hexdigest() == record["sha256"], record["path"]
    assert len(payload["cases"]) == 2
    for case in payload["cases"]:
        for side in ("before", "after"):
            links.resources.add(case[side]["path"])
        for record in case["evidence"].values():
            links.resources.add(record["path"])
            assert hashlib.sha256((web / record["path"]).read_bytes()).hexdigest() == record["sha256"]
        links.resources.add(case["prompt_path"])
        prompt = json.loads((web / case["evidence"]["prompt-manifest.json"]["path"]).read_text(encoding="utf-8"))["prompts"][0]
        assert hashlib.sha256((web / case["before"]["path"]).read_bytes()).hexdigest() == prompt["sources"][0]["sha256"]
        assert hashlib.sha256((web / case["after"]["path"]).read_bytes()).hexdigest() == prompt["reference_output"]["sha256"]
        assert case["compiled_prompt"] == (ROOT / case["prompt_path"]).read_text(encoding="utf-8") == prompt["compiled_prompt"] + "\n"
    verified = []
    for relative in sorted(links.resources):
        path = (web / relative).resolve()
        assert path.is_relative_to(web.resolve()) and path.is_file(), relative
        content = path.read_bytes()
        if base_url:
            with urlopen(urljoin(base_url, relative), timeout=15) as response:
                assert response.status == 200, relative
                assert response.read() == content, f"HTTP bytes differ: {relative}"
        verified.append({"path": relative, "sha256": hashlib.sha256(content).hexdigest()})
    result = {"checked_date": "2026-10-21", "status": "passed", "local_resource_count": len(verified),
              "http_byte_checks": bool(base_url), "fragment_links": len(links.fragments),
              "prompt_tabs": len(payload["prompts"]), "canonical_profiles": len(payload["profiles"]),
              "compatibility_pairs": sum(len(s["profiles"]) for s in payload["systems"]),
              "upstream_images": len(media["assets"]), "complete_cases": len(payload["cases"]), "study_guide_images": 1, "resources": verified}
    if report:
        browser = ROOT / "browser-checks.json"
        if browser.is_file():
            result["browser"] = json.loads(browser.read_text(encoding="utf-8"))
        (ROOT / "web-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in {"resources", "browser"}}, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url")
    parser.add_argument("--report", action="store_true")
    args = parser.parse_args()
    verify(args.base_url, args.report)
