"""Package and validate the static SparkVSR understanding page; stdlib only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse
import csv
import hashlib
import io
import json
import shutil
import struct

PROJECT = Path(__file__).resolve().parents[1]
WEB = PROJECT / "web"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def artifacts():
    manifest = json.loads((PROJECT / "assets/manifest.json").read_text(encoding="utf-8"))
    guide = PROJECT / "assets/sparkvsr-overview.png"
    assert sha(guide) == manifest["sha256"], "Guide differs from the approved original"
    raw = guide.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", raw[16:24]) == (2400,3970)
    source = json.loads((PROJECT / "source-manifest.json").read_text(encoding="utf-8"))
    for item in source["source_files"]:
        assert sha(PROJECT / item["local_file"]) == item["sha256"], item["local_file"]
    out = io.StringIO(newline="")
    writer = csv.writer(out,lineterminator="\n")
    writer.writerow(["dataset","model","PSNR_dB","CLIP-IQA","DOVER","source"])
    for model, values in source["metrics"].items():
        if not isinstance(values,dict):
            continue
        writer.writerow(["UDM10",model,format(values["PSNR"],".2f"),format(values["CLIP-IQA"],".4f"),format(values["DOVER"],".4f"),source["paper"]+"#S4.T1"])
    return {
        "assets/sparkvsr-overview.png":guide.read_bytes(),
        "assets/manifest.json":(PROJECT/"assets/manifest.json").read_bytes(),
        "assets/source-manifest.json":(PROJECT/"source-manifest.json").read_bytes(),
        "assets/LICENSE.upstream.txt":(PROJECT/"source-snapshot/LICENSE.upstream.txt").read_bytes(),
        "downloads/UNDERSTANDING.md":(PROJECT/"UNDERSTANDING.md").read_bytes(),
        "downloads/author-metrics.csv":out.getvalue().encode("utf-8-sig"),
    }

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]
        self.links=[]
        self.images=[]
        self.buttons=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if "id" in attrs: self.ids.append(attrs["id"])
        for key in ("href","src"):
            if attrs.get(key): self.links.append(attrs[key])
        if tag=="img": self.images.append(attrs)
        if tag=="button" and "data-mode" in attrs: self.buttons.append(attrs["data-mode"])

def validate():
    html=(WEB/"index.html").read_text(encoding="utf-8")
    page=Page()
    page.feed(html)
    assert len(page.ids)==len(set(page.ids)), "Duplicate element ids"
    for path in page.links:
        parsed=urlsplit(path)
        if parsed.scheme or parsed.netloc or path=="../": continue
        if parsed.path:
            target=(WEB/unquote(parsed.path)).resolve()
            assert target.is_relative_to(WEB.resolve()), path
            assert target.is_file(), path
        if not parsed.path and parsed.fragment:
            assert parsed.fragment in page.ids, path
    assert page.images and all(image.get("alt") for image in page.images)
    assert set(page.buttons)=={"none","nbp","pisa"}
    for required in ["research-summary","principle","effects","reuse","scenarios","limits","sources","posterDialog"]:
        assert required in page.ids, required
    for required in ["关键帧审核","单图修复与时序传播","暂不深入研究","模型训练、推理、画质","作者论文"]:
        assert required in html or required in (PROJECT/"README.md").read_text(encoding="utf-8"), required
    return {"internal_resources_checked":len(page.links),"images":len(page.images),"metric_modes":page.buttons}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    outputs=artifacts()
    for rel,data in outputs.items():
        target=WEB/rel
        if args.check:
            assert target.is_file() and target.read_bytes()==data, "Stale publication copy: "+rel
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
    result=validate()
    result.update(status="passed",generated_files=len(outputs),guide_sha256=sha(WEB/"assets/sparkvsr-overview.png"))
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
