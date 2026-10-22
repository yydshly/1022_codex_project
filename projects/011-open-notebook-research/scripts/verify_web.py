"""Check the actual static archive, downloads and optional HTTP responses."""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import urlopen
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.urls.append(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", help="Optional local preview origin")
    args = parser.parse_args()
    raw = (WEB / "data.js").read_text(encoding="utf-8")
    data = json.loads(raw.split("window.RESEARCH_DATA = ", 1)[1].rstrip().removesuffix(";"))
    refs = References()
    refs.feed((WEB / "index.html").read_text(encoding="utf-8"))
    refs.urls += [p["pdf"] for p in data["papers"]]
    refs.urls += [a["download"] for a in data["answers"]]
    refs.urls += [d["href"] for d in data["downloads"]]
    page_counts = {"PMC13162690": 17, "PMC11851982": 19, "PMC10819493": 15}
    report_checks = []
    for report in data["reports"]:
        refs.feed(report["html"])
        refs.urls += [report[k] for k in ("download", "standalone", "evidenceDownload")]
        refs.urls += [figure["src"] for figure in report["figures"]]
        standalone_refs = References()
        standalone_refs.feed((WEB / report["standalone"]).read_text(encoding="utf-8"))
        refs.urls += [urljoin(report["standalone"], ref) for ref in standalone_refs.urls]
        headings = set(re.findall(r'id="([^"]+)"', report["html"]))
        if not all(item["id"] in headings for item in report["toc"]):
            raise ValueError("Missing report TOC destination")
        if "<script" in report["html"].lower():
            raise ValueError("Unexpected executable report markup")
        raw_report = (ROOT / "results/detailed" / report["file"]).read_text(encoding="utf-8")
        links = re.findall(r"(PMC\d+)\.pdf#page=(\d+)", raw_report)
        for paper_id, page in links:
            if not 1 <= int(page) <= page_counts[paper_id]:
                raise ValueError(f"Invalid PDF page: {paper_id} {page}")
        if not links or len(raw_report) < 5000:
            raise ValueError("Incomplete detailed report")
        if (WEB / report["download"]).read_text(encoding="utf-8") != raw_report:
            raise ValueError("Detailed report download differs from source")
        report_checks.append({"id": report["id"], "characters": len(raw_report), "han_characters": len(re.findall(r"[\u4e00-\u9fff]", raw_report)), "pdf_page_references": len(links), "toc_entries": len(report["toc"])})
    for answer in data["answers"]:
        if "<script" in answer["html"].lower():
            raise ValueError("Unexpected executable markup in answer")
    local = {"index.html"}
    for ref in refs.urls:
        parsed = urlsplit(ref)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        relative = unquote(parsed.path)
        path = (WEB / relative).resolve()
        if not path.is_relative_to(WEB.resolve()) or not path.is_file():
            raise ValueError(f"Missing or out-of-root resource: {ref}")
        local.add(relative)
    if len(data["papers"]) != 3 or len(data["answers"]) != 3 or len(data["reports"]) != 4:
        raise ValueError("Unexpected research inputs/outputs")
    architecture = json.loads((ROOT / "results/evidence/architecture-evidence.json").read_text(encoding="utf-8"))
    observed = architecture["observed_results"]
    if observed["pdf_page_reference_occurrences"] != sum(r["pdf_page_references"] for r in report_checks):
        raise ValueError("Overview citation count differs from reports")
    if observed["extracted_characters_total"] != sum(p["chars"] for p in data["papers"]):
        raise ValueError("Overview text extraction total differs from evidence")
    if observed["complete_model_answers_characters"] != [a["characters"] for a in data["answers"] if a["finishReason"] == "stop"]:
        raise ValueError("Overview model output sizes differ from originals")
    diagram = ET.fromstring((WEB / "assets/research-overview.svg").read_text(encoding="utf-8"))
    if diagram.attrib.get("viewBox") != "0 0 1600 1500":
        raise ValueError("Unexpected diagram dimensions")
    for p in data["papers"]:
        if hashlib.sha256((WEB / p["pdf"]).read_bytes()).hexdigest() != p["sha256"]:
            raise ValueError(f"PDF hash mismatch: {p['id']}")
    archive = WEB / "downloads/research-archive.zip"
    with zipfile.ZipFile(archive) as zf:
        if failed := zf.testzip():
            raise ValueError(f"Corrupt offline archive member: {failed}")
        for p in data["papers"]:
            if zf.read(p["pdf"]) != (WEB / p["pdf"]).read_bytes():
                raise ValueError("Archive PDF changed")
        for relative in sorted(local - {"downloads/research-archive.zip"}):
            if zf.read(relative) != (WEB / relative).read_bytes():
                raise ValueError(f"Archive resource differs: {relative}")
        archive_files = len(zf.namelist())
    http = []
    if args.url:
        if urlsplit(args.url).hostname not in ("127.0.0.1", "localhost"):
            parser.error("This check only targets the local preview")
        for relative in sorted(local):
            with urlopen(urljoin(args.url.rstrip("/") + "/", relative), timeout=30) as response:
                content = response.read()
                if response.status != 200 or content != (WEB / relative).read_bytes():
                    raise ValueError(f"HTTP content mismatch: {relative}")
                http.append({"path": relative, "status": response.status, "sha256": hashlib.sha256(content).hexdigest()})
    report = {"schema_version": 2, "checked_on": "2026-10-22", "static_local_references": len(local), "pdf_hashes_verified": 3, "answer_count": 3, "complete_answer_count": 2, "detailed_reports": report_checks, "archive_members": archive_files, "http": http, "browser_validation": "Recorded separately in web-ui-verification.json", "new_external_model_api_calls": 0, "new_research_agent_analysis": True, "deployment_performed_by_this_check": False, "publication_record": "publication-verification.json"}
    (ROOT / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(local)} local resources, 3 PDF hashes, {archive_files} ZIP members, {len(http)} HTTP responses.")


if __name__ == "__main__":
    main()
