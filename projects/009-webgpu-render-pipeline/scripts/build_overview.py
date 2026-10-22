"""Build the complete Chinese entry map from the 89 canonical capability records.

SVG generation/checking uses the standard library. --render-png additionally uses
Pillow and a Chinese font (Windows YaHei, or --font / --bold-font on other systems).
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
from html import escape
import json
import math
from pathlib import Path
import re
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from research_catalog import CATEGORIES

W, H = 2200, 4400
BG, PANEL, LINE = '#101d20', '#1a2b2d', '#36514e'
INK, MUTED, MINT, GOLD, BLUE = '#eff4ed', '#b7ccc2', '#9de2c5', '#e5c38b', '#96d0e7'
STATUS = {
    '主管线': ('主', MINT), '按场景': ('场', BLUE), '可选': ('选', GOLD),
    '实验室': ('实', '#d6b4ed'), '历史路径': ('史', '#c7b39e'),
    '集成待补': ('待', '#efb7a8'), '独立资料': ('文', '#bcc9d8'),
}
EFFECTS = {
    'pipeline': '效果：多种场景共享计算、绘制与画面合成流程。',
    'gi': '效果：背光处有环境补光，物体受到周围颜色影响。',
    'lightmap': '效果：静态照明可反复读取，按镜头需求使用显存。',
    'lighting': '效果：受光方向、投影、接触关系与环境反射更明确。',
    'water': '效果：水下景物、波面、岸线、泡沫和湿沙形成层次。',
    'nature': '效果：叶片逆光、地表纹理与成片植被共同构成环境。',
    'sky': '效果：晴空、云影、雾与远景呈现不同的空气层次。',
    'post': '效果：稳定边缘，控制曝光、颜色与运动表现。',
    'tools': '效果：拆开画面，定位漏光、缓存问题与运行成本。',
    'integration': '效果：把不同三维场景接入同一套显示流程。',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Drawing:
    def __init__(self):
        self.ops = []
        self.regions = []

    def rect(self, x, y, w, h, fill=PANEL, stroke=None, radius=14):
        self.ops.append(('rect', (x, y, w, h, fill, stroke, radius)))

    def text(self, x, y, value, size=24, color=INK, bold=False, id=None):
        self.ops.append(('text', (x, y, value, size, color, bold, id)))

    def line(self, x1, y1, x2, y2, color=LINE, width=2):
        self.ops.append(('line', (x1, y1, x2, y2, color, width)))

    def arrow(self, x1, y, x2, color=MINT):
        self.line(x1, y, x2 - 9, y, color, 3)
        self.ops.append(('poly', ([(x2 - 13, y - 7), (x2, y), (x2 - 13, y + 7)], color)))

    def image(self, x, y, w, h, path):
        self.ops.append(('image', (x, y, w, h, path)))

    def link(self, x, y, w, h, label, href, **data):
        self.regions.append(dict(x=x, y=y, width=w, height=h, label=label, href=href, **data))

    def section(self, y, number, title, note=''):
        self.text(80, y, number, 23, MINT, True)
        self.text(142, y + 2, title, 36, INK, True)
        if note:
            self.text(142, y + 43, note, 23, MUTED)

    def svg(self):
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
                 '<title id="title">WebGPU 渲染库一图总览：价值、原理、全部 89 项能力、实测效果与复用方向</title>',
                 '<desc id="desc">依据固定源码 ca576b6 整理。10 类能力全量列名并标注接入范围；四张缩略图来自本机真实 WebGPU 运行。图解、推导应用方向与运行证据分别标明。</desc>',
                 '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif}text{font-variant-numeric:tabular-nums}</style>']
        for kind, values in self.ops:
            if kind == 'rect':
                x, y, w, h, fill, stroke, radius = values
                parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke or "none"}"/>')
            elif kind == 'text':
                x, y, value, size, color, bold, id = values
                ident = f' id="{id}"' if id else ''
                parts.append(f'<text{ident} x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}">{escape(value)}</text>')
            elif kind == 'line':
                x1, y1, x2, y2, color, width = values
                parts.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="{width}" fill="none"/>')
            elif kind == 'poly':
                points, color = values
                parts.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in points)}" fill="{color}"/>')
            elif kind == 'image':
                x, y, w, h, path = values
                encoded = base64.b64encode(path.read_bytes()).decode()
                parts.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{encoded}"/>')
        parts.append('</svg>\n')
        return '\n'.join(parts)

    def png(self, font_path, bold_path):
        from PIL import Image, ImageDraw, ImageFont, ImageOps
        canvas = Image.new('RGB', (W, H), BG)
        draw = ImageDraw.Draw(canvas)
        fonts = {}
        for kind, values in self.ops:
            if kind == 'rect':
                x, y, w, h, fill, stroke, radius = values
                draw.rounded_rectangle((x, y, x+w, y+h), radius, fill, stroke, width=1)
            elif kind == 'text':
                x, y, value, size, color, bold, _ = values
                key = size, bold
                if key not in fonts:
                    fonts[key] = ImageFont.truetype(str(bold_path if bold else font_path), size)
                draw.text((x, y), value, fill=color, font=fonts[key], anchor='ls')
            elif kind == 'line':
                x1, y1, x2, y2, color, width = values
                draw.line((x1, y1, x2, y2), color, width)
            elif kind == 'poly':
                points, color = values
                draw.polygon(points, color)
            elif kind == 'image':
                x, y, w, h, path = values
                img = ImageOps.contain(Image.open(path).convert('RGB'), (w, h), Image.Resampling.LANCZOS)
                canvas.paste(img, (x + (w-img.width)//2, y + (h-img.height)//2))
        canvas.save(PROJECT / 'assets/project-overview.png', optimize=True)


def compose(capabilities):
    d = Drawing()
    d.rect(0, 0, W, H, BG, radius=0)
    d.rect(0, 0, 18, H, MINT, radius=0)
    d.text(80, 77, 'RENDER ATLAS   /   009   /   一图入口', 24, MINT, True)
    d.text(1100, 77, '89 项能力 · 14 场景 / 资料 · 163 参数名 · 334 文本取证', 22, MUTED)
    d.text(80, 159, '让光照成为可复用的场景能力', 64, INK, True)
    d.text(82, 213, 'WebGPU Render Pipeline · 浏览器三维光照与自然环境渲染实验工程', 29, MUTED)
    d.rect(80, 248, 2040, 116, '#243d35', '#537c67')
    d.text(108, 294, '核心价值：预先计算复杂间接光，逐帧组合直接光、材质与环境效果。', 32, MINT, True)
    d.text(108, 337, '可沉淀：光照管线、场景接口、水面与植被、资源和缓存、画面合成、诊断工具。', 26, INK)
    d.link(80, 248, 2040, 116, '阅读通俗原理与算法', '#principles')

    d.section(423, '01', '它怎样把三维场景变成画面？', '准备与烘焙 → 读取缓存 → 按当前光源和相机持续成像；以下为流程示意。')
    nodes = [
        ('输入', '三维场景', ['几何 / 材质 / 相机', '太阳 / 环境 HDR'], BLUE),
        ('准备', '采样与估计', ['BVH 加速查找命中', 'Surfel 迭代估计反弹光'], GOLD),
        ('保存', '两类光照缓存', ['Lightmap：静态表面', '空间探针：其他接收对象'], GOLD),
        ('逐帧', '光照与环境', ['直接光 / 阴影 / 缓存光', '水面 / 植被 / 大气'], MINT),
        ('输出', '合成最终画面', ['抗锯齿 / 曝光 / 调色', '同一场景支持连续换视角'], MINT),
    ]
    for i, (phase, title, lines, color) in enumerate(nodes):
        x = 80 + i*414
        d.rect(x, 492, 384, 165, PANEL, LINE)
        d.text(x+22, 527, phase, 21, color, True)
        d.text(x+22, 570, title, 31, INK, True)
        for n, text in enumerate(lines): d.text(x+22, 610+n*29, text, 23, MUTED)
        d.link(x, 492, 384, 165, f'阅读{title}的原理', '#principles')
        if i < 4: d.arrow(x+389, 574, x+409, color)
    d.rect(80, 678, 2040, 97, '#202f31')
    d.text(104, 714, '通俗例子：阳光照红墙，反弹光让旁边的白球偏红；把结果存好，后续每帧读取。', 26, INK)
    d.text(104, 751, '移动相机 → 直接重新绘制；改变太阳 → 直接光与阴影更新，静态间接光仍需重烘焙。', 25, GOLD)

    d.section(835, '02', '能力版图 · 10 类 / 全部 89 项列名', '标记表示源码接入范围；89 为本研究的组织计数，不等于 89 项运行验收。')
    status_used = Counter(x['availability'] for x in capabilities)
    legend_names = [x for x in STATUS if x in status_used]
    # A compact scope key follows the category map, avoiding tiny repeated prose.
    for i, (cat_id, name, _) in enumerate(CATEGORIES):
        x, y = 80 + (i%2)*1030, 913 + (i//2)*400
        items = [item for item in capabilities if item['category'] == cat_id]
        d.rect(x, y, 1010, 380, PANEL, LINE)
        d.text(x+23, y+42, f'{i+1:02d}', 24, MINT, True)
        d.text(x+79, y+43, name, 32, INK, True)
        d.text(x+907, y+41, f'{len(items):02d} 项', 23, MINT, True)
        d.text(x+23, y+82, EFFECTS[cat_id], 23, MUTED)
        d.line(x+23, y+99, x+987, y+99)
        split = math.ceil(len(items)/2)
        for j, item in enumerate(items):
            col, row = divmod(j, split)
            tx, ty = x+24+col*489, y+137+row*32
            short, color = STATUS[item['availability']]
            d.text(tx, ty, '·', 24, color, True)
            d.text(tx+16, ty, item['title'], 24, INK, id=f'capability-{item["id"]}')
            d.rect(tx+425, ty-21, 34, 27, '#263c3b', radius=4)
            d.text(tx+434, ty-1, short, 18, color, True)
        if cat_id == 'integration':
            d.text(x+24, y+240, '工程接入：SceneHost + 原库帧流程 + 固定版本依赖', 24, BLUE)
            d.text(x+24, y+278, '先整理接口与预算，再接目标项目的资产和玩法。', 24, MUTED)
        d.text(x+24, y+354, '逐项效果、算法、条件与固定源码 → 能力清单', 21, MINT)
        d.link(x, y, 1010, 380, f'查看{name}全部 {len(items)} 项能力', f'#group-{cat_id}', category=cat_id)
    for i, name in enumerate(legend_names):
        short, color = STATUS[name]
        x = 80 + i*273
        d.rect(x, 2930, 34, 27, '#263c3b', radius=4)
        d.text(x+9, 2950, short, 18, color, True)
        d.text(x+45, 2951, name, 22, MUTED)

    d.section(3022, '03', '真实效果 · 四个场景已运行', '以下为本机 WebGPU 原始画面缩略图；仅缩放排版，未用 AI 重绘或调色。')
    shots = [
        ('cornell', 'Cornell Box', '看彩色墙面反弹光与投影', 'default-light.png'),
        ('midsee-village', '完整海岸村庄', '看建筑、植被、码头与海水', 'village-default.png'),
        ('beach', '热带海滩', '看浅水、泡沫、浮球与棕榈', 'beach-default.png'),
        ('forest', '针叶林与溪流', '看树群、地表与溪流波纹', 'forest-default.png'),
    ]
    for i, (scene, title, caption, file) in enumerate(shots):
        x, y = 80+i*515, 3098
        d.rect(x, y, 495, 405, PANEL, LINE)
        d.image(x+12, y+12, 471, 293, PROJECT/'assets/runtime'/file)
        d.text(x+18, y+344, title, 27, INK, True)
        d.text(x+18, y+382, caption, 23, MUTED)
        d.link(x, y, 495, 405, f'选择{title}真实演示', '#live-demo', scene=scene)
    d.text(80, 3543, '可调太阳方位 / 高度 / 强度，以及相机环绕 / 仰角 / 距离；可切细节视角、暂停与重烘焙。', 25, MINT)

    d.section(3617, '04', '可复用到哪里？', '以下为基于能力的应用方向，需要在目标项目中集成和验收。')
    uses = [
        ('浏览器游戏', '海岛探索 / 农场 / 场景漫游', '复用环境光、阴影与自然材质'),
        ('建筑与空间漫游', '室内外空间 / 场景展示', '呈现受光关系与空间层次'),
        ('产品与 Web3D 展厅', '材质展示 / 互动场景', '组织环境反射、阴影与镜头'),
        ('图形学教学与研究', '拆通道 / 对比 / 算法实验', '观察光路、缓存与性能取舍'),
    ]
    for i, (title, line1, line2) in enumerate(uses):
        x = 80+i*515
        d.rect(x, 3694, 495, 136, PANEL, LINE)
        d.text(x+20, 3735, title, 29, BLUE, True)
        d.text(x+20, 3772, line1, 23, INK)
        d.text(x+20, 3806, line2, 22, MUTED)
    d.rect(80, 3851, 2040, 107, '#243b34', '#426456')
    d.text(105, 3890, '沉淀路线：固定依赖 → 抽离场景与渲染接口 → 整理资产和缓存 → 调整预算 → 目标设备验收', 27, MINT, True)
    d.text(105, 3933, '复用的是“场景怎样被看见”。角色操作、任务、战斗、存档等玩法系统由游戏项目另外实现。', 25, INK)
    d.link(80, 3851, 2040, 107, '阅读架构、运行与复用条件', '#boundaries')

    d.section(4024, '05', '一起理解这些边界')
    boundaries = [
        ('验证与画质', ['四个场景的指定配置通过，非全库验收。', '海滩 / 村庄：原库浅水模拟。', '森林：不透明波纹溪流；海滩房车未加载。', '低分辨率烘焙仍有噪声与少量告警。']),
        ('复用与工程条件', ['需要 WebGPU 与足够的设备计算上限。', '使用作者 Three.js / R3F fork 的固定版本。', '本次有一条有效表面补采样修复。', '尚未做跨设备 FPS / 全库类型检查。']),
        ('能力定位', ['依据三维几何与数值近似成像。', '没有现成 AI 接口；可另外辅助制作资产。', '未包含完整游戏玩法与生产级插件接口。', '采光可视化不等于定量建筑日照分析。']),
    ]
    for i, (title, lines) in enumerate(boundaries):
        x = 80+i*689
        d.rect(x, 4055, 662, 205, '#272f2b', '#4e5c4c')
        d.text(x+20, 4097, title, 29, GOLD, True)
        for j, line in enumerate(lines): d.text(x+20, 4135+j*31, line, 23, INK)
        d.link(x, 4055, 662, 205, f'阅读{title}的准确范围', '#boundaries')
    d.text(80, 4310, '阅读路径：一图总览 → 亲手调画面 → 看原理与 AI 对照 → 查 89 项能力 → 按源码与运行记录复现', 27, MINT, True)
    d.text(80, 4350, '依据：vibegameengine/web-starter-kit-webgpu-pipline @ ca576b6 · 中文研究 009 · 2026-10-22', 23, MUTED)
    d.text(80, 4383, '原库未提供仓库级 LICENSE；来源、依赖许可、补丁与实测边界见研究资料。图解为本研究原创。', 21, MUTED)
    return d, shots


def generate_overview(check=False, render_png=False, font=None, bold_font=None):
    capabilities = json.loads((PROJECT/'capabilities.json').read_text(encoding='utf-8'))
    assert len(capabilities) == len({x['id'] for x in capabilities}) == 89
    drawing, shots = compose(capabilities)
    svg = drawing.svg()
    assert len(re.findall(r'id="capability-[^"]+"', svg)) == 89
    svg_path = PROJECT/'assets/project-overview.svg'
    svg_hash = hashlib.sha256(svg.encode('utf-8')).hexdigest()
    png_path = PROJECT/'assets/project-overview.png'
    record_path = PROJECT/'overview.json'
    if render_png:
        assert not check
        regular = Path(font or 'C:/Windows/Fonts/msyh.ttc')
        bold = Path(bold_font or (font if font else 'C:/Windows/Fonts/msyhbd.ttc'))
        assert regular.is_file() and bold.is_file(), 'Provide Chinese fonts using --font and --bold-font'
        drawing.png(regular, bold)
    else:
        assert record_path.is_file() and png_path.is_file(), 'Build first: build_overview.py --render-png'
        old = json.loads(record_path.read_text(encoding='utf-8'))
        assert old['svg_sha256'] == svg_hash and old['png_sha256'] == sha(png_path), 'Overview changed; regenerate PNG with --render-png'
    record = {
        'title':'WebGPU 渲染库一图总览', 'date':'2026-10-22', 'upstream_commit':'ca576b601bf84527102f1768372aa8cd96a3c55a',
        'dimensions':{'width':W,'height':H}, 'capability_ids':[x['id'] for x in capabilities],
        'category_counts':dict(Counter(x['category'] for x in capabilities)),
        'svg_sha256':svg_hash, 'png_sha256':sha(png_path),
        'inputs':{str(p.relative_to(PROJECT)).replace('\\','/'):sha(p) for p in [PROJECT/'capabilities.json',*[PROJECT/'assets/runtime'/x[3] for x in shots]]},
        'scope':'Original explanatory infographic; all 89 capability titles and source scopes; four real screenshots scaled for composition; application directions are inferred, not finished product integrations',
        'hotspots':drawing.regions,
    }
    anchors = []
    for region in drawing.regions:
        attrs = ' '.join(f'data-overview-{k}="{v}"' for k,v in region.items() if k in ('category','scene'))
        style = ';'.join(f'{key}:{100*region[val]/base:.5f}%' for key,val,base in [('left','x',W),('top','y',H),('width','width',W),('height','height',H)])
        anchors.append(f'          <a class="overview-hotspot" href="{region["href"]}" {attrs} style="{style}" aria-label="{region["label"]}" title="{region["label"]}"><span class="sr-only">{region["label"]}</span></a>')
    page_path = PROJECT/'web/index.html'
    page = page_path.read_text(encoding='utf-8')
    start, end = '<!-- OVERVIEW_HOTSPOTS_START -->', '<!-- OVERVIEW_HOTSPOTS_END -->'
    assert page.count(start) == page.count(end) == 1
    updated_page = page[:page.index(start)+len(start)]+'\n'+'\n'.join(anchors)+'\n          '+page[page.index(end):]
    outputs = {svg_path:svg, record_path:json.dumps(record,ensure_ascii=False,indent=2)+'\n', page_path:updated_page}
    for path, value in outputs.items():
        if check:
            assert path.is_file() and path.read_text(encoding='utf-8') == value, f'Overview output differs: {path}'
        else:
            path.write_text(value,encoding='utf-8')
    return {'overview_capabilities':89,'overview_categories':10,'overview_hotspots':len(drawing.regions),'overview_png':'hash_verified'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--render-png',action='store_true')
    parser.add_argument('--font')
    parser.add_argument('--bold-font')
    args = parser.parse_args()
    print(json.dumps(generate_overview(args.check,args.render_png,args.font,args.bold_font),ensure_ascii=False))
