"""Package our original research page; upstream archives stay outside web/."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


def markdown(data: dict) -> str:
    overview = data["overview"]
    lines = [f"# {data['title']}", "", f"研究日期：{data['date']}", "", data["scope"], "", "## 我们的理解主线", "", overview["thesis"], ""]
    lines.extend(f"- {item}" for item in overview["relationships"])
    lines += ["", "### 我们可以扩展的三层（提案）", ""]
    lines.extend(f"- {item}" for item in overview["expansion_layers"])
    lines += ["", f"核心价值：{overview['value']}", "", overview["boundary"], "", "## 核心理解", ""]
    lines.extend(f"- {item}" for item in data["theses"])
    lines += ["", "## 六步实现链路", ""]
    for index, step in enumerate(data["steps"], 1):
        lines += [f"### {index}. {step['short']}", "", step["description"], "",
                  f"- 输入：{step['input']}", f"- 输出：{step['output']}", f"- 关键点：{step['key']}",
                  f"- 源码位置：`{step['code']}`", f"- [对应来源]({step['source']})", ""]
    lines += ["## 四个项目的分工", ""]
    for project in data["projects"]:
        lines += [f"### {project['name']} · {project['layer']}", "", project["provides"], "",
                  f"依赖：{project['depends']}", "", f"研究状态：{project['status']}；固定版本 {project['revision']}。", ""]
    lines += ["## 八个扩展方向（我们的提案，尚未实现）", ""]
    for index, item in enumerate(data["extensions"], 1):
        lines += [f"### {index}. {item['title']} / {item['horizonLabel']}", "", item["subtitle"], "",
                  f"- 场景：{item['scenario']}", f"- 复用：{item['reuse']}",
                  f"- 新增工作：{item['work']}", f"- 验收：{item['acceptance']}", ""]
    lines += ["## 两种工程目标", ""]
    for route in data["routes"].values():
        lines += [f"### {route['label']}", "", route["intro"], "", route["dependency"], ""]
        lines.extend(f"- {item}" for item in route["work"])
        lines += ["", route["limit"], ""]
    lines += ["## 对话问题", ""]
    for item in data["questions"]:
        lines += [f"### {item['question']}", "", item["answer"], ""]
    lines += ["## 验证与保全", "", "为防止上游删除、封禁或访问中断，已于 2026-10-22 保存 jianying-headless 与整个 yichen-skills（含目标 Skill），并于 2026-10-23 将既有备份统一打包，随本子项目保存。共 67 个引用、187 个全引用可达提交、357 个主分支文件。归档含两个 bundle、两个源码 ZIP、原许可、校验与恢复说明，不含剪映官方引擎或安装包。没有在本机运行剪映原生流程。", "", "备份与恢复说明：https://github.com/yydshly/1022_codex_project/tree/main/projects/010-jianying-headless/backups", "",
              "Mac 平台描述固定到核心 27c2627：11.5.0 / 11.4.2 有原生导出配置；11.6.0 的无界面导出仍拒绝，界面导出另行校验。原项目 Windows 为 FFmpeg；jy-draftc 是另一条 Windows 原生路线。", "",
              "## 来源", ""]
    lines.extend(f"- [{item['title']}]({item['url']}) · {item['revision']}：{item['description']}" for item in data["sources"])
    lines += ["", "上游核心与 Skill 的原创部分为个人学习和非商业使用许可，第三方内容和剪映运行时遵循各自条款。网页仅分发原创研究说明与图解。", ""]
    return "\n".join(lines)


def outputs() -> dict[Path, bytes]:
    data = json.loads((ROOT / "research.json").read_text(encoding="utf-8"))
    notes = markdown(data)
    public_data = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    runtime = dict(data, export_markdown=notes)
    data_js = "window.RESEARCH = " + json.dumps(runtime, ensure_ascii=False, indent=2).replace("</", "<\\/") + ";\n"
    index = (WEB / "index.html").read_text(encoding="utf-8")
    css = (WEB / "style.css").read_text(encoding="utf-8")
    app = (WEB / "app.js").read_text(encoding="utf-8")
    svg = (ROOT / "assets/research-overview.svg").read_bytes()
    standalone = index.replace('<link rel="stylesheet" href="./style.css">', "<style>" + css + "</style>")
    standalone = standalone.replace('<script src="./data.js" defer></script>', "").replace('<script src="./app.js" defer></script>', "")
    image = "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii")
    standalone = standalone.replace('src="./assets/research-overview.svg"', f'src="{image}"')
    standalone = standalone.replace('href="./assets/research-overview.svg"', f'href="{image}"')
    standalone = standalone.replace("</body>", "<script>\n" + data_js + app + "\n</script>\n</body>")
    standalone = standalone.replace('<a class="text-link" href="./standalone.html" download>保存完整离线网页 ↓</a>', '<span class="text-link">当前为完整离线版，可直接保存此文件</span>')
    standalone = "\n".join(line.rstrip() for line in standalone.splitlines()) + "\n"
    backup = json.loads((ROOT / "backup-record.json").read_text(encoding="utf-8"))
    summary = {"created_at": backup["created_at"], "status": backup["verification"]["status"],
               "repositories": [{key: record[key] for key in ("name", "head_commit", "ref_count", "reachable_commits", "source_file_count")}
                                for record in backup["repositories"]]}
    generated = {WEB / "data.js": data_js.encode("utf-8"),
                 WEB / "assets/research-data.json": public_data.encode("utf-8"),
                 WEB / "assets/research-notes.md": notes.encode("utf-8"),
                 WEB / "assets/research-overview.svg": svg,
                 WEB / "assets/backup-summary.json": (json.dumps(summary, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
                 WEB / "standalone.html": standalone.encode("utf-8")}
    manifest = {"schema": "jianying-research-web/v1", "date": data["date"],
                "scope": data["scope"], "upstream_code_included": False,
                "files": {path.relative_to(WEB).as_posix(): {"bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}
                          for path, content in generated.items()},
                "source_files": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in (WEB / "index.html", WEB / "app.js", WEB / "style.css")}}
    generated[WEB / "assets/build-manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = outputs()
    for path, content in generated.items():
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise SystemExit(f"Stale or missing web artifact: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(f"Research web {'verified' if args.check else 'packaged'}: {len(generated)} generated files; no upstream code copied")


if __name__ == "__main__":
    main()
