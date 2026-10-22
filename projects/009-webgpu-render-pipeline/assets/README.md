# 图片与图解来源

| 文件 | 用途与说明 | 来源与处理 |
| --- | --- | --- |
| `upstream/lighting-baseline.png` | 作者文档中的村庄历史运行画面，展示建筑、植被、水面、泡沫与水下物体 | 固定上游 HTML 的 `live-image`，按字节提取，未修改；非本次运行 |
| `upstream/lighting-concept.png` | 作者用于说明光照/画面目标的概念参考 | 同一 HTML 的 `concept-image`，按字节提取，未修改；非运行结果 |
| `capability-map.svg` | 准备阶段、逐帧阶段与十类能力的原创研究图解 | 本次按固定源码组织的 SVG，不是效果截图或物理计算结果 |
| `project-overview.svg` / `project-overview.png` | 一图入口：价值、原理、10 类全部 89 项能力、四场景实测、应用与复用边界 | 原创图解，同一组排版指令生成；嵌入四张本机实测图，只缩放排版，没有 AI 重绘或调色。来源、覆盖 ID 和哈希见 `overview.json`，读图说明见 `OVERVIEW.md` |
| `overview-entry-desktop.png` / `overview-entry-mobile.png` | 展示页一图入口在桌面和手机宽度下的布局证据 | 本机浏览器截图；图内能力与场景链接、放大、键盘滚动和无横向溢出均另行检查，不是新的 GPU 或手机硬件测试 |
| `light-transport-explained.svg` | 红墙与白球的直接光、反弹光、采样和缓存复用 | 原创 SVG 教学示意；箭头表示能量关系，非逐光子模拟或上游运行结果 |
| `rendering-vs-ai.svg` | 三维场景渲染与常见 AI 单图重绘的输入、依据及视角对照 | 原创 SVG 流程示意，没有调用 AI；结构条件的补充依据见原理文档中的 ControlNet 论文 |
| `study-desktop.png` / `study-mobile.png` | 本次研究展示页的浏览器布局证据 | 本地静态资料页截图，不是上游 WebGPU 画面实测 |
| `principles-desktop.png` / `principles-mobile.png` | 新增通俗原理与交互讲解的桌面、手机展示记录 | 本地静态教学页截图，不是光照计算或 AI 效果实测 |
| `runtime/cornell-initial.png` | 原库 Cornell Box 首次实际出帧 | 本机 Chromium / WebGPU 截图；固定来源与配置见 `runtime/screenshots.json` |
| `runtime/default-light.png` / `runtime/sun-zero.png` / `runtime/sun-low-angle.png` | 同一相机下默认光、强度归零与低角度太阳 | 同一真实三维场景画面区域截图，无调色或重绘；改变太阳后旧间接光尚未重烘焙 |
| `runtime/camera-side.png` | 默认太阳下的斜侧相机视图 | 同一几何重新渲染；与太阳参数分开记录，不将其视为单纯补光 A/B |
| `runtime/demo-desktop.png` / `runtime/demo-mobile.png` | 真实 WebGPU 画面与中文面板的桌面、手机宽度记录 | 原库在本机桌面 Chromium 运行，不表示已验证实体手机 GPU |
| `runtime/village-default.png` / `runtime/village-sun-zero.png` / `runtime/village-low-sun.png` | 完整村庄的默认太阳、强度归零与低角度太阳 | 本机运行固定源码场景，旧间接光未随滑杆自动重算；水面持续运动，非静态像素 A/B |
| `runtime/village-side.png` | 完整村庄原始侧面相机预设 | 同一几何重新渲染；完整房屋、植被、码头、船与水面均保留 |
| `runtime/village-desktop.png` / `runtime/village-mobile.png` | 村庄阶段的两场景选择器、真实村庄和共享控制面板 | 本机桌面 WebGPU 的响应式验证；记录不等于实体手机或统一性能测试 |

两张上游图来自：

[public/lighting-look-development.html @ ca576b601bf84527102f1768372aa8cd96a3c55a](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/public/lighting-look-development.html)。

原始俄文替代文字、HTML id、SHA-256 和字节数见 [media.json](../media.json)。现有画面和概念图的构图不完全相同，因此不把它们制作成严格像素前后对照。

没有调用 ImageGen 或合成声称为真实运行效果的图片。新增 `runtime/` 截图是本机运行证据，参数与哈希见 [runtime/screenshots.json](../runtime/screenshots.json)。上游图片和场景/素材的权利仍归原作者/素材权利人；原库未提供仓库级许可证，详见 [NOTICE.md](../NOTICE.md)。

四场景阶段的 `runtime/beach-*.png` 与 `runtime/forest-*.png` 为本机固定源码加明确补采样修复后的真实 WebGPU 截图，包含默认、细节、太阳变化与页面布局；参数、哈希和处理范围见 `runtime/screenshots.json`。海滩保留原浅水模拟，森林溪流为原不透明波纹材质，截图不代表跨设备性能验收。
