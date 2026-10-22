# 014 · Seijaku 研究笔记

## 2026-10-22 · 来源核对与网页创建

- 用户要求新建子项目，以网页演示与分析能力、效果、价值，并对比同类历史研究。
- 通过脚本分配 `014-seijaku`，保留既有编号。
- 固定 Seijaku `e0cb3b5`，对照 Sublevel `355a158`、Kage `4399487` 和已有住宅 README / DESIGN_CONTRACT。
- 将房间图、平面图、开门、导览和有限环绕列为已有基础；季节、构造、启动预热与背景采样列为研究增量。
- 沿用无依赖静态网页与 GitHub Pages 汇总结构，没有新增后台或账号系统。
- 官方图片在线引用，iframe 加载原作，仅打包自有总览图与原创住宅历史截图。
- 页面包括三原作切换、章节入口、8 项能力、5 步原理、11 项对比、4 类应用、6 项研究方向与 JSON 下载。
- 实际验证结果补记到 `verification.json`；没有进行同设备性能横评。

## 检查命令

```powershell
python projects/014-seijaku/scripts/package_web.py
python projects/014-seijaku/scripts/package_web.py --check
python projects/014-seijaku/scripts/verify_web.py
python scripts/project_catalog.py sync
python scripts/project_catalog.py check
```

## 浏览器与发布目录验证结果

- 1280×720、390×844、768×1024 布局无页面横向溢出；窄屏对比表在自己的滚动容器内显示。
- 8 项能力、6 项研究方向、对比筛选、原理页签和键盘 ArrowDown 已检查；实际下载 JSON 经解析包含 8 / 11 / 6 项及固定 SHA。
- Seijaku 原库在内嵌区成功出帧，冬季切换文字与选中状态正确，构造章节画面和 Canvas 已观察。
- Sublevel 观察到 HTML 与源库加载器，未确认完整 WebGL 就绪；Kage 独立原作可打开，本次内嵌未完成加载，因此增加超时回到预览及独立入口。没有将两者记为完整运行验收。
- 静态检查、ES module 语法、登记表检查与根汇总构建通过。准确范围见 verification.json。

## 2026-10-22 · 单图研究总览

- 根据用户追加要求，生成 `assets/research-summary.png`（1024×1536），将可见效果、实现流程、Kage / Sublevel 对比、已有住宅基础、优先研究模块和应用方向整理在一张图中。
- 使用内置 Imagegen；完整生成指令保存在 `assets/research-summary-prompt.txt`。庭院参照作者在线运行截图，其余场景为示意，图文均注明 AI 概览；参考截图仅在忽略目录本地留存。
- 总览接入网页 `#overview`、顶部导航、项目 README 及登记表封面，保留原有流程 SVG。提供打开原图、下载原图和查看生成指令入口。
- 桌面 1280×720 与窄屏 390×844 无页面横向溢出；PNG 已完整加载，实际浏览器下载与源文件逐字节一致，PNG / 指令 HTTP 返回 200。
- 项目打包、来源摘要、静态路径、登记表同步与检查通过；根站点重新汇总到 `_site/seijaku-summary-20261022-01/`，总览与指令均随编号页面打包。
- 后续模块仍是研究建议，未新增 SDK 或性能收益声明。浏览器检查范围记录在 `verification.json` 的 `summary_infographic`。
