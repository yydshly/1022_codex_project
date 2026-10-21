# 多项目 Web 部署

本仓库使用 **GitHub Actions → GitHub Pages**。一个站点承载多个编号项目，静态资源使用相对路径，不要求各项目采用相同前端框架。

## 线上入口

| 入口 | 地址 |
| --- | --- |
| 总导航 | https://yydshly.github.io/1022_codex_project/ |
| 001 · SwiftUIShaders | https://yydshly.github.io/1022_codex_project/001-swiftui-shaders/ |
| 002 · Todofy | https://yydshly.github.io/1022_codex_project/002-todofy/ |
| 004 · XXD Panel 106 | https://yydshly.github.io/1022_codex_project/004-xxd-panel-106/ |

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


## 006 · oil-tone

[写作约束研究网页](../projects/006-oil-tone/web/index.html) 说明能力、原理、使用场景与对我们的意义：将 23 条文字规则交给 AI，引导起草、润色和结构调整，保留事实、减少空话；可复用为文章、产品文案和口播的编辑标准与完整提示词。引导图采用我们已生成的理解总结图。

页面包含六步执行链路、23 条规则检索、完整提示词复制与下载、21 处改稿批注、脚本结果和源码阅读。网页只展示已保存的研究材料，没有在线模型接口。教学产品与数据为虚构设定，Python 检查真实执行；9 → 0 是提醒数变化，不是质量评分。

已生成的 web/data.js 与发布资源随项目提交；根汇总器直接复制到 `/006-oil-tone/`，现有 Actions 无需新增依赖。内容或上游快照变更后执行 `python projects/006-oil-tone/scripts/package_web.py`；加 `--check` 核对生成结果、快照哈希和脚本输出。源码与 MIT 许可经 web/assets/source/ 发布，不复制整个研究目录。

2026-10-21 已发布至 [006 · oil-tone](https://yydshly.github.io/1022_codex_project/006-oil-tone/)。内容提交 `863c9e1`，[Actions 构建与部署成功](https://github.com/yydshly/1022_codex_project/actions/runs/39605092607)；13 个发布文件 HTTP 200，响应与提交字节一致，指定总结图哈希一致。线上流程、规则搜索、21 处批注、提示词复制与下载、桌面及手机布局已检查。记录见项目 [部署验证](../projects/006-oil-tone/deployment-verification.json) 与 [verification.md](../projects/006-oil-tone/verification.md)。
