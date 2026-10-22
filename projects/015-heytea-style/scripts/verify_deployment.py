"""Compare every public page file to this checkout's packaged bytes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def verify(url, commit, run_id):
    files = sorted(path for path in (ROOT / "web").rglob("*") if path.is_file())
    nonce = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")

    def check(path):
        relative = path.relative_to(ROOT / "web").as_posix()
        expected = sha256(path.read_bytes()).hexdigest()
        request = Request(url.rstrip("/") + "/" + quote(relative) + "?verify=" + commit[:12] + "&check=" + nonce,
                          headers={"User-Agent": "heytea-style-deployment-verification", "Cache-Control": "no-cache", "Accept-Encoding": "gzip"})
        with urlopen(request, timeout=90) as response:
            digest = sha256()
            total = 0
            stream = gzip.GzipFile(fileobj=response) if response.headers.get("Content-Encoding") == "gzip" else response
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                total += len(chunk)
            actual = digest.hexdigest()
            if response.status != 200 or actual != expected:
                raise ValueError(f"Published file differs: {relative}, HTTP {response.status}, expected {expected}, actual {actual}")
            print(f"Verified {relative}", flush=True)
            return {"path": relative, "url": request.full_url, "http_status": response.status, "bytes": total,
                    "sha256": actual, "matches_local": actual == expected}

    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(check, files))
    report = {"date": "2026-10-22", "checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "passed", "published_and_verified": True,
              "url": url.rstrip("/") + "/", "content_commit": commit,
              "workflow_run_id": run_id,
              "workflow_url": f"https://github.com/yydshly/1022_codex_project/actions/runs/{run_id}",
              "files_checked": len(results), "all_http_200": True, "all_sha256_match": True,
              "guide_image": "assets/capability-overview.png", "files": results,
              "browser_verification": "public-browser-verification.json",
              "limits": ["No new upstream poster/character generation", "No native Electron runtime execution"]}
    (ROOT / "deployment-verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key != "files"}, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://yydshly.github.io/1022_codex_project/015-heytea-style/")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    args = parser.parse_args()
    verify(args.url, args.commit, args.run_id)
