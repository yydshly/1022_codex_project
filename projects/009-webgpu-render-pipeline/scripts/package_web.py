"""Package canonical research media/documents for a standalone, buildless static page."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile

from build_research import generate
from build_explainer import generate_explainer
from build_overview import generate_overview

PROJECT = Path(__file__).resolve().parents[1]


def archive_bytes(files: list[Path]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(files):
            entry = zipfile.ZipInfo(file.relative_to(PROJECT).as_posix(), date_time=(2026, 10, 21, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, file.read_bytes())
    return buffer.getvalue()


def main(check: bool) -> dict:
    summary = generate(check)
    explanation = generate_explainer(check)
    overview = generate_overview(check)
    runtime_manifest = PROJECT / "web/live/build-info.json"
    assert runtime_manifest.is_file(), "Build the real upstream demo first: python projects/009-webgpu-render-pipeline/scripts/build_runtime.py"
    runtime = json.loads(runtime_manifest.read_text(encoding="utf-8"))
    for item in runtime["files"]:
        file = (runtime_manifest.parent / item["path"]).resolve()
        assert file.is_relative_to(runtime_manifest.parent.resolve()) and file.is_file(), item["path"]
        assert hashlib.sha256(file.read_bytes()).hexdigest() == item["sha256"], f"Runtime file differs: {item['path']}"
    media = json.loads((PROJECT / "media.json").read_text(encoding="utf-8"))
    for item in media:
        original = PROJECT / item["path"]
        assert original.is_file() and hashlib.sha256(original.read_bytes()).hexdigest() == item["sha256"], item["path"]
    overview_images = [PROJECT / "assets" / name for name in ("project-overview.png", "overview-entry-desktop.png", "overview-entry-mobile.png")]
    overview_images += sorted((PROJECT / "assets").glob("deployed-*.png"))
    assets = [PROJECT / item["path"] for item in media] + sorted((PROJECT / "assets").glob("*.svg")) + overview_images + sorted((PROJECT / "assets/runtime").glob("*.png"))
    documents = list(PROJECT.glob("*.md"))
    json_files = [PROJECT / name for name in ("SOURCE.json", "capabilities.json", "scenes.json", "parameters.json", "media.json", "evidence.json", "verification.json", "explain.json", "overview.json")]
    if (PROJECT / "deployment-verification.json").is_file():
        json_files.append(PROJECT / "deployment-verification.json")
    copies = [(file, PROJECT / "web" / file.relative_to(PROJECT)) for file in assets]
    copies += [(file, PROJECT / "web/downloads" / file.name) for file in documents + json_files]
    runtime_records = [PROJECT / "runtime" / name for name in ("SOURCES.json", "verification.json", "screenshots.json")]
    assert all(file.is_file() for file in runtime_records), "Missing runtime source or verification record"
    verified = json.loads(runtime_records[1].read_text(encoding="utf-8"))
    assert verified["status"] == "passed" and verified["upstream_commit"] == runtime["repositories"]["upstream"]["commit"], "Runtime verification does not match pinned source"
    assert all(verified.get("scenes", {}).get(scene, {}).get("status") == "passed" for scene in ("cornell", "midsee-village", "beach", "forest")), "All four bundled scenes need explicit runtime verification"
    screenshots = json.loads(runtime_records[2].read_text(encoding="utf-8"))["screenshots"]
    for item in screenshots:
        file = (PROJECT / item["path"]).resolve()
        assert file.is_relative_to((PROJECT / "assets/runtime").resolve()), item["path"]
        assert file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest() == item["sha256"], item["path"]
    copies += [(file, PROJECT / "web/downloads/runtime" / file.name) for file in runtime_records]
    for source, target in copies:
        if check:
            assert target.is_file() and source.read_bytes() == target.read_bytes(), f"Published copy differs: {target}"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    archive = archive_bytes(assets + documents + json_files + runtime_records)
    archive_path = PROJECT / "web/downloads/research-bundle.zip"
    if check:
        assert archive_path.is_file() and archive_path.read_bytes() == archive, "Research archive differs"
    else:
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.write_bytes(archive)
    return {**summary, **explanation, **overview, "packaged_files": len(copies) + 1, "runtime_files": len(runtime["files"]) + 1, "archive_bytes": len(archive), "original_media_hashes": "verified"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(main(args.check), ensure_ascii=False))
