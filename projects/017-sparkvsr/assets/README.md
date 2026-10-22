# 图片与来源

| 文件 | 用途 / 替代文字 | 来源与边界 |
| --- | --- | --- |
| sparkvsr-overview.png | SparkVSR 能力、原理、效果、价值与当前判断总览；2400 × 3970 | 本次对话已交付原图，按字节复制。Pillow 精确排版，非运行截图；作者指标非本机实测 |
| manifest.json | 身份、尺寸、SHA-256 与制作方式 | 本仓库元数据 |
| web-preview-desktop.png / web-preview-mobile.png | 1280 / 375 宽度的理解页预览 | 本次浏览器真实截图，仅证明静态网页排版，不证明模型效果 |

首页封面、项目说明与网页首屏使用同一张图。原文件名为 sparkvsr-overview-2026-10-22.png；图内来源为上游、论文与演示，不含第三方截图。

制作过程：一次内置 ImageGen 请求网络失败，随后用 Pillow 绘制。可选重建脚本位于 scripts/build_overview.py；中文字体和 Pillow 版本可能影响新产物。日常打包和 CI 只校验复制现成 PNG，无需绘图依赖。

首要边界为“清晰度提升不等于真实细节完全恢复”，末尾保留“了解并留档，暂不深入研究”。本次没有重绘或更改原图。

公开发布截图为 publication-desktop.png / publication-mobile.png，分别为 1280 / 375 宽度的线上真实截图；同样不作为模型效果证据。
