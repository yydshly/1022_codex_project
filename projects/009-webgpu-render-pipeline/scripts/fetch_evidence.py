"""Fetch pinned upstream text for research; keep third-party source in ignored _upstream/."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
REPO = "vibegameengine/web-starter-kit-webgpu-pipline"
COMMIT = "ca576b601bf84527102f1768372aa8cd96a3c55a"
CACHE = ROOT / "_upstream" / f"webgpu-{COMMIT[:7]}"


def get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Codex-project-research", "Accept-Encoding": "identity"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def main() -> None:
    api = f"https://api.github.com/repos/{REPO}"
    metadata = json.loads(get(api))
    head = json.loads(get(f"{api}/commits/main"))
    commit = json.loads(get(f"{api}/commits/{COMMIT}"))
    tree = json.loads(get(f"{api}/git/trees/{COMMIT}?recursive=1"))
    assert not tree.get("truncated"), "Upstream tree is truncated"
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "tree.json").write_text(json.dumps(tree, indent=2), encoding="utf-8")
    paths = []
    for entry in tree["tree"]:
        path = entry["path"]
        if entry["type"] != "blob":
            continue
        include = (
            path in {"package.json", "package-lock.json", "vite.config.ts", "vite.webgiya.config.ts", "tsconfig.json", ".gitignore", "index.html"}
            or path.startswith("docs/") and path.endswith((".md", ".diff"))
            or path.startswith("src/") and path.endswith((".ts", ".tsx")) and "/bvh/" not in path and not path.startswith("src/dashboard/")
            or path.startswith("scripts/check-") and path.endswith(".mjs")
        )
        if include:
            paths.append(path)

    def fetch(path: str) -> dict:
        target = CACHE / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(get(f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}"))
        content = target.read_bytes()
        text = content.decode("utf-8")
        return {"path": path, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content), "lines": len(text.splitlines()), "url": f"https://github.com/{REPO}/blob/{COMMIT}/{path}"}

    files, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, path): path for path in paths}
        for future in concurrent.futures.as_completed(futures):
            try:
                files.append(future.result())
            except Exception as error:
                errors.append({"path": futures[future], "error": str(error)})
    license_paths = [entry["path"] for entry in tree["tree"] if entry["type"] == "blob" and Path(entry["path"]).name.lower().startswith(("license", "licence", "copying"))]
    source = {
        "repository": f"https://github.com/{REPO}", "owner": metadata["owner"]["login"],
        "commit": COMMIT, "commit_date": commit["commit"]["committer"]["date"],
        "commit_message": commit["commit"]["message"], "main_at_review": head["sha"],
        "review_date": "2026-10-21", "license_api": metadata["license"], "license_files": license_paths,
        "license_observation": "固定版本未找到仓库级许可证；公开可读不等于授予复用许可。本研究链接源码，不收录完整上游代码或素材。",
        "upstream_execution": "not_run", "homepage": metadata.get("homepage"),
        "research_method": "固定提交的源码与作者文档审阅；静态研究展示另行本地验证。清单不是上游画质或性能实测。",
        "tree_complete": True, "tree_blob_count": sum(x["type"] == "blob" for x in tree["tree"]),
        "text_file_count": len(files), "files": sorted(files, key=lambda item: item["path"]), "fetch_errors": errors,
    }
    (PROJECT / "SOURCE.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"cache": str(CACHE), "files": len(files), "errors": errors, "main": head["sha"], "licenses": license_paths}, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
