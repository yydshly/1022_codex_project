# Historical inspection excerpt: search/prepare and helpers only.
# No CLI or NotebookLM generate/download entry points are included.
# See README.md for original path, hashes, prerequisites and limitations.
"""Europe PMC adapter for a real aquatic-toxicology reproduction.

Search/download is an addition to this study. NotebookLM upload and artifact
download call the unchanged upstream APD functions. No public publishing occurs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from run_apd import PROJECT, configure

config = configure()
from apd.db import get_paper, init_db, upsert_paper

API = "https://www.ebi.ac.uk/europepmc/webservices/rest"
PERIOD = "2026-43"
SOURCE_DIR = config.DATA_DIR / "aquatic-toxicology"
RESULTS = PROJECT / "results"
QUERY = ('(TITLE_ABS:"aquatic toxicity" OR TITLE_ABS:ecotoxicology OR '
         '(TITLE_ABS:zebrafish AND TITLE_ABS:toxicity) OR '
         '(TITLE_ABS:fish AND TITLE_ABS:PFOS)) AND OPEN_ACCESS:Y '
         'AND FIRST_PDATE:[2024-01-01 TO 2026-10-21]')
DEFAULT_SELECTION = ["PMC13162690", "PMC11851982", "PMC10819493"]


def session():
    client = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    client.mount("https://", HTTPAdapter(max_retries=retry))
    client.headers["User-Agent"] = "APD-AquaticToxicology-Reproduction/1.0"
    return client


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def plain(text):
    return html.unescape(re.sub(r"<[^>]+>", "", html.unescape(text or "")))


def metadata(client, query, limit=30):
    response = client.get(f"{API}/search", params={
        "query": query, "format": "json", "resultType": "core", "pageSize": limit,
    }, timeout=(15, 60))
    response.raise_for_status()
    return response.json()


def search(limit):
    data = metadata(session(), QUERY, limit)
    write_json(SOURCE_DIR / "search-raw.json", data)
    fields = ["id", "source", "pmcid", "doi", "pubYear", "license", "isOpenAccess"]
    report = {
        "queried_at": datetime.now(timezone.utc).isoformat(), "provider": "Europe PMC REST API",
        "query": QUERY, "hit_count": data["hitCount"],
        "screening": "Pilot selection: fish PFOS/PFAS toxicity, original research, accessible licensed full text; not a systematic review.",
        "candidates": [dict({k: paper.get(k) for k in fields}, title=plain(paper.get("title")))
                       for paper in data["resultList"]["result"]],
    }
    write_json(RESULTS / "aquatic-search.json", report)
    print(f"Europe PMC: {report['hit_count']} hits; saved {len(report['candidates'])} candidates.")
    for paper in report["candidates"][:8]:
        print(f"{paper['pmcid']} | {paper['pubYear']} | {paper['title']}")


def prepare(pmcids):
    init_db()
    client = session()
    papers = []
    for pmcid in pmcids:
        if not re.fullmatch(r"PMC\d+", pmcid):
            raise ValueError(f"Invalid PMCID: {pmcid}")
        candidates = metadata(client, pmcid, 5)["resultList"]["result"]
        paper = next(p for p in candidates if p.get("pmcid") == pmcid)
        if paper.get("isOpenAccess") != "Y":
            raise ValueError(f"Not marked open access: {pmcid}")
        source = SOURCE_DIR / pmcid
        source.mkdir(parents=True, exist_ok=True)
        write_json(source / "metadata.json", paper)
        xml_response = client.get(f"{API}/{pmcid}/fullTextXML", timeout=(15, 60))
        xml_response.raise_for_status()
        (source / "article.xml").write_bytes(xml_response.content)
        tree = ET.fromstring(xml_response.content)
        pdf_names = [element.attrib.get("{http://www.w3.org/1999/xlink}href", "")
                     for element in tree.iter("self-uri")]
        pdf_name = next((name for name in pdf_names if re.fullmatch(r"[a-z]+-\d+-\d+\.pdf", name)), None)
        if not pdf_name:
            raise ValueError(f"No supported publisher PDF name in JATS for {pmcid}: {pdf_names}")
        # Publisher-hosted open-access PDF; no challenge bypass or login is used.
        journal = pdf_name.split("-")[0]
        stem = Path(pdf_name).stem
        pdf_url = f"https://mdpi-res.com/d_attachment/{journal}/{stem}/article_deploy/{pdf_name}"
        destination = config.PDF_DIR / "weekly" / PERIOD / f"{pmcid}.pdf"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            response = client.get(pdf_url, timeout=(15, 90))
            response.raise_for_status()
            if not response.content.startswith(b"%PDF-"):
                raise ValueError(f"Response is not a PDF: {pmcid}")
            destination.write_bytes(response.content)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        record = {
            "paper_id": pmcid, "title": plain(paper["title"]), "doi": paper.get("doi"),
            "pmid": paper.get("id"), "year": paper.get("pubYear"),
            "authors": paper.get("authorString"), "license": paper.get("license"),
            "article_url": f"https://europepmc.org/articles/{pmcid}", "pdf_url": pdf_url,
            "pdf_path": str(destination.relative_to(PROJECT)).replace("\\", "/"),
            "pdf_bytes": destination.stat().st_size, "pdf_sha256": digest,
            "source_abstract": plain(paper.get("abstractText")),
            "source_abstract_provenance": "Europe PMC indexed author abstract; not a NotebookLM-generated result.",
        }
        # hf_url is the legacy upstream field; this adapter stores the actual article URL.
        previous = get_paper(pmcid)
        status = previous.status if previous and previous.pdf_sha256 == digest else config.Status.PDF_OK
        upsert_paper(paper_id=pmcid, week_id=PERIOD, title=record["title"],
                     hf_url=record["article_url"], pdf_url=pdf_url,
                     pdf_path=str(destination), pdf_sha256=digest, status=status)
        papers.append(record)
        write_json(RESULTS / "aquatic-papers.json", {
            "prepared_at": datetime.now(timezone.utc).isoformat(), "period": PERIOD,
            "topic": "Aquatic toxicology: PFOS/PFAS effects in fish",
            "selection_type": "Three-paper pilot; not an exhaustive or systematic review.",
            "papers": papers,
        })
        print(f"PDF_OK | {pmcid} | {destination.stat().st_size} bytes | {record['title']}", flush=True)
