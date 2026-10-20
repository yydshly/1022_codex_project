# 多项目 Web 部署

## 目录与地址

GitHub Pages 为一个仓库提供一个静态站点。多个研究项目的 Web 演示可以作为同一站点下的不同路径发布，而不是各自覆盖站点根目录。

```text
源码与独立构建                       汇总后的部署产物（不提交）
projects/001-alpha/web/             _site/
projects/002-beta/web/              ├── index.html          # 总演示导航
                                   ├── .nojekyll
                                   ├── 001-alpha/         # alpha 的构建结果
                                   │   └── index.html
                                   └── 002-beta/          # beta 的构建结果
                                       └── index.html
```

默认地址规划：

| 入口 | 预计地址（启用 Pages 后生效） |
| --- | --- |
| 演示导航 | `https://yydshly.github.io/1022_codex_project/` |
| 项目 001 | `https://yydshly.github.io/1022_codex_project/001-alpha/` |
| 项目 002 | `https://yydshly.github.io/1022_codex_project/002-beta/` |

这些都是路径示例；当前没有演示项目，也没有启用部署工作流。

## 添加第一个演示

1. 在实际子项目中新增 `web/`，记录依赖、构建命令、输出目录和必要的环境变量示例。
2. 为应用设置包含仓库名和项目编号的资源路径，例如 `/1022_codex_project/001-alpha/`。Vite 可使用 `base`；其他框架按其静态导出配置设置。
3. 构建每个待发布项目，将**构建结果**分别复制到 `_site/<编号-slug>/`。避免把源码、凭据、`node_modules/` 或整个研究目录当作部署产物。
4. 创建 `_site/index.html` 作为总导航，并创建 `_site/.nojekyll`。本初始化不预设导航页面样式或前端技术栈。
5. 用 `python -m http.server 8000 --directory _site` 做基础预览；涉及绝对资源路径时，还应模拟 `/1022_codex_project/` 前缀，确认样式、图片、懒加载模块和跳转正常。
6. 将 [工作流模板](../templates/workflows/deploy-pages.yml.example) 复制到 `.github/workflows/deploy-pages.yml`，在指定位置填入实际构建与汇总步骤。
7. 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**，再手动运行 **Deploy research demos**。
8. 验证线上地址后，将完整链接写入 `projects/catalog.json` 的 `demo_url` 字段，再同步首页。

工作流模板使用手动触发。项目稳定后，可以按需增加 `push` 触发和路径过滤。

## 路由与后端

- 页面资源优先使用正确的构建前缀或相对路径，避免直接请求域名根路径 `/assets/`。
- 单页应用可优先采用 hash 路由；如果使用 history 路由，需要自行实现并验证刷新后的回退行为。
- GitHub Pages 托管静态 HTML、CSS、JavaScript；需要常驻服务、数据库或私密服务端凭据的项目，应另行部署后端，在研究页说明地址与运行方式。
- 本地浏览器会获得前端构建中包含的配置，私密凭据应保留在后端。

## 官方参考

- [GitHub Pages 的站点类型、默认地址和静态托管能力](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
- [使用自定义工作流部署 GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
