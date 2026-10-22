"""Show actual aquatic papers and exported cloud answers on local Gradio."""
import ast
import json
import os
from urllib.parse import quote
import gradio as gr
from run_apd import PROJECT, UPSTREAM, configure

config = configure()
from apd.db import init_db, list_papers
from aquatic_research import PERIOD

init_db()
os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")


def local_file(path):
    if not path:
        return None
    from pathlib import Path
    target = Path(path)
    return "/file=" + quote(target.as_posix(), safe="/:") if target.is_file() else None


def metadata():
    papers = []
    for paper in list_papers(week_id=PERIOD):
        papers.append({
            "paper_id": paper.paper_id, "title": paper.title,
            "pdf_url": local_file(paper.pdf_path) or paper.pdf_url,
            "hf_url": paper.hf_url,
            "video_url": local_file(paper.video_path),
            "slides_url": local_file(paper.slides_path), "summary": paper.summary,
        })
    return {"weeks": {PERIOD: papers}}


# Execute only the upstream show_papers function, avoiding its remote dataset
# download and top-level server launch. Keep the original video/slides rendering.
source = ast.parse((UPSTREAM / "portal" / "app.py").read_text(encoding="utf-8"))
function = next(node for node in source.body if isinstance(node, ast.FunctionDef) and node.name == "show_papers")
namespace = {"load_metadata": metadata}
exec(compile(ast.Module(body=[function], type_ignores=[]), str(UPSTREAM / "portal" / "app.py"), "exec"), namespace)


def refresh():
    papers = list_papers(week_id=PERIOD)
    rows = [[p.paper_id, p.status, "已下载" if p.video_path else "待生成 / 下载", p.title] for p in papers]
    rendered = namespace["show_papers"](PERIOD).replace("🤗 HuggingFace Paper", "🔎 原文来源")
    videos = sum(bool(p.video_path) for p in papers)
    message = f"已准备 {len(papers)} 篇水生毒理学论文；原 APD/NotebookLM 生成视频 {videos} 个。"
    if videos == 0:
        message += " 原 NotebookLM 路线未完成生成；下方解读来自云端 Open Notebook + MiniMax 的真实运行。"
    return message, rows, rendered


RESULTS = PROJECT / "results"
EXPORT_NAMES = [
    "open-notebook-single-answer.md", "open-notebook-synthesis-answer.md",
    "open-notebook-single-truncated.md", "open-notebook-minimax-check.json",
    "open-notebook-cloud-check.json", "open-notebook-publication-diagnostics.json",
]
EXPORTS = [RESULTS / name for name in EXPORT_NAMES if (RESULTS / name).is_file()]


def exported_answer(name):
    path = RESULTS / name
    return path.read_text(encoding="utf-8") if path.is_file() else "该实测产出尚未生成。"


with gr.Blocks(title="008 · 水生毒理学实测结果") as demo:
    gr.Markdown("# 水生毒理学 · 真实研究结果")
    gr.Markdown("**结果查看页** · 2026-10-22 · 三篇原始论文 → 云端 Open Notebook → MiniMax 解读。此页读取本次运行保存的真实回答，保留模型原文和错误。")
    gr.Markdown("云端主界面仍缺少可用的浏览器访问入口；本页可查看与下载已有产出，不发送新的模型请求。")
    state = gr.Markdown()
    gr.Markdown("| 论文输入 | 完整研究回答 | 本轮模型调用 | 音频 / 视频 |\n| --- | --- | --- | --- |\n| 3 份期刊 PDF，SHA256 已核对 | 单篇 1,460 字符 · 综合 3,056 字符 | 3 次，含 1 次截断 | 0 / 0 |")
    gr.Markdown("**阅读提示：** 原文中的“羊头鱼 / 羊头鰕鲷”俗名不准确，请使用 *Cyprinodon variegatus*；综合回答对“发育毒性”的归纳过宽。关键数值已抽查，全部回答尚未逐句科学审定。")
    with gr.Tabs():
        with gr.Tab("单篇论文解读"):
            gr.Markdown("### PFOS 与 PFOA 的混合毒性\n论文：[PMC10819493 · DOI 10.3390/toxics12010091](https://doi.org/10.3390/toxics12010091)。以下为模型完整原文；`source:…` 为原生来源标记，不能点击定位 PDF 段落。")
            gr.Markdown(exported_answer("open-notebook-single-answer.md"))
        with gr.Tab("三篇综合比较"):
            gr.Markdown("### 斑马鱼 · 鲫鱼 · Cyprinodon variegatus\n以下保留模型完整原文。研究建议属于待验证假设；不同物种、剂量、时长和终点不能直接作毒性排序。")
            gr.Markdown(exported_answer("open-notebook-synthesis-answer.md"))
        with gr.Tab("论文与原始 PDF"):
            gr.Markdown("### 来源对照\n| 原生来源标记 | 原论文 |\n| --- | --- |\n| `source:vhshfa8xv8wi6xozjagl` | [PMC13162690 · 斑马鱼肝毒性](https://doi.org/10.3390/ani16091368) |\n| `source:bezlz9t8sr5pu12stjfu` | [PMC11851982 · 鲫鱼肝毒性](https://doi.org/10.3390/ani15040610) |\n| `source:i8m54onbhh6bq0q0w7sd` | [PMC10819493 · PFAS 混合效应](https://doi.org/10.3390/toxics12010091) |")
            refresh_button = gr.Button("刷新论文下载记录")
            table = gr.Dataframe(headers=["论文编号", "APD 处理状态", "视频", "论文标题"], interactive=False)
            output = gr.Markdown()
            gr.Markdown("论文卡片保留原 APD 门户渲染。作者摘要与模型解读分别保存，未把 Open Notebook 结果回写为 NotebookLM 成功。")
        with gr.Tab("核对说明与下载"):
            gr.Markdown("### 已核对的边界\n- 1:1 PFOS/PFOA 混合：LC50 1.99 mg/L，与 PFOS 单独 1.97 mg/L 无显著差异。\n- 固定 100 mg/L PFOA 配合 PFOS：LC50 3.10 mg/L，仅此条件提示拮抗，不能推广到所有 PFAS 混合物。\n- 全文上下文问答已运行；向量检索、图表理解和媒体生成未验证。\n- 原版第一次仅返回 350 字符；参数适配后两次完整返回。累计实际 usage 108,597 tokens，不等于账单金额。")
            gr.Markdown("### 下载本次原始产出与脱敏证据\n" + "\n".join(f"- [{p.name}]({local_file(p)})" for p in EXPORTS))
            gr.Markdown("[完整质量核对报告](" + local_file(PROJECT / "open-notebook-effect-review.md") + ")")
    demo.load(refresh, outputs=[state, table, output])
    refresh_button.click(refresh, outputs=[state, table, output])

demo.launch(server_name="127.0.0.1", server_port=7868, show_api=False,
            allowed_paths=[str(config.PDF_DIR), str(config.VIDEO_DIR), str(config.SLIDES_DIR),
                           *(str(p) for p in EXPORTS), str(PROJECT / "open-notebook-effect-review.md")])
