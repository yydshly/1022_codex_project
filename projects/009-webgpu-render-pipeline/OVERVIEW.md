# 一图入口 · 从理解到复用

[打开可点击的总览](web/index.html#overview) · [高清 PNG](assets/project-overview.png) · [矢量 SVG](assets/project-overview.svg) · [生成来源与覆盖记录](overview.json)

![WebGPU 渲染库一图总览：核心价值、光照计算流程、10 类全部 89 项能力、四场景真实截图、应用方向与工程边界](assets/project-overview.png)

## 怎样阅读

1. 先看核心价值：把复杂间接光计算、实时直接光与自然环境表现组合成可复用的场景渲染流程。
2. 沿五步流程看原理：三维场景 → BVH / Surfel 采样估计 → Lightmap / 空间探针 → 逐帧光照与环境 → 画面合成。
3. 看能力版图：10 类、89 个条目全部列名，并保留每项的源码接入标记。网页里的分类板块可直接进入对应清单；会清除旧搜索和接入范围筛选，避免跳到空分类。
4. 看真实效果：四张图依次为 Cornell Box、完整海岸村庄、海滩和森林。网页中的缩略图可以选择相应演示场景；尚未启动时，点击“启动真实演示”再运行。
5. 看复用方向与边界：浏览器游戏、建筑与空间漫游、产品展厅和教学研究是基于能力推导的应用方向，需要单独集成和验收。画面渲染可复用，角色控制和任务等玩法仍由游戏项目实现。

太阳变化会使静态间接光过期，换相机不会。海滩/村庄使用浅水系统，森林使用不透明波纹溪流。图中同时保留固定依赖、补采样修复、海滩缺失房车模型、低分辨率烘焙、设备与许可等条件，详细记录见 [RUNTIME.md](RUNTIME.md)。

## 来源与准确范围

- 能力名称和接入范围来自本项目 [capabilities.json](capabilities.json)，分类来自 `research_catalog.py`。生成器检查 89 个 ID 无重复、无遗漏；数量为本研究的组织方式，不是上游官方功能计数。
- 四张缩略图依次来自 `assets/runtime/default-light.png`、`village-default.png`、`beach-default.png`、`forest-default.png`，均为先前本机 Chromium / WebGPU 实测原始截图。本图仅缩放排版，没有重绘或调色；原始参数、阶段和哈希见 [截图记录](runtime/screenshots.json)。
- 原理说明依据固定上游 `ca576b601bf84527102f1768372aa8cd96a3c55a` 的既有研究，详见 [ARCHITECTURE.md](ARCHITECTURE.md)、[PRINCIPLES-AND-AI.md](PRINCIPLES-AND-AI.md)。流程箭头是教学示意，不是模拟测量结果。
- 本图不是新的性能或全库验收。应用方向是本研究的推导，没有声称已经提供完整游戏引擎、Unity/Unreal 插件、AI 接口或定量日照分析。
- SVG 内嵌四张原始截图，无需外部图片文件；中文字体由查看设备提供。PNG 已栅格化，适合直接分享。图解为本研究原创，截图中的原库与素材权利归相应作者，见 [NOTICE.md](NOTICE.md)。

## 维护与导出

在仓库根目录执行，渲染 PNG 需要 Pillow 和可用中文字体：

```powershell
python projects/009-webgpu-render-pipeline/scripts/build_overview.py --render-png
python projects/009-webgpu-render-pipeline/scripts/package_web.py
python projects/009-webgpu-render-pipeline/scripts/verify_structure.py
python scripts/project_catalog.py check
```

Windows 默认使用系统微软雅黑。其他系统可传入 `--font /path/to/CJK-font --bold-font /path/to/CJK-bold-font`。只检查 SVG、PNG 哈希、覆盖记录和网页热点不需要 Pillow：

```powershell
python projects/009-webgpu-render-pipeline/scripts/build_overview.py --check
```

`build_overview.py` 以同一组排版指令生成 SVG 和 PNG，并更新网页中 `OVERVIEW_HOTSPOTS` 标记内的链接。能力清单或源截图改变后，重新导出 PNG；打包会拒绝使用与 SVG 不匹配的旧 PNG。
