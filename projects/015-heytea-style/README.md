# 015 · heytea-style · 照片二次创作与桌宠

> 以已有照片为素材，用 AI 二次创作手绘海报、风味怪兽和产品互动图，再把角色制成可点击拖拽的桌宠；可沉淀风格规则、分阶段生成与身份约束、透明帧校验及事件驱动运行，扩展到餐饮电商内容、原创 IP 系列、互动营销与轻陪伴应用。

- **能力与效果**：海报和互动图把实物摄影质感与手绘元素结合；怪兽按照片的配色、配料和材质重设计；桌宠让确认后的角色响应点击、拖拽、闲置与光标。
- **可沉淀技术**：把风格约束变成 Skill 与提示模板，拆分生成和返修阶段，固定角色身份，再用可校验的透明动画资产和事件行为运行器交付。
- **后期使用场景**：自有商品内容、原创角色系列、活动角色互动、桌面陪伴，以及可更换风格和模型的创作工具。下面区分上游已有能力与需要继续开发的方向。

| 信息 | 内容 |
| --- | --- |
| 上游仓库 | [Hchen1218/heytea-style](https://github.com/Hchen1218/heytea-style) |
| 作者 / 署名 | heytea-style contributors |
| 固定版本 | [d5125372adcc945c2314cfb649c50407379a18ab](https://github.com/Hchen1218/heytea-style/commit/d5125372adcc945c2314cfb649c50407379a18ab)，2026-09-04 |
| 收录与研究日期 | 2026-10-22 |
| 上游代码许可 | MIT，见 [完整许可证](LICENSE.upstream.txt) |
| 示例素材许可 | CC BY 4.0；内嵌第三方商标等权利单独保留，见 [NOTICE.md](NOTICE.md) |
| 网页技术 | 原生 HTML / CSS / JavaScript，无前端依赖、无 CDN、无在线生成接口 |
| 网页入口 | [web/index.html](web/index.html)，通过下述本地 HTTP 服务打开 |
| 离线入口 | [web/standalone.html](web/standalone.html)，单文件内嵌图片、动画、源码播放器及下载内容，可直接用浏览器打开 |
| 发布状态 | 已准备 GitHub Pages 编号路径；尚未推送或验证线上发布，登记表 demo_url 留空 |

![heytea-style 能力、四种效果、原理与价值总览：照片经 AI 二次创作，走向海报、怪兽、互动图与桌宠](assets/capability-overview.png)

*内置 ImageGen 参考上游样张绘制的研究总览，桌面场景为示意；不计作本次运行源库生成的四种新作品。样张与角色署名 heytea-style contributors，CC BY 4.0。原始样张与哈希见 [SOURCE.json](SOURCE.json)，提示词、来源和图中文字说明见 [OVERVIEW.md](OVERVIEW.md)。原网页截图仍保存在 assets/overview.png。*

## 网页包含什么

1. **真实效果图集**：四类产物与七个查看版本，包括原始照片、带字 / 无字海报、两类角色、产品互动图和桌宠动作预览，可切换、对照和放大。
2. **可操作动画实验**：读取原始 v3 pet.json 和 20 条透明帧条，复用上游 EpisodePlayer 播放 8 个行为。观察进入、循环、退出，发送行走完成、落地、松手和唤醒事件，并暂停 / 继续。
3. **分阶段原理**：切换带字海报、风味小怪兽和可运行桌宠三条路径，逐步查看操作、产物和固定版本源码依据。
4. **价值与场景**：分析产品表达、反馈定位、身份延续的意义；按内容创作、系列角色、桌面陪伴、创作工作流四种需求说明可复用部分和待验证事项。
5. **来源与下载**：提供研究笔记、原始素材哈希、许可声明和带署名的上游示例角色包。

## 能力与实现

| 产物 | 发生的变化 | 主要机制 |
| --- | --- | --- |
| 带字海报 | 实物保留摄影感，背景与构图重整，加入标题及小人 | 无标题底图 → 构字参考 → 独立标题层 → Pillow 合成 |
| 无字海报 | 用一个明确动作组织实物和小人 | 独立构图、动作语法、少量道具与大留白 |
| 风味小怪兽 | 颜色、配料和材料关系转成独立角色 | 来源关系提取 → 黑线身份稿 → 锁线着色 → 人工确认 |
| 产品互动图 | 已确认怪兽与真实产品产生动作联系 | 原图 + canonical identity；锁定外观，只调整姿势 |
| 桌宠 | 角色响应点击、闲置、光标、拖拽和释放 | 透明帧条 + manifest + 多阶段行为 + Electron 透明窗口 |

风格来自提示规则与参考约束；实际创作需要宿主图像生成 / 编辑能力。Python 负责图片处理与格式校验，原生桌面运行由 Electron 完成。详细证据和取舍见 [研究笔记](notes.md)。

## 可沉淀的技术

| 技术 | 上游已有的依据 | 可进一步提炼的产物 |
| --- | --- | --- |
| 风格规则与参考协议 | Skill 路由、构图与动作语法、字形和材料规范 | 可切换视觉风格的 Skill、提示模板和审核表 |
| 分阶段生成与局部返修 | 底图与标题分离、角色先线后色、通过项锁定 | 可记录阶段输入输出、定向返修的创作流程 |
| 角色身份约束 | canonical identity 固定轮廓、脸、四肢与材料 | 跨海报、角色姿态和动画共用的角色身份档案 |
| 透明动画资产与校验 | PNG/WebP 帧条、锚点、贴地、manifest、审核图与 ZIP | 可复用的动画资产处理、审核和打包工具链 |
| 事件驱动行为与共享运行器 | 阶段完成事件、交互优先级、冷却、角色包与 Electron 分离 | 可导入不同角色的轻陪伴或活动互动运行层 |

这些是基于源码提炼的复用方向，本研究尚未将它们独立封装为通用 SDK。图像生成、自动校验和人工审美审核的责任需要分别保留。

## 后期可扩展的使用场景

| 方向 | 可以形成的体验 | 仍需增加或验证 |
| --- | --- | --- |
| 餐饮、电商与生活方式内容 | 同一商品的海报、上新图、社交内容 | 商品细节与文字保真、品牌风格、批量任务和人工筛选 |
| 原创 IP 与系列视觉 | 角色身份稿、系列互动图、贴纸或表情素材 | 多姿态一致性、素材规格、授权与跨媒介适配 |
| 互动营销与活动角色 | 产品角色在活动页或展陈终端回应用户 | 网页事件接入、行为语义、任务状态和终端交互 |
| 轻陪伴与多风格创作工具 | 桌面角色陪伴；让用户切换风格、模型和输出类型 | 原生兼容性与资源占用；模型接入、任务队列、审核与版本管理 |

活动页、贴纸导出和多模型产品化属于后续扩展；当前源库重点覆盖照片创作流程与桌宠交付。效率、转化率与留存收益需要真实任务和受众实测。

## 本地运行

本次环境：Windows、Python 3.10.11、Node.js v22.15.0。网页只需现代浏览器；打包使用 Python 标准库。Pillow 用于上游角色包校验，Playwright 仅用于开发验证。`web/standalone.html` 可直接离线打开；普通多文件版使用 HTTP 服务。

在仓库根目录执行：

```powershell
python projects/015-heytea-style/scripts/package_web.py
python projects/015-heytea-style/scripts/package_web.py --check
python projects/015-heytea-style/scripts/verify_web.py
node --check projects/015-heytea-style/web/app.js
python scripts/project_catalog.py check
python -m http.server 8015 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8015/projects/015-heytea-style/web/>。页面 fetch 读取角色数据，请使用 HTTP 服务。

素材已保存在 assets/ 与 upstream/，常规打包不访问网络。重建快照可执行 `python projects/015-heytea-style/scripts/fetch_upstream.py`，脚本验证固定上游文件的 Git blob 与 SHA-256，不抓取 private study cutouts。

### GitHub Pages

package_web.py 将素材、许可、播放器及下载文件写入忽略的 web/assets/ 与 web/downloads/，另生成内嵌资源的 standalone.html。Pages 工作流在根汇总器前执行本项目打包与检查，再由 scripts/build_site.py 复制到 015-heytea-style/。资源均为相对路径，支持 /1022_codex_project/015-heytea-style/ 前缀。

web/ 可独立静态托管。真实部署并验证后，再填写登记表 demo_url。

## 验证范围

- 固定来源的 Git blob / SHA-256，发布副本、许可证、下载角色包由脚本检查，见 [verification.json](verification.json)。
- 浏览器验证效果切换、放大、键盘、三条原理路径、场景切换、帧播放、睡眠唤醒、行走完成、松手后恢复、暂停及窄屏布局，见 [browser-verification.json](browser-verification.json)。
- 上游示例角色包通过上游 Python 校验器，见 [pack-validation.json](pack-validation.json)。
- 初版编号路径构建的 42 个文件已完成 HTTP 与字节验证，见 [初版编号构建记录](site-build-verification.json)；新增总览的发布与离线检查见 [overview-verification.json](overview-verification.json)。
- 四类效果图集仍为上游样张；新增 ImageGen 总览仅用于研究说明，尚未实测上游海报或角色创作流程。未安装或启动 Electron，未测试系统托盘、多屏和原生物理。网页完成事件由按钮发送，实际显示上游动画并推进阶段。

## 复用价值

可借鉴的是把审美经验分解为规则、参考、阶段产物、人工确认与局部返修。它可以为自有海报、原创角色、轻陪伴体验和 AI 创作流程提供结构参考。效率与一致性收益仍需自己的任务验证。

## 目录与来源

- assets/upstream/：未修改样张、GIF 与 v3 角色包素材。
- upstream/：固定版本源码与参考文档研究快照。
- web/：网页源码；assets/、downloads/ 由脚本打包。
- scripts/：固定版本抓取、发布打包与验证。
- SOURCE.json：每个引入文件的来源、许可与 SHA-256。
- notes.md / NOTICE.md：详细分析与署名边界。

[图片说明](assets/README.md) · [研究笔记](notes.md) · [源仓库](https://github.com/Hchen1218/heytea-style) · [返回项目索引](../../README.md#项目索引)
