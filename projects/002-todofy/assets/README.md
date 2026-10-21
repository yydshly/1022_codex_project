# 图片与来源

本目录分为源库官方界面原图和本研究的源码分析图。网页以官方原图展示产品能力，中文说明与分析图作为解释内容，分别标明来源。

## 源库官方原图

固定提交：[`2ae76fc80b0b96ad8191e3d1ae4949ee340190a7`](https://github.com/salarzeidanlou/todofy/tree/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7)。作者 / 版权：Salar Zeidanlou / unifybrowse。八张 PNG 直接提取自该提交的 Git 内容，不裁切、不翻译、不重新绘制或编码；图片日期和示例任务保留作者拍摄状态。

| 本地文件 | 展示内容 | 上游路径 |
| --- | --- | --- |
| [today.png](upstream/today.png) | 今日与逾期、下一步任务、预估与实际用时 | docs/today.png |
| [board.png](upstream/board.png) | 四列看板及带完整任务信息的卡片；作为总结引导图中的真实界面来源 | docs/board.png |
| [calendar.png](upstream/calendar.png) | 本地日历中的任务与日程 | docs/calendar.png |
| [focus.png](upstream/focus.png) | 专注倒计时、休息配置和历史 | docs/focus.png |
| [quickadd.png](upstream/quickadd.png) | 快速输入及日期、时间、优先级、重复与标签提示 | docs/quickadd.png |
| [journal.png](upstream/journal.png) | Markdown 日志、心情和当天摘要 | docs/journal.png |
| [voice.png](upstream/voice.png) | 本地语音引擎、模型和模式开关 | docs/voice.png |
| [settings.png](upstream/settings.png) | Cloud Sync、Google Calendar 和语音设置入口 | docs/settings.png |

每张图的固定上游 URL、原始尺寸、文件字节数、SHA-256 及网页副本路径完整记录在 [screenshots.json](../screenshots.json)。网页发布副本位于 `../web/assets/upstream/`，与本目录文件逐字节一致。

保留的上游许可：[LICENSE.todofy.txt](upstream/LICENSE.todofy.txt)，原文见 [上游 LICENSE](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/LICENSE)。本项目以图片配合注解研究其能力，图片及界面版权仍归上游，不对其追加本仓库许可，也不将截图当成本机原生复现结果。

## 本研究整理的分析图

| 文件 | 解释内容 | 来源说明 |
| --- | --- | --- |
| [overview.svg](overview.svg) | 同一任务与列表、看板和日历的关系 | 原创概念图，供文档解释，非产品界面 |
| [architecture.svg](architecture.svg) | 界面、Tauri 命令、Rust、SQLite 和可选服务的数据流 | 原创源码分析图，网页中明确标为我们的分析 |
| [网页架构图副本](../web/assets/architecture.svg) | 独立发布页面使用的分析图 | 与本目录 architecture.svg 内容一致 |
| [understanding-summary.png](understanding-summary.png) / [SVG](understanding-summary.svg) | 一图总结我们的理解、能力、本质、效果和参考意义；突出看板样式与信息组织 | 本研究绘制文字与结构，等比引用上游官方 Board 原图；来源、图像哈希、字体和生成环境见 [summary-image.json](../summary-image.json) |
| [网页总结图 PNG](../web/assets/understanding-summary.png) / [SVG](../web/assets/understanding-summary.svg) | 首页封面、网页首屏引导与原尺寸查看 | 与本目录同名总结图逐字节一致 |

源码证据见 [原理分析](../ARCHITECTURE.md) 与 [SOURCE.json](../SOURCE.json)。图中并列模块用于说明职责，不意味着它们分别运行一个独立的系统服务进程。

总结图由 [scripts/build_summary.py](../scripts/build_summary.py) 生成，PNG 使用 Pillow 排版并等比引用原始截图，SVG 内嵌原始 PNG 内容；原始截图文件没有改写。图中的界面版权与上游署名保留，其余文字、排版和总结为本研究整理。字体用于本机渲染，不随仓库分发字体文件。
