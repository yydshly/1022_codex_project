"""Promote the verified AI film to the video entry; fold historical code previews."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]


def section_bounds(html: str, identifier: str) -> tuple[int, int]:
    start = html.index('<section id="' + identifier + '"')
    level = 0
    for match in re.finditer(r"<(\s*/)?section\b[^>]*>", html[start:]):
        level += -1 if match.group(1) else 1
        if level == 0:
            return start, start + match.end()
    raise ValueError("Unclosed section: " + identifier)


def main() -> None:
    assets = PROJECT / "assets" / "ai-film"
    study = json.loads((assets / "study.json").read_text(encoding="utf-8"))
    assert study["generated"] and study["status"] == "completed"
    actual = study["actual"]
    assert hashlib.sha256((assets / actual["file"]).read_bytes()).hexdigest() == actual["sha256"]
    path = PROJECT / "web" / "index.html"
    html = path.read_text(encoding="utf-8")
    if 'id="ai-film"' in html:
        print("AI film already integrated; verified original still matches.")
        return
    fragment = (PROJECT / "scripts" / "ai-film-section.html").read_text(encoding="utf-8")
    start, end = section_bounds(html, "motion-demo")
    old = html[start:end]
    html = html[:start] + fragment + '\n<details id="motion-sketch-history" class="motion-archive"><summary>历史预演 / 《夜香》关键画面与代码合成</summary>\n' + old + '\n</details>' + html[end:]
    start, end = section_bounds(html, "motion-emotions")
    old = html[start:end]
    html = html[:start] + '<details id="motion-code-history" class="motion-archive"><summary>历史预演 / 《候光》代码动画与V1/V2对照</summary>\n' + old + '\n</details>' + html[end:]
    html = html.replace('<link rel="stylesheet" href="./motion-review.css">', '<link rel="stylesheet" href="./motion-review.css">\n  <link rel="stylesheet" href="./ai-film.css">')
    html = html.replace('<script src="./motion-review.js" defer></script>', '<script src="./motion-review.js" defer></script>\n  <script src="./ai-film.js" defer></script>')
    html = html.replace('class="nav-motion" href="#motion-emotions"', 'class="nav-motion" href="#ai-film"')
    html = html.replace('看一段已完成的情绪影像 ↓', '看AI模型实际生成的短片 ↓')
    html = html.replace('想看动态？播放同一雨夜的「孤独 / 不安 / 希望」三段有声影片 ↓', '看实际AI视频：艺术意图、实际指令与原片 ↓')
    html = html.replace('进阶动态：看人物行动、节奏与声音的三种情绪对照 ↓', '看视频模型实际生成的短片 ↓')
    html = html.replace('未调用视频模型，未进行稳定成功率或身份保真测试。', '历史预演未调用视频模型；新增《留一点位置》实际调用Seedance 2.0生成，原片与完整指令保留。未进行稳定成功率或身份保真测试。')
    path.write_text(html, encoding="utf-8")
    print("Integrated verified AI film; both historical previews retained and folded.")


if __name__ == "__main__":
    main()
