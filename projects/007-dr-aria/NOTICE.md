# 第三方来源与修改说明

本项目的 ASCII 角色图案、调色板、动画动作和字符音效逻辑衍生自：

- 项目：[MPMyburgh/dr-aria](https://github.com/MPMyburgh/dr-aria)
- 作者：Michael Myburgh
- 固定版本：`ff26c94cf1d6879ad98838df9c50104d06419eb6`
- 原始文件：`build/page.html`、`build/art.json`；截图 `docs/aria.png`
- 原始许可：MIT，Copyright (c) 2026 Michael Myburgh
- 完整许可保留于：[web/LICENSE.dr-aria.txt](web/LICENSE.dr-aria.txt)

本次将角色绘制、动作和可选音效抽取为独立浏览器组件；使用 Shadow DOM 隔离，增加统一事件入口，并处理停止、销毁、队列、Unicode 和减少动画设置等生命周期问题。新增的 Claude / Codex 适配器仅翻译事件，不含模型服务、登录或进程启动。

原项目的心理陪聊提示词、技巧卡、记忆和 Python bridge 未纳入此组件。此研究组件不代表原作者维护的正式发行包。

复制或分发包含上游实质代码、角色图案的文件时，应同时保留上游 MIT 版权与许可声明。上游截图的来源说明见 [assets/README.md](assets/README.md)。
