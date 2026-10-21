# Todofy 原理分析

研究固定提交：[`2ae76fc80b0b96ad8191e3d1ae4949ee340190a7`](https://github.com/salarzeidanlou/todofy/tree/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7)。以下分析基于源代码阅读，未以运行结果代替源码证据。

[研究首页](README.md) · [能力展示](CAPABILITIES.md) · [使用场景](SCENARIOS.md)

## 1. 系统架构

![界面、Tauri 命令、Rust 服务、本地 SQLite 和可选服务之间的数据流](assets/architecture.svg)

| 层 | 技术 / 模块 | 职责 | 源码证据 |
| --- | --- | --- | --- |
| 界面 | Preact、TypeScript、Tailwind CSS | 任务编辑、列表、看板、日历、专注与日志页面 | [package.json](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/package.json)、[components](https://github.com/salarzeidanlou/todofy/tree/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/components) |
| 界面状态 | Zustand | 保持任务、标签与页面状态，编辑后更新视图 | [store.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/store.ts) |
| 桌面桥接 | Tauri 2，invoke / 事件 | 前端调用 Rust 命令，后台向窗口发送状态变化 | [api.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/api.ts)、[lib.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/lib.rs) |
| 本地业务 | Rust | 任务写入、完成、重复、计时、后台提醒、托盘 | [commands.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/commands.rs) |
| 本地数据 | rusqlite / SQLite，WAL | 持久化记录；互斥锁协调命令与后台线程的连接访问 | [db.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/db.rs) |
| 可选同步 | Supabase Auth、Postgres、RLS | 同一用户的远端保存、增量拉取、权限隔离 | [sync.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/sync.ts)、[migrations](https://github.com/salarzeidanlou/todofy/tree/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/supabase/migrations) |

新增任务的主路径：**编辑器输入 → 前端结构化字段 → Tauri create_task → Rust 写入 SQLite → 返回任务 → 界面状态更新 → 各视图按规则展示**。未登录时，这条本地路径也能成立。

## 2. 数据模型：为什么同一任务能有多种视图

`tasks` 是核心实体，标签、时间记录等通过 ID 与它关联。以下是概念化解释，不是上游代码摘录：

| 字段 / 数据 | 含义 | 设计作用 |
| --- | --- | --- |
| `id` | 本地生成的 UUID | 离线创建后仍可参与跨设备合并 |
| `title`、`notes`、`subtasks` | 标题、备注、JSON 检查清单 | 记录要做的事与步骤 |
| `due_date`、`remind_at` | 日期、提醒时间 | 日历定位和后台提醒是两个相关维度 |
| `status` | active 或 done | 记录真正的完成状态 |
| `stage` | 看板工作列 ID | 记录未完成任务的工作阶段 |
| `order_index`、`board_index` | 列表顺序、看板顺序 | 一种视图的重排不必改动另一种视图 |
| `repeat` | 日 / 工作日 / 周 / 月 / 年 | 定义完成后的日期推进规则 |
| `estimate_minutes` | 预估耗时 | 与时间记录累计值比较 |
| `updated_at`、`deleted_at` | 修改时间、删除标记 | 增量同步和删除传播 |

关联表包括 `labels`、`task_labels`、`time_sessions`、`journal_entries`、`settings`、`pomodoro`、`events` 和 Google 日历映射 `calendar_links`。独立日历事件与任务是不同实体，不能把本地日程能力全部当成可同步任务的能力。

列表的“今日”分开显示逾期与今天到期任务；“未来”按未来日期分组；置顶影响所在分组内的排序。看板按阶段与完成状态分列，日历按任务日期和独立事件时间定位。证据：[db.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/db.rs)、[grouping.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/grouping.ts)、[board.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/board.ts)。

Done 由完成状态推导。拖入 Done 会走任务完成逻辑，避免绕开重复任务规则；拖出会重新激活任务。自定义列有稳定 ID，重命名不更换任务关联。

拖动排序通常取相邻排序值的中点，减少重排写入量。反复插进同一位置会耗尽浮点间隔；Rust 检测到拥挤时重编该组索引，把受影响记录一并返回界面。证据：[ordering.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/ordering.ts)、[commands.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/commands.rs#L379)。

## 3. 自然语言添加与语音

### 文本解析

`parseQuickAdd` 依次处理优先级、重复规则、已有标签，调用 `chrono-node` 解析日期时间，最后把无法识别的文字保留为标题。

| 输入元素 | 机制 | 限制 |
| --- | --- | --- |
| p1–p4、!1–!4 | 独立标记的正则匹配 | 提取匹配的优先级 |
| every day、every week 等 | 英文重复短语正则 | 没有任意复杂重复规则的语义推理 |
| #home、@home | 对照已有标签名，不区分大小写 | 未知标签留在标题；名称可含 Unicode 字母 |
| friday 5pm 等 | chrono.parse，设置 forwardDate | 当前默认英文解析，取第一个日期结果 |
| 其余文本 | 清理空白与剩余连接词 | 作为最终标题 |

这是可离线的字段提取，不需要大模型请求。支持范围由规则和日期库决定，不能从“自然语言”推导成通用任务理解或自动计划。证据：[nlp.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/nlp.ts)。

### 语音转写

用户主动下载 whisper.cpp 引擎与多语言 GGML 模型，再启用语音。Rust 捕获音频、转换为 16kHz PCM WAV，启动本地引擎并传入模型、录音和自动语言检测参数，读取转写 JSON，把结果放回编辑器；仍需用户确认添加任务或保存日志。

临时录音有完成 / 取消后的清理路径；下载通过签名目录和哈希校验。音频在本机推理，保存后的文本是否云同步取决于账号设置。多语言识别不代表快速添加器具有中文日期语义解析。

证据：[voice.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/voice.rs#L307)、[audio.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/voice/audio.rs)、[assets.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/voice/assets.rs)。本次未测中文准确率、下载或推理耗时。

## 4. 提醒、计时与重启恢复

Rust 后台线程约每 **20 秒**检查任务：有明确 `remind_at` 时按该时间处理；只有日期时使用当天本地 **09:00**，并避免为默认时刻之后新建的当天任务立刻补发。提醒后更新次数和时间；重复提醒依赖间隔设置与用户是否已响应。

通知交给操作系统或应用角落弹窗；主窗口隐藏时，后台仍可执行。系统权限、睡眠和调度可能造成延迟，源码不能证明全平台准时送达。完全退出或电脑关机后，没有进程执行提醒。

任务秒表与番茄钟把状态保存在 SQLite，计时的核心关系为：

```text
当前累计时间 = 已累计的有效秒数 + 当前时刻与最近恢复时刻的差值
暂停：保存累计值，并清除运行起点
继续：记录新的运行起点
停止：记录会话结束与最终用时
```

重启后读出起点与累计值即可重算，无需每秒写入计数。如果关闭前未暂停，恢复时会计入离开期间的墙上时间，受安全上限约束；这并不表示操作系统在应用退出后代为执行提醒。

**说明与实现差异**：README 表述计时器不自动停止，而 `timer.rs` 有 `MAX_SESSION_SECS = 12 * 3600`，会清理超长会话，不能将其当作无限累计保证。

证据：[scheduler.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/scheduler.rs)、[timer.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/timer.rs#L1)。

## 5. 重复任务的实质

完成普通任务会写入 done 状态和完成时间。完成带有效重复规则及日期的任务，会把**原任务的日期与提醒推进到下一期**、清除提醒响应状态，保留任务可继续执行。

| 规则 | 下一期算法 |
| --- | --- |
| 每天 / 每周 | 原日期加 1 天 / 7 天 |
| 工作日 | 加一天后跳过周六、周日 |
| 每月 / 每年 | 加 1 / 12 个月，溢出的日收敛到目标月最后一天 |

由此可推导：过期多天的重复任务完成一次只推进一期，可能仍逾期；不是自动跳到未来最近一期。这个分支没有为每一期建立已完成任务，因此不能当成完整习惯历史，也不能期望每次重复完成都计入当天完成任务数。如果缺少可推进的日期，可能回到普通完成逻辑。

证据：[toggle_task](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/commands.rs#L480)、[recur.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/recur.rs)、[journal.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/journal.ts)。

## 6. 可选账号同步

本地用 UUID 标识记录，写入后更新 `updated_at`。同步以已保存的水位时间为起点：

1. 核对账号与同步资格，处理切换账号时的数据归属选择。
2. 调用 sync_pull 拉取水位以来的内容与删除标记。
3. Rust 比较更新时间，将较新的远端记录合并到本机。
4. 导出本地变化并推送；删除先写不含正文的 tombstone，再清理云端内容行。
5. 成功后把水位前进到本轮开始时间，重载界面；中途产生的变化留到下一轮。

本地编辑后约 **1.5 秒**防抖触发同步；轮询从 **30 秒**起，无变化时退避至 **15 分钟**，隐藏窗口采用慢速周期。它不是逐字实时协同编辑；删除标记传播与清理也存在时间窗口，长期离线的收敛情况需实测。

Supabase Auth 与数据库 RLS 隔离用户数据；会话令牌使用系统凭据存储。这不等于任务数据库已加密。按更新时间覆盖的策略可能丢失同一任务的并发编辑，设备时钟偏差也是需要验证的因素。

证据：[sync.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/sync.ts)、[sync.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/sync.rs)、[secret.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/secret.rs)。这里记录代码策略，未验证全部远端触发器、网络异常与跨设备冲突结果。

## 7. Google Calendar 与日志摘要

Google 集成单独授权，创建专用 todofy 日历，使用 `calendar.app.created` 权限。任务 ID 与 Google 事件 ID 保存在 `calendar_links` 中；仅日期任务变全天事件，有提醒时间的变定时事件；更新、完成或删除时按设置维护事件。

方向为 **Todofy 任务 → 专用 Google 日历**，没有原有会议导入和双向编辑路径，本地独立 events 也不在该推送中。证据：[googleCalendar.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/googleCalendar.ts)、[calendar.rs](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/src/calendar.rs)。

日志一键摘要统计当天普通已完成任务数与对应时间记录，拼成简短文本，没有调用大模型生成日报。证据：[journal.ts](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src/lib/journal.ts)。

## 8. 实现边界与取舍

| 设计 | 价值 | 代价 |
| --- | --- | --- |
| 一份任务，多种视图 | 日期、状态与细节关联 | 用户仍需决定计划 |
| 本地 SQLite 优先 | 未登录、离线仍可工作 | 需考虑本机备份；系统凭据保护不等于内容端到端加密 |
| 规则解析 | 便宜、离线、可追溯 | 语言和语法范围有限 |
| 轮询提醒 | 隐藏窗口仍可执行 | 需进程运行，存在轮询与系统延迟 |
| 时间戳计时恢复 | 重启后可恢复计算 | 未暂停时会计入离开时长；有 12 小时安全上限 |
| 重复任务原地推进 | 继续使用原任务细节 | 缺少每次完成的独立事件历史 |
| 更新时间覆盖合并 | 机制直接，适合个人多端 | 并发可能覆盖，不是团队协同算法 |
| 专用日历单向推送 | 权限范围窄、流程明确 | 无法双向汇总已有会议 |

后续验收重点见 [REPRODUCTION.md](REPRODUCTION.md)。
