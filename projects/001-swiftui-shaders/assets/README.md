# 图片与素材来源

| 文件 | 说明与替代文字 | 来源与许可 |
| --- | --- | --- |
| `overview.png` | 首页引导图：与网页能力全景 PNG 相同，说明输入、原理、输出、场景与扩展 | 本研究排版与真实 WebGL 截图，源文件见 `../web/assets/understanding-overview.svg` |
| `cover.png` | 完整特效实验室桌面截图：目录、镭射预览、参数、代码和图集入口 | 2026-10-21 由浏览器集成验证脚本截图；界面与素材由本研究制作，特效算法派生自上游 MIT 源码 |
| `collection.png` | 同一张封面经过全部 41 个算法后的完整效果图集 | 同上；展示预设见 `web/app.js`，不代表全部上游默认参数 |
| `gallery-mobile.png` | 390px 手机布局，展示横向目录、画布与参数入口 | 同上 |
| `usage-guide.png` | 用途与价值说明：核心能力、封面/卡片/展示页场景、体验按钮和使用范围 | 2026-10-21 从本研究网页截图，核对桌面与手机布局；内容来自本研究对源码与适用场景的整理 |
| `sample-cover.png` | 原创山野测试封面的无特效栅格图，供原生工程使用 | 由 `web/assets/sample-cover.svg` 栅格化；本研究原创 |
| `../web/assets/sample-cover.svg` | 山野、夕阳、地形线和英文字体组成的 3:4 测试封面 | 本研究用 SVG 绘制，非真实出版物或第三方书籍封面 |
| `../web/assets/sample-flower.svg` | 深色网格上的八瓣花与排版，用于观察边缘和纹理 | 本研究原创 SVG |
| `../web/assets/sample-type.svg` | 绿色背景上的高对比大字和几何线条 | 本研究原创 SVG |
| `../web/assets/favicon.svg` | 绿色底的八向放射标记 | 本研究原创 SVG |
| `../web/assets/understanding-overview.svg` / `.png` | 全部理解的图像总览：输入、原理、输出、能力分类、价值、使用场景和扩展方向 | 本研究编辑排版；嵌入的效果图为实际 WebGL 输出。SVG 2000×2460，可编辑；PNG 为同尺寸高清导出 |
| `../web/assets/effect-atlas.svg` / `.png` | 同一原创封面的原图与 8 种代表效果对照 | 真实着色器输出，未生成虚构效果；SVG/PNG 1800×2750 |
| `../web/assets/effects/*.png` | 可独立使用的效果模块：原图、镭射、霓虹、万花筒、水墨、数据损坏、消散、涟漪与透镜 | 在本地 WebGL 浏览器中渲染并导出，每张 600×800；实际参数与时间记录在相邻同名 JSON 中 |

实验室与完整 41 项图集截图由 `scripts/verify_gallery.py` 生成。能力图解与代表效果模块由 `scripts/capture_visuals.py` 和 `scripts/build_visuals.py` 生成，来源清单见 [visuals-source.json](../web/assets/visuals-source.json)。验证边界记录于 [verification.json](../verification.json) 与[研究说明](../README.md)。这些都不是 Apple 设备运行截图。

上游派生着色器的著作权与 MIT 声明保留在 [upstream/LICENSE](../upstream/LICENSE) 和网页的 [LICENSE.upstream.txt](../web/LICENSE.upstream.txt)。没有复制上游演示 GIF 中可能包含的书籍封面图片。
