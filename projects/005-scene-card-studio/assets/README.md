# 配图来源

`understanding-summary.png`：本研究使用内置 ImageGen 于 2026-10-21 生成的理解总结图（1536×1024）。内容包含能力、基于原图二次创作的原理、四种效果参考、可扩展场景与意义；效果区参考下方上游样张，并经过生成模型重新呈现，不是原件逐像素拼贴或新的改图实测。完整提示词为 `understanding-summary-prompt.txt`，生成方式、五张参考图及文件哈希见 [study-guide.json](../study-guide.json)。扩展场景为应用方向。

`overview.svg`：本研究于 2026-10-21 原创绘制，依据上游固定 commit 的流程。替代文字：照片与意图经场景卡、叙事和材质规则、十模块提示词，再经外部生图、原图对照审核与独立排字。

图中没有第三方照片或字体文件；这是流程说明，非生图实测效果。上游版本与来源见 `../SOURCE.json`。

## 网页上游效果图

六张图片均按字节复制，没有裁切或重新生成；网页缩略图支持打开完整图。许可为上游项目及素材声明提供的 Apache-2.0 范围。完整 URL 与 SHA-256 见 [media.json](../media.json)，声明原件见 [ASSET_LICENSE.md](upstream/ASSET_LICENSE.md)。

| 文件 | 内容／替代文字 | 上游相对路径 |
| --- | --- | --- |
| `upstream/selective-relief.png` | 蓝船保持摄影质感，山体和岸边为浅浮雕；v0.7成片，源图未公开 | `examples/cases/v0.7-director-gallery/after/selective-material-relief.png` |
| `upstream/lake-before.png` | 蓝船、湖泊、芦苇与栏杆；上游AI输入示例 | `examples/cases/v0.6-gallery/before/mountain-lake.png` |
| `upstream/lake-threaded.png` | 同一场景转为连续刺绣和编织；上游成片 | `examples/cases/v0.6-gallery/after/threaded-landscape.png` |
| `upstream/ink-poetry.png` | 猫与窗台保留摄影质感，边缘水墨化，诗句独立排字；上游v0.7成片 | `examples/cases/v0.7-director-gallery/after/chinese-ink-poetry-final.png` |
| `upstream/watercolor.jpg` | 黄色雨伞人物和海边环境统一水彩；上游虚构人物成片 | `examples/cases/v0.4-gallery/after/watercolor-chronicle.jpg` |
| `upstream/watercolor-before.jpg` | 撑黄色雨伞的人、左侧自行车、蓝色海堤和阴天海面；与水彩成片配对的上游AI输入 | `examples/cases/v0.4-gallery/before/watercolor-chronicle.jpg` |

`upstream/records/` 包含两例各自的原始 `story.json` 与 `prompt-manifest.json`，均未改动。来源和哈希见 [cases.json](../cases.json)。两例 before／after 的 SHA-256 与原始 Prompt Manifest 的 source／reference-output 一致，不能混配其他源图。

`web-preview-inputs.png` 为补齐后的完整案例桌面截图，`web-preview-inputs-mobile.png` 为手机截图，均来自实际浏览器渲染；不是新生图结果。

`web-preview-effects-restored.png` 与 `web-preview-effects-restored-mobile.png` 为恢复默认可见的四种效果总览截图，分别在桌面与手机视口采集；图片仍为上述上游原件。

`web-preview-essence.png` 为首屏补充“基于原图二次创作、可复用与可检查的规则流程”后的实际浏览器截图。

`web-preview-understanding.png` 和 `web-preview-understanding-mobile.png` 为理解总结图接入网页后的实际浏览器截图，分别检查桌面与手机显示；不属于额外的图像生成请求。

`web-preview.png` 为本地网页桌面截图，`web-preview-mobile.png` 为 375 像素视口效果区截图；由浏览器实际渲染采集，包含上述有来源的图片及本研究编写的页面。它们是网页 QA 记录，不是本次重新生图的结果。
