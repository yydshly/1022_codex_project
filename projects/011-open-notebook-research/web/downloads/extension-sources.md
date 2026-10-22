# 本研究扩展的源码快照

这些文件用于检视本次扩展怎样实现，**不是独立可运行的安装包，也不参与静态网页构建或执行**。它们来自本地研究 008；[来源清单](../extensions/source-manifest.json)记录历史路径、原文件 SHA-256 和公开副本 SHA-256。文件中没有模型密钥、登录会话或私有配置。

| 文件 | 可检视的实现 | 发布范围 |
| --- | --- | --- |
| [aquatic_research.py](../extensions/archives/aquatic_research.py) | Europe PMC 查询、JATS 中 PDF 线索、所选 MDPI 下载规则、文件头与哈希检查、PMCID 入库 | 仅保留 `search()`、`prepare()` 及所需导入/辅助函数；移除 CLI 和未成功验收的媒体调度入口 |
| [run_apd.py](../extensions/archives/run_apd.py) | 原 APD 的路径重定位、数据目录与数据库配置 | 原文件按字节保留 |
| [launch_aquatic_portal.py](../extensions/archives/launch_aquatic_portal.py) | 实际文件链接、SQLite 状态和上游 `show_papers()` 的复用 | 原文件按字节保留；其中的 008 标题、路径和启动行为为历史状态 |
| [runtime.patch](../extensions/archives/runtime.patch) | 指定 MiniMax 模型及中国区地址下，传入 `reasoning_effort=low` 与 `max_retries=0` | 原差异按字节保留；未改变 8192-token 上限 |

运行前提是当时的 APD 固定源码、对应 Python 依赖、008 目录结构与已准备资料；本目录没有提供这些运行环境。`run_apd.py` 中的 `_upstream/008-auto-paper-digest` 是历史定位方式，不能据此把本目录当作已验证可运行应用。当前发布只运行静态打包与验证脚本。

原完整 `aquatic_research.py` 中未执行的媒体下载分支用两个变量接收上游三个返回值。本次公开的是检索/准备部分，未运行或修复该媒体分支；原 APD 发布仍以 arXiv 为前提，没有完成 PMC 发布适配。所选 MDPI 的下载规则也不是通用出版商下载器。

固定上游：Auto Paper Digest `e1663ba5e73a3501904b2a43699f3c12fb4a4300`；Open Notebook `a0f6f3081ae06328f0a451b3a3ef2959ca25721d`；模型补丁目标 Esperanto 2.28.0。Esperanto 许可证见 [MIT 许可](../assets/licenses/Esperanto-LICENSE.txt)，完整版本来源见 [SOURCE.json](SOURCE.json)。
