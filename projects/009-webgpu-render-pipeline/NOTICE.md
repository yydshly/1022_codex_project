# 来源与新增范围

研究对象为 `vibegameengine/web-starter-kit-webgpu-pipline`，固定提交 `ca576b601bf84527102f1768372aa8cd96a3c55a`。源码链接均指向该版本，取证元数据与 SHA-256 见 `SOURCE.json`。

该固定树未找到仓库级 LICENSE、LICENCE 或 COPYING 文件，GitHub API 的 `license` 字段为 `null`。本记录不为上游指定 MIT、Apache 或其他许可，也不把公开可读理解为已取得任意复制、修改或商用许可。单项依赖与素材的权利条件还需各自核对。

本目录新增的中文说明、能力分类、JSON 索引、原创 SVG 图解、HTML/CSS/JavaScript、取证和打包脚本属于本次研究工作。早期静态资料不含上游引擎；后续真实演示从固定上游及作者 fork 构建，由 `runtime/` 增加启动和控制桥接，没有重写渲染算法，也没有把教学图或作者历史图当成本机运行成果。

运行工作副本对 `src/shared/gi/bake/lightmapSurfels.ts` 增加一条有效表面条件，修复空白边缘抢占 chart 补采样名额的问题。原始与修改后的 SHA-256、精确替换文本记录在 `runtime/SOURCES.json` 的 `source_patches`；原始文本取证缓存保持不变。原库所有正确性检查保留。该补丁、桥接与运行配置共同构成本研究的复现版本。

`assets/project-overview.svg` / `.png` 是本研究原创的总览图，文字、流程、分类与应用方向由已有研究组织；四张场景缩略图从已记录的本机原始截图缩放排版，没有重绘或调色。它是带实测缩略图的研究图解，不是单张原始渲染帧或新的效果验收。具体来源、覆盖 ID 和哈希见 `overview.json`、`OVERVIEW.md`。

真实演示的原库、Three.js fork、React Three Fiber fork 与 npm 锁文件记录于 [runtime/SOURCES.json](runtime/SOURCES.json)。构建器保留 Three.js / R3F 的 MIT 原文及 npm 依赖通知至 `web/live/licenses/`，仍不为缺少仓库级许可证的主快照指定额外许可。HDR 环境与蓝噪声来自固定上游，按原始 Git blob 和 SHA-256 校验；没有用 AI 替换这些运行资源。

`assets/runtime/` 中的 PNG 是本机 Chromium 运行 Cornell Box、完整村庄、海滩与森林的原始截图或展示页截图；裁取画面区域只用于保持控制变量，不重绘或调色。其参数与哈希见 [runtime/screenshots.json](runtime/screenshots.json)，实际通过的范围见 [RUNTIME.md](RUNTIME.md)。

新增的红墙/白球与三维渲染/AI 对照图解由 SVG 图形编写，是教学资料，不是数值求解结果或 AI 生成效果。`explain.json` 统一维护通俗讲解，生成文档和网页数据；算法依据链接固定上游源码，AI 空间条件的补充链接 ControlNet 原始论文。没有复制论文图像、整段内容或模型代码，也没有接入 AI 服务。

`assets/upstream/lighting-baseline.png` 与 `lighting-concept.png` 从上游 `public/lighting-look-development.html` 的 data URI 原样提取，仅用于具体研究对象的必要图像引用，保留作者文档原始说明、固定来源、哈希及“历史画面/概念参考”分类。权利归原作者及素材权利人；本记录不授予这些图片的额外复用权利。图片没有经过 AI 重绘、裁切或调色。

运行截图与概念图不是同一状态的严格 A/B，也不是本机当前版本验收。概念图中出现的表现不能自动计入已实现能力。网页截图若另存于 `assets/`，只用于验证本次研究展示的界面和布局。
