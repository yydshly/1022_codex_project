"""Verify public Pages bytes and the root entry for this project."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
import argparse
import hashlib
import json
import subprocess

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--base-url",default="https://yydshly.github.io/1022_codex_project/")
parser.add_argument("--commit",default=None)
parser.add_argument("--run-url",default="")
args=parser.parse_args()
commit=args.commit or subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
base=args.base_url.rstrip("/")+"/"
folder="017-sparkvsr"
query="?verify="+commit[:12]
def digest(data):return hashlib.sha256(data).hexdigest()
def get(url):
    req=Request(url+query,headers={"User-Agent":"SparkVSR-publication-verification","Cache-Control":"no-cache"})
    with urlopen(req,timeout=45) as response:
        return response.status,response.read()
def check(path):
    rel=path.relative_to(PROJECT/"web").as_posix()
    status,body=get(base+folder+"/"+rel)
    return {"path":rel,"http_status":status,"bytes":len(body),"sha256":digest(body),"expected_sha256":digest(path.read_bytes()),"matches":body==path.read_bytes()}
paths=sorted(p for p in (PROJECT/"web").rglob("*") if p.is_file())
with ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(check,paths))
status,root=get(base)
root=root.decode("utf-8")
catalog=json.loads((ROOT/"projects/catalog.json").read_text(encoding="utf-8"))
entry=next(p for p in catalog["projects"] if p["id"]=="017")
summary=entry["summary"] in root
guide="./017-sparkvsr/assets/sparkvsr-overview.png" in root
project_link='./017-sparkvsr/' in root
passed=all(r["http_status"]==200 and r["matches"] for r in results) and status==200 and summary and guide and project_link
record={"schema_version":1,"checked_at":datetime.now(timezone(timedelta(hours=8))).isoformat(),"status":"passed" if passed else "failed","project_url":base+folder+"/","root_url":base,"content_commit":commit,"actions_run":args.run_url,"files":results,"root":{"http_status":status,"summary_matches":summary,"guide_present":guide,"project_link_present":project_link},"scope":"Static publication and original guide bytes. Does not verify model inference, quality, memory or speed."}
(PROJECT/"deployment-verification.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
print(json.dumps({"status":record["status"],"files":len(results),"root":record["root"],"url":record["project_url"]},ensure_ascii=False))
raise SystemExit(0 if passed else 1)
