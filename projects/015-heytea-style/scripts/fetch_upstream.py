"""Fetch a pinned, attributed research snapshot. Never fetch private study cutouts."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1, sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "d5125372adcc945c2314cfb649c50407379a18ab"
REPO = "https://github.com/Hchen1218/heytea-style"
RAW = f"https://raw.githubusercontent.com/Hchen1218/heytea-style/{COMMIT}/"


def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "heytea-style-research"}), timeout=60) as response:
        return response.read()


def main():
    tree = json.loads(fetch(f"https://api.github.com/repos/Hchen1218/heytea-style/git/trees/{COMMIT}?recursive=1"))["tree"]
    jobs = []
    for item in tree:
        path = item["path"]
        if item["type"] != "blob":
            continue
        if path.startswith("assets/examples/"):
            local = "assets/upstream/" + path.removeprefix("assets/examples/")
            license_name = "CC BY 4.0; embedded third-party marks retain their rights"
        elif path.startswith("examples/desktop-pet/pink-green-flavor-monster-v3/"):
            local = "assets/upstream/pet-v3/" + path.removeprefix("examples/desktop-pet/pink-green-flavor-monster-v3/")
            license_name = "CC BY 4.0"
        elif path in {"README.md", "SKILL.md", "LICENSE", "ASSET-NOTICE.md", "requirements.txt", "assets/desktop-pet-runtime/package.json"} or path.startswith(("references/", "scripts/", "assets/desktop-pet-runtime/src/")):
            local = "upstream/" + path
            license_name = "MIT; see upstream/ASSET-NOTICE.md for references"
        else:
            continue
        jobs.append((path, local, item["sha"], license_name))

    def download(job):
        path, local, blob, license_name = job
        target = ROOT / local
        data = target.read_bytes() if target.is_file() else fetch(RAW + path)
        actual_blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual_blob != blob:
            raise ValueError(f"Upstream blob mismatch: {path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return {"upstream_path": path, "local_path": local, "url": RAW + path,
                "sha256": sha256(data).hexdigest(), "bytes": len(data),
                "license": license_name, "attribution": "heytea-style contributors", "modified": False}

    with ThreadPoolExecutor(max_workers=6) as pool:
        files = sorted(pool.map(download, jobs), key=lambda record: record["local_path"])
    record = {"repository": REPO, "commit": COMMIT, "commit_date": "2026-09-04T07:11:37Z",
              "research_date": "2026-10-22", "files": files,
              "scope": "Public original examples and source only; no private-assets/reference-cutouts"}
    (ROOT / "SOURCE.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "LICENSE.upstream.txt").write_bytes((ROOT / "upstream/LICENSE").read_bytes())
    print(f"Fetched and verified {len(files)} files at {COMMIT[:12]}")


if __name__ == "__main__":
    main()
