"""Verify public Pages bytes against the exact committed source files."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

project = Path(__file__).resolve().parents[1]
repo = project.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base-url", default="https://yydshly.github.io/1022_codex_project/007-dr-aria/")
parser.add_argument("--commit", required=True)
parser.add_argument("--run-url", required=True)
parser.add_argument("--output", type=Path, default=project / "deployment-verification.json")
args = parser.parse_args()
commit = subprocess.check_output(["git", "rev-parse", args.commit], cwd=repo, text=True).strip()

def fetch(url):
    with urlopen(Request(url, headers={"User-Agent": "dr-aria-deployment-check"}), timeout=30) as response:
        return response.status, response.read()

records = []
for path in sorted((project / "web").rglob("*")):
    if not path.is_file():
        continue
    relative = path.relative_to(project / "web").as_posix()
    source = project / relative if relative == "assets/understanding-summary.png" else path
    source_path = source.relative_to(repo).as_posix()
    expected = subprocess.check_output(["git", "show", f"{commit}:{source_path}"], cwd=repo)
    url = urljoin(args.base_url, quote(relative))
    status, actual = fetch(url)
    if status != 200 or actual != expected:
        raise SystemExit(f"Published bytes differ: {relative}")
    records.append({"path": relative, "url": url, "http_status": status,
                    "bytes": len(actual), "sha256": hashlib.sha256(actual).hexdigest(),
                    "matches_commit": True})

home_url = urljoin(args.base_url, "../")
status, home_bytes = fetch(home_url)
home = home_bytes.decode("utf-8")
assert status == 200 and "007-dr-aria/" in home and "角色效果与表达图鉴" in home
assert "./007-dr-aria/assets/understanding-summary.png" in home
report = {"verified_date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
          "status": "passed", "content_commit": commit,
          "workflow_run": args.run_url, "base_url": args.base_url,
          "files": records, "home": {"url": home_url, "http_status": status,
          "project_link": True, "generated_guide": True},
          "scope": "静态页面、资源与引导图的发布字节一致性；没有真实模型调用"}
args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PASS {len(records)} published files match commit; navigation and guide verified.")
