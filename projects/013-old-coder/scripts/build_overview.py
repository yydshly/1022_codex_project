"""Draw the original, editable overview and export its matching high-res PNG.

Generation requires Pillow and a local Chinese font; verification uses stdlib.
Two built-in ImageGen calls failed on network transport; no API fallback used.
"""
from __future__ import annotations
import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
WEB = ROOT / "web/assets"
WIDTH, HEIGHT = 1800, 2600
PAPER, INK, MUTED = "#f4f1e9", "#202a24", "#697361"
ORANGE, GREEN, LINE = "#bc4b2d", "#226b4a", "#cdd3c2"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    metadata = json.loads((ASSETS / "overview-generation.json").read_text(encoding="utf-8"))
    for file in metadata["files"]:
        assert digest(ASSETS / file["name"]) == file["sha256"], file["name"]
        assert (ASSETS / file["name"]).read_bytes() == (WEB / file["name"]).read_bytes()
    svg = (ASSETS / "old-coder-overview.svg").read_text(encoding="utf-8")
    for phrase in ["写清验收标准", "多层质量检查", "库存 0", "库存 9", "原子提交模型", "完整对话", "CI", "教学模型"]:
        assert phrase in svg, phrase
    print("Overview OK: SVG/PNG identities, release copies and required content match.")


def build(font_path, bold_path):
    from PIL import Image, ImageDraw, ImageFont, __version__ as pillow_version
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    fragments = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"><title>Old Coder：能力、原理、场景与价值总览</title><desc>以重复通知只能扣一次库存的教学案例解释证据优先的 AI 编码。</desc><rect width="1800" height="2600" fill="{PAPER}"/>']
    fonts = {}
    def font(size, bold=False):
        key = (size, bold)
        if key not in fonts:
            fonts[key] = ImageFont.truetype(str(bold_path if bold else font_path), size)
        return fonts[key]
    def rect(x,y,w,h,fill,stroke=None,radius=0):
        draw.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=fill,outline=stroke,width=2)
        fragments.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')+'/>')
    def line(x1,y1,x2,y2,color=LINE,width=2):
        draw.line((x1,y1,x2,y2),fill=color,width=width)
        fragments.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def text(x,y,value,size=30,color=INK,bold=False):
        draw.text((x,y),value,font=font(size,bold),fill=color,anchor="lt")
        fragments.append(f'<text x="{x}" y="{y}" dominant-baseline="text-before-edge" font-family="Microsoft YaHei,Noto Sans CJK SC,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')
    def wrap(x,y,value,max_width,size=28,color=INK,bold=False,leading=1.6):
        cursor = y
        for paragraph in value.split("\n"):
            current = ""
            for char in paragraph:
                if current and font(size,bold).getlength(current+char) > max_width:
                    text(x,cursor,current,size,color,bold); cursor += size*leading; current = ""
                current += char
            if current:
                text(x,cursor,current,size,color,bold); cursor += size*leading
        return cursor
    def arrow(x1,y1,x2,y2,color=MUTED,width=3):
        line(x1,y1,x2,y2,color,width)
        if x1 == x2:
            direction_y=1 if y2>y1 else -1
            points=[(x2-7,y2-11*direction_y),(x2,y2),(x2+7,y2-11*direction_y)]
        else:
            direction=1 if x2>x1 else -1
            points=[(x2-11*direction,y2-7),(x2,y2),(x2-11*direction,y2+7)]
        draw.line(points,fill=color,width=width)
        fragments.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}"/>')
    def section(number,title,y):
        text(110,y+7,number,23,ORANGE,True); text(175,y,title,40,INK,True)
    def document_icon(x,y,color):
        rect(x,y,40,47,PAPER,color,3)
        for i in range(3): line(x+10,y+13+i*10,x+30,y+13+i*10,color,2)
    def check_icon(x,y,color):
        rect(x,y,46,46,PAPER,color,7)
        line(x+10,y+24,x+20,y+33,color,4); line(x+20,y+33,x+37,y+12,color,4)
    def stack_icon(x,y,color):
        for i in range(3): rect(x+i*5,y+16-i*8,40,30,PAPER,color,3)
    def evidence_icon(x,y,color):
        document_icon(x,y,color); line(x+9,y+32,x+17,y+39,color,3); line(x+17,y+39,x+30,y+24,color,3)

    # Header: positioning and one-sentence value.
    text(112,59,"013 / OPEN SOURCE RESEARCH",21,MUTED)
    text(111,112,"Old Coder",99,INK,True)
    rect(1490,115,198,88,INK,radius=6); text(1518,137,"oc_",46,PAPER,True)
    text(113,249,"让 AI 写的代码，有据可验",55,ORANGE,True)
    text(113,333,"把验收经验写成可复用 Skill，交付可复跑证据。",31,MUTED)
    line(110,399,1690,399)

    # Capabilities: no invented testing runtime.
    section("01","能力是什么？",433)
    capabilities=[("写清验收标准",document_icon),("测试先行",check_icon),("多层质量检查",stack_icon),("交付证据报告",evidence_icon)]
    for i,(title,icon) in enumerate(capabilities):
        x=110+i*400
        rect(x,506,380,122,"#ebeede",radius=5);icon(x+22,542,GREEN);text(x+91,550,title,30,INK,True)
    text(112,653,"old-coder：开发流程与证据",28,INK)
    text(890,653,"old-coder-api：HTTP/JSON 接口规则",28,INK)
    rect(110,707,1580,63,"#e7e5d9",radius=3)
    text(135,724,"Markdown 规则 + 参考文档 + 模板  →  编程 Agent + 测试工具",28,MUTED)

    # The six stages with an explicit repeat loop.
    section("02","原理：先定义怎么算对，再验证",813)
    stages=[("规格确认","SPEC"),("先看到失败","RED"),("实现通过","GREEN"),("整理代码","REFACTOR"),("多层检查","GAUNTLET"),("证据报告","EVIDENCE")]
    for i,(title,english) in enumerate(stages):
        x=110+i*268
        rect(x,886,240,112,INK if i in (0,5) else "#e6eadc",radius=5)
        text(x+23,908,title,29,PAPER if i in (0,5) else INK,True)
        text(x+23,958,english,20,"#cedbbf" if i in (0,5) else MUTED)
        if i<5:arrow(x+245,941,x+262,941)
    line(1030,1006,1030,1030,GREEN);line(1030,1030,507,1030,GREEN);arrow(507,1030,507,1006,GREEN)
    text(663,1044,"逐项行为循环",22,GREEN)
    text(112,1095,"测试 · 类型 · 覆盖率 · 变异测试 · 随机输入 · 真实执行",28,MUTED)

    # Business example is the visual center, with exact stock numbers.
    section("03","实际场景：支付通知重复，库存只能扣一次",1173)
    text(113,1242,"一笔订单  ·  初始库存 10  ·  同一通知重复 10 次",29,MUTED)
    for i in range(10):
        x=115+i*56;rect(x,1300,41,29,PAPER,ORANGE,2);line(x,1300,x+20,1315,ORANGE);line(x+20,1315,x+41,1300,ORANGE)
    arrow(718,1314,813,1314,ORANGE)
    text(845,1295,"同一验收标准，检查不同实现",29,INK,True)
    panels=[(110,"#f2e3db",ORANGE,"缺陷实现","每次通知都扣库存","库存 0","FAIL"),(920,"#e3ecda",GREEN,"修复实现 · 原子提交模型","防重复记录与扣库存原子提交","库存 9","PASS")]
    for x,fill,color,label,description,stock,status in panels:
        rect(x,1360,770,252,fill,radius=6)
        text(x+30,1387,label,33,color,True)
        rect(x+625,1383,113,42,color,radius=3);text(x+644,1393,status,22,PAPER,True)
        text(x+31,1452,description,27,INK)
        text(x+31,1507,stock,67,color,True)
        # Warehouse boxes, a meaningful illustration of business stock.
        rect(x+640,1500,80,70,PAPER,color,3);line(x+680,1500,x+680,1532,color,3);line(x+657,1534,x+702,1534,color,3)
    cards=[("开发前 · SPEC","通知 10 次只扣 1 次；并发、重启、中断重试也要检查。"),("开发中 · 测试","旧实现先失败\n修复后通过\n故意改坏，测试应报警"),("开发后 · EVIDENCE","需求 → 测试 → 命令\n结果 → 源码版本\n保留可复跑入口")]
    for i,(heading,body) in enumerate(cards):
        x=110+i*538
        rect(x,1641,504,225,"#faf8f2",LINE,4);text(x+24,1665,heading,29,INK,True)
        wrap(x+24,1721,body,456,27,MUTED,leading=1.6)
    text(113,1888,"业务案例为教学模型，未接入真实支付系统或数据库。",25,MUTED)

    section("04","适合哪些任务？",1950)
    scenarios=["修复 Bug 与防回归","订单、库存等关键逻辑","权限与多租户","并发与公共 API"]
    for i,label in enumerate(scenarios):
        x=110+i*400
        rect(x,2025,380,89,"#e8ebdf",radius=4);text(x+20,2055,label,27,INK,True)
    text(113,2141,"选择标准：预期行为能写清楚，且出错代价较高。",27,MUTED)

    section("05","核心价值",2210)
    rect(110,2280,1580,214,INK,radius=6)
    text(146,2313,"减少反复提醒，让验收可审查、可复跑。",42,PAPER,True)
    text(146,2390,"完整对话也能提出同样要求；Skill 的增量在复用与减少遗漏。",26,"#d8e2cf")
    text(146,2435,"测试通过不等于绝对正确；强制门槛仍需测试脚本与 CI。",26,"#d8e2cf")
    text(112,2533,"013 · 开源项目研究  |  AmazingAng/old-coder  |  a0eb529 · MIT",23,MUTED)
    fragments.append("</svg>")
    ASSETS.mkdir(parents=True,exist_ok=True);WEB.mkdir(parents=True,exist_ok=True)
    svg=ASSETS / "old-coder-overview.svg";png=ASSETS / "old-coder-overview.png"
    svg.write_text("\n".join(fragments)+"\n",encoding="utf-8");image.save(png,optimize=True)
    files=[{"name":p.name,"sha256":digest(p),"bytes":p.stat().st_size} for p in (svg,png)]
    metadata={"date":"2026-10-22","kind":"original code-native infographic","method":"Editable SVG and matching PNG drawn from the same text/shape operations; Pillow raster output.","dimensions":[WIDTH,HEIGHT],"upstreamCommit":"a0eb529d393a1cb3ccc564e32b2104e7e75c7a29","files":files,"renderer":{"pillow":pillow_version,"font":str(font_path),"boldFont":str(bold_path)},"imagegenAttempts":[{"attempt":1,"status":"failed","reason":"network error: error sending request"},{"attempt":2,"status":"failed","reason":"network error: error sending request"}],"apiFallbackUsed":False,"failedImagegenPrompt":"overview-imagegen-prompt.txt","contentSource":"Fixed upstream skill sources and this project's analysis; the stock example is a teaching model, not a live business-system test."}
    (ASSETS / "overview-generation.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for p in [svg,png,ASSETS/"overview-generation.json",ASSETS/"overview-imagegen-prompt.txt"]:shutil.copyfile(p,WEB/p.name)
    print(f"Wrote {WIDTH}x{HEIGHT} overview PNG + editable SVG")
    verify()


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true")
    parser.add_argument("--font",type=Path,default=Path("C:/Windows/Fonts/msyh.ttc"))
    parser.add_argument("--bold-font",type=Path,default=Path("C:/Windows/Fonts/msyhbd.ttc"))
    args=parser.parse_args()
    if args.check:verify()
    else:build(args.font,args.bold_font)
