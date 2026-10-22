"""Assemble registered static demos into one GitHub Pages site (stdlib only)."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/yydshly/1022_codex_project"


def build(output: Path) -> None:
    output = output.resolve()
    # Refuse to replace files or copy a source tree into itself.
    if output == ROOT or output in ROOT.parents or output.is_relative_to(ROOT / "projects"):
        raise ValueError("Output must be separate from the source directories.")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Output directory must be empty; no files will be removed.")
    projects = json.loads((ROOT / "projects/catalog.json").read_text(encoding="utf-8"))["projects"]
    cards = []
    for project in projects:
        folder = f"{project['id']}-{project['slug']}"
        source_name = project["repo"].rstrip("/").rsplit("/", 1)[-1]
        web = ROOT / "projects" / folder / "web"
        if not (web / "index.html").is_file():
            continue
        shutil.copytree(web, output / folder)
        guides = []
        for filename, title, caption in (
            ("understanding-overview.png", "能力全景", "输入 → GPU 原理 → 实时视图输出，以及价值、场景与扩展方向。"),
            ("effect-atlas.png", "真实效果对照", "同一张原创封面：原图与 8 种代表特效，来自实际 WebGL 渲染。"),
        ):
            if project["slug"] != "swiftui-shaders":
                continue
            if (web / "assets" / filename).is_file():
                src = f"./{folder}/assets/{filename}"
                alt = escape(title + "：" + caption, quote=True)
                guides.append(f'<figure><a href="{src}"><img src="{src}" alt="{alt}" loading="lazy"></a><figcaption><strong>{title}</strong>{caption}</figcaption></figure>')
        # Other projects can publish their own catalog cover without shader-specific names.
        cover = Path(project["cover"])
        if not guides and (web / cover).is_file():
            src = escape(f"./{folder}/{cover.as_posix()}", quote=True)
            caption = escape(project["cover_caption"])
            alt = escape(project["name"] + "：" + project["cover_caption"], quote=True)
            guides.append(f'<figure><a href="./{folder}/"><img src="{src}" alt="{alt}" loading="lazy"></a><figcaption><strong>能力与原理</strong>{caption}</figcaption></figure>')
        backup_link = (f'<a href="{REPO_URL}/tree/main/projects/{folder}/backups">双仓备份与恢复 ↗</a>'
                       if project["slug"] == "jianying-headless" else "")
        cards.append(f'''<article><div class="project-heading"><span>研究项目 {project['id']}</span><h2>{escape(project['name'])}</h2><p>{escape(project['summary'])}</p><div class="actions"><a class="primary" href="./{folder}/">打开项目展示 ↗</a><a href="{REPO_URL}/tree/main/projects/{folder}">研究文档 ↗</a><a href="{escape(project['repo'], quote=True)}">关注源库：{escape(source_name)} ↗</a>{backup_link}</div></div><div class="guides">{''.join(guides)}</div></article>''')
    output.mkdir(parents=True, exist_ok=True)
    html = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="GitHub 开源项目研究：能力、原理、真实效果、适用场景与扩展方向。"><title>开源项目研究 · 图解与演示</title><style>
    *{box-sizing:border-box}body{margin:0;background:#101510;color:#edf1e7;font-family:system-ui,"Microsoft YaHei",sans-serif;line-height:1.8}main{max-width:1280px;margin:auto;padding:64px 32px}a{color:#cced96;text-decoration:none}a:hover{text-decoration:underline}header{margin-bottom:48px}header>p:first-child,.project-heading>span{font:12px ui-monospace,monospace;letter-spacing:2px;color:#a9c393}h1{font-size:clamp(28px,4vw,46px);font-weight:500;margin:20px 0}header p{color:#b3bdab;max-width:800px}article{border:1px solid #35442e;border-radius:14px;overflow:hidden;margin-bottom:36px;background:#171e15}.project-heading{padding:32px}h2{font-size:30px;font-weight:500;margin:14px 0}.project-heading p{max-width:880px;color:#bdc8b4}.actions{display:flex;flex-wrap:wrap;align-items:center;gap:24px;margin-top:24px;font-size:14px}.primary{background:#c8ec90;color:#17200e;padding:10px 18px;border-radius:6px}.guides>figure:only-child{grid-column:1/-1;max-width:1100px}.guides{display:grid;grid-template-columns:1fr 1fr;align-items:start;gap:20px;padding:0 24px 24px}figure{margin:0;background:#101710;border-radius:8px;overflow:hidden;border:1px solid #303d2b}img{width:100%;height:auto;display:block}figcaption{font-size:12px;color:#adbaa2;padding:16px}figcaption strong{display:block;color:#e4edda;font-size:15px;margin-bottom:6px}footer{font-size:12px;color:#99a58e}footer a{margin-left:18px}@media(max-width:650px){main{padding:32px 16px}.project-heading{padding:24px 20px}.guides{grid-template-columns:1fr;padding:0 12px 12px}.actions{gap:16px}h2{font-size:26px}}
    </style></head><body><main><header><p>GITHUB PROJECT RESEARCH</p><h1>看懂能力，再亲手体验。</h1><p>从源码确认项目能做什么、如何工作；用图解和真实效果理解输入、输出、适用场景与扩展方向。</p></header>''' + "".join(cards) + f'<footer>按收录顺序持续整理。每个项目保留上游版本、许可与验证范围。<a href="{REPO_URL}">研究仓库 ↗</a></footer></main></body></html>'
    (output / "index.html").write_text(html, encoding="utf-8", newline="\n")
    (output / ".nojekyll").touch()
    print(f"Built {len(cards)} demo(s): {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    try:
        build(args.output)
    except ValueError as exc:
        parser.error(str(exc))
