# 我们的理解：库的能力、架构、场景、扩展与实际效果

研究快照：2026-10-22。本文总结固定版本源码及本次真实测试；不是当前云服务价格、产品全量能力或模型排名调查。

## 研究摘要

本次从 Auto Paper Digest 出发，验证它能否支持水生毒理学论文的理解与整理。原库用 Python / SQLite 管理论文和处理状态，以 Playwright 调用 NotebookLM，用 Gradio 展示产物，并提供归档发布步骤。我们先补充 Europe PMC 检索和公开 PDF 获取；NotebookLM 接入没有取得生成结果后，转向 Open Notebook 的 Next.js 前端、FastAPI 后端与 SurrealDB 资料库，经 Esperanto 接入 MiniMax。随后通过参数适配取得完整短回答，再由研究代理精读原文，补足实验、图表、统计和机制分析。

最终目的，是让用户在网页中读到有来源、有分析深度、能够复核的研究结果。本次已形成 3 篇精读、1 篇综合、2 份历史模型短回答以及原 PDF 和验证证据。当前发布静态成果网站；完整应用的持续访问、用户上传和在线生成仍不在已交付能力中。

### 路线如何切换

1. **输入切换：AI 论文榜单 → 水生毒理学检索。** 原入口与选题不匹配，因此新增 Europe PMC REST 查询、PMCID 登记与所选公开 PDF 下载规则，得到真实的领域论文输入。
2. **生成切换：NotebookLM → Open Notebook + MiniMax。** NotebookLM 企业许可及个人 HTTP 接入受阻，未生成内容；替代路线通过应用原生 REST 接口组织来源全文并调用模型，保留一次截断和两次完整返回记录。
3. **深度扩展：模型短回答 → 原文精读与交叉核对。** 完整返回仍有译名、概括和引用问题，因此读取 51 页原文并核对关键图页，形成详细理解和证据边界。
4. **交付切换：完整云端应用 → 静态研究网页。** 云机内 API 验证通过，但用户应用入口未打通。停止该访问排查后，将已验证材料、详细报告及失败记录打包发布，让用户直接阅读和下载。

这是逐步探索的替代路径，并非已实现的自动服务切换引擎。下面分别说明各库原生能力与本次实测结果。

![能力、架构、扩展与效果总览](../assets/research-overview.svg)

## 1. 先分清三个对象

**Auto Paper Digest 是论文处理流程的编排工具。** 原生输入为 Hugging Face 日榜、周榜与 arXiv 论文。它将采集、PDF 下载、处理状态、NotebookLM 会话操作、摘要/视频/幻灯片生成与下载、本地归档和发布串联起来。Python 负责流程，NotebookLM 承担云端分析与生成。媒体生成代码存在，不等于本次成功产出了媒体。未找到独立音频文件生成与下载链路。

**Open Notebook 是资料组织和模型交互应用。** 它管理笔记本与来源、提取文本、组织问答上下文，通过 provider 接入模型。固定版本还提供全文/向量搜索、transformations 与播客等能力。本次只统计已经验证的 PDF 导入和选定来源全文问答，不把未测功能算作成果。

**本项目是结果研究档案。** 我们把公开论文、历史调用、模型原文、研究代理精读、质量问题和验证证据放在一个静态网页中。当前可阅读、核对、下载和独立打印报告；页面没有上传、实时提问或在线生成服务。

## 2. 底层技术架构

| 层次 | 技术与职责 | 本次验证范围 |
| --- | --- | --- |
| 原 APD 采集 | Python / Click CLI，Requests / BeautifulSoup，HF 榜单与 arXiv PDF | 复用数据模型、SQLite 与门户；领域查询为另加适配 |
| 原 APD 生成与展示 | Playwright 操作 NotebookLM；SQLite 状态；Gradio 门户；独立发布步骤 | NotebookLM 生成产出 0；媒体生成/下载/发布未验收 |
| Open Notebook 前端与接口 | Next.js / React / TypeScript → Python FastAPI | 云机内应用/API 通过，用户完整网页访问未打通 |
| 来源处理 | LangGraph / LangChain；content-core 抽取文档；SurrealDB 保存来源与全文 | 3 PDF 提取合计 171,441 字符 |
| 模型与会话 | 选定来源组成上下文；Esperanto → MiniMax；聊天检查点另用 SQLite | 2 份完整短回答及 1 次截断记录 |
| 任务执行 | surreal-commands 支持同步执行与异步后台任务 | 原 3 篇同步导入；后续单独异步上传 API 验收完成 |
| 当前档案 | HTML / CSS / JavaScript；Python 标准库打包与静态预览 | 完整报告、PDF 页码、图页、MD/JSON/HTML/ZIP |

PDF 调用链为 `FastAPI → process_source → source_graph → content-core.extract_content(file_path) → source.full_text → SurrealDB`。保存证据没有给出最终使用的具体 PDF 解析器，不能将 OCR、PyMuPDF 或 Docling 标为已验证；本次 Docling/Crawl4AI 关闭。提取文本存在空格丢失与重复标题，图表由研究代理回到原 PDF 核读。

本次聊天采用选定来源的完整文本。未生成 embedding，未测试向量召回与重排，因此不宣称已验证完整 RAG。外部 MiniMax 完成推理；“应用可以自托管”不表示本实验所有计算都在本地完成。

## 3. 适合哪些场景

- **跟踪 AI 论文与做周报**：使用原 APD 的榜单入口和编排能力，前提是 NotebookLM 登录、访问和生成链路可用。
- **围绕选定资料问答与初读**：Open Notebook 组织来源，模型帮助提取条件、归纳和比较。结果适合作为需要核对的初稿。
- **专题研究、文献精读与汇报**：增加领域检索、来源登记、图表和统计核对，保留可追溯的长报告及原始依据。本次水生毒理学工作属于这一场景。

持续使用的线上研究应用、跨库系统综述、扫描件通用解析、自动媒体生产与发布，都需要另外验收，不能由本次只读网页推定完成。

## 4. 我们做了什么扩展，如何实现

| 扩展层 | 具体实现 | 实现位置与边界 |
| --- | --- | --- |
| 文献输入 | Europe PMC REST 主题查询，开放获取和日期限制；保存候选，JATS 取得 PDF，验证文件头与 SHA-256，按 PMCID 调用原 `upsert_paper()` | [aquatic_research.py](../extensions/archives/aquatic_research.py) 的 `search()` / `prepare()`。目前为本次 MDPI PDF 规则，非通用出版商下载器 |
| 原库复用 | 重定位运行目录，保留上游代码，复用 Paper/SQLite/`show_papers()`；用真实本地文件和标签展示 | [run_apd.py](../extensions/archives/run_apd.py)、[launch_aquatic_portal.py](../extensions/archives/launch_aquatic_portal.py)。原发布仍以 arXiv 为前提，未适配 PMC |
| 模型路线 | PDF 导入 Open Notebook；`/api/chat/context` → `/api/chat/execute`；只给指定 MiniMax 模型和中国区地址设置 `reasoning_effort=low`、`max_retries=0`，保留 8192 上限 | [runtime.patch](../extensions/archives/runtime.patch)。这是独立替代路线及针对性适配，不是 APD 通用引擎改造 |
| 理解深度 | 阅读完整主文与关键图页，记录实验、独立重复、统计、机制与限制，交叉核对数字 | [详细报告](detailed-report-index.json)。研究代理新增，不归入历史 MiniMax 原始产出 |
| 结果交付 | 白名单导入及哈希核验，生成目录、页码和静态报告，打包可离线阅读的 ZIP | [import_artifacts.py](scripts/import_artifacts.py)、[package_web.py](scripts/package_web.py)、[report_renderer.py](scripts/report_renderer.py)、[verify_web.py](scripts/verify_web.py) |

已发现 `aquatic_research.py` 未执行的媒体下载分支与上游返回值数量不匹配；原分支未修改或执行；公开快照只保留检索和准备函数及其辅助代码，详见[扩展说明](extension-sources.md)。结合尚未适配 PMC 的发布路径，不能将扩展描述为全自动媒体流水线已经完成。

## 5. 实际效果是什么

**资料效果：真实全文可获取、可定位。** 本次查询命中 916 条，保存 30 条候选，按主题与可用性选取 3 篇公开论文。3 份 PDF 共 51 页，下载与上传输入哈希一致；模型侧共提取 171,441 字符。916 是这次查询的结果数，30 条没有构成系统综述级筛选。

**模型效果：产生可用的初读草稿，但仍有错误。** 原版首次正文 350 字符并截断；针对模型参数适配后，单篇 1,460 字符、综合 3,056 字符完整返回。关键剂量、时间、LC50 与置信区间抽查有据，但物种译名、综合概括和局部引用存在问题。“完整返回”只表示生成结束，不能等同科学正确。3 次调用累计 108,597 tokens，未据此计算账单或费用节省。

**深入理解效果：把实验和论证展开，并找出影响结论的细节。** 后续研究代理完成 3 篇逐篇精读与 1 篇综合；逐篇约 4,000–4,500 汉字，配 6 张图页和 119 处 PDF 页码引用。例如鲫鱼论文的高剂量 DEG 正文 1036、图中 612，斑马鱼的病理/MDA/DEG 不同步，混合物不同配比与不同终点不能被合并为普适拮抗。每个判断都回到原文说明其条件与不确定性。

**使用效果：现在可以直接阅读和留存。** 网页提供总览图、效果说明、逐篇全文、目录跳转、原 PDF 页码、历史模型原文、证据 JSON、独立 HTML 打印和离线档案。它解决本轮成果无法方便阅读的问题；完整 Open Notebook 云应用的持续访问、用户上传和在线问答仍未交付。

**没有证明的效果：** NotebookLM 本次生成 0；未生成音频、视频、幻灯片或 embedding。没有模型盲评、耗时对照和成本收益试验，不报告准确率、提效百分比或“最好”的工具排名。精读未重算原始实验数据，补充材料未全部取得。

## 6. 依据与版本

- APD 固定源码 `e1663ba5e73a3501904b2a43699f3c12fb4a4300`：[NotebookLM 编排](https://github.com/brianxiadong/auto-paper-digest/blob/e1663ba5e73a3501904b2a43699f3c12fb4a4300/apd/nblm_bot.py#L1569)。
- Open Notebook 固定源码 `a0f6f3081ae06328f0a451b3a3ef2959ca25721d`：[前端依赖](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/frontend/package.json)、[后端依赖](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/pyproject.toml)、[文档处理](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/open_notebook/graphs/source.py)、[聊天](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/open_notebook/graphs/chat.py)。镜像身份与源码提交分别记录。
- 本地证据：[检索](aquatic-search.json)、[原始导入](open-notebook-cloud-check.json)、[模型运行](open-notebook-minimax-check.json)、[后续异步上传检查](public-validation.json)、[精读索引](detailed-report-index.json)、[架构核对索引](architecture-evidence.json)、[来源与许可](SOURCE.json)。

本图由研究代理依上述依据重新编排，SVG 为本项目原创建图，文本可选择、可缩放；不是上游宣传图或原版应用截图。

离线档案包含正文、论文与证据文件；原文中的上游链接需要网络。检索和模型适配的源码快照、必要历史验证摘要已独立接入本项目，来源路径与哈希用于记录其出处。
