# 验证范围

## 2026-10-22 GitHub Pages 正式发布

- 发布提交 `01510fd` 的构建和部署任务均通过。线上入口明确说明光照效果实现、缓存原理、实际效果及游戏 / 空间漫游 / 展厅等复用方向，使用既有总览图引导。
- 总导航与项目页均可访问，总览 PNG 与本地规范原图 SHA-256 一致；运行清单包含的 55 个文件逐一按发布清单哈希核验。
- 线上海滩真实出帧；太阳低角度参数、光照强度归零、水面近看相机与恢复默认均回传正确状态，未发现浏览器运行错误。其他场景的完整既有验收保留在运行记录中。
- 1280 / 375 px 下没有页面横向溢出，摘要、三个价值说明、总览引导图与四个场景选项均存在。资料 ZIP 中的价值说明、总览图和 89 项能力清单核对通过。
- 具体发布来源、设备与参数、截图哈希和准确范围见 [部署验收记录](deployment-verification.json)。此次线上验收不增加跨设备 FPS 或全库验收结论。

## 2026-10-22 一图入口

- `project-overview.svg` / `.png` 覆盖 10 类全部 89 个能力 ID、源码接入标记、五步成像流程、四张实测缩略图、复用方向与工程边界。图像尺寸 2200 × 4400，四张原始截图内嵌在 SVG 中。
- 总览由同一组排版指令导出 SVG 和 PNG，逐段检查中文、布局与真实截图。`overview.json` 保存输入、输出哈希和全部覆盖 ID；打包会拒绝与 SVG 不匹配的旧 PNG。
- 网页主导航、主按钮和子项目 README 都加入入口。24 个图中链接覆盖原理、全部能力分类、四场景和边界；图中能力入口会重置旧搜索和接入范围，实测 FFT / 实验室筛选后进入 GI 显示 10 项，再进入水分类显示 13 项。
- 四张实测缩略图依次选中正确场景，未启动时仍按需启动。放大查看显示 1600 px 宽的 SVG，Escape 可关闭，手机宽度下键盘横向滚动到 40 px，页面本身不横向溢出。
- 375、768、1280 px 下图片正常加载、热点在图内、页面没有横向溢出；浏览器没有新增控制台错误。入口布局证据见 `assets/overview-entry-desktop.png`、`assets/overview-entry-mobile.png`。
- 此次只更新研究入口与图解，没有改动已经验证的 WebGPU 渲染桥接或算法。

## 2026-10-22 海滩与森林接入

- 原库 `createBeachScene`、`createForestScene` 在固定依赖、主管线和真实 WebGPU 上完成首帧，四场景共享六个滑杆。新增水面/棕榈、溪流/树冠细节预设，森林允许负仰角向上看。
- 海滩保留浅水 Worker、浮球与植被更新；缺少房车 GLB，采用原参数 `van=0`。森林保留近远景植被、地表和不透明波纹溪流，不声称采用海滩水模拟。
- 海滩 2048 页排布失败；1024 页与稀疏采样触发空 chart 检查；每纹素采样超过 262144 surfel。定位到补采样原子计数先于覆盖判断，增加一个有效表面条件后，原 1024 / 0.5 m 配置完成出帧及重烘焙。所有原正确性检查保留，补丁及 SHA-256 随构建记录。
- 两新增场景分别验证太阳方位、高度、强度归零、三个相机滑杆和细节视角；重烘焙后 `bakedSun=[110,18,4]`、`stale=false`。暂停检查只针对主渲染器，不声称冻结独立水 Worker。
- 连续调整输入时，旧状态回传曾覆盖较新滑杆值；增加每次会话内的递增控制编号，丢弃落后的回传，在森林中连续调整六项参数通过。
- 375、768、1280 px 下四个选项与细节控件均存在，页面没有横向溢出；这是桌面浏览器响应式检查，不是实体手机 GPU 测试。
- 原始截图与完整回传见 `assets/runtime/`、`runtime/screenshots.json`、`runtime/verification.json`。历史记录中的“尚未运行”仅对应当时阶段。

## 2026-10-22 完整海岸村庄接入

运行原库 `createMidseeVillageScene` 的完整场景，保留房屋、钟楼、植被、码头、小船、海岸与 Worker 浅水系统，并与 Cornell Box 共用主管线与六个控制滑杆。村庄资源从固定提交读取，React/Fiber 场景与 Worker 都由 production build 打包，本地静态目录提供全部文件。

- 实际场景遍历：181 个网格对象、22,169 个网格实例，约 2,894,054 个三角形；是几何量统计，非逐帧可见量或性能承诺。
- 村庄默认光、太阳强度归零、低角度太阳和侧视预设均保存引擎回传及原始截图。水面持续运动，截图之间不作严格静态像素 A/B。
- 村庄重烘焙后 `bakedSun` 从 `[45,55,4]` 更新为 `[110,18,4]`，旧间接光提示消失。暂停时主渲染器累计绘制/计算调用保持不变；暂停画面不声称停掉独立水 Worker。
- Cornell → 村庄与村庄 → Cornell 通过重新启动 iframe 完成，场景采用独立相机半径与默认视角；通道 session 防止旧场景回传覆盖新状态。
- 固定版本在村庄 512 光照页试验中触发 chart 测量检查，2048 单页配置完成真实出帧。未删除检查或改写算法；不把此结果推广为所有分页配置均通过。
- 额外双标签并行加载时出现浏览器页面崩溃；并行多实例不计入通过范围，单页切换始终只保留一个场景。该现象保留在机器记录中，未作未经定位的归因。

准确配置、设备、控制检查、最终浏览器状态与资源记录见 [runtime/verification.json](runtime/verification.json) 和 [RUNTIME.md](RUNTIME.md)。

## 2026-10-22 原库 Cornell Box 真实运行

后续任务已从静态资料扩展到真实 WebGPU。固定源码、依赖、配置、按钮到引擎的调用链与重建步骤见 [RUNTIME.md](RUNTIME.md)。机器记录在 [runtime/verification.json](runtime/verification.json)，真实截图的来源和参数在 [runtime/screenshots.json](runtime/screenshots.json)。

- 原库场景与主管线完成 WebGPU 初始化、BVH / Surfel、Lightmap 与探针烘焙、着色器编译和真实出帧。不是把作者历史图放进画布。
- 太阳强度归零、高度/方位预设与相机侧视均有引擎回传与真实画面记录；画面变化的像素比较仅作交互证据，不作画质评分。
- 太阳改变后提示旧间接光；按当前太阳重烘焙后，缓存依据从 `[45,55,4]` 变为 `[110,18,4]`，状态恢复一致。
- 375px 手机宽度中，相机预设与滑杆仍能控制实际画面，页面不横向溢出。它是桌面浏览器的响应式检查，不是实体手机 GPU 验收。
- 编号路径 `/1022_codex_project/009-webgpu-render-pipeline/` 中的引擎、纹理与父页控制正常工作。最终控制、资源、暂停与构建检查结果以运行记录为准。
- 依赖按锁文件执行 `npm ci --ignore-scripts --no-audit --no-fund` 成功；真实产物来自 Vite production build。资料与资源检查继续覆盖此前的 89 条清单和原理页。

以下为前两阶段的历史验证记录；其中“未运行上游”描述当时范围，不覆盖新增 Cornell 与村庄实测。仍未验证其余场景、全库类型检查、跨设备画质和统一 FPS。

## 2026-10-22 原理与 AI 对照补充

本次在既有研究上增加通俗教学资料，原有 89 项能力计数不变。`explain.json` 是维护源，由 `scripts/build_explainer.py` 生成 [PRINCIPLES-AND-AI.md](PRINCIPLES-AND-AI.md) 与 `web/explain-data.js`；打包和 `--check` 同时检查两份产物。

- 四个光照步骤均可切换；Tab / Enter 可选择下一步，焦点留在按钮上。
- 九张算法卡片展开后均包含方法、边界和固定源码；24 个算法来源链接均指向 `ca576b601bf84527102f1768372aa8cd96a3c55a`。
- 三种房屋情境可切换，分别说明换光、换视角、只有照片时的输入和限制；七项比较完整显示。
- 三种“模型”术语可展开，AI 空间条件的补充和 ControlNet 原始论文链接可见。
- 两张新图可放大，Escape 关闭；375px 小屏中，960px 图解位于可滚动图片区域内，方向键滚动有效，页面本身不横向溢出。
- 375、768、1280px 页面布局检查通过；手机对照表按行纵向展示，已加载图片无破损，控制台未见错误或警告。
- 本地与仓库编号前缀路径分别检查 30 个页面文件，HTTP 200，返回字节与打包源文件相同。编号路径下新增卡片和情境交互正常。
- ZIP 中新增文档、讲解 JSON 与两张 SVG 均与维护源字节相同。三张 SVG 语法、Markdown 链接、页面资源、JavaScript 语法、资料生成一致性和根项目登记检查通过。
- 界面记录：[桌面](assets/principles-desktop.png)、[手机](assets/principles-mobile.png)。只证明本次静态教学页面的布局和内容，不代表引擎或 AI 运行效果。

补充检查命令：

```powershell
python projects/009-webgpu-render-pipeline/scripts/build_explainer.py --check
python projects/009-webgpu-render-pipeline/scripts/package_web.py --check
python projects/009-webgpu-render-pipeline/scripts/verify_structure.py
node --check projects/009-webgpu-render-pipeline/web/explain.js
node --check projects/009-webgpu-render-pipeline/web/explain-data.js
```

本次未运行上游 3D 场景，也未调用 AI 生成或编辑图片。以下保留最初能力展示的验证记录与边界。

本轮的用户任务是“创建子项目，尽可能完整地汇总与展示能力”。验证对象是研究条目的证据、资料一致性和静态展示的数据流，不是上游 3D 引擎的画质验收。

研究页流程：打开页面 → 加载本地清单 → 搜索/筛选 → 展示匹配项 → 查看原理与固定源码 → 复制场景路由或下载资料。

## 源码与资料

- 固定 SHA、完整树与许可字段均已核对；334 个文本文件已记录 SHA-256 与行数。
- 89 个条目的来源文件、锚点和行号逐项核对；场景引用与参数示例检查可定位。
- 14 个入口包括资料页和缺装配的独立实验室，清单明确标注，并未全部认定为可运行场景。
- 作者两张图片的原始字节和 SHA-256 可核对；历史画面与概念参考分开标注。
- 能力 Markdown、JSON 与页面数据从同一份维护数据生成，`--check` 可检查漂移。

## 静态展示

结构、资源、浏览器操作、手机布局和编号路径验证的最终机器记录保存在 [verification.json](verification.json)。

```powershell
python projects/009-webgpu-render-pipeline/scripts/build_research.py --check
python projects/009-webgpu-render-pipeline/scripts/package_web.py --check
python projects/009-webgpu-render-pipeline/scripts/verify_structure.py
node --check projects/009-webgpu-render-pipeline/web/app.js
python scripts/project_catalog.py check
```

检查重点包括：89 项默认可见；类别、关键词与接入范围组合；空搜索结果与重置；详情打开与 Escape；参数索引；14 个路由复制按钮；图片放大与标签；JSON/ZIP 下载和图片资源；桌面/手机无横向溢出；浏览器错误与失败资源。

## 明确未验证

- 未安装、构建、启动或修改上游 3D 应用；没有本机上游渲染截图。
- 未测量 GPU 兼容性、实时 FPS、CPU/GPU 帧预算、冷/热缓存启动或内存峰值。
- 未执行上游 Playwright、Vitest 和 npm 全部检查。
- 未补齐缺失 vendor、React 依赖、JSX 配置或独立实验室页面接线。
- 未推送或部署；`demo_url` 留空。

原库运行环境的已知缺口见 [REPRODUCTION.md](REPRODUCTION.md)，后续实验见 [notes.md](notes.md)。
