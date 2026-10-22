# 引导图、来源与使用说明

沿用本次对话最终确认的原创理解长图，用于根索引封面、研究首页与网页首屏。替代文字描述角色分工、执行架构、十二项沙箱能力、Docker 对比、价值与效果。PNG 和 SVG 与对话原件逐字节一致。

| 文件 | 说明 | SHA-256 |
| --- | --- | --- |
| orchard-agentic-overview.png | 2400×5480，PNG 展示 / SVG 编辑 | 22f4f96ac276acc89fbd1d046b8210e9e15fffa0102f3665c4035a7e3e111866 |
| orchard-agentic-overview.svg | 2400×5480，PNG 展示 / SVG 编辑 | 1908d54ddf4a19b18a8e104178d8b985b21c598572bfa3653d6df4539b955a49 |

## 制作与事实来源

最终采用 Python/Pillow 文字排版与同步 SVG 绘制，无第三方产品标识或官方界面截图。初次 ImageGen 请求网络失败，未使用其结果。source/ 保留实际脚本、来源说明和初次尝试指令。

事实来自固定版本上游文档和论文第三版，见 ../research-evidence.json。图中实验是作者报告，非本次实测；使用建议为研究判断，快照分叉已标为后续计划。

## 发布副本

web/assets/ 下同名文件与原件保持字节一致，verify_web.py 核对原件、发布副本与 guide-manifest.json。只使用相对路径，不依赖对话本地文件系统。
