"""Save selected, byte-identical upstream sources and generate a browser reader."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "a0eb529d393a1cb3ccc564e32b2104e7e75c7a29"
REPO = "https://github.com/AmazingAng/old-coder"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    actual = subprocess.check_output(
        ["git", "-C", str(args.checkout), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != COMMIT:
        raise SystemExit(f"Expected {COMMIT}, got {actual}")
    tracked = subprocess.check_output(
        ["git", "-C", str(args.checkout), "ls-files", "-z"], text=True
    ).split("\0")
    selected = [p for p in tracked if p and (
        p.startswith(("skills/", "demo-rate-limiter/", ".github/workflows/"))
        or p in ("LICENSE", "README.md", "README-zh.md")
    )]
    manifest = []
    reader = []
    for relative in selected:
        source = args.checkout / relative
        raw = source.read_bytes()
        destination = ROOT / "upstream" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
        manifest.append({"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
        reader.append({"path": relative, "text": raw.decode("utf-8"),
                       "url": f"{REPO}/blob/{COMMIT}/{relative}"})
    assets = ROOT / "web/assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "upstream/LICENSE", assets / "LICENSE.upstream.txt")
    (assets / "sources.json").write_text(json.dumps(reader, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata = {"repository": REPO, "commit": COMMIT, "research_date": "2026-10-22",
                "license": "MIT", "files": manifest,
                "selection": "Both skills and all references; full demo; README files; CI workflow; license. No Git metadata or dependencies."}
    (ROOT / "SOURCE.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copyfile(ROOT / "SOURCE.json", assets / "source-manifest.json")
    print(f"Saved {len(manifest)} upstream files at {COMMIT}")


if __name__ == "__main__":
    main()
