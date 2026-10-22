"""Verify the public forest page against committed source bytes (stdlib only)."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html import escape
import json
from pathlib import Path
import subprocess
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
PREFIX = "projects/016-verdant-forest/"


def verify(revision: str, base: str, run_url: str, output: Path) -> None:
    revision = subprocess.check_output(["git", "rev-parse", revision], cwd=ROOT).decode().strip()

    def blob(path: str) -> bytes:
        return subprocess.check_output(["git", "show", f"{revision}:{path}"], cwd=ROOT)

    def fetch(url: str) -> tuple[int, bytes]:
        request = Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "Verdant-Forest-Research-Verification"})
        with urlopen(request, timeout=45) as response:
            return response.status, response.read()

    manifest = json.loads(blob(PREFIX + "assets/source-manifest.json"))
    tracked = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", revision, PREFIX + "web/"], cwd=ROOT).decode().splitlines()
    sources = {path.removeprefix(PREFIX + "web/"): path for path in tracked}
    for item in manifest["files"]:
        sources[item["path"]] = PREFIX + item["path"]
    for path in ("assets/source-manifest.json", "assets/understanding-overview.png", "assets/overview-prompt.txt", "assets/overview.json"):
        sources[path] = PREFIX + path
    sources["assets/THIRD_PARTY_NOTICES.md"] = PREFIX + "THIRD_PARTY_NOTICES.md"

    def check(item: tuple[str, str]) -> dict:
        path, source = item
        status, data = fetch(base.rstrip("/") + "/" + path)
        expected = hashlib.sha256(blob(source)).hexdigest()
        actual = hashlib.sha256(data).hexdigest()
        return {"path": path, "status": status, "bytes": len(data), "sha256": actual,
                "expected_sha256": expected, "matches": status == 200 and actual == expected}

    with ThreadPoolExecutor(max_workers=4) as pool:
        files = list(pool.map(check, sorted(sources.items())))
    catalog = json.loads(blob("projects/catalog.json"))
    project = next(item for item in catalog["projects"] if item["id"] == "016")
    navigation_url = base.rstrip("/").rsplit("/", 1)[0] + "/"
    nav_status, nav_data = fetch(navigation_url)
    nav = nav_data.decode("utf-8")
    summary_ok = escape(project["summary"]) in nav
    caption_ok = escape(project["cover_caption"]) in nav
    guide_ok = "./016-verdant-forest/assets/understanding-overview.png" in nav
    page_status, page_data = fetch(base)
    page = page_data.decode("utf-8")
    page_summary_ok = all(text in page for text in ("能力与效果", "可沉淀技术", "后续扩展场景"))
    passed = (all(item["matches"] for item in files) and nav_status == 200 and page_status == 200
              and summary_ok and caption_ok and guide_ok and page_summary_ok)
    report = {"status": "verified" if passed else "mismatch", "content_commit": revision,
              "page_url": base, "actions_run": run_url, "files": files,
              "navigation": {"url": navigation_url, "status": nav_status, "summary_matches": summary_ok,
                             "caption_matches": caption_ok, "generated_guide_present": guide_ok},
              "page_summary": {"status": page_status, "three_topics_present": page_summary_ok},
              "scope": "Public HTTP bytes, generated guide image, navigation summary and captions. Browser interactions are recorded separately; no interactive GPU FPS benchmark."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if not passed:
        failed = [item["path"] for item in files if not item["matches"]]
        raise SystemExit(f"Deployment mismatch: {failed}; navigation/page checks: {report['navigation']}, {report['page_summary']}")
    print(f"Verified {len(files)} public files, source hashes, generated guide and navigation summary: {base}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--base", default="https://yydshly.github.io/1022_codex_project/016-verdant-forest/")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--output", type=Path, default=PROJECT / "deployment-verification.json")
    args = parser.parse_args()
    verify(args.revision, args.base, args.run_url, args.output)
