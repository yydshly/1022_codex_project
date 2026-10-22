# 多项目 Web 部署

本仓库使用 **GitHub Actions → GitHub Pages**。一个站点承载多个编号项目，静态资源使用相对路径，不要求各项目采用相同前端框架。

## 线上入口

| 入口 | 地址 |
| --- | --- |
| 总导航 | https://yydshly.github.io/1022_codex_project/ |
| 001 · SwiftUIShaders | https://yydshly.github.io/1022_codex_project/001-swiftui-shaders/ |
| 002 · Todofy | https://yydshly.github.io/1022_codex_project/002-todofy/ |
| 004 · XXD Panel 106 | https://yydshly.github.io/1022_codex_project/004-xxd-panel-106/ |
| 009 · WebGPU 光照效果实现与复用 | https://yydshly.github.io/1022_codex_project/009-webgpu-render-pipeline/ |

2026-10-21 已完成首次发布。构建与部署任务成功，两个入口及运行资源返回 HTTP 200；两张引导图的线上内容与本地 SHA-256 一致。已在浏览器检查 41 项效果入口、完整图集、8 个真实效果模块与摘要内容。详见 [部署检查记录](../projects/001-swiftui-shaders/deployment-verification.json)。

总导航展示项目能力摘要、研究入口及已发布项目的引导图。项目页包含能力、原理、效果、适用场景与扩展方向，以及完整的 41 种实时特效实验。

## 构建与预览

构建仅需 Python 3.10+ 标准库，无需 npm、外部 CDN 或前端构建依赖。仓库根目录执行：

```bash
python scripts/project_catalog.py check
python projects/001-swiftui-shaders/scripts/build_gallery.py --check
python projects/001-swiftui-shaders/scripts/build_native.py --check
python projects/001-swiftui-shaders/scripts/package_web.py
python scripts/build_site.py
python -m http.server 8000 --bind 127.0.0.1 --directory _site
```

预览 [总导航](http://127.0.0.1:8000/) 和 [SwiftUIShaders](http://127.0.0.1:8000/001-swiftui-shaders/)。`build_site.py` 汇总登记表中具有 `web/index.html` 的项目，只复制其专门用于发布的 `web/`；研究文档、原生工程、凭据与依赖目录不进入部署产物。

输出目录必须为空，脚本不会删除已有文件。再次构建时使用新的空目录，例如 `python scripts/build_site.py --output _site/preview-next`，并相应调整 HTTP 服务目录。`_site/` 为忽略的产物目录，不提交 Git。

```text
_site/
├── index.html                   # 总导航、能力摘要、两张引导图
├── .nojekyll
└── 001-swiftui-shaders/
    ├── index.html               # 在线入口，按需加载相对路径资源
    ├── app.js / renderer.js / style.css / shaders.json
    ├── LICENSE.upstream.txt
    ├── assets/                  # 原创素材、图解与真实效果模块
    └── standalone.html          # 可另存本地的完整离线版本
```

## 自动发布

实际工作流：[deploy-pages.yml](../.github/workflows/deploy-pages.yml)。

- 推送 `main` 时，项目、登记表、构建脚本或部署工作流发生变更即自动发布；也可手动触发 **Deploy research demos**。
- 构建任务检查登记表、首页和生成代码，再打包离线页、汇总总导航及项目资源。
- 上传 Pages artifact，由单独部署任务发布，权限为 `pages: write` 与 `id-token: write`，环境为 `github-pages`。
- 仓库 Pages 的发布源需设为 **GitHub Actions**（API 对应 `build_type: workflow`）。
- 每次在 Actions 中确认构建和部署成功，再检查真实网址、样式、图片与交互。新项目的 `demo_url` 在验证通过后填写，然后执行 `python scripts/project_catalog.py sync`。

新增静态项目时，在自己的 `web/` 中准备可发布产物即可汇总；需要构建的项目先在工作流中加入依赖安装与构建步骤，再输出到对应 `web/` 或调整汇总器。编号、上游版本、许可和复现环境仍记录于子项目。

## 002 · Todofy 网页

Todofy 的 [源库官方界面展示网页](../projects/002-todofy/web/index.html) 采用无依赖 HTML / CSS / JavaScript，直接引用八张未改动的上游 PNG，已移除自制任务模拟。现有 Actions 汇总步骤即可复制，无需额外安装或打包。`build_site.py` 在未找到专项引导图时，会使用项目登记表指定且已经放入 `web/` 的封面，保留原有 SwiftUIShaders 展示方式。

本地构建到新的空目录后，入口为 `<预览根目录>/002-todofy/`；编号路径为 `/1022_codex_project/002-todofy/`。官方截图与保留的许可位于 `web/assets/upstream/`，分析图位于 `web/assets/`，资源不依赖 `web/` 以外的文件；原始来源和哈希保存在项目 `screenshots.json`。

引导图采用我们生成的 `understanding-summary.png`，与首页封面、项目研究首页保持一致。页面明确概括“任务展示板＋管理驱动”，并说明对我们参考看板样式、卡片信息层级和交互组织的意义。

2026-10-21 已发布到 [002 · Todofy](https://yydshly.github.io/1022_codex_project/002-todofy/)，内容提交 `09ee048`，Actions 构建与部署均成功。16 个线上文件返回 HTTP 200 且内容与 Git 提交一致；已在浏览器验证八图切换、放大、键盘导航、四个原理页签、六个场景和截图跳转。375 / 768 / 1280 宽度没有页面横向溢出或损坏图片，控制台无警告或错误。

发布、HTTP 与文件哈希记录见 [deployment-verification.json](../projects/002-todofy/deployment-verification.json)，展示网页的检查范围见 [web-verification.json](../projects/002-todofy/web-verification.json)。原生应用、通知、语音与外部同步未运行。

## 路径与验证范围

资源与内部链接使用相对路径，可在 `/1022_codex_project/<编号-slug>/` 下运行。效果深链接使用 `#effect=Holographic` 等片段，无需服务端路由回退。修改链接后应模拟仓库前缀，检查导航、模块跳转、图解、素材、手机宽度与下载。

Pages 提供静态托管。SwiftUIShaders 的浏览器演示在客户端执行 WebGL；原库的 SwiftUI/Metal 实现需在 Apple 平台运行。PNG 导出是展示页功能，GIF/视频录制与编码属于待扩展方向。原生 Metal 画面与真机性能仍待验证。

## 官方参考

- [GitHub Pages 与静态托管](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [使用自定义工作流部署 Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

## 004 · XXD Panel 106

2026-10-21补充完整提示词阅读区与一张理解总结图：原始风格正文和10份实际请求均打包进media.js，可切换全文／追加指令、复制当前显示内容、下载完整原文件；成品、壁纸和失败记录可直接定位到相应请求。总结图和其生成请求以study_guides单独登记，不增加原海报实验的10次请求计数。打包及验证脚本同时核对11份提示词原文、总结图哈希与编号路径资源。

[柔彩像素记研究与真实演示](../projects/004-xxd-panel-106/README.md) 使用无依赖静态网页。先运行 `python projects/004-xxd-panel-106/scripts/package_web.py`，按字节复制全部8张官方样张、独立实拍、7张本次成品、3张失败结果、来源声明、许可证和完整请求，并生成图集数据；该步骤已加入现有Pages工作流。发布检查可执行同一命令加 `--check`。

源素材维护在子项目 `assets/`，打包副本、媒体数据和提示词副本在 `web/` 中按项目规则忽略，构建器再将完整 `web/` 复制到编号路径 `/1022_codex_project/004-xxd-panel-106/`。资源均使用相对路径，不依赖CDN或在线生图接口。网页支持官方图集筛选、完整图片放大、键盘切图、演示切换、四端壁纸下载、失败记录与场景说明。

2026-10-21 已发布到 [004 · XXD Panel 106](https://yydshly.github.io/1022_codex_project/004-xxd-panel-106/)，内容提交 `329ec7b`，[Actions构建与部署成功](https://github.com/yydshly/1022_codex_project/actions/runs/39597904164)。42个项目发布文件均返回HTTP 200且字节一致；线上图集、11条提示词及指定引导图已检查，详见项目 [部署验证](../projects/004-xxd-panel-106/deployment-verification.json)。真实生成的模式与文字结果、尺寸偏差和失败过程保存在项目文档，验证范围见 [verification.md](../projects/004-xxd-panel-106/verification.md)。


## 005 · Scene Card Studio

[照片创作规则网页](../projects/005-scene-card-studio/web/index.html) 包含三张清单、四步流程、六张上游图片和可复制的精简／完整／返修提示词。首页直接展示原图与成片；湖泊刺绣与人物水彩两组完整案例同步展示原图、据场景卡整理的要求、变换规则、结果观察和原始编译提示词，并提供记录下载。四种效果默认并列展示，可点击放大；浮雕与国风未公开源图，明确标注仅成片。展开后可选择 11 种叙事、24 种表达；页面没有在线生图服务。

新增一张使用内置 ImageGen 生成的理解总结图，覆盖能力、图生图原理、四种效果参考、可扩展场景与意义。网页理解总览支持放大及下载，导航封面同步使用；生成请求、参考图来源及文件哈希记入 `study-guide.json`。它是研究信息图，效果区为模型参考呈现；六张原始样张仍保留，未新增原图改图实测。打包脚本将总结图、请求和记录纳入副本校验。

构建前执行 `python projects/005-scene-card-studio/scripts/package_web.py`，已接入 Pages 工作流。该脚本将素材、提示词、规则 JSON 和许可原样打包，生成用于选择与复制的 `data.js`，`--check` 可核对副本；随后根汇总器复制至 `/1022_codex_project/005-scene-card-studio/`，并自动加入总导航。

2026-10-21 已发布到 [005 · Scene Card Studio](https://yydshly.github.io/1022_codex_project/005-scene-card-studio/)，内容提交 `224b0fe`，[Actions 构建与部署成功](https://github.com/yydshly/1022_codex_project/actions/runs/39619790319)。34 个项目文件与总导航均返回 HTTP 200 且字节一致；七项摘要明确说明能力、输入、处理、输出、使用场景、扩展方向与意义，网页及导航采用已生成的理解总结图。主要交互及桌面／手机布局已检查，记录见 [部署验证](../projects/005-scene-card-studio/deployment-verification.json)。

## 006 · oil-tone

[写作约束研究网页](../projects/006-oil-tone/web/index.html) 说明能力、原理、使用场景与对我们的意义：将 23 条文字规则交给 AI，引导起草、润色和结构调整，保留事实、减少空话；可复用为文章、产品文案和口播的编辑标准与完整提示词。引导图采用我们已生成的理解总结图。

页面包含六步执行链路、23 条规则检索、完整提示词复制与下载、21 处改稿批注、脚本结果和源码阅读。网页只展示已保存的研究材料，没有在线模型接口。教学产品与数据为虚构设定，Python 检查真实执行；9 → 0 是提醒数变化，不是质量评分。

已生成的 web/data.js 与发布资源随项目提交；根汇总器直接复制到 `/006-oil-tone/`，现有 Actions 无需新增依赖。内容或上游快照变更后执行 `python projects/006-oil-tone/scripts/package_web.py`；加 `--check` 核对生成结果、快照哈希和脚本输出。源码与 MIT 许可经 web/assets/source/ 发布，不复制整个研究目录。

2026-10-21 已发布至 [006 · oil-tone](https://yydshly.github.io/1022_codex_project/006-oil-tone/)。内容提交 `863c9e1`，[Actions 构建与部署成功](https://github.com/yydshly/1022_codex_project/actions/runs/39605092607)；13 个发布文件 HTTP 200，响应与提交字节一致，指定总结图哈希一致。线上流程、规则搜索、21 处批注、提示词复制与下载、桌面及手机布局已检查。记录见项目 [部署验证](../projects/006-oil-tone/deployment-verification.json) 与 [verification.md](../projects/006-oil-tone/verification.md)。

## 007 · dr-aria

[角色效果与表达图鉴](../projects/007-dr-aria/README.md) 汇总能力、原理、效果和价值：用预制 ASCII 形象、状态驱动动作和文字驱动气泡及嘴型，把 Agent 回复和部分运行状态转成可见反馈。演示包含四状态切换、一键完整播放、中文文字、可选字符短音和情绪能力说明；当前仅一套 warm 温和基础表情，未连接真实模型。

引导图和首页封面均采用本次生成的 understanding-summary.png。效果区由 ImageGen 参考四张本地实际截图绘制，原始截图与完整提示词保留。图可放大和下载。构建前运行 python projects/007-dr-aria/scripts/package_web.py；--check 核对图像副本，随后根汇总器发布至 /1022_codex_project/007-dr-aria/。工作流已加入此步骤。

2026-10-22 已发布至 [007 · dr-aria](https://yydshly.github.io/1022_codex_project/007-dr-aria/)。内容提交 `2643cd8`，[Actions 构建与部署均成功](https://github.com/yydshly/1022_codex_project/actions/runs/39631036413)；9 个发布文件 HTTP 200，内容与提交字节一致，指定 ImageGen 引导图哈希一致。线上摘要、图像放大下载、状态与一键演示、中文流式回复、模拟 Agent 样例和三种宽度已验证。记录见 [文件验证](../projects/007-dr-aria/deployment-verification.json) 与 [网页交互验证](../projects/007-dr-aria/deployment-ui-verification.json)。未连接真实模型。

## 003 · Algorithmic Sublime Poster

[情绪引导的图片与视频创作研究](../projects/003-algorithmic-sublime-poster/README.md)将源库海报设计规范与本研究的情绪、艺术意图方法分开说明。以目标感受组织提示词，匹配像素、点云、字符、扫描和数据连接等视觉语言，展示源库三组原始效果、图片对照与返修、两条实际AI短片，并提供emotion-art-direction Skill与图片/视频/返修模板。

引导图和总导航封面采用已生成的第三版总览图`emotion-art-research-overview-v3.png`；源库数字连接横图为主要视觉。图内案例是依据原件的AI概览合成，原始海报、原片、准确历史指令和偏差独立保留。适用场景包括科技传播、文化展览、产品概念、人物叙事和系列/短片导演方案。实际价值、情绪稳定性和Skill独立增益尚待进一步验证。

构建前运行`python projects/003-algorithmic-sublime-poster/scripts/package_web.py`，再执行同一命令加`--check`。现有Pages工作流已加入两步，之后由根汇总器发布编号路径；静态网页无需在线生成接口。原始资源在`assets/`维护，`web/assets/`副本不重复提交；项目记录固定上游提交、媒体来源及许可边界。

已于2026-10-22通过[公开入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/)验证；内容提交`3a51bb7`的[GitHub Actions构建与部署](https://github.com/yydshly/1022_codex_project/actions/runs/39731082554)成功。32个页面文件与160项素材共192项HTTP200且SHA-256与提交内容一致，两条真实AI原片Range206；桌面/手机、原作切换、真实原片播放、完整指令展开及Skill ZIP下载检查通过。登记表已填写demo_url并同步索引。[完整验证记录](../projects/003-algorithmic-sublime-poster/assets/deployment-verification.json)。

## 009 · WebGPU 光照效果实现与复用

009 的核心是浏览器三维光照效果：先用 BVH / Surfel 估计反弹光，存入 Lightmap / 空间探针，再实时组合直接光、阴影、水面和植被。入口使用本研究已有的一图总览，说明效果、原理、游戏与空间漫游等复用方向；四场景交互按需加载。

GitHub Actions 使用 Node.js 22，先运行本项目 setup_runtime.py / build_runtime.py，再运行 package_web.py / verify_structure.py，最后由统一 build_site.py 汇总。源码、Three.js / R3F fork 与 npm 锁定到明确版本；运行依赖、资源与许可说明随静态产物发布。

总览图的 PNG 已随研究文件保存，SVG 与覆盖记录由标准库校验；只有重新栅格化总览图才需要 Pillow 和中文字体。详细配置与范围见 [RUNTIME.md](../projects/009-webgpu-render-pipeline/RUNTIME.md)、[VALUE.md](../projects/009-webgpu-render-pipeline/VALUE.md)。

2026-10-22：009 已正式发布，构建与部署任务通过；总览图、全部运行文件和线上海滩交互已核验。详见 [009 部署验收记录](../projects/009-webgpu-render-pipeline/deployment-verification.json)。


## 011 · 水生毒理学研究档案

- 正式入口：https://yydshly.github.io/1022_codex_project/011-open-notebook-research/
- 首次发布提交：`a496004a00b6bf277ae616e24e7cabbed3be858c`；[Pages 构建与部署成功](https://github.com/yydshly/1022_codex_project/actions/runs/39743460386)。
- 摘要覆盖 Auto Paper Digest 的论文采集、NotebookLM 生成与归档能力及技术架构，说明 Europe PMC 领域适配、Open Notebook + MiniMax 替代路线、参数修复、原文精读和静态交付。
- 页面包含总览图、3 篇详细报告、1 篇综合、原 PDF、关键图页、历史回答与扩展源码快照；浏览不调用模型。
- 构建使用 Python 标准库：`package_web.py` → `package_web.py --check` → `verify_web.py` → 根 `build_site.py`。原始证据以项目 `.gitattributes` 关闭换行归一化，保持 SHA-256。
- 这是静态成果网站发布，未开放 Open Notebook 原版应用的上传与在线问答入口。验收见项目 `publication-verification.json`。

## 012 · Super Hermes

[多 Skill 问题定位与审查](../projects/012-super-hermes/README.md)通过五个问题说明能力、底层原理、模块、步骤和复用价值。上游提供 5 个 Markdown Skill 与 7 份分析模板，模型结合材料分析，宿主提供工具与证据检验；网页进一步展示我们提炼的七步定位协议、逐步输入与产物、九项报告、内存和并发实测、69 条规则及固定版本原文。七步和完整报告是研究提炼，原库主要用提示词引导且代码分析侧重单文件。

首屏、网页全图与总导航封面统一使用已生成的 `super-hermes-diagnosis-v3.png`。项目无前端构建依赖，工作流先执行 `python projects/012-super-hermes/scripts/verify_web.py`，由根汇总器复制 `web/` 到 `/1022_codex_project/012-super-hermes/`。正式入口为 https://yydshly.github.io/1022_codex_project/012-super-hermes/ ；准确部署状态与线上字节核对见 [发布记录](../projects/012-super-hermes/deployment-verification.json)。

2026-10-22 内容提交 `d1ac92e` 的 [Pages 构建与部署](https://github.com/yydshly/1022_codex_project/actions/runs/39776656381)成功。43 个项目文件均 HTTP 200 且与本地发布版本逐字节一致；总导航的五项理解摘要与指定引导图已核验。新增网页交互未在本轮重新复核，验证范围如实记录。

## 014 · Seijaku 住宅导览与三项目对比

014 使用原生 HTML/CSS/ES modules，发布文件均在 `projects/014-seijaku/web/`。Actions 先执行本项目 `scripts/package_web.py`、`--check` 和 `scripts/verify_web.py`，再由根汇总器复制到 `/014-seijaku/`，不增加前端构建依赖。首页、项目说明与网页首屏统一以生成的 `research-summary.png` 引导；摘要明确连续漫游、四季和构造效果，季节材质、构件标注、资源调度技术，以及住宅、展馆、产品与作品集扩展场景。

官方图像通过固定提交在线引用，体验区按需加载作者 GitHub Pages，每次仅运行一个 iframe；不打包未获再分发授权的原库代码和素材。分析固定版本，在线演示可能随作者更新。研究页和对比内容不要求本地 WebGL，官方实时体验需要网络与相应图形支持。

2026-10-22 内容提交 `f92e770` 的 [Pages 构建与部署](https://github.com/yydshly/1022_codex_project/actions/runs/39787944045)成功，[014 公开网页](https://yydshly.github.io/1022_codex_project/014-seijaku/)的 8 个发布文件均 HTTP 200 且与提交字节一致；总导航完整摘要和生成引导图已核对。桌面／窄屏、能力切换、对比筛选、研究方向和实际清单下载检查通过；已登记 `demo_url`，详见 [部署验证记录](../projects/014-seijaku/deployment-verification.json)。

## 013 · Old Coder 验收与证据研究

[研究网页](../projects/013-old-coder/web/index.html)使用无依赖 HTML/CSS/JavaScript，解释两套 Skill、六阶段原理、直接聊天与 CI 的差别，并提供库存幂等、限流、权限和 API 兼容的可执行教学模型。源库 Python 示例的本机部分复现、作者历史报告与教学结果分别标注。

`web/` 已含全部相对路径资源、31 份上游原文阅读副本、MIT 许可与结果 JSON，由现有 `scripts/build_site.py` 直接汇总到 `/013-old-coder/`，无需增加根构建步骤。源码哈希相关文件关闭换行归一化。检查命令：`node projects/013-old-coder/scripts/verify_labs.cjs --check`、`python projects/013-old-coder/scripts/verify_web.py` 和登记表检查。

2026-10-22 内容提交 `d727862` 的 [Pages 构建与部署](https://github.com/yydshly/1022_codex_project/actions/runs/39791306660)成功，[013 公开网页](https://yydshly.github.io/1022_codex_project/013-old-coder/)的 16 个发布文件均 HTTP 200 且与提交字节一致；首页的能力效果、技术沉淀、扩展场景摘要与指定引导图已核对。线上四个实验、原文阅读、放大/下载与 375/768/1440 宽度通过，已登记 `demo_url`。原版完整 POSIX gauntlet 和独立复核仍未执行。详见子项目 `deployment-verification.json`、`publication-browser-verification.json` 与 `verification.md`。

013 的首页封面与网页“一图读懂”使用同一份 `old-coder-overview.png`（1800 × 2600），附可编辑 SVG、放大阅读和下载。图解为本研究代码原生绘制，ImageGen 两次网络失败记录另存；库存业务是教学模型。图像及发布副本已经保存到源文件目录，CI 不需要安装绘图依赖；可运行 `python projects/013-old-coder/scripts/build_overview.py --check` 仅校验产物身份。


## 015 · heytea-style 照片二次创作与桌宠

[heytea-style 研究网页](../projects/015-heytea-style/README.md)以已有照片的二次创作为主线，展示手绘海报、风味怪兽、产品互动图与可运行桌宠。引导图使用我们生成的 capability-overview.png；原始样张与总览合成图分开标注。网页还归纳风格规则、分阶段生成、身份约束、透明帧校验与事件运行器的技术沉淀，并解释餐饮电商、原创 IP、互动营销及轻陪伴的扩展条件。

构建步骤为 `python projects/015-heytea-style/scripts/package_web.py` 和 `python projects/015-heytea-style/scripts/verify_web.py`，随后由根汇总器发布到 `015-heytea-style/`。打包仅使用 Python 标准库，核对固定上游哈希，生成自包含资源、许可、示例角色 ZIP 与离线单文件；源文件换行通过项目 .gitattributes 保持。

本地已检查七个效果版本、八种行为、十四个原理阶段、场景切换、键盘和六种屏宽。网页使用上游真实动画帧与阶段播放器，物理完成事件由按钮发送；未运行原生 Electron，也未按上游流程创作四类新作品。正式发布状态与证据以项目 deployment-verification.json 为准。

015 源码已于 2026-10-22 推送 main，[正式网页](https://yydshly.github.io/1022_codex_project/015-heytea-style/)已上线，登记表 demo_url 已登记。公网已检查七个效果版本、十四个原理阶段、桌宠交互、下载和六档屏宽，未出现页面脚本错误、图片缺失或水平溢出。文件 HTTP / SHA-256 证据见 [部署记录](../projects/015-heytea-style/deployment-verification.json)，交互证据见 [公网浏览器记录](../projects/015-heytea-style/public-browser-verification.json)。

## 016 · Verdant Forest

[程序化森林研究网页](../projects/016-verdant-forest/README.md)展示可漫游森林的立体枝叶、林下花草、风动和光雾；归纳参数化植物、确定性布局、实例化与LOD、GPU风动、体积光与镜头采集，探索自然展厅、庭院旅宿导览、交互叙事和氛围短片。引导图统一使用已有 `understanding-overview.png`，原始运行截图与生成图明确区分。

构建前运行 `python projects/016-verdant-forest/scripts/package_web.py` 及 `--check`，由根汇总器发布 `016-verdant-forest/`。网页无npm依赖；图片、来源与生成指令按哈希校验。本页五个原理实验独立绘制，完整原版按需访问作者站点；当前未提供通用资产导出SDK或与009的直接代码整合。

公开部署以本项目的 `deployment-verification.json` 和Actions记录为准；通过线上文件、引导图与摘要核对后填写登记表 `demo_url`。
