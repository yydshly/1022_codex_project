# 素材与来源

- `old-coder-overview.png`：本研究原创能力总览图，1800 × 2600。覆盖能力、原理、库存通知案例、适用场景与核心价值。Pillow 按矢量排版操作绘制高清 PNG；同源操作生成 `old-coder-overview.svg` 供编辑。图中文字为研究归纳，库存案例为教学模型，不是 Skill 效果基准或真实支付系统实测。
- `overview-generation.json`：图解方法、尺寸、字体与渲染版本、SHA-256、两次 ImageGen 网络失败记录。原始生成请求保留在 `overview-imagegen-prompt.txt`，它没有产生本次成图；最终内容与形状以 `scripts/build_overview.py` 为准。未使用模型 API 回退。
- 上述四个文件以同名发布副本保存在 `web/assets/`；网页提供放大、原图、PNG 与 SVG 下载。字体从本机加载渲染，未将系统字体文件分发到仓库。

- `cover.jpg`：2026-10-22 在桌面响应式检查时，用内置浏览器截取本研究网页，视口 1440 × 900。库存数字是教学示意，不是 Skill 效果基准。发布副本 `web/assets/cover.jpg`。
- `publication-preview.jpg`：正式公开网页的真实浏览器截图，来源为本次内容提交 `d727862` 的 GitHub Pages 发布。用于记录公开首屏的摘要与指定引导图；主封面仍为 `old-coder-overview.png`。
- `web/assets/favicon.svg`：本研究原创 SVG 文字标识。
- `web/assets/sources.json`：31 份上游文件纯文本，固定到 `a0eb529d393a1cb3ccc564e32b2104e7e75c7a29`，每项附固定版本链接。
- `web/assets/LICENSE.upstream.txt`：MIT，© 2026 amazingang，上游许可原文。
- `web/assets/source-manifest.json`：与 SOURCE.json 一致的路径和 SHA-256。
- `web/assets/upstream-reproduction.json`：本机上游部分复现的命令与结果，审计超时标 unverified。
- `web/assets/lab-verification.json`：本研究教学引擎验证，不能替代上游原始报告。

原始仓库 <https://github.com/AmazingAng/old-coder>。本项目没有使用外部照片、CDN 或在线字体。总览图最终为代码绘制，非成功生成的 AI 图片。
