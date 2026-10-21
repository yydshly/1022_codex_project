# 多项目 Web 部署

本仓库使用 **GitHub Actions → GitHub Pages**。一个站点承载多个编号项目，静态资源使用相对路径，不要求各项目采用相同前端框架。

## 线上入口

| 入口 | 地址 |
| --- | --- |
| 总导航 | https://yydshly.github.io/1022_codex_project/ |
| 001 · SwiftUIShaders | https://yydshly.github.io/1022_codex_project/001-swiftui-shaders/ |

2026-10-21 已完成首次发布。构建与部署任务成功，两个入口及运行资源返回 HTTP 200；两张引导图的线上内容与本地 SHA-256 一致。已在浏览器检查 41 项效果入口、完整图集、8 个真实效果模块与摘要内容。详见 [部署检查记录](../projects/001-swiftui-shaders/deployment-verification.json)。

总导航展示项目能力摘要、研究入口及两张生成的引导图。项目页包含能力、原理、效果、适用场景与扩展方向，以及完整的 41 种实时特效实验。

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

本地原图哈希、资源路径与静态检查已完成，当前页面尚未发布线上地址；登记表 `demo_url` 保持为空。发布后核对线上资源与交互，再更新登记表。当前浏览器与静态验证范围见 [web-verification.json](../projects/002-todofy/web-verification.json)。

## 路径与验证范围

资源与内部链接使用相对路径，可在 `/1022_codex_project/<编号-slug>/` 下运行。效果深链接使用 `#effect=Holographic` 等片段，无需服务端路由回退。修改链接后应模拟仓库前缀，检查导航、模块跳转、图解、素材、手机宽度与下载。

Pages 提供静态托管。SwiftUIShaders 的浏览器演示在客户端执行 WebGL；原库的 SwiftUI/Metal 实现需在 Apple 平台运行。PNG 导出是展示页功能，GIF/视频录制与编码属于待扩展方向。原生 Metal 画面与真机性能仍待验证。

## 官方参考

- [GitHub Pages 与静态托管](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [使用自定义工作流部署 Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
