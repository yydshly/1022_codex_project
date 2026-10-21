"""Package the complete, attributed gallery using only the Python standard library."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

PROJECT = Path(__file__).resolve().parents[1]

PROMPT_DETAILS = (
    ("original.zh-CN.md", "原始风格正文 · 唯一审美依据", "固定风格", "上游原文默认3:4上下对照，决定视觉锚点、像素语言、配色、留白与文字气质。不同输出的完整请求会在原文后追加容器与文字覆盖。"),
    ("left-right.txt", "左右对照 · 本次准确中文", "成功输出", "保留原始风格正文，追加横向画布、左右各50%及准确中文「把巴黎留在这一刻」。改变的是交付容器与文案，风格不另写一套。"),
    ("top-bottom.txt", "上下对照 · 本次自动英文", "成功输出", "保留原始风格正文，追加当前3:4画布、上下各50%及英文自动配文要求。"),
    ("design-only.txt", "纯设计 · 首轮请求", "首轮失败", "追加全幅设计与无文字要求，但模型首轮仍保留摄影分区；可与重试请求比较。"),
    ("design-only-retry.txt", "纯设计 · 最终重试请求", "重试后保留", "保留首轮完整内容，在末尾只加强失败项：明确撤销摄影展示，整张画布均为无文字像素艺术。"),
    ("wallpaper-phone.txt", "手机壁纸 · 首轮请求", "首轮失败", "追加手机长画幅、连贯定调与无文字要求；首轮仍有摄影区。"),
    ("wallpaper-phone-retry.txt", "手机壁纸 · 最终定调请求", "重试后保留", "只加强全幅设计与不可见摄影参考，重试后作为其余三端的定调图。"),
    ("wallpaper-ipad.txt", "平板壁纸 · 原照＋定调图", "成功输出", "同时参考原始实拍与手机定调图，按平板画幅重新构图，并明确全画布转译。"),
    ("wallpaper-desktop.txt", "电脑壁纸 · 原照＋定调图", "成功输出", "同时参考原照与手机定调图，改成横向画布，维持家族风格并重新组织主体。"),
    ("wallpaper-watch.txt", "手表壁纸 · 首轮请求", "首轮失败", "请求1024×1024和全幅无文字设计；首轮仍返回3:4竖图。"),
    ("wallpaper-watch-retry.txt", "手表壁纸 · 最终方形请求", "重试后保留", "只加强失败的画幅要求：明确1:1正方形，而非竖版。原照与手机定调图仍同时作为参考。"),
)


def prompt_library() -> list[dict]:
    original = (PROJECT / "prompts/original.zh-CN.md").read_text(encoding="utf-8").strip()
    entries = []
    for filename, title, kind, note in PROMPT_DETAILS:
        path = PROJECT / "prompts" / filename
        text = path.read_text(encoding="utf-8")
        if not text.startswith(original):
            raise ValueError(f"Original style brief changed in {filename}")
        entries.append({"path": f"prompts/{filename}", "title": title, "kind": kind,
                        "note": note, "text": text,
                        "addition": "" if filename == "original.zh-CN.md" else text[len(original):].lstrip("\n")})
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((PROJECT / "media.json").read_text(encoding="utf-8"))
    records = [manifest["source"], *manifest["upstream_samples"], *manifest["demo_outputs"], *manifest["rejected_outputs"], *manifest.get("study_guides", [])]
    paths = [record["path"] for record in records]
    paths += ["assets/README.md", "assets/NOTICE.md", "assets/upstream/LICENSE.txt", "assets/upstream/README.original.md", "media.json"]
    paths += [path.relative_to(PROJECT).as_posix() for path in sorted((PROJECT / "prompts").glob("*")) if path.is_file()]
    paths += [guide["prompt"] for guide in manifest.get("study_guides", [])]
    for record in records:
        if hashlib.sha256((PROJECT / record["path"]).read_bytes()).hexdigest() != record["sha256"]:
            parser.error(f"Source changed without manifest update: {record['path']}")
    for relative in dict.fromkeys(paths):
        source, destination = PROJECT / relative, PROJECT / "web" / relative
        if args.check:
            if not destination.is_file() or source.read_bytes() != destination.read_bytes():
                parser.error(f"Stale or missing published resource: {relative}; run package_web.py")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    data_js = "window.PANEL_MEDIA = " + json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + ";\n"
    data_js += "window.PANEL_PROMPTS = " + json.dumps(prompt_library(), ensure_ascii=False, separators=(",", ":")) + ";\n"
    data_path = PROJECT / "web/media.js"
    if args.check:
        if not data_path.is_file() or data_path.read_text(encoding="utf-8") != data_js:
            parser.error("Stale or missing media.js; run package_web.py")
    else:
        data_path.write_text(data_js, encoding="utf-8", newline="\n")
    print(f"{'Verified' if args.check else 'Packaged'} {len(dict.fromkeys(paths))} unchanged resources and media.js.")


if __name__ == "__main__":
    main()
