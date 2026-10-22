# 历史验证摘要与质量核对

这份说明整理于 2026-10-22，来自已保存的 008 研究文件，不表示重新运行了接口或生成。公开的[验证摘要](public-validation.json)保留必要结果、原始文件路径及 SHA-256；省略账号、云端聊天/回合、笔记本和来源实例标识。旧环境私有会话、配置、密钥和运行缓存没有发布。

## 路线为何切换

1. **Auto Paper Digest → 领域检索适配。** 原库读取 Hugging Face 榜单和 arXiv；本次改由 Europe PMC 查询水生毒理学，保存 30 个候选、取得 3 篇公开 PDF，使用原 Paper/SQLite 和 Gradio 展示。3 篇文件头与哈希检查通过，均登记为 `PDF_OK`。
2. **NotebookLM → Open Notebook。** 官方企业接口因当前项目缺少所需许可返回 `FAILED_PRECONDITION`；个人 HTTP/RPC 请求被转到 `location=unsupported`，用户同时报告浏览器笔记本列表可用。这说明当时两条程序接入路径未取得产出，不能推断个人网页不可用或所有地区被限制。NotebookLM 本轮产出为 0。
3. **Open Notebook → MiniMax 参数适配。** 3 篇 PDF 的全文提取与原生问答接口跑通。首次默认参数正文 350 字符且 `finish_reason=length`；特定模型参数适配后，1,460 字符单篇和 3,056 字符综合均以 `stop` 结束。原文、用量和哈希见[模型证据](../evidence/open-notebook-minimax-check.json)，实现见[扩展快照](../../extensions/README.md)。
4. **云端应用试跑 → 静态成果展示。** 云机内健康、页面和 API 响应通过，未认证 API 为 401；未取得用户可访问的原版应用入口。后来单独异步上传完成 59,970 字符提取，仍属于 API 验收。ngrok 和 Microsoft Dev Tunnels 的目标返回代理 `403 Domain forbidden`，同代理 npm 对照返回 200；原因未完全确定，不能概括为所有云环境都禁止隧道。停止的是这条完整应用访问排查路线。现在另行发布静态研究档案，提供结果阅读与下载。

## 完整回答不等于科学审定

历史短回答抽查能对应原文的剂量、时长及部分 LC50/CI，例如 PFOS 单独 1.97 mg/L、1:1 混合 1.99 mg/L、固定 100 mg/L PFOA 背景下 3.10 mg/L。两种混合设计不能互换，特定条件下拮抗不能推广为所有 PFAS 混合物。

已知问题包括 *Cyprinodon variegatus* 的中文俗名错误、把不同终点概括成“三种鱼均有肝脏或发育毒性”，以及综合断言的紧邻引用不足。原始模型回答保留错误，没有经过改写再冒充原始产出。来源 ID 是会话标记，本身不是经过验证的 PDF 页码。

后续研究代理另行完成[三篇精读与一篇综合](../detailed/index.json)，读取 51 页主文并核对关键图表，补充样本、重复单位、统计口径、机制与外推限制。详细报告不是历史 MiniMax 短回答，也不是 NotebookLM 生成。本次没有完整补充材料或原始实验数据重分析。

## 对应的完整公开材料

- [检索与候选](../evidence/aquatic-search.json)、[论文元数据](../evidence/aquatic-papers.json)、[PDF 导入](../evidence/open-notebook-cloud-check.json)、[实际模型调用](../evidence/open-notebook-minimax-check.json)已经独立保存在 011。
- [原始接入清单](../import-manifest.json)中的 `source` 是历史文件定位，`path` 是当前公开副本，哈希以当前副本字节核验；不需要取得整个 008 才能阅读与打包。
- [公开验证摘要](public-validation.json)是选定字段的派生摘要，不冒充逐字复制的原始日志。历史路径/哈希供来源核对，不是可访问的下载地址。
