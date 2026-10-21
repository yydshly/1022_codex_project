# Todofy 复现与验证

[研究首页](README.md) · [能力展示](CAPABILITIES.md) · [原理分析](ARCHITECTURE.md)

## 本次已经完成的工作

| 项目 | 结果 |
| --- | --- |
| 固定 main 源码快照 | 2ae76fc80b0b96ad8191e3d1ae4949ee340190a7 |
| 核对发布标签 | v1.14.0 → 19a8907fc85e608027014e49f9d1e704754f2656，与快照不同 |
| 核对关键实现与许可 | 任务、视图、规则解析、计时、提醒、语音、同步与日历等，见 SOURCE.json |
| 研究机器 | Windows / PowerShell；Python 3.10.11、Node.js 22.15.0、Rust 1.95.0 |
| 原生开发依赖 | 本次没有安装 Bun、Tauri 前置依赖或语音模型 |
| 验证范围 | 静态源码、官方界面观察、原创图解与研究文档检查 |

以下原生安装、构建与验收步骤供后续执行，**尚未实际跑通**。官方截图来自作者环境，不能当作本机原生运行证据，也未测原生启动速度、内存占用或语音识别准确率。

## 官方原图展示网页

直接打开 [web/index.html](web/index.html)，不需要 Bun、Rust、npm、外部 CDN 或后台账号。页面展示固定提交中的八张官方 PNG，原始字节与尺寸保留，可切换、放大和追溯来源；不再包含自制任务数据、拖动或计时实现。产品画面与我们的原理分析、场景说明分别标注。来源清单见 [screenshots.json](screenshots.json)。

如果需要 HTTP 预览，在仓库根目录运行：

```powershell
python -m http.server 8000 --bind 127.0.0.1 --directory projects/002-todofy/web
```

浏览器打开 `http://127.0.0.1:8000/`。也可通过根 `scripts/build_site.py` 汇总到新的空产物目录，以 `/1022_codex_project/002-todofy/` 前缀检查。网页文件说明见 [web/README.md](web/README.md)，实际浏览器检查结果见 [web-verification.json](web-verification.json)。

## 重新生成理解总结图

网页运行无需安装图像依赖；PNG / SVG 产物已经保存在项目与 `web/assets/` 中。只有修改总结图时才需要生成脚本。当前生成环境为 Pillow 11.3.0 与 Windows 微软雅黑字体：

```powershell
python -m pip install -r projects/002-todofy/scripts/requirements-visuals.txt
python -X utf8 projects/002-todofy/scripts/build_summary.py
python -X utf8 projects/002-todofy/scripts/build_summary.py --check
```

在其他平台，用 `--font-regular` 与 `--font-bold` 指定本机可显示中文的字体文件；字体变化会影响 PNG 渲染与哈希，因此 `--check` 针对相同渲染环境。脚本检查文字宽度与画布边界，并核对引用的官方 Board 源图哈希，输出两处一致的 PNG / SVG 和 `summary-image.json`。

总结图中的产品画面直接引用官方原图，三层结构、能力效果与看板参考意义由本研究整理；它不是新的模拟应用界面。

## 路径 A：体验官方版本

从 [v1.14.0 发布页](https://github.com/salarzeidanlou/todofy/releases/tag/v1.14.0) 选择相应平台安装包：Windows 的 EXE / MSI、macOS 的 DMG、Linux 的 AppImage / DEB / RPM。

安装后先不登录账号，创建一条带日期、提醒、标签与子任务的任务，完成下方本地验收。这个路径验证的是发布版本，不是 main 快照；记录结果时写清安装包版本、平台、文件哈希与验证日期。

## 路径 B：固定源码构建

按 [Tauri 官方前置依赖](https://v2.tauri.app/start/prerequisites/) 准备当前平台的工具链，安装 Bun 和 Rust。依赖版本范围见上游 [package.json](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/package.json) 与 [Cargo.toml](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/src-tauri/Cargo.toml)，用锁文件解析具体版本。

在本研究库根目录运行，临时源码放入已忽略的 `_upstream/`：

```powershell
git clone https://github.com/salarzeidanlou/todofy.git _upstream/todofy
git -C _upstream/todofy checkout --detach 2ae76fc80b0b96ad8191e3d1ae4949ee340190a7
git -C _upstream/todofy rev-parse HEAD
Set-Location _upstream/todofy
bun install --frozen-lockfile
bun run tauri dev
```

如果该临时目录已经存在，先检查其中的来源、版本和未提交修改，不覆盖已有工作。单独运行 `bun run dev` 仅启动 Vite，不能用来证明需要 Tauri 命令的数据库、通知、托盘等桌面能力正常。

检查上游已有测试：

```powershell
bun run test
cargo test --manifest-path src-tauri/Cargo.toml
```

这两条命令需要相应依赖，本次未执行。正式打包命令是 `bun run tauri build`；上游更新包流程涉及签名配置，具体按固定版本 README 操作，不把没有官方签名的自建包当作官方发布。

## 本地功能验收清单

使用新的测试任务，避免修改个人真实记录。每项均为“待执行”；预期结果根据源码整理，不是当前实测结果。

| 编号 | 操作 | 源码预期 / 检查重点 |
| --- | --- | --- |
| L01 | 未登录创建任务，退出后重开 | 数据仍在本机；写入应用数据目录 |
| L02 | 同一任务在列表、看板、日历间查看并改标题 | 同一个 ID 的标题保持一致 |
| L03 | 无日期任务留在收件箱，再补日期 | 不排期也可记录；有日期后进入对应日期视图 |
| L04 | 拖动列内顺序，再跨列移动 | 看板顺序持久化，列表顺序不被扰乱 |
| L05 | 自定义列、设置 WIP，超限并删除列 | 超限提醒但允许移动；删除需选择迁入列 |
| L06 | 普通任务拖入 Done，再拖出 | 完成后出现在已完成，拖出可重新打开 |
| L07 | 建立 home 标签，测试英文日期与未知标签 | 已有标签提取；未知标记留在标题 |
| L08 | 中文标题含“明天下午五点” | 观察文本保留，不预设中文日期识别 |
| L09 | 设置两分钟后提醒，隐藏到托盘 | 记录是否送达、延迟、声音、稍后 / 重复响应 |
| L10 | 计时后暂停、继续、重启 | 暂停时间不累加；未暂停关闭后的恢复值需核对 |
| L11 | 任务计时与番茄钟分别运行 | 核对阶段切换、实际用时与历史记录，避免混为一种计时 |
| L12 | 完成每日重复任务，再测多天逾期任务 | 原任务推进一天；核对是否仍逾期与是否产生完成历史 |
| L13 | 日志插入当天摘要 | 核对普通完成数、专注分钟数；重复任务完成的统计差异 |
| L14 | 下载语音引擎和模型，离线录中英文 | 检查可编辑转写、取消、临时音频清理和推理耗时 |
| L15 | 创建独立本地日程 | 与任务并列展示；不要把它当成参与云同步的任务 |

计时 12 小时上限应通过受控测试环境或上游单元测试进一步核验，不需要为了检查而让实际任务长时间运行。

## 可选服务验收

| 编号 | 前提与操作 | 需要记录的结果 |
| --- | --- | --- |
| S01 | 自己的两个设备、有效官方同步资格或自建后端 | 创建 / 编辑 / 删除能否传播，离线后联网能否收敛 |
| S02 | 两端离线编辑同一测试任务后联网 | 更新时间覆盖的最终结果，时钟偏差与丢失修改情况 |
| S03 | 在同一安装切换测试账号 | 是否提示选择账号数据或复制本地数据，是否混入其他账号记录 |
| S04 | 单独授权 Google Calendar，修改有日期任务 | 专用日历事件创建 / 更新 / 清理；原有会议未导入 |
| S05 | 在 Google 修改推送的事件 | 记录单向集成的实际表现，不预设改动回写任务 |

自建账号后端按 [固定版本 README 的完整说明](https://github.com/salarzeidanlou/todofy/blob/2ae76fc80b0b96ad8191e3d1ae4949ee340190a7/README.md) 执行，按文件名顺序应用该快照内全部迁移，并核对认证、删除账号函数、计费模式与 HTTP 域名白名单。不要把数据库连接信息或访问令牌提交到研究目录。本次未创建账号、购买服务或连接外部日历。

## 本研究库的检查

在本仓库根目录执行：

```powershell
python scripts/project_catalog.py sync
python scripts/project_catalog.py check
git diff --check
```

本次未修改目录脚本，不需要因文档新增而扩展脚本回归测试。后续若修改 `scripts/project_catalog.py`，按根 AGENTS.md 执行其现有单元测试。

把实际验证日期、应用版本、系统版本、步骤和截图追加到 [notes.md](notes.md)，再更新研究进度与验证范围。
