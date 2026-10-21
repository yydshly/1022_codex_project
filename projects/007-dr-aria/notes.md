# 007 · dr-aria · 独立角色动画：研究笔记

## 2026-10-21 · 抽取角色层

- 研究问题：能否将角色动画从原来的 Claude 心理陪聊应用拆出，连接用户自己的 Agent。
- 上游版本：`ff26c94cf1d6879ad98838df9c50104d06419eb6`，MIT，Copyright © 2026 Michael Myburgh。
- 核心来源：`build/page.html` 的 `AsciiTherapist`、`Voice`、调色板与角色样式；`build/art.json` 的字符 / 颜色网格。
- 不需要引入：原项目 Python bridge、心理陪聊提示词、技巧卡、记忆 wiki、账号登录、Claude 进程管理。
- 抽取目标：原生浏览器模块 + 内嵌 ART + Shadow DOM + 明确的事件协议。

### 源码审查发现

1. `setState()` 全局查找 `lamp`；独立组件应使用实例内 DOM，不依赖页面 id。
2. 上游 `stop()` 清除说话计时器却不兑现当前 Promise，可能让 `say()` / `stream().done` 悬挂；需要明确的取消与结算。
3. 重置 Promise 队列不会删除已经注册的旧播放任务；需代次或任务取消标记。
4. `destroy()` 遗漏说话定时器和 blink、nod、gaze、气泡隐藏的匿名 timeout；需统一登记并清理。
5. 旧气泡隐藏计时器可能干扰下一条消息；新播放应取消旧隐藏任务。
6. `think()` / `write()` 与播放中的文字会争用状态；适配层和组件需明确状态衔接。
7. 原版逐 UTF-16 单元取字符，会拆开 emoji；应按 Unicode 字符消费，并考虑流式片段边界。
8. 原版中文字符使用默认嘴型，中文标点没有停顿，音效过滤规则只涵盖英文和部分符号；中文可读不等于中文语音口型。
9. 原版减少动画设置只关闭 CSS 呼吸，JS 环境动画仍运行；组件需真正尊重系统偏好。
10. 原版 Voice 是全局单例，音量、静音、存储和音频生命周期共享；独立实例应明确资源归属。
11. 原版 fit 依赖全局 1240×720 舞台；组件应按自身容器适配尺寸。

### 事件协议核对

按 OpenAI Docs 技能先搜索，再 fetch [Codex 非交互模式官方文档](https://learn.chatgpt.com/docs/non-interactive-mode#make-output-machine-readable)。确认 `codex exec --json` 输出 JSONL，常见事件为 `thread.started`、`turn.started`、`item.*`、`turn.completed`、`turn.failed` 与 `error`。官方示例中的 `item.completed` / `agent_message.text` 是完整消息，不是 token delta。

核对 [Claude Code headless](https://code.claude.com/docs/en/headless) 与 [SDK streaming-output](https://code.claude.com/docs/en/agent-sdk/streaming-output)。开启 partial 后，`stream_event` 中的 `text_delta` 与 `assistant` 完整块快照会同时存在；完整块快照可在 `content_block_stop` 之前到达，同一 message id 可能有多个内容块。适配器必须避免增量与快照重复播放，过滤推理和工具参数，区分子 Agent 消息。

### 本次验证记录

本次运行静态演示与 `tests/browser.mjs`，七组检查通过，详见 `verification.json`。覆盖状态按钮、中文、跨流片段 emoji、文本转义、流式播放、停止和销毁、多实例隔离、Claude/Codex 去重、工具前后多段回复、390px 布局和初始减少动态设置。确认停止与销毁会兑现当前和排队的 Promise；销毁后登记的计时器集合均为空。

CLI 事件可能比逐字播放更快，因此 `handle(thinking/working)` 在前一段文字之后排队，直接控制方法仍可中断。增加快速事件回归，确认工具前后的两段文字均完整展示。

没有执行真实模型调用。演示中的 Claude / Codex 事件是按官方结构编写的样例，不是实录。未运行上游陪聊、技巧卡或记忆测试，未实测语音朗读（本组件仅含字符音效）。

## 2026-10-21 · 收敛为角色效果展示

- 按用户要求，把网页主线改为角色效果、四类状态和情绪表达汇总；复用编号 007。
- 新增状态说明卡片、可中断的一键演示、情绪能力说明、输入文字播放；接入细节放入折叠区，原长文保留为 integration.md。
- 如实说明仅有 warm 基础表情，喜怒哀乐表情组及语义情绪判断未内置。
- 当前展示页和组件共八组浏览器检查通过，真实截图及范围记录于 verification.json，未连接真实模型。

## 2026-10-21 · 一图汇总能力、原理、效果与价值

- 定位收敛为“Agent 回复和部分运行状态的角色化呈现”，并区分原库 Claude 应用与本次独立角色层。
- 内置 ImageGen 生成 1536×1024 理解图，完整请求与输入截图均保留；效果区由模型参考四状态截图绘制，不作为额外模型实测。
- 以该图作为首页封面与网页总览，支持放大、关闭和下载；桌面、390px 手机检查通过。图片及输入哈希见 study-guide.json，网页检查见 summary-verification.json。
- web/assets/ 为打包副本，使用 scripts/package_web.py 生成并逐字节校验；已加入现有 Pages 工作流。

## 2026-10-22 · 发布并核验

- 整理能力、原理、效果和价值四项摘要，保留指定理解图，并明确它参考真实本地截图绘制。
- 在独立工作树提交 007 内容，保留共享工作区其他项目的改动；推送 main 后 Pages 构建与部署成功。
- 9 个线上文件与 Git 提交字节一致；线上图片、状态、演示、流式文字、模拟样例、导航和响应布局检查通过。详细证据见 deployment-verification.json、deployment-ui-verification.json。
