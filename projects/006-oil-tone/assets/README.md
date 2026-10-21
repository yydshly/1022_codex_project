# 图片与来源

## understanding-summary.png

- 内容：能力、规则进入上下文的原理、五组共 23 条约束、可选 Python 检查、使用场景、对我们的意义与能力边界。
- 类型：本研究使用内置 ImageGen 生成的原创 PNG 信息图，不是上游产品截图或效果评测。
- 尺寸：1536 × 1024；生成日期：2026-10-21。
- 来源依据：[固定版本上游](https://github.com/oil-oil/oil-tone/tree/39cbf92f76c90b7bb27a5b5d4ed88a1fc5fa31f6)。
- 生成与修订指令见 understanding-summary.prompts.json；初始文字稿见 understanding-summary.prompt.txt。
- 一次定向修订只调整可选 Python 分支：从 AI 改稿阶段进入扫描，提醒回到复核环节；避免把扫描画成交付后的步骤。
- 已目视核对正文关键表述、23 条与 16 组的区别、五组数量 4/6/7/2/4、能力边界和教学案例声明。生成记录与哈希见 understanding-summary.image.json。
- 替代文字：oil-tone 理解总结：任务与事实和 23 条规则进入 AI 上下文，由模型编辑、自查，可选正则提示；展示五组约束、场景、可复用意义与边界。
- 已作为本项目和首页封面，并在网页“我们的理解”中展示；打包器将同一 PNG 原样复制至 web/assets/。

## cover.svg

- 内容：输入事实与任务 → 模型按 23 条规则编辑与复核 → 可选 Python 扫描和语境判断。
- 类型：本研究原创 SVG 图解，非模板占位图，非上游产品截图。
- 来源依据：[固定版本上游](https://github.com/oil-oil/oil-tone/tree/39cbf92f76c90b7bb27a5b5d4ed88a1fc5fa31f6)。
- 制作日期：2026-10-21。
- 替代文字：oil-tone 能力与实现流程：材料进入宿主 AI，23 条规则指导编辑与复核，程序只提供可选提示。
- 旧版简要图解，继续保留；同一文件由 package_web.py 原样复制到 web/assets/cover.svg，作为网页图标使用。总导航封面改用新的 understanding-summary.png。

页面其余图形均由 HTML/CSS 构成，不包含外部图片或字体。源码快照按 MIT 使用，许可位于 upstream/LICENSE 和 web/assets/source/LICENSE。

## 浏览器预览截图

- desktop-preview.png：本研究网页首屏，1280px 浏览器窗口下实际截图。
- mobile-preview.png：375px 手机宽度下实际截图。
- prompt-preview.png：新增完整提示词区域的桌面截图，展示一键复制与下载入口。
- prompt-mobile-preview.png：新增提示词区域在 375px 宽度下的实际截图。
- summary-web-preview.png：理解总结图加入网页后的桌面实际截图。
- 以上截图均为本次网页 UI 验证的证据，由浏览器截图 API 保存，不是上游产品界面；不作为线上发布证明，也不进入 web/ 发布资源。


## 正式网页预览

- deployed-preview.png：2026-10-21 对 GitHub Pages 正式地址的实际浏览器截图，1280×1120 视口，展示“我们的理解”与指定总结图。来源为本研究已部署网页，不是上游产品界面；作为线上验证证据保留，不进入 web/ 发布资源。
