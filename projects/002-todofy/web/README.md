# Todofy 源库官方界面展示网页

[打开网页](index.html) · [研究首页](../README.md) · [原图来源与哈希](../screenshots.json) · [当前版本校验](../web-verification.json)

本页直接展示源库的八张官方 PNG，使用原始文件内容、尺寸、英文界面、拍摄日期和作者示例，不重新绘制产品界面。原先自制的任务工作台、任务编辑、拖动、计时和场景数据模拟已经移除。

首屏与项目索引采用我们生成的 [总结引导图](assets/understanding-summary.png)，概括“任务展示板＋管理驱动”的本质、能力、效果，以及对我们参考看板样式与交互组织的意义。

## 页面结构

1. **官方原图展示**：Today、Board、Calendar、Focus、Quick capture、Journal、Voice、Settings。可切换、放大、打开原尺寸文件及追溯上游文件。
2. **我们的源码分析**：解释输入、Tauri / Rust / SQLite、视图组织和后台调度；字段职责来自真实源码，不生成自制任务记录。
3. **使用场景**：六个建议使用路径与边界，每个场景链接到对应官方界面。
4. **理解与参考意义**：以任务数据、管理界面、驱动逻辑三层解释本质，用一张图总览能力与效果，并将看板布局、卡片信息层级和交互组织作为我们重点研究的参考价值。

产品画面、中文注解和原创源码分析图分别标明来源。截图不是可操作的原生程序；其按钮、数字和安装状态均为作者展示环境的画面。需要实际操作时，使用页面中的官方安装包入口。

## 运行

直接用浏览器打开 `index.html`，或在仓库根目录运行：

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory projects/002-todofy/web
```

再访问 `http://127.0.0.1:8000/`。页面采用无依赖 HTML / CSS / JavaScript，无需 npm、账号、CDN、语音模型或原生后端。根站点汇总器会复制本目录到 `002-todofy/`，详见 [部署指南](../../../docs/deployment.md)。

## 资源与来源

| 文件 | 用途与来源 |
| --- | --- |
| index.html / style.css | 本研究的展示排版、原理与场景容器 |
| app.js | 仅负责图片切换、放大、章节和场景导航；没有任务数据模型或计时器 |
| assets/upstream/*.png | 上游固定提交 docs/ 中的八张原始截图，与项目 assets/upstream/ 同名文件及 Git 内容哈希一致 |
| assets/upstream/LICENSE.todofy.txt | 保留的上游 LICENSE 原文 |
| assets/architecture.svg | 本研究的源码分析图，明确标为分析内容 |
| assets/understanding-summary.png / .svg | 本研究的一图总结，内含上游 Board 原图和我们的三层理解、能力效果及参考重点 |

固定研究提交：`2ae76fc80b0b96ad8191e3d1ae4949ee340190a7`。图片版权归 Salar Zeidanlou / unifybrowse，作为本项目研究引用；不对上游材料追加本仓库许可。变更截图版本时，应同时更新两处图片、来源清单、许可、页面注解和校验记录。

原生任务、通知、语音与外部同步仍未在本机运行。当前版本的实际校验范围以 [web-verification.json](../web-verification.json) 为准，不继承已移除模拟页面的任务操作测试结果。

总结图原始文件位于项目 `assets/`，网页副本与之相同。生成方式及依赖见 [复现说明](../REPRODUCTION.md)，来源和渲染环境记录在 [summary-image.json](../summary-image.json)。
