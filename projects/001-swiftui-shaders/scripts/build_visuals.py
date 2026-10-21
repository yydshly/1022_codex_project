"""Build editable, factual SVG explainers using genuine captured shader images.

Pillow is used only for font measurement. SVG text and layout remain editable;
capture_visuals.py rasterizes the results in a browser without inventing effects.
"""
from __future__ import annotations
import base64
from html import escape
import json
from pathlib import Path
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "web/assets"
BG, PANEL, LINE = "#101713", "#19231d", "#344138"
WHITE, MUTED, LIME = "#eff3e8", "#b1beb1", "#d9f279"
FONT = "Microsoft YaHei, PingFang SC, sans-serif"
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")


class Diagram:
    def __init__(self, width: int, height: int, title: str, description: str):
        self.width, self.height = width, height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
                      f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
                      f'<rect width="{width}" height="{height}" fill="{BG}"/>']

    def rect(self, x, y, w, h, color=PANEL, stroke=LINE, radius=18):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{color}" stroke="{stroke}"/>')

    def text(self, x, y, text, size=28, color=WHITE, weight=400, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y + size}" fill="{color}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(text))}</text>')

    def paragraph(self, x, y, text, width, size=27, color=MUTED, line_height=None, bottom=None):
        font = ImageFont.truetype(str(FONT_PATH), size)
        lines, current = [], ""
        for char in text:
            if char == "\n" or (current and font.getlength(current + char) > width):
                lines.append(current)
                current = "" if char == "\n" else char
            else:
                current += char
        if current:
            lines.append(current)
        step = line_height or round(size * 1.55)
        for index, line in enumerate(lines):
            self.text(x, y + index * step, line, size, color)
        end = y + len(lines) * step
        assert bottom is None or end <= bottom, (text, end, bottom)
        return end

    def line(self, x1, y1, x2, y2, color=LINE, width=2):
        self.parts.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def arrow(self, x1, y, x2, color=LIME):
        self.line(x1, y, x2, y, color, 3)
        self.parts.append(f'<path d="M{x2-12} {y-9}L{x2} {y}L{x2-12} {y+9}" fill="none" stroke="{color}" stroke-width="3"/>')

    def image(self, image_id, x, y, width, height):
        raw = (ASSETS / f"effects/{image_id}.png").read_bytes()
        uri = "data:image/png;base64," + base64.b64encode(raw).decode()
        self.parts.append(f'<image x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid meet" xlink:href="{uri}"/>')

    def save(self, name):
        path = ASSETS / name
        path.write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8", newline="\n")
        print(f"Generated {path.relative_to(ROOT)}")


def overview():
    d = Diagram(2000, 2460, "SwiftUIShaders：能力、输入、原理、输出、使用场景与扩展方向", "41 种 SwiftUI 原生视图特效的研究总览；包含真实 WebGL 移植效果及源库、展示页和待开发方向的区别。")
    d.text(70, 45, "001 / OPEN-SOURCE PROJECT RESEARCH", 23, LIME)
    d.text(70, 94, "SwiftUIShaders", 82, WHITE, 600)
    d.text(70, 195, "给已有的图片、文字与卡片，增加质感、动感和交互反馈。", 33, MUTED)
    d.text(70, 248, "价值：复用现成着色器与修饰器，减少开发工作，并增强视觉表达与操作反馈。", 25, MUTED)
    d.rect(1510, 63, 420, 115, "#26341f", "#52643d")
    d.text(1540, 77, "41", 61, LIME, 600)
    d.text(1650, 97, "种原生视图特效", 27, WHITE)

    # The central contract: source View + controls -> GPU layer -> resulting View.
    positions = [70, 710, 1350]
    for x in positions:
        d.rect(x, 292, 580, 510)
    d.arrow(658, 545, 699)
    d.arrow(1298, 545, 1339)
    d.text(104, 323, "01  输入是什么", 36, "#f2c38b", 600)
    d.text(104, 388, "已有的 SwiftUI View", 31)
    d.paragraph(104, 443, "图片、封面、文字、卡片及可渲染的组合视图。", 505, 27)
    d.image("Original", 105, 548, 130, 174)
    d.text(263, 545, "＋ 效果参数", 28, LIME)
    d.text(263, 591, "强度 / 速度 / 尺度", 26, MUTED)
    d.text(263, 634, "＋ 尺寸、时间、触点", 26, MUTED)
    d.text(104, 747, "触点由应用传入，动画封装推进时间。", 23, MUTED)

    d.text(744, 323, "02  原理是什么", 36, "#b9c3ff", 600)
    for y, text in [(392, "SwiftUI 生成栅格图层"), (461, "layerEffect 调用 Metal 着色器"), (530, "GPU 逐像素取色、变换与混合")]:
        d.text(744, y, text, 29)
    d.line(745, 587, 1255, 587)
    for i, (a, b) in enumerate([("换采样位置", "水波 / 旋涡 / 折射"), ("改颜色与亮度", "镭射 / 热成像 / 霓虹"), ("多点采样", "模糊 / 浮雕 / 重影")]):
        d.text(744, 612 + i * 48, a, 25, LIME)
        d.text(941, 612 + i * 48, b, 24, MUTED)
    d.text(744, 757, "时间与交互数据让输出持续变化。", 23, MUTED)

    d.text(1384, 323, "03  输出是什么", 36, LIME, 600)
    d.text(1384, 388, "实时渲染的 SwiftUI 视图", 31)
    d.image("Holographic", 1385, 454, 145, 193)
    d.text(1560, 465, "动态光影与形变", 26)
    d.text(1560, 516, "静态材质与轮廓", 26)
    d.text(1560, 567, "跟随触摸的视觉响应", 25)
    d.paragraph(1384, 682, "原库直接输出视图效果；保存图片或视频，需要应用层另行采集与编码。", 505, 25, bottom=790)

    d.text(70, 850, "能力覆盖", 35, WHITE, 600)
    categories = [("光影材质", "镭射 / 磨砂 / 金属"), ("流体波纹", "水墨 / 热浪 / 焦散"), ("几何空间", "万花筒 / 旋涡 / 虫洞"), ("色彩轮廓", "霓虹 / 双色 / 等高线"), ("故障解构", "错块 / 熔化 / 消散"), ("触摸交互", "透镜 / 点击涟漪")]
    for i, (title, desc) in enumerate(categories):
        x = 70 + i * 313
        d.rect(x, 913, 292, 109, "#17211a")
        d.text(x + 19, 928, title, 27, LIME)
        d.text(x + 19, 975, desc, 21, MUTED)
    d.text(70, 1048, "36 种随时间变化  /  3 种静态或参数驱动  /  2 种触摸交互", 27)
    d.text(1930, 1053, "Shatter 由 explode 参数控制", 22, MUTED, anchor="end")

    d.text(70, 1120, "同一张素材，不同的真实输出", 35, WHITE, 600)
    d.text(1930, 1130, "下图为本研究 WebGL 移植实渲染", 22, MUTED, anchor="end")
    for i, (key, title) in enumerate([("Original", "原始输入"), ("Holographic", "全息镭射"), ("NeonEdge", "霓虹轮廓"), ("Kaleidoscope", "万花筒")]):
        x = 70 + i * 477
        d.rect(x, 1190, 455, 427, "#17201a")
        d.image(key, x + 91, 1208, 273, 364)
        d.text(x + 227.5, 1577, title, 25, WHITE, anchor="middle")

    d.text(70, 1662, "最适合用在哪里", 35, WHITE, 600)
    cases = [
        ("封面与海报", "书籍 / 专辑 / 电影", "突出选中内容，营造氛围。"),
        ("卡片与徽章", "会员 / 收藏 / 成就", "表现材质、珍藏感与等级。"),
        ("展示页主视觉", "产品介绍 / 活动 / 游戏", "建立主题，增强辨识度。"),
        ("局部交互反馈", "点击 / 拖动 / 状态变化", "让操作获得可感知的响应。"),
    ]
    for i, (title, types, value) in enumerate(cases):
        x = 70 + i * 477
        d.rect(x, 1725, 455, 180)
        d.text(x + 23, 1743, title, 29, LIME)
        d.text(x + 23, 1794, types, 23, MUTED)
        d.text(x + 23, 1842, value, 24, WHITE)

    d.text(70, 1951, "可扩展方向", 35, WHITE, 600)
    d.text(342, 1962, "以下方向需要额外开发与性能验证", 24, MUTED)
    expansions = [
        ("更丰富的输入与交互", "接入滚动进度、手势或设备运动数据，驱动同一套特效参数。"),
        ("效果预设与算法扩展", "建立材质主题、组合多个效果，或新增 Metal 算法与 View 修饰器。"),
        ("素材生产工作流", "在应用层增加批量处理、截图，以及 GIF / 视频录制与编码。"),
    ]
    for i, (title, body) in enumerate(expansions):
        x = 70 + i * 640
        d.rect(x, 2016, 580, 190)
        d.text(x + 24, 2037, title, 29, LIME)
        d.paragraph(x + 24, 2090, body, 530, 25, bottom=2196)

    d.rect(70, 2240, 1860, 105, "#23301f", "#52643d")
    d.text(96, 2253, "本展示补充", 27, LIME, 600)
    d.text(295, 2256, "参数实验 / 素材切换 / 原图对比 / PNG 导出 / WebGL 浏览器移植", 27)
    d.text(96, 2302, "原库面向 Apple 的 SwiftUI；网页能力不等于原库直接支持网页或文件导出。", 24, MUTED)
    d.text(70, 2371, "选型判断：优先服务视觉重点与局部反馈；阅读和效率场景少量使用。业务收益需实验验证。", 24, MUTED)
    d.text(70, 2420, "来源：Kris Puckett / SwiftUIShaders · MIT · commit 6b644a8 · 研究日期 2026-10-21", 21, MUTED)
    d.save("understanding-overview.svg")


MODULES = [
    ("Original", "原始输入", "一张原创封面，作为统一比较的基准。"),
    ("Holographic", "全息镭射", "按亮度叠加彩虹光泽，适合卡片质感。"),
    ("NeonEdge", "霓虹轮廓", "检测图像边缘，生成彩色发光轮廓。"),
    ("Kaleidoscope", "万花筒", "折叠与镜像采样坐标，形成对称图案。"),
    ("InkBleed", "水墨晕染", "用噪声扰动取色位置，形成有机流动。"),
    ("Datamosh", "数据损坏", "块状位移与颜色分离，表现数字故障。"),
    ("Disintegrate", "粒化消散", "噪声阈值控制消散边界与发亮的边缘。"),
    ("TouchRipple", "触摸涟漪", "以触点与经过时间控制扩散的波纹。"),
    ("RefractLens", "交互透镜", "围绕触点折射取色，形成玻璃球观感。"),
]


def atlas():
    d = Diagram(1800, 2750, "SwiftUIShaders 实际效果图集：原图与八种代表效果", "同一素材、固定参数和时间，以真实 WebGL 移植输出对照；每个模块可在实验区复现。")
    d.text(60, 45, "REAL OUTPUT / 同一素材的真实渲染", 24, LIME)
    d.text(60, 96, "8 种代表效果，与原图对照", 66, WHITE, 600)
    d.text(60, 190, "原始封面 + 8 种独立着色器 · 完整库包含 41 种效果", 29, MUTED)
    for i, (key, name, desc) in enumerate(MODULES):
        x = 60 + (i % 3) * 570
        y = 270 + (i // 3) * 790
        d.rect(x, y, 540, 760)
        d.image(key, x + 30, y + 22, 480, 640)
        d.text(x + 25, y + 677, f"{i:02}  {name}", 29, LIME if i else WHITE)
        d.text(x + 25, y + 723, desc, 21, MUTED)
    d.text(60, 2660, "所有效果图来自本研究的 WebGL 2 移植运行，原生 Metal 的精度、色彩与采样边界可能不同。", 24, MUTED)
    d.text(60, 2705, "固定帧 t = 1.7s；交互点 (0.5, 0.5)；示例参数记录于 assets/effects/*.json；MIT / 6b644a8", 22, MUTED)
    d.save("effect-atlas.svg")


if __name__ == "__main__":
    for key, _, _ in MODULES:
        assert (ASSETS / f"effects/{key}.png").is_file(), f"Run capture_visuals.py first: {key}"
    overview()
    atlas()
    (ASSETS / "visuals-source.json").write_text(json.dumps({
        "method": "Editable SVG layout, embedded genuine WebGL captures, browser PNG rasterization; no synthetic effect images",
        "sourceCommit": "6b644a8bd4f3131401bd6765990e476352d3cdef",
        "date": "2026-10-21",
        "modules": [{"id": key, "name": name, "description": desc} for key, name, desc in MODULES],
        "outputs": ["understanding-overview.svg", "understanding-overview.png", "effect-atlas.svg", "effect-atlas.png"],
        "note": "PNG generation is performed by capture_visuals.py after these SVGs are available."}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
