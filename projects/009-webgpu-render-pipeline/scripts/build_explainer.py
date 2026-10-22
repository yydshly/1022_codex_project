"""Build the plain-language algorithm guide and web data from one maintained JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def generate_explainer(check=False):
    lesson = json.loads((PROJECT / "explain.json").read_text(encoding="utf-8"))
    capabilities = {item["id"]: item for item in json.loads((PROJECT / "capabilities.json").read_text(encoding="utf-8"))}

    def references(ids):
        result = []
        for item_id in ids:
            item = capabilities[item_id]
            result.append({"title": item["title"], "url": item["source"]["url"]})
        return result

    def links(ids):
        return " · ".join(f"[{item['title']}]({item['url']})" for item in references(ids))

    for item in lesson["algorithms"] + lesson["red_wall"]["steps"]:
        item["sources"] = references(item["references"])

    md = ["# " + lesson["title"], "", lesson["summary"], "", "[展示页的通俗原理](web/index.html#principles) · [AI 区别](web/index.html#ai-comparison) · [详细技术架构](ARCHITECTURE.md) · [完整能力清单](CAPABILITIES.md)", "", "## 先分清三种“模型”", "", "| 词语 | 通俗例子 | 在这里做什么 |", "| --- | --- | --- |"]
    md += [f"| {item['name']} | {item['example']} | {item['meaning']} |" for item in lesson["model_meanings"]]
    md += ["", "这里把“AI 直接处理”理解为常见的图像补光、编辑、重绘或生成。" + lesson["scope"], "", "## 例子一：红墙旁边的白球", "", lesson["red_wall"]["setup"], "", "![红墙旁白球的光路、表面采样、空间探针与缓存复用示意；非运行结果](assets/light-transport-explained.svg)", "", "*" + lesson["red_wall"]["diagram_note"] + "*", ""]
    for index, item in enumerate(lesson["red_wall"]["steps"], 1):
        md += [f"### {index}. {item['title']}", "", item["text"], "", "**记住**：" + item["takeaway"], "", "源码依据：" + links(item["references"]) + "。", ""]
    md += ["### 怎样理解“采样”", "", "可以把它想成：想估计一个房间各方向来的光，先量一批方向，再按权重合成结果。量得更多通常更稳定，但计算也更多。表面某点的入射光估计、材质的反射规则和最后像素颜色属于不同环节，不应把它们全部理解成简单平均亮度。", "", "### 怎样理解“探针插值”", "", "把探针想成固定在空间中的测光站。球移动到两个测光站之间时，按位置和其他权重混合附近数据；实际实现读取周围八个探针，还考虑朝向、遮挡距离、有效状态和室内外层。它是已有测量的插值，不是 AI 猜测一个球该有多亮。", "", "## 九组主要算法：名字、工作与边界", ""]
    for index, item in enumerate(lesson["algorithms"], 1):
        md += [f"### {index:02d}. {item['name']}", "", "**通俗理解**：" + item["plain"], "", "**例子**：" + item["example"], "", "**方法**：" + item["method"], "", "**边界**：" + item["boundary"], "", "源码依据：" + links(item["references"]) + "。", ""]
    md += ["## 与 AI 直接改图的区别", "", "![显式三维渲染与常见 AI 图像重绘的输入、处理和输出对照；两条流程均为教学示意](assets/rendering-vs-ai.svg)", "", "| 对比点 | 本项目的三维渲染管线 | 常见 AI 图像重绘 |", "| --- | --- | --- |"]
    md += [f"| {item['aspect']} | {item['render']} | {item['ai']} |" for item in lesson["comparison"]]
    md += ["", lesson["ai_nuance"], ""]
    for source in lesson["external_sources"]:
        md += [f"参考：[{source['title']}]({source['url']})。{source['purpose']}", ""]
    md += ["## 例子二：同一栋房子的三个问题", ""]
    for item in lesson["scenarios"]:
        md += ["### " + item["title"], "", "- **三维渲染**：" + item["render"], "- **AI 图像处理**：" + item["ai"], "- **如何选择**：" + item["decision"], ""]
    md += ["## 为什么两种方式可以组合", "", "可以用 AI 辅助准备概念、贴图或资产，再让三维场景提供共同的空间依据，交给渲染器持续生成不同视角。也可以把渲染器输出的深度、法线和图像作为图像模型的约束。组合方案需要另外开发接口和验证一致性，不是当前库已具备的完整工作流。", "", "## 图解与验证范围", "", lesson["illustration_scope"], "", "这些讲解新增为研究资料，没有增加原清单的 89 项能力计数。交互步骤只选择图解和说明，不会运行 GI 求解或 AI 推理。验证记录见 [verification.md](verification.md)。", ""]
    outputs = {"PRINCIPLES-AND-AI.md": "\n".join(md), "web/explain-data.js": "window.EXPLAINER = " + json.dumps(lesson, ensure_ascii=False, separators=(",", ":")) + ";\n"}
    for relative, content in outputs.items():
        path = PROJECT / relative
        if check:
            assert path.is_file() and path.read_text(encoding="utf-8") == content, f"Explainer output differs: {relative}"
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    return {"algorithm_groups": len(lesson["algorithms"]), "light_steps": len(lesson["red_wall"]["steps"]), "comparison_rows": len(lesson["comparison"]), "everyday_scenarios": len(lesson["scenarios"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate_explainer(args.check), ensure_ascii=False))
