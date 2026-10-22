# 配图与来源

本目录用于研究总览和展示页真实截图。图片不能代替原始 PDF、接口响应或模型回答。

## cover.png

- 用途：项目索引和研究首页的网页效果入口。
- 内容：本项目静态研究网页，展示 3 篇论文的详细精读入口、1 篇跨论文综合与历史模型短回答。
- 来源：2026-10-22 本项目本地展示页的实际截图，不是云端 Open Notebook 官方界面截图，也不是新生成的论文结论。
- 替代文字：水生毒理学研究档案的实际网页：论文、解读与验证结果。
- 数据出处：[导入证据](open-notebook-cloud-check.json)、[问答证据](open-notebook-minimax-check.json)。

## 其他材料

`reader.png` 为本地静态网页阅读器的实际截图，展示单篇模型原文及独立质量提示。该截图不是 Open Notebook 云端应用界面；与 `cover.png` 同日通过内置浏览器保存，未重绘或修饰。

3 篇论文的作者、DOI、公开 PDF 与 CC BY 许可记录见 [SOURCE.json](SOURCE.json) 和原[论文清单](aquatic-papers.json)。原文归原作者，本研究未修改原始 PDF。

模型回答取自本次原生问答导出，保留原始文字和来源标记；研究代理的理解图、页面编排与核对说明属于本次整理。后续页面截图应记录实际本地页面、日期与验证范围，不能标为已部署云端应用。

`papers/` 保存 3 份字节未改动的原始 PDF；`licenses/` 保存 Open Notebook、Esperanto 与 SurrealDB 的原始许可文本。逐文件来源及 SHA256 见 [接入清单](import-manifest.json)。

## 本轮详细报告配图

`detailed-reader.png` 是 2026-10-22 本项目新增详细报告的实际网页截图，无重绘；展示报告选择、章节目录和精读正文。

`figures/` 保存从三份已归档 PDF 渲染的原文整页 PNG，未改写或标注科学内容，网页提供对应 PDF 页码入口：

| 文件 | 原文位置 | 来源与署名 |
| --- | --- | --- |
| PMC13162690-p05.png / -p10.png | 图2 / 图7 | Zhang 等，Animals 2026，DOI 10.3390/ani16091368，CC BY 4.0 |
| PMC11851982-p07.png / -p10.png | 图1 / 图4 | Tang 等，Animals 2025，DOI 10.3390/ani15040610，CC BY 4.0 |
| PMC10819493-p05.png / -p08.png | 表1 / 图4 | Tanabe 等，Toxics 2024，DOI 10.3390/toxics12010091，CC BY 4.0 |

论文作者、原始地址与许可见 [SOURCE.json](SOURCE.json)，许可说明也随每份原始 PDF 保留。图像是原论文再现，不是本报告新增实验数据。报告中的不确定性与图文差异由研究代理另行解释。

## research-overview.svg

- 用途：将库的能力、底层技术、使用场景、扩展实现与实际效果汇总为一张图。
- 来源：研究代理按固定版本源码和保存的实测证据原创编排，2026-10-22；非上游截图或宣传图。
- 依据：[能力与效果总结](knowledge-summary.md)、[架构证据索引](architecture-evidence.json)。
- 复现：`python projects/011-open-notebook-research/scripts/build_overview_diagram.py`；1600×1500 SVG，可选文本与缩放。字体使用设备已有的微软雅黑/Segoe UI，不附带字体文件。
- 替代文字：Auto Paper Digest 原库流程、Open Notebook 替代分析架构、领域检索与精读扩展、实际产出及验证边界。

`overview-page.png` 为新增总览区的本地网页实际截图，仅证明展示效果，不代表原版云应用已经部署。

`research-overview.png` 为同一 SVG 使用已有 Sharp 运行库渲染的 1600×1500 PNG，便于下载和分享；内容与矢量图一致，未生成额外科学数据。
