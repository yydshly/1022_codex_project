"""Build the original research summary using an unchanged upstream board image."""
from __future__ import annotations

import argparse
import base64
import hashlib
from html import escape
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version


PROJECT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1800, 1460
INK, MUTED, GREEN = "#193b34", "#60715b", "#477048"
PAPER, LINE, WHITE = "#f5f6f0", "#d7e0cf", "#fffef9"


def build(regular: Path, bold: Path) -> dict[Path, bytes]:
    for font_path in (regular, bold):
        if not font_path.is_file():
            raise ValueError("需要中文字体；请用 --font-regular 和 --font-bold 指定字体文件。")
    manifest = json.loads((PROJECT / "screenshots.json").read_text(encoding="utf-8"))
    source = next(item for item in manifest["screenshots"] if item["upstream_path"] == "docs/board.png")
    board = (PROJECT / source["file"]).read_bytes()
    assert hashlib.sha256(board).hexdigest() == source["sha256"], "官方原图与登记哈希不同"

    canvas = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(canvas)
    fonts: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
           '<title id="title">Todofy：我们的理解、能力、本质、效果和参考意义</title>',
           '<desc id="desc">左侧是上游官方看板截图；右侧以任务数据、管理界面、驱动逻辑三层说明本质；下方总结能力如何形成效果，以及我们参考看板布局、卡片信息与交互组织的价值。产品画面来自上游，注解为我们的研究总结。</desc>',
           f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>']

    def rect(x: int, y: int, w: int, h: int, fill: str, stroke: str | None = None, radius: int = 14) -> None:
        draw.rounded_rectangle((x, y, x + w, y + h), radius, fill=fill, outline=stroke, width=2 if stroke else 1)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="2"/>')

    def text(x: int, y: int, value: str, size: int = 24, color: str = INK, strong: bool = False, max_width: int = 1672) -> None:
        key = (size, strong)
        if key not in fonts:
            fonts[key] = ImageFont.truetype(str(bold if strong else regular), size)
        font = fonts[key]
        assert draw.textlength(value, font=font) <= max_width, f"文本过宽：{value}"
        box = draw.textbbox((x, y), value, font=font, anchor="lt")
        assert 0 <= box[0] and box[2] <= WIDTH and 0 <= box[1] and box[3] <= HEIGHT, value
        draw.text((x, y), value, fill=color, font=font, anchor="lt")
        svg.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="{size}" font-weight="{700 if strong else 400}" fill="{color}">{escape(value)}</text>')

    text(64, 40, "002 / TODOFY / 我们的理解与参考价值", 20, GREEN, max_width=1500)
    text(64, 92, "Todofy：任务管理的界面 + 驱动逻辑", 48, strong=True)
    text(64, 164, "任务是核心；日历、看板和列表负责组织展示，业务逻辑负责推进、提醒和记录。", 26, MUTED)

    text(64, 221, "01  实际效果 / 上游官方 Board 画面", 22, GREEN, True, 950)
    picture = Image.open(BytesIO(board)).convert("RGB")
    picture = picture.resize((950, 594), Image.Resampling.LANCZOS)
    canvas.paste(picture, (64, 264))
    data_url = "data:image/png;base64," + base64.b64encode(board).decode("ascii")
    svg.append(f'<image x="64" y="264" width="950" height="594" preserveAspectRatio="xMidYMid meet" href="{data_url}"/>')
    text(64, 879, "官方原图等比缩放引用 · 待办 / 进行中 / 受阻 / 已完成", 18, MUTED, max_width=950)
    text(64, 916, "效果：把任务、阶段、日期与用时放在一起看。", 25, INK, True, 950)

    rect(1050, 264, 686, 680, "#e9efdf", LINE)
    text(1080, 292, "本质：三层一起工作", 28, INK, True, 626)
    layers = [
        (344, "任务数据 / 管什么", "标题、日期、优先级、完成状态", "子任务、标签、预计与实际耗时"),
        (508, "管理界面 / 怎么看", "列表看事项，看板看阶段", "日历看日期，同一批任务多角度展示"),
        (672, "驱动逻辑 / 怎么运转", "新增修改、状态流转、重复任务推进", "到期提醒、计时、保存与可选同步"),
    ]
    for top, title, first, second in layers:
        rect(1080, top, 626, 146, WHITE, LINE, 10)
        text(1102, top + 18, title, 25, INK, True, 582)
        text(1102, top + 66, first, 22, MUTED, max_width=582)
        text(1102, top + 103, second, 22, MUTED, max_width=582)
    text(1080, 844, "本质：以任务为中心的个人管理应用。", 23, INK, True, 626)
    text(1080, 889, "规划与工作内容仍由使用者决定。", 21, MUTED, max_width=626)

    rect(64, 986, 950, 310, WHITE, LINE)
    text(92, 1014, "02  能力如何形成效果", 27, INK, True, 894)
    rows = [
        (1073, "记录与拆解", "把零散事项变成可管理的任务"),
        (1133, "日期与状态管理", "看清什么时候到期、推进到哪里"),
        (1193, "提醒、计时与回顾", "提示行动，记录投入，支持复盘"),
    ]
    for top, title, result in rows:
        text(92, top, title, 23, GREEN, True, 235)
        text(345, top, "→  " + result, 23, MUTED, max_width=635)
    text(92, 1253, "任务由人执行，应用负责组织、呈现和辅助。", 20, MUTED, max_width=894)

    rect(1050, 986, 686, 310, "#e9efdf", LINE)
    text(1080, 1014, "03  对我们的意义 / 重点参考", 26, INK, True, 626)
    for top, title, detail in [
        (1070, "看板布局与样式", "列分组、数量、卡片间距、视觉层级。"),
        (1144, "卡片信息与交互", "优先级、标签、日期、进度、拖动反馈。"),
        (1218, "界面与业务的分工", "把样式与组织思路用于我们自己的流程。"),
    ]:
        text(1080, top, title, 23, INK, True, 626)
        text(1080, top + 36, detail, 20, MUTED, max_width=626)

    rect(64, 1334, 1672, 72, INK, radius=12)
    text(92, 1356, "我们的结论：参考看板的呈现与组织方式，结合自己的任务数据和业务规则实现。", 26, "#e1edc9", True, 1616)
    text(64, 1427, "官方画面 © Salar Zeidanlou / unifybrowse · Todofy 2ae76fc · 其余为我们的研究总结 · 2026-10-21", 17, MUTED)
    svg.append("</svg>")
    svg_bytes = ("\n".join(svg) + "\n").encode("utf-8")
    png_buffer = BytesIO()
    canvas.save(png_buffer, format="PNG", optimize=True)
    png_bytes = png_buffer.getvalue()
    outputs = {PROJECT / folder / f"understanding-summary.{suffix}": data
               for folder in ("assets", "web/assets")
               for suffix, data in (("svg", svg_bytes), ("png", png_bytes))}
    metadata = {
        "date": "2026-10-21", "type": "original research summary with an attributed upstream screenshot",
        "dimensions": [WIDTH, HEIGHT], "source_commit": manifest["source_commit"],
        "embedded_screenshot": {"source_url": source["source_url"], "sha256": source["sha256"],
                                "treatment": "aspect-preserving reduced preview; original screenshot file unchanged", "author": manifest["author"]},
        "summary_topics": ["我们的理解", "能力", "本质", "效果", "对我们的参考意义"],
        "reference_focus": ["看板布局与样式", "卡片信息层级", "状态与日期组织", "界面交互与业务规则分工"],
        "renderer": {"library": "Pillow", "version": pillow_version, "regular_font": regular.name, "bold_font": bold.name},
        "files_sha256": {path.relative_to(PROJECT).as_posix(): hashlib.sha256(data).hexdigest() for path, data in outputs.items()},
    }
    outputs[PROJECT / "summary-image.json"] = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-regular", type=Path, default=Path("C:/Windows/Fonts/msyh.ttc"))
    parser.add_argument("--font-bold", type=Path, default=Path("C:/Windows/Fonts/msyhbd.ttc"))
    parser.add_argument("--check", action="store_true", help="Verify existing generated files in the same rendering environment")
    args = parser.parse_args()
    outputs = build(args.font_regular, args.font_bold)
    for path, data in outputs.items():
        if args.check:
            if not path.is_file() or path.read_bytes() != data:
                raise ValueError(f"Summary output differs: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"Summary {'verified' if args.check else 'built'}: {WIDTH} x {HEIGHT}; original source screenshot retained.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
