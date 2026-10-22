# 013 · Old Coder：AI 编码的验收与证据

**让 AI 交付带有验证证据的代码，降低反复提醒与验收的成本。** Old Coder 把验收规格、测试驱动、多层检查与证据报告整理成可复用 Skill。完整直接对话也能提出这些要求；Skill 的增量在复用与减少遗漏，强制门槛仍需测试脚本、CI 和合并规则。

## 我们的理解摘要

- **能力与效果**：先把需求、边界和不能破坏的行为写成 SPEC，再以测试驱动、多层检查和证据报告核对实现。效果是让已表达的错误能被具体断言暴露、需求与结果能逐项对应、验收能复跑。本研究的四类教学模型中，完整检查发现了 11 个手选行为缺陷；这不是 Skill 在真实 AI 编码任务中的质量提升率。
- **可沉淀技术**：场景与 Must NOT 模板、故障模型、RED 回归保护、变异与属性测试、独立参考模型、检查器负向对照、失败退出码、CI 门槛，以及绑定源码版本与环境的可复跑证据。API 专项可沉淀兼容、授权、幂等与影响范围检查清单。这些资产需要按项目实现和维护。
- **可扩展场景**：存量系统修 Bug 与重构，订单/库存/消息消费的重试和原子性，多租户与公共 API 契约，数据库迁移与回滚演练，以及团队合并前和发布后的验收。真实数据库、身份服务、压力、迁移与生产环境需单独集成和验证。

源库以自然语言规则与模板约定 Agent 的工作；测试工具产生执行结果，验收者审查规格与证据。它不改变模型权重，也不能保证规格完整或绝无未知缺陷。

[在线研究网页](https://yydshly.github.io/1022_codex_project/013-old-coder/) · [一图读懂](https://yydshly.github.io/1022_codex_project/013-old-coder/#summary) · [本地网页](web/index.html) · [详细分析](analysis.md) · [验证范围](verification.md) · [来源清单](SOURCE.json) · [上游仓库](https://github.com/AmazingAng/old-coder)

![Old Coder 能力总览：能力、六阶段原理、重复通知扣库存案例、适用任务与价值边界](assets/old-coder-overview.png)

*本研究原创矢量图解，1800 × 2600；提供 [高清 PNG](assets/old-coder-overview.png) 与 [可编辑 SVG](assets/old-coder-overview.svg)。以初始库存 10、同一通知 10 次为例，对照缺陷实现库存 0 与原子提交模型库存 9；仅为教学模型。网页支持放大、原图与下载。原版 [网页截图](assets/cover.jpg) 保留。来源与生成过程见 [素材说明](assets/README.md) 和 [绘制记录](assets/overview-generation.json)。*

图解使用 [build_overview.py](scripts/build_overview.py) 绘制。初次尝试内置 ImageGen 两次均因网络错误失败，最终改为同一套形状与文字操作输出 SVG 与 PNG，未使用外部模型 API。重新生成需要 Pillow 与可用的中文字体；校验只需 Python 标准库：`python projects/013-old-coder/scripts/build_overview.py --check`。

## 完整网页内容

1. 核心价值、我们的理解与源库/研究扩展归属。
2. 功能对话、完整提示、Skill 和 CI 的差别与增量。
3. 六阶段原理：各步的输入、动作、产物与边界。
4. 四个可执行实验：库存幂等、限流、跨租户权限、API 兼容。
5. 11 项检查解释：通用层、领域层和检查器自身。
6. old-coder-api 的 9 项规则与两套 Skill 的组合方式。
7. 三组证据分开呈现：作者报告、本机上游部分复现、教学实验。
8. 风险分级与可复制/下载的中文要求、SPEC 草案和 EVIDENCE 模板。
9. 成本、规格盲区、测试全绿与独立复核等 FAQ。
10. 31 份上游原文件全文阅读、搜索、复制、下载与固定版本链接。

## 交互实验

先运行默认有缺陷实现的完整测试，再试简化检查，观察错误如何漏过；切到修复实现后重跑。点击“检验测试：运行坏实现”，检查当前测试能否发现手选缺陷。展开轨迹区，可选择重试、固定交错、模拟重启和中断等输入。运行后可导出带引擎版本、SHA-256、种子、断言结果与未验证范围的 JSON。

| 场景 | 实际执行 | 关键验收 | 边界 |
| --- | --- | --- | --- |
| 库存通知 | 内存订单状态与模型事务、固定调度交错 | 重复、交错、重启、中断重试、订单独立 | 无真实数据库、跨进程或支付服务 |
| 限流 | 四种 JS 实现与独立参考模型 | 闭窗口边界、整秒交界、用户隔离、4000 次随机输入 | 未移植 Python 锁与 key 回收；非 Hypothesis |
| 权限 | 详情、列表、导出的授权函数 | 可信身份、伪造租户、跨租户、未认证 | 无真实会话、Token、数据库 |
| API | JSON 响应与旧客户端断言 | 字段、类型、旧请求与新增响应字段 | 非完整 OpenAPI 或消费者测试 |

这些是本研究编写的可执行教学模型，不是源库自带网页或 AI 当场生成。结果只说明当前代码与断言的关系，不证明 Skill 的因果效果。

## 运行与检查

网页为无框架 HTML/CSS/JavaScript，无运行时 npm 依赖、CDN 或外部字体。需要 HTTP 服务读取 JSON。仓库根目录运行：

```powershell
python -m http.server 8013 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8013/projects/013-old-coder/web/>。支持 `?scenario=limiter#laboratory` 等场景定位。

结构校验用 Python 3.10+，教学引擎校验用 Node.js 22+：

```powershell
node projects/013-old-coder/scripts/verify_labs.cjs
python projects/013-old-coder/scripts/verify_web.py
python scripts/project_catalog.py check
```

教学引擎：16 项检查通过；4 套完整契约各 6 项，11 个手选缺陷全部被发现；10 个种子各验证 4000 次输入。简化套件为刻意保留的反例。

上游 Python 示例的本机部分复现：Windows / Python 3.12.13，用项目隔离环境与上游固定版本依赖：

```powershell
uv venv --python 3.12 projects/013-old-coder/.venv
uv pip install --python projects/013-old-coder/.venv/Scripts/python.exe -r projects/013-old-coder/upstream/demo-rate-limiter/requirements-dev.txt -e projects/013-old-coder/upstream/demo-rate-limiter
python projects/013-old-coder/scripts/reproduce_upstream.py
```

41 个应用与属性测试通过，49/49 语句、20/20 分支覆盖 100%；mypy、ruff check、ruff format、原始 demo 通过。依赖审计 120 秒超时，标为 `unverified`。**未运行完整 POSIX gauntlet、原始变异器、9 个源码绑定测试、shell 自测、10 次重复套件和独立复核协议。** 部分复现不等于完整原版检查通过。

结果：[upstream-reproduction.json](results/upstream-reproduction.json) · [环境版本](results/environment-freeze.txt) · [教学引擎验证](results/lab-verification.json) · [浏览器验证](results/browser-verification.json)。

## 上游与许可

- 上游：<https://github.com/AmazingAng/old-coder>；作者 amazingang。
- 研究日期：2026-10-22，Asia/Shanghai；当日远端 main 与快照一致。
- 固定提交：`a0eb529d393a1cb3ccc564e32b2104e7e75c7a29`。
- 作者报告绑定的应用源码状态：`42528d9`，与仓库 HEAD 概念不同。
- MIT，© 2026 amazingang，原文见 [upstream/LICENSE](upstream/LICENSE)，网页随附同一许可。
- `upstream/` 保存两套 Skill、references、完整 demo、README 与 CI，共 31 文件；它是研究快照，没有安装到 Agent 的技能目录。
- 原始路径与 SHA-256 见 [SOURCE.json](SOURCE.json)；[快照脚本](scripts/snapshot_upstream.py)仅接受固定提交。

## 发布

`web/` 是完整发布产物，根 `scripts/build_site.py` 自动汇总到 `/013-old-coder/`。`.venv`、研究快照与缓存不进入发布产物。Pages 工作流运行教学引擎、图像身份与静态来源检查后汇总发布；登记表 `demo_url` 仅在公开部署验收通过后填写。

CI 使用 `node projects/013-old-coder/scripts/verify_labs.cjs --check` 执行检查而不改写历史结果，再运行 `build_overview.py --check` 与 `verify_web.py`；无需安装本机绘图字体或上游 Python 示例依赖。引导图统一使用我们绘制的 `old-coder-overview.png`，首屏、图解阅读区与总导航封面一致。

2026-10-22 已发布：内容提交 [`d727862`](https://github.com/yydshly/1022_codex_project/commit/d7278623e192ae6148eaf59961c9132c0746d052) 的 [Pages 构建与部署](https://github.com/yydshly/1022_codex_project/actions/runs/39791306660)成功，16 个线上发布文件均 HTTP 200 且与提交字节一致，总导航完整摘要与指定引导图已核对。线上四实验缺陷/修复与变异检查、原文阅读、图片放大与下载及 375/768/1440 宽度检查通过。记录：[部署身份校验](deployment-verification.json) · [线上交互校验](publication-browser-verification.json) · [真实公开网页截图](assets/publication-preview.jpg)。
