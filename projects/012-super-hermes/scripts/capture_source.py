"""Fetch a small, pinned MIT-licensed research snapshot; never install the skills."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
REVISION = "ffe2d10042041dcc23325f013e8b7e607e069952"
REPO = "https://github.com/Cranot/super-hermes"
SKILLS = ["prism-scan", "prism-full", "prism-3way", "prism-discover", "prism-reflect"]
LENSES = ["error_resilience", "l12", "optimize", "identity", "deep_scan", "claim", "simulation"]
PATHS = ["README.md", "LICENSE", "install.ps1", "examples/circuit_breaker.py",
         "examples/prism-scan-output.md", "examples/growth-demo.md"]
PATHS += [f"skills/{name}/SKILL.md" for name in SKILLS]
PATHS += [f"skills/prism-scan/references/{name}.md" for name in LENSES]


def fetch(path):
    url = f"https://raw.githubusercontent.com/Cranot/super-hermes/{REVISION}/{path}"
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise RuntimeError("Source capture needs curl with HTTPS certificate validation enabled.")
    content = subprocess.run([curl, "--fail", "--location", "--silent", "--show-error",
                              "--max-time", "30", "--retry", "4", "--retry-all-errors", "--retry-delay", "1", url],
                             check=True, capture_output=True).stdout
    target = ROOT / "web/assets/upstream" / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return {"upstream_path": path, "local_path": target.relative_to(ROOT).as_posix(),
            "url": url, "bytes": len(content), "sha256": sha256(content).hexdigest()}


def main():
    with ThreadPoolExecutor(max_workers=3) as pool:
        files = list(pool.map(fetch, PATHS))
    manifest = {"repository": REPO, "revision": REVISION, "revision_date": "2026-07-27",
                "research_date": "2026-10-22", "timezone": "Asia/Shanghai", "license": "MIT",
                "author": "Cranot", "modifications": "Snapshot bytes preserved without edits.", "files": files}
    (ROOT / "SOURCE.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    documents = {entry["upstream_path"]: (ROOT / entry["local_path"]).read_text(encoding="utf-8-sig") for entry in files}
    (ROOT / "web/source-data.js").write_text("window.UPSTREAM = " + json.dumps(documents, ensure_ascii=False) + ";\n", encoding="utf-8")
    with ZipFile(ROOT / "web/assets/super-hermes-study-kit.zip", "w", ZIP_DEFLATED) as archive:
        for entry in files:
            archive.write(ROOT / entry["local_path"], "super-hermes/" + entry["upstream_path"])
        archive.writestr("RESEARCH-NOTICE.txt", "Research snapshot of Cranot/super-hermes\nCommit: " + REVISION + "\nMIT license included. This archive is not an installer.\n")
    print(f"Captured {len(files)} pinned source files, source-data.js and study ZIP.")


if __name__ == "__main__":
    main()
