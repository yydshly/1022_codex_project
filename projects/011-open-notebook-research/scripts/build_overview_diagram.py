"""Build the evidence-based project overview as selectable vector text."""
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/research-overview.svg"
W, H = 1600, 1500
C = dict(paper="#f6f5ef", white="#fffef9", ink="#193d36", text="#334a44", muted="#6e8073", line="#d5ded0", green="#285f50", mint="#e5eee4", blue="#397e8a", pale="#e9f1f2", amber="#876234", amberbg="#f5eedf")
parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="overview-title overview-desc">
<title id="overview-title">从论文自动摘要库到水生毒理学研究档案：能力、架构、扩展与效果</title>
<desc id="overview-desc">本图分开呈现 Auto Paper Digest 原库流程、Open Notebook 与 MiniMax 的实际分析路线，以及研究代理新增的详细精读。原库负责 AI 论文采集与 NotebookLM 生成编排；我们的领域检索扩展获得三篇论文，替代路线产生两份完整短回答，研究代理另行完成三篇精读及一篇综合，当前网页只展示结果。没有生成音视频或 embedding，原版云应用用户访问没有打通。</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 L8 5 L1 9" fill="none" stroke="{C['muted']}" stroke-width="1.4"/></marker></defs>
<style>text{{font-family:'Microsoft YaHei','Segoe UI',sans-serif}}.small{{font-size:19px}}.body{{font-size:21px}}.title{{font-size:26px;font-weight:600}}.section{{font-size:25px;font-weight:600}}.metric{{font-size:32px;font-weight:600}}.headline{{font-size:45px;font-weight:600}}</style>
<rect width="1600" height="1500" fill="{C['paper']}"/>''']


def rect(x, y, w, h, fill="white", stroke="line", radius=10, dashed=False):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{C.get(fill, fill)}" stroke="{C.get(stroke, stroke)}" stroke-width="1.5"' + (' stroke-dasharray="7 5"' if dashed else '') + '/>')


def text(x, y, value, cls="body", color="text", **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    parts.append(f'<text x="{x}" y="{y}" class="{cls}" fill="{C.get(color, color)}" {extra}>{escape(value)}</text>')


def lines(x, y, values, cls="body", color="text", step=30):
    for i, value in enumerate(values):
        text(x, y + i * step, value, cls, color)


def label(x, y, number, heading):
    text(x, y, number, "section", "blue")
    text(x+49, y, heading, "section", "ink")


def node(x, y, heading, body, fill="white", dashed=False):
    rect(x, y, 232, 103, fill, dashed=dashed)
    text(x+18, y+32, heading, "body", "ink", font_weight=600)
    lines(x+18, y+63, body, "small", "text", 26)


def arrows(y):
    for i in range(4):
        x=230+i*256+236
        parts.append(f'<path d="M{x} {y}H{x+17}" fill="none" stroke="{C["muted"]}" stroke-width="1.5" marker-end="url(#arrow)"/>')


text(48, 55, "OPEN-SOURCE RESEARCH / 011", "small", "blue", letter_spacing=2)
text(48, 112, "从论文自动摘要，到可核对的研究理解", "headline", "ink")
text(48, 153, "一张图读懂：库能做什么、如何运行、适合谁、我们改了什么，以及实际得到什么。", "body")
rect(1155, 33, 397, 38, "mint", "mint", 19)
text(1174, 59, "实测快照 · 2026.10.22 · 水生毒理学", "small", "green")

label(48, 207, "01", "能力与使用场景")
rect(1065, 186, 26, 22, "mint", "#b4cbb6", 4)
text(1101, 204, "本次已验证", "small", "green")
rect(1270, 186, 26, 22, "white", "muted", 4, dashed=True)
text(1307, 204, "源码能力 / 未跑通", "small", "amber")
cards = [
    (48, "Auto Paper Digest · 自动编排", ["AI 论文榜单采集、PDF 下载与状态管理", "连接 NotebookLM：摘要、视频、幻灯片", "适合：论文追踪、周报与内容整理"], "white"),
    (556, "Open Notebook · 资料与问答", ["管理来源、提取文本、问答与保存笔记", "模型通过 provider 接入，可选择服务商", "适合：专题阅读、多篇比较、资料归纳"], "white"),
    (1064, "我们的场景 · 水生毒理学", ["检索 PFAS / PFOS 对鱼类的毒性研究", "理解实验、图表、统计与机制证据", "最终阅读：详细报告＋原文＋核对记录"], "mint"),
]
for x, heading, body, fill in cards:
    rect(x, 227, 488, 151, fill)
    text(x+22, 263, heading, "title", "ink")
    lines(x+22, 300, body, "small", step=29)

label(48, 424, "02", "底层技术与两条路线")
rect(48, 445, 1504, 154, "white", dashed=True)
text(70, 480, "原库路径", "title", "ink")
lines(70, 514, ["源码已核对", "生成未跑通"], "small", "amber", 29)
original_nodes = [
    ("Hugging Face", ["日 / 周榜采集", "arXiv PDF"]),
    ("Python + SQLite", ["编排 / 状态登记", "下载与去重"]),
    ("Playwright", ["控制 NotebookLM", "云端分析与生成"]),
    ("NotebookLM 产物", ["摘要 / 视频 / 幻灯片", "本次没有产出"]),
    ("归档与展示", ["本地文件 + Gradio", "独立发布流程"]),
]
for i, (heading, body) in enumerate(original_nodes):
    node(230+i*256, 468, heading, body, "paper", dashed=i in (2, 3))
arrows(519)

rect(48, 615, 1504, 226, "mint", "#b4cbb6")
text(70, 652, "实测路径", "title", "ink")
lines(70, 686, ["领域检索扩展", "替换分析路线", "已得到回答"], "small", "green", 29)
actual_nodes = [
    ("Europe PMC", ["REST 检索 / JATS", "MDPI 公开 PDF"]),
    ("Python 适配", ["PMCID → SQLite", "SHA-256 校验"]),
    ("Open Notebook", ["content-core 提取", "SurrealDB 保存"]),
    ("全文上下文问答", ["原生聊天 API", "Esperanto→MiniMax"]),
    ("保存原始输出", ["2 份完整短回答", "1 次截断另存"]),
]
for i, (heading, body) in enumerate(actual_nodes):
    node(230+i*256, 639, heading, body)
arrows(690)
parts.append(f'<path d="M230 765H1486" stroke="{C["line"]}"/>')
text(230, 794, "应用栈：Next.js / React → FastAPI → LangGraph / LangChain；surreal-commands 提供异步任务机制。", "small", "green")
text(230, 825, "本次选定来源全文送入模型；未生成 embedding。模型调用在云端，结果阅读不依赖云端服务。", "small", "green")

label(48, 888, "03", "我们做的四层扩展，以及如何扩展")
extensions = [
    ("1 · 扩展文献输入", ["Europe PMC REST 检索", "JATS → MDPI PDF 获取", "PMCID 登记 + SHA-256"]),
    ("2 · 适配分析引擎", ["原生聊天 API → MiniMax", "low 推理 / max_retries=0", "输出上限保留 8192 tokens"]),
    ("3 · 加深理解与核对", ["研究代理重新精读原文与图表", "分析实验 / 统计 / 机制证据", "3 份逐篇精读 + 1 份综合"]),
    ("4 · 扩展结果呈现", ["HTML / CSS / JS 只读网页", "页码引用 + 结构化证据 JSON", "图页 / Markdown / 离线 ZIP"]),
]
for i, (heading, body) in enumerate(extensions):
    x=48+i*380
    rect(x, 909, 364, 166, "pale" if i < 2 else "white")
    text(x+20, 949, heading, "title", "ink")
    lines(x+20, 988, body, "small", step=29)
text(48, 1108, "归属说明：后两层是本轮研究整理；详细精读不是 APD / NotebookLM / MiniMax 自动产出的效果。", "small", "blue")

label(48, 1154, "04", "实际效果：拿到了什么，质量到哪里")
effects = [
    (48, "资料获取", "916 → 30 → 3", ["检索命中 → 保存候选 → 选取论文", "3 份原始 PDF / 51 页，哈希一致", "效果：获得可追溯的研究输入"]),
    (556, "模型初读", "2 份完整短回答", ["1,460 / 3,056 字符；另有 350 字截断", "能抽取关键条件；仍有译名与概括问题", "效果：可做初读草稿，需回原文核对"]),
    (1064, "详细理解与呈现", "3 篇精读 + 1 篇综合", ["逐篇约 4,000–4,500 汉字", "6 张图页 / 119 处 PDF 页码引用", "效果：解释依据、发现矛盾、形成后续问题"]),
]
for x, heading, metric, body in effects:
    rect(x, 1175, 488, 185, "white")
    text(x+22, 1209, heading, "small", "blue")
    text(x+22, 1251, metric, "metric", "ink")
    lines(x+22, 1288, body, "small", step=27)

rect(48, 1380, 1504, 68, "amberbg", "#e1d6bf", 8)
text(68, 1408, "验证边界：未生成音频、视频、幻灯片或 embedding；原版云应用的用户入口未打通；当前网页仅阅读已保存结果。", "small", "amber")
text(68, 1435, "详细精读核对主文与关键图表，未重算原始实验数据；3 篇样本不构成系统综述，也未量化提效或准确率。", "small", "amber")
text(48, 1480, "依据：固定源码 + 本地实测证据 + 原论文精读  ｜  APD e1663ba · Open Notebook a0f6f30（镜像另记）", "small", "muted")
parts.append('</svg>')
svg="\n".join(parts)+"\n"
ET.fromstring(svg)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT.name}: {W} × {H}; {len(svg)} characters; valid XML.")
