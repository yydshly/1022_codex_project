# heytea-style：能力、原理与价值研究

研究日期：2026-10-22。固定版本：d5125372adcc945c2314cfb649c50407379a18ab。
上游：[Hchen1218/heytea-style](https://github.com/Hchen1218/heytea-style)。

## 研究结论

项目将“实物摄影 + 不规则手绘”的视觉表达组织成 Skill 工作流，并补充图片工具、角色包协议和桌宠运行器。生成质量依赖宿主模型与人工审核；运行阶段由已生成帧和事件规则驱动。

我们的理解可以概括为：以已有照片做 AI 二次创作，输出海报、怪兽、产品互动图，并进一步交付可点击拖拽的桌宠。可沉淀的是风格规则、分阶段生成与局部返修、身份约束、透明帧校验和事件运行层；后续可接自有商品内容、原创 IP、活动互动与轻陪伴体验。

本研究查看固定源码、引用上游样张、验证示例角色包并制作浏览器展示。另用内置 ImageGen 合成一张能力、四类效果、原理与价值总览；这张概览不计作源库创作流程实测。未启动原生桌宠。下述上游能力依据说明和代码；复用价值为本研究推导，需要具体业务实测。

## 能力：从照片到哪些产物

带字海报保留主体摄影质感，以留白重整构图，歪扭中文标题优先，小人动作服务于标题。无字版让主体和动作组织成独立场景。上游原始食物图含多盘食物，两版选择不同主体、不同构图。

角色有两条路线。source-faithful 让原物本身成为角色，保留轮廓、分区和识别细节；flavor-monster 从颜色、配料、材料和关系重新设计独立怪兽，要求非颜色线索参与身体结构。确认后的 canonical identity 锁定身体、脸、四肢、颜色与材料，约束产品互动图和后续动作。

产品互动图同时使用原始照片和确认角色，以投、抱、推等一个主动作建立联系。示例把黄色风味块投回真实饮品，用轨迹表达因果。

v2 写实卡通有十二个固定动作，可加 fall / touch。v3 怪兽定义六至十个行为，本例八个。v3 支持多阶段、持续睡眠、点击和拖拽互斥、逐帧贴地。两协议编译为统一内部模型，共用窗口、物理、托盘。怪兽要求运行器 3.1.0 或以上。

## 原理：规则、生成、处理与运行

### Skill 负责流程

SKILL.md 选择路径并规定参考文件与确认节点。实际视觉生成需要宿主图像能力。Python 依赖只有 Pillow；仓库未提供执行整套视觉创作的独立推理服务。

约束包括主体可用性、两版独立构图、实物摄影感、人物比例和线条、标题和动作主次、来源特征映射、身份锁定、动作与透明边缘审核。

### 海报分层

流程：无标题底图 → 构字参考 → 独立标题层 → 合成。字形参考把手写感落实到骨架、笔画、间距和版式。文字可单独返修。

composite_title_layer.py 将标题转换 RGBA，提取灰度，以阈值区分暗笔画，与源 alpha 相乘，再裁去空白，形成黑色透明标题。随后缩放、定位并 alpha 合成。它负责像素处理，不理解或纠正字义。

### 先线后色

怪兽黑线阶段检查轮廓、清楚友好的脸和两手两腿，按原尺寸、300% 局部和 120–140 px 小尺寸审核。着色阶段锁定通过的黑线，用蜡笔等材料表达包含、沉积、覆盖等来源关系。失败部分定向修正，已通过部分继续锁定。

### 从帧条到行为

pet.json 描述画布、锚点、命中区域、行为、时间和触发绑定。动画是带真实 alpha 的水平 PNG/WebP 帧条。每帧宽高对应画布。

阶段可以使用 fps 或逐帧 durationsMs。once 通常在 animation-finished 后结束；loop 等待 motion-finished、floor-impact、pointer-released、wake-requested 或 timeout 等外部事件。

runtime-model.js 编译两种协议，EpisodePlayer 管理阶段，TriggerController 负责优先级、环境行为和冷却，renderer 用 Canvas 切片绘帧，Electron 主进程提供透明窗口、位置和物理完成通知。

网页直接复用 MIT EpisodePlayer 并读取原始 manifest，适配器加载 20 条帧条，按 alpha 可见底边为 grounded 阶段对齐锚点。移动和落地事件由按钮发送，以便观察；未运行完整触发调度器和 Electron。

## 交付为什么有价值

运行器只安装一次，角色通过轻量 ZIP 导入，换角色不需复制整个 Electron 应用。工具生成审核表、暗底逐帧审计、预览与交付入口，检查路径、尺寸、透明度、行为可达性等。

格式检查覆盖可量化条件；审美、角色自然程度和动作语义仍需要看图。因此上游设立形象与动作两个确认关卡。

## 场景与复用价值

### 可沉淀的技术及证据

| 技术模块 | 关键证据 | 可复用价值与边界 |
| --- | --- | --- |
| 风格与参考协议 | SKILL.md、style-guide.md、lettering-guide.md、mixed-media-style-guide.md | 用规则、参考角色和阶段材料控制风格；换风格需要重新建立规范和样本 |
| 分阶段生成与返修 | 海报底图 / 标题分层；黑线 / 着色分离；desktop-pet-workflow.md 的局部修复规则 | 限定返修范围并锁定通过项；实际图像仍依赖模型与人工判断 |
| 身份约束 | desktop-pet-character-modes.md、canonical identity | 让系列图和动作共享身体、脸、四肢与材料定义；跨姿态稳定性仍要实测 |
| 透明动画资产管线 | prepare_generated_animation_strips.py、validate_desktop_pet_pack.py、build_desktop_pet_pack.py | 拆帧、透明度、画布和锚点、结构验证与打包可工程化复用 |
| 事件行为与运行层 | runtime-model.js、episode-player.js、trigger-controller.js、main.js | 复用阶段推进、优先级与冷却，让角色包独立于运行器；网页、终端等新宿主需适配 |

本研究完成了规则和代码的归纳、上游帧条与阶段播放器的网页展示，尚未交付独立通用 SDK。

### 后期扩展场景

| 方向 | 可复用内容 | 下一步验证 |
| --- | --- | --- |
| 餐饮与生活内容 | 实物 + 留白 + 单动作语法、标题独立返修 | 产品保真、中文、可用率、返修次数和耗时 |
| 原创角色与系列视觉 | 来源映射、身份约束、两阶段设计 | 多姿态多画幅的脸、轮廓、肢体和材料一致性 |
| 轻陪伴原型 | 透明帧协议、多阶段事件、角色包分离 | 多屏、拖拽、落地、资源占用和受众接受度 |
| AI 创作工作流 | Skill 路由、阶段产物、锁定通过项与局部返修 | 用固定任务比较质量、耗时和修改成本 |

在这些基础上可以继续开发：餐饮与电商商品内容批量任务；原创 IP 的系列互动图、贴纸和表情导出；活动页、展陈终端的角色回应；多角色桌面轻陪伴；可切换视觉风格、图像模型并记录生成版本的创作工具。它们需要额外的品牌规范、模型和任务管理、输出适配及业务事件接入，不能把候选场景视为源库开箱即用功能。

减少重复沟通、定位返修范围和延续身份是价值推断。没有对照实验时，不写成量化效率或商业转化承诺。

## 验证边界

原始来源固定到一个 commit，并验证 Git blob 和 SHA-256。发布网页不依赖上游在线素材、CDN 或模型。打包脚本检查发布副本和下载内容；浏览器检查图集、行为、流程、场景、键盘和响应式布局。

本次图像模型仅用于生成研究总览，未按上游流程创作新海报或角色，未运行 Electron。网页没有覆盖原生托盘、跨屏和系统物理。作者样张说明已有输出形态，不能单独证明任意照片的成功率。

## 固定版本证据

- [Skill 路由与确认](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/SKILL.md)
- [风格与动作语法](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/references/style-guide.md)
- [字形与分层](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/references/lettering-guide.md)
- [角色设计](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/references/desktop-pet-character-modes.md)
- [角色与动作工作流](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/references/desktop-pet-workflow.md)
- [角色包协议](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/references/desktop-pet-pack.md)
- [阶段播放器](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/assets/desktop-pet-runtime/src/core/episode-player.js)
- [素材授权](https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/ASSET-NOTICE.md)

独立研究，与喜茶没有合作或授权关系。代码 MIT；自制例图与角色素材 CC BY 4.0，署名 heytea-style contributors；第三方商标等权利另行保留。未引入上游 private study cutouts。
