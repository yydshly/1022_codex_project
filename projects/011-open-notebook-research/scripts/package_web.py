"""Build the read-only archive from local evidence using Python stdlib only."""
from __future__ import annotations

import argparse
import hashlib
from html import escape
import io
import json
import posixpath
from pathlib import Path
import re
from urllib.parse import urlsplit
import zipfile
from report_renderer import render as render_report

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
SOURCE_IDS = {
    "vhshfa8xv8wi6xozjagl": "PMC13162690",
    "bezlz9t8sr5pu12stjfu": "PMC11851982",
    "i8m54onbhh6bq0q0w7sd": "PMC10819493",
}


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def inline(text):
    # Raw HTML is escaped. The only generated links are our known source IDs.
    text = escape(text)
    text = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)
    for source, paper in SOURCE_IDS.items():
        text = text.replace(f"[source:{source}]", f'<a class="source-ref" href="#paper-{paper}" title="查看 {paper} 的原始论文">[来源：{paper}]</a>')
    return text


def markdown(text):
    # Deliberately small renderer for these preserved Markdown outputs.
    result, paragraph, listing = [], [], []

    def flush():
        if paragraph:
            result.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()
        if listing:
            result.append("<ol>" + "".join("<li>" + inline(item) + "</li>" for item in listing) + "</ol>")
            listing.clear()

    for line in text.splitlines():
        if not line.strip():
            flush()
        elif match := re.match(r"^(#{1,6})\s+(.+)$", line):
            flush()
            level = min(len(match[1]) + 1, 6)
            result.append(f"<h{level}>" + inline(match[2]) + f"</h{level}>")
        elif match := re.match(r"^\d+\.\s+(.+)$", line):
            if paragraph:
                flush()
            listing.append(match[1])
        else:
            if listing:
                flush()
            paragraph.append(line.strip())
    flush()
    return "\n".join(result)


def expected_files():
    files = {}
    manifest = read_json("results/import-manifest.json")
    for record in manifest["records"]:
        path = ROOT / record["path"]
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != record["sha256"]:
            raise ValueError(f"Imported artifact changed: {record['path']}")
        if record["path"].startswith("assets/"):
            files[record["path"]] = content
        else:
            files["downloads/" + path.name] = content

    papers_doc = read_json("results/evidence/aquatic-papers.json")
    search = read_json("results/evidence/aquatic-search.json")
    cloud = read_json("results/evidence/open-notebook-cloud-check.json")
    usage = read_json("results/evidence/open-notebook-minimax-check.json")
    chars = {p["paper_id"]: p["characters"] for p in cloud["papers"]}
    details = {
        "PMC13162690": ("PFOS 与 6:2 FTSA 的肝毒性比较", "成年雌性斑马鱼", "30 d · 肝脏组织学与转录组"),
        "PMC11851982": ("PFOS 暴露下的鲫鱼肝毒性", "Carassius auratus（鲫鱼）", "21 d · 肝损伤与分子通路"),
        "PMC10819493": ("PFAS 对胚胎与幼体的混合效应", "Cyprinodon variegatus", "96 h · 急性与亚致死效应"),
    }
    papers = []
    for p in papers_doc["papers"]:
        title, organism, focus = details[p["paper_id"]]
        papers.append({"id": p["paper_id"], "title": title, "titleEn": p["title"], "year": p["year"], "doi": p["doi"], "organism": organism, "focus": focus, "bytes": p["pdf_bytes"], "chars": chars[p["paper_id"]], "pdf": f"assets/papers/{p['paper_id']}.pdf", "license": "CC BY（见原文许可页）", "authors": p["authors"], "article_url": p["article_url"], "sha256": p["pdf_sha256"]})
    specs = [
        ("single", "单篇论文解读", "完整回答", "open-notebook-single-answer.md", "single_low", ["原文中的“羊头鱼”译名不可靠，应使用 Cyprinodon variegatus。", "LC50、置信区间和两种混合条件已抽查；全文尚未逐句审定。"]),
        ("synthesis", "三篇论文综合比较", "完整回答", "open-notebook-synthesis-answer.md", "synthesis_low", ["原文中的“羊头鰕鲷”译名错误，应使用 Cyprinodon variegatus。", "“三种鱼均具有肝脏或发育毒性”概括过宽：两篇关注肝毒性，第三篇关注胚胎与幼体的急性及亚致死效应。", "部分综合断言缺少紧邻引用；后续研究问题属于模型建议。"]),
        ("truncated", "首次截断记录", "截断 · 不计成功", "open-notebook-single-truncated.md", "baseline", ["接口返回 HTTP 成功，但 finish_reason=length，置信区间尚未写完。", "原版默认参数下的失败记录，不能计入两份完整解读。"]),
    ]
    answers = []
    for id_, title, status, filename, key, notes in specs:
        content = (ROOT / "results/answers" / filename).read_text(encoding="utf-8")
        body = content.rstrip("\r\n")
        actual = hashlib.sha256(body.encode("utf-8")).hexdigest()
        if actual != usage["exports"][filename]["body_sha256_utf8_without_terminal_newlines"]:
            raise ValueError(f"Model answer differs from original generation: {filename}")
        call = usage[key]
        answers.append({"id": id_, "title": title, "status": status, "model": usage["model"], "content": content, "html": markdown(content), "download": "downloads/" + filename, "notes": notes, "characters": len(body), "inputTokens": call["usage"]["input_tokens"], "outputTokens": call["usage"]["output_tokens"], "finishReason": call["finish_reason"], "sourceIds": ["PMC10819493"] if id_ != "synthesis" else list(details)})
        if id_ == "synthesis":
            answers[-1]["notes"].append("本轮精读发现：鲫鱼高剂量 DEG 正文为 1036，火山图与 Venn 图均为 612；原模型回答中的数值不能无条件复用。详见上方逐篇精读。")

    downloads = []
    documents = [
        ("knowledge-summary.md", "能力、架构、场景、扩展与效果总结", "MD"),
        ("results/evidence/architecture-evidence.json", "架构与扩展证据索引", "JSON"),
        ("research-method.md", "研究方法与检查清单", "MD"),
        ("notes.md", "架构、手段与研究理解", "MD"),
        ("SOURCE.json", "上游版本与来源", "JSON"),
        ("results/import-manifest.json", "原始材料哈希清单", "JSON"),
        ("results/study-status.json", "研究状态与访问验证摘要", "JSON"),
        ("results/evidence/open-notebook-minimax-check.json", "模型请求与实际用量", "JSON"),
        ("results/evidence/open-notebook-cloud-check.json", "PDF 导入与云端检查", "JSON"),
        ("results/evidence/aquatic-search.json", "检索式与 30 条候选", "JSON"),
        ("results/evidence/aquatic-papers.json", "三篇论文完整元数据", "JSON"),
        ("assets/README.md", "论文与素材来源声明", "MD"),
        ("results/history/README.md", "路线切换与历史验证摘要", "MD"),
        ("extensions/README.md", "领域检索与模型适配源码说明", "MD"),
    ]
    for relative, title, type_ in documents:
        path = ROOT / relative
        name = {"assets/README.md": "asset-sources.md", "extensions/README.md": "extension-sources.md", "results/history/README.md": "history-summary.md"}.get(relative, path.name)
        files["downloads/" + name] = path.read_bytes()
        downloads.append({"title": title, "href": "downloads/" + name, "type": type_})
    for path in sorted((ROOT / "results/history").glob("*.json")):
        files["downloads/" + path.name] = path.read_bytes()
    for path in sorted((ROOT / "extensions").rglob("*")):
        if path.is_file() and path.suffix in (".py", ".patch", ".json"):
            relative = path.relative_to(ROOT).as_posix()
            files[relative] = path.read_bytes()
    downloads.insert(0, {"title": "完整离线研究档案", "href": "downloads/research-archive.zip", "type": "ZIP · 含网页与 PDF"})
    detailed = read_json("results/detailed/index.json")
    reports = []
    files["downloads/detailed-report-index.json"] = (ROOT / "results/detailed/index.json").read_bytes()
    for spec in detailed["reports"]:
        content = (ROOT / "results/detailed" / spec["file"]).read_text(encoding="utf-8")
        html, toc = render_report(content, spec["id"])
        standalone_body, standalone_toc = render_report(content, spec["id"], "../")
        download = "downloads/" + spec["file"]
        standalone = "reports/" + spec["id"] + ".html"
        evidence = "downloads/" + spec["evidence"]
        files[download] = content.encode("utf-8")
        files[evidence] = (ROOT / "results/detailed" / spec["evidence"]).read_bytes()
        figures = []
        for figure in spec.get("figures", []):
            path = "assets/figures/" + figure["file"]
            files[path] = (ROOT / path).read_bytes()
            figures.append({**figure, "src": path})
        report = {**spec, "html": html, "toc": toc, "download": download, "standalone": standalone, "evidenceDownload": evidence, "characters": len(content), "figures": figures}
        reports.append(report)
        toc_html = "".join(f'<a href="#{x["id"]}">{escape(x["title"])}</a>' for x in standalone_toc)
        files[standalone] = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(spec["title"])} · 论文精读</title><link rel="stylesheet" href="../styles.css"></head><body class="standalone-report"><main><div class="standalone-tools"><a href="../index.html#report-{spec["id"]}">← 返回研究档案</a><a href="../{download}" download>下载 Markdown ↓</a></div><p class="eyebrow">原文精读 · 2026.10.22 · 研究代理分析</p><p class="report-origin">基于完整论文和关键图表的研究分析；原始 MiniMax 短回答单独保留。可用浏览器打印功能保存当前报告。</p><details class="standalone-toc"><summary>报告目录</summary><nav>{toc_html}</nav></details><article class="deep-prose">{standalone_body}</article><p class="report-origin">来源：报告内 PDF 页码链接。未经原始实验数据重分析；正文保留不能确定的问题。</p></main></body></html>'''.encode("utf-8")
        downloads.append({"title": spec["title"], "href": download, "type": "精读 MD"})
    data = {"testedOn": "2026-10-22", "query": search["query"], "queryTime": search["queried_at"], "papers": papers, "answers": answers, "reports": reports, "downloads": downloads, "metrics": {"papers": 3, "detailedReports": len(reports), "completeAnswers": 2, "generations": 3, "media": 0, "embeddings": 0, "searchHits": search["hit_count"], "candidates": len(search["candidates"]), "totalTokens": usage["usage_total"]["total_tokens"]}}
    serialized = json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")
    files["data.js"] = ("// Generated from byte-verified local research artifacts.\nwindow.RESEARCH_DATA = " + serialized + ";\n").encode("utf-8")
    for screenshot in ("cover.png", "reader.png", "detailed-reader.png", "research-overview.svg", "research-overview.png", "overview-page.png"):
        if (ROOT / "assets" / screenshot).is_file():
            files["assets/" + screenshot] = (ROOT / "assets" / screenshot).read_bytes()

    # Guide copies live in downloads/. Preserve original answers/reports, while
    # keeping guide links usable inside both the published site and offline ZIP.
    for relative, _, _ in documents:
        if not relative.endswith(".md"):
            continue
        name = {"assets/README.md": "asset-sources.md", "extensions/README.md": "extension-sources.md", "results/history/README.md": "history-summary.md"}.get(relative, Path(relative).name)
        def rewrite_link(match):
            target = urlsplit(match[2])
            if target.scheme or target.netloc or not target.path:
                return match[0]
            source = (ROOT / relative).parent.joinpath(target.path).resolve()
            try:
                key = source.relative_to(ROOT.resolve()).as_posix()
            except ValueError:
                return match[0]
            destination = key.removeprefix("web/") if key.startswith("web/") else key
            if destination not in files and destination not in ("index.html", "styles.css", "overview.css", "app.js"):
                destination = "downloads/" + {"assets/README.md": "asset-sources.md", "extensions/README.md": "extension-sources.md", "results/history/README.md": "history-summary.md", "results/detailed/index.json": "detailed-report-index.json"}.get(key, source.name)
            if destination not in files and destination != "index.html":
                return match[0]
            suffix = ("?" + target.query if target.query else "") + ("#" + target.fragment if target.fragment else "")
            return match[1] + posixpath.relpath(destination, "downloads") + suffix + ")"
        content = (ROOT / relative).read_text(encoding="utf-8")
        files["downloads/" + name] = re.sub(r"(!?\[[^\]]*\]\()([^\s)]+)\)", rewrite_link, content).encode("utf-8")

    # ZIP is deterministic and self-contained, including a real copy of each PDF.
    bundle = io.BytesIO()
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        archive_files = dict(files)
        for filename in ("index.html", "styles.css", "overview.css", "app.js"):
            archive_files[filename] = (WEB / filename).read_bytes()
        archive_files["READ-ME.txt"] = "水生毒理学研究档案\n解压后打开 index.html。3篇详细精读和1篇综合可离线阅读；reports/ 内各自有独立 HTML，可用浏览器打印。\n原始 PDF、6张关键图页、证据 JSON 及历史模型输出均保留；DOI 等外部链接需要网络。\n新增精读来自本轮研究代理；历史 MiniMax 原文保留错误，二者分别归档；无在线模型服务。\n".encode("utf-8")
        for filename, content in sorted(archive_files.items()):
            info = zipfile.ZipInfo(filename, date_time=(2026, 10, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, content)
    files["downloads/research-archive.zip"] = bundle.getvalue()
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = expected_files()
    for relative, content in files.items():
        path = WEB / relative
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError(f"Missing or stale web artifact: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(f"{'Checked' if args.check else 'Built'} {len(files)} static artifacts; model outputs and PDF hashes match originals.")


if __name__ == "__main__":
    main()
