# 图片与来源

| 文件 | 用途 / 图注 | 来源与许可 |
| --- | --- | --- |
| `understanding-summary.png` | 一张图汇总角色展示层的定位、原理、四状态效果、价值、可扩展场景与边界；当前首页封面与网页引导图。 | 2026-10-21，内置 ImageGen 生成，1536×1024。效果区由模型参考本地四状态截图绘制，并非截图像素的原样拼贴；原图保留于 `effects/`。完整请求见 `understanding-summary-prompt.txt`，输入、哈希与说明见 `../study-guide.json`。 |
| `effects/01-listening.png` ～ `04-speaking.png` | 等待、思考、工作、回复的四张实际浏览器截图，作为理解图的参考。 | 2026-10-21，本地 Playwright Chromium；独立角色组件、预设文字与模拟状态事件，角色美术衍生自上游 MIT 项目。环境记录见 `effects/capture.json`。 |
| `upstream-aria.png` | 上游原版应用截图：左侧 ASCII 动画角色，右侧为原版聊天和记忆界面。用于识别外观与说明抽取对象，不作为本次独立组件的实测截图。 | 原仓库 [`docs/aria.png`](https://github.com/MPMyburgh/dr-aria/blob/ff26c94cf1d6879ad98838df9c50104d06419eb6/docs/aria.png)，Michael Myburgh，随上游 MIT 项目提供；[许可与修改说明](../NOTICE.md)。 |
| `demo-desktop.png` | 加入总结图前的角色效果展示页：实时角色、四状态体验、情绪能力和文字播放。 | 2026-10-21，本地 Chromium，1440px 宽，本次实际网页截图；角色美术与渲染衍生自上游 MIT 项目。 |
| `demo-mobile.png` | 角色效果展示页在 390px 宽度的完整页面，技术详情默认折叠。 | 2026-10-21，本地 Chromium，本次实际截图；文字与 Claude/Codex 事件为模拟，未调用模型。 |
| `overview-web-desktop.png`、`overview-web-mobile.png` | 新增总结图在桌面、390px 手机宽度的网页集成截图。 | 2026-10-21，本地 Chromium 实际截图；检查图片加载、放大、关闭、下载和布局，见 `../summary-verification.json`。 |

README 使用相对路径并提供替代文字。独立组件的截图由 `tests/browser.mjs` 生成，验证记录见 `../verification.json`。

线上发布截图：`deployed-desktop.png` 和 `deployed-mobile.png`，于 2026-10-22 使用 Playwright Chromium 在真实 Pages 地址采集；覆盖指定引导图、四项摘要和角色演示，事件为模拟。检查范围见 `../deployment-ui-verification.json`。
