# 018 · Orchard-Agentic：Agent 沙箱与评测训练

> 基于 Kubernetes 为 Agent 批量提供可控容器，执行代码、文件和终端操作，配套轨迹记录、评测与训练；作者报告 SWE 修复率 69.7%，六候选重排后 73.0%（未复现）。可沉淀沙箱 API、生命周期治理、网络资源策略和评测数据规范，扩展到远程代码执行、自动修复、回归评测、浏览器任务及 Agent 训练。

| 信息 | 内容 |
| --- | --- |
| 上游 | [https://github.com/microsoft/Orchard-Agentic](https://github.com/microsoft/Orchard-Agentic) |
| 研究版本 | [bd8da32b3a075128700caab75bbc491fb6fdc16e](https://github.com/microsoft/Orchard-Agentic/commit/bd8da32b3a075128700caab75bbc491fb6fdc16e)；提交日期 2026-10-09 |
| trainer/slime 子模块 | 331efaaeef75c98aad6ba1a2f5f50bd8149f6ab9；不是其随后更新的 main |
| 论文 | [arXiv:2605.15040v3](https://arxiv.org/html/2605.15040v3)，2026-07-30 |
| 许可 | 上游 MIT，见 [LICENSE.upstream.txt](LICENSE.upstream.txt)；模型、数据及后续项目分别核对 |
| 收录日期 | 2026-10-22（Asia/Shanghai） |
| 网页 | [静态研究入口](web/index.html)；发布证据见 [deployment-verification.json](deployment-verification.json) |
| 验证范围 | 固定版本代码与文档、引导图、静态网页和公开发布；未运行上游集群、模型或训练 |

![Orchard-Agentic 理解引导图：角色分工、执行架构、沙箱功能、Docker 对比、价值与效果](assets/orchard-agentic-overview.png)

沿用本次讨论最终确认的 2400 × 5480 中文长图，PNG 与 SVG 保持原始字节。最终是文字与矢量排版绘图；ImageGen 初次调用因网络错误失败，没有使用模型生成结果。见 [图片来源与哈希](assets/README.md)。

## 先用一句话理解

Orchard Env 是“容器隔离环境 + Agent 操作接口 + 批量管理服务”。整个仓库在此基础上组织评测、训练配方与研究数据。

| 角色 | 负责什么 | 配置边界 |
| --- | --- | --- |
| 大模型 | 判断下一步做什么 | 模型接口与凭据由使用者准备。 |
| Agent 框架 | 组织任务、上下文与工具调用 | 可使用不同框架，行为与成绩也受框架影响。 |
| Orchard Env | 执行操作，管理环境并返回结果 | Pod 内的轻量 agent 是执行服务，不是大模型。 |

## 能力与工作原理

| 沙箱能力 | 具体行为 | 接口 / 模块 |
| --- | --- | --- |
| 环境与镜像 | 为每个任务准备独立的 Linux 容器；自选镜像，创建、等待就绪、查询和删除。 | create_sandbox / get_sandbox / delete_sandbox |
| 命令与代码 | 运行脚本、编译、安装依赖、执行测试，取得标准输出、错误与退出码。 | exec / jobs |
| 文件与补丁 | 上传、下载、列目录；用命令编辑文件或生成差异，应用 Git 补丁。 | files / apply_patch |
| 交互式终端 | 通过 PTY 和 WebSocket 持续输入、读取输出。 | exec/pty |
| 资源与时限 | 为环境配置 CPU、内存与运行时限，对命令设置超时。 | cpu / memory / timeout |
| 网络策略 | 禁外网、开放出口或使用 IP/CIDR 与端口白名单；可更新运行中的策略。 | network / Calico NetworkPolicy |
| 状态与回收 | 命令任务状态、心跳、TTL 与清理机制，减少遗留环境。 | heartbeat / jobs / sandbox_manager |
| 批量与远程 | HTTP API、同步/异步 Python SDK，并发控制；多副本通过 Redis 共享状态与锁。 | SandboxClient / AsyncSandboxClient |
| 预装 Agent 工具 | Codex CLI、Claude Code、pi、OpenCode、Hermes、mini-swe-agent；模型和项目依赖另外配置。 | 只读工具载荷 |

Python、浏览器、项目依赖和数据按任务镜像或准备步骤配置。实际隔离强度取决于底层容器和集群，不应据名称推断为虚拟机级隔离。

1. **创建环境**：选镜像，约定资源、网络和时限。
2. **准备任务**：放入代码、数据、依赖和任务说明。
3. **执行与反馈**：Agent 调用模型决定动作；沙箱执行并返回输出、错误或文件。
4. **循环尝试**：读取反馈、修改并继续，直到提交结果或达到预算。
5. **导出与评分**：保留补丁、日志、轨迹与制品，按具体任务评分。
6. **回收环境**：主动删除，并以心跳和 TTL 进行补充清理。

编排服务通过 Kubernetes 管理创建、调度、策略和删除；高频命令与文件请求经 Pod 内执行服务处理。多副本可用 Redis 共享状态，CPU 沙箱与模型推理/训练资源可独立配置。

| 组成 | 定位 | 能力 |
| --- | --- | --- |
| Orchard Env | 环境底座 | 可控执行、文件与终端、网络资源策略、批量管理。 |
| Orchard Eval | 配套评测 | 保存轨迹、日志、补丁和成绩；区分环境故障。原生 SWE 流程使用新的评分 Pod。 |
| trainer / slime | 研究训练 | 专家轨迹 SFT、任务反馈 RL；BAR、OPD、RPR 与价值模型重排按具体配方选用。 |
| 数据与后续项目 | 研究资产 | SWE/GUI 轨迹；OpenWebRL 与 OpenForge RL 为独立后续项目，需分别配置和核对许可。 |

## 效果与评测口径

| 对象 | 作者报告 | 条件 |
| --- | --- | --- |
| 代码修复 · SWE-bench Verified | 61.4% → 69.7% → 73.0%；Qwen3.5-35B-A3B：基础 → RPR → 价值模型重排。 | 73.0% 使用六候选筛选，包含额外推理预算。 |
| 网页操作 · 4B 模型 | 74.1% / 67.0% / 64.0%；依次为 WebVoyager、Online-Mind2Web、DeepShop；平均 68.4%。 | 特定网页任务与协议上的成功率。 |
| 工具工作流 · Claw-Eval | 59.6% → 73.9%；原框架 → ZeroClaw；两项均为 pass@3。 | 三次尝试至少一次成功，不能当作单次成功率。 |
| 沙箱性能 · 作者测试配置 | 0.28 秒 / 1,000 个；平均命令延迟 0.28 秒；并行启动 1,000 个沙箱约 26 秒。 | 配置相关，未本地复现，不是任意部署的性能保证。 |

以上来自作者论文与仓库，本研究未复现。不同基座与框架的成绩不应串成同一模型升级过程；pass@3 与三次都成功的 pass³ 也不同。环境服务改善执行与管理，模型能力提升依赖训练和推理方法。

## 与直接使用 Docker 的区别

| 对比项 | 直接 Docker | Orchard |
| --- | --- | --- |
| 执行与隔离 | 基础容器、命令、文件、资源和网络能力。 | 复用容器技术，封装为面向任务的沙箱服务。 |
| 批量任务 | 自行写并发、状态、超时和清理脚本，或组合其他工具。 | 已有统一接口及状态、并发、心跳、TTL 和回收机制。 |
| 跨机器运行 | 另外配置集群编排与服务管理。 | 基于 Kubernetes 调度；仍需维护集群和网络策略。 |
| AI 研究配套 | 自行组织任务、轨迹、评分与训练。 | 仓库提供评测、研究数据与训练配方。 |
| 部署与维护 | 单机使用通常简单。 | 引入编排服务、策略和状态组件，有额外运维成本。 |

本机、少量固定任务或现有脚本稳定时，Docker + 脚本通常足够。统一远程服务、跨机器任务、批量评测或训练有实际需求时再评估 Orchard；没有只由数量决定的切换阈值。GitHub Pages 仅承载本研究静态网站，不运行真正的沙箱控制面。

## 可沉淀的技术

以下为研究归纳，尚未抽取为独立产品或 SDK。

| 顺序 | 技术资产 | 可沉淀内容 | 验收前提 |
| --- | --- | --- | --- |
| P0 | 统一沙箱后端契约 | 把创建、执行、文件、补丁和销毁抽成稳定接口，业务层可适配本地 Docker 或远程服务。 | 同一任务在不同后端产生可解释的状态和可追踪制品。 |
| P0 | 生命周期与预算治理 | 沉淀任务状态、超时、取消、心跳、TTL、幂等清理与失败分类。 | 失败与重复清理不遗留环境，任务取消和重试有明确语义。 |
| P0 | 轨迹与干净评测协议 | 保留原始事件与标准化轨迹，绑定补丁、评分、模型、框架和任务版本。 | 区分任务失败和环境故障；相同预算与版本下比较成绩。 |
| P1 | 资源与网络策略模板 | 按任务类型配置 CPU、内存、镜像、时限和出口白名单。 | 在支持策略的集群验证准备阶段与执行阶段的实际边界。 |
| P1 | 集群执行与并发治理 | 借鉴 Pod IP 执行路径、多副本共享状态与并发管理，让环境规模与模型资源独立扩展。 | 在自己的集群验证容量和故障恢复，不照搬论文性能。 |
| P2 | 训练反馈与候选排序 | 在确有训练需求时沉淀轨迹筛选、结果/过程奖励、教师指导及价值模型重排。 | 模型、数据许可、GPU 预算与评测条件齐备，先验证小规模数据闭环。 |

输入输出和分阶段顺序见 [REUSE.md](REUSE.md)。

## 后期可扩展的使用场景

| 场景 | 可复用底座 | 仍需补充 | 状态 |
| --- | --- | --- | --- |
| 远程代码执行与数据处理 | 命令、文件、预算与自动回收 | 语言与数据工具镜像、制品存储、上层用户权限 | 可复用底座，需任务适配 |
| AI 自动修复与回归检查 | Agent 环境、Git 补丁、干净测试和日志 | 项目依赖、验收测试、模型与失败处理 | 可复用评测流程，需仓库适配 |
| 模型 / Agent 框架对比 | 一致环境、任务与轨迹规范 | 固定模型、框架、镜像、推理预算与统计口径 | 适合批量研究 |
| 浏览器多步任务 | 并行沙箱、网络策略与轨迹基础 | 浏览器镜像、观察/动作工具、视觉模型、成功判定和网站故障处理 | 需额外任务环境与工具 |
| 编程教学与自动评分 | 每题独立环境、测试、时限与回收 | 题库、评分器、账户权限和课程流程 | 需业务层与题库 |
| Agent 交互数据工厂与训练 | 多轮执行、失败分类、环境与评测一致性 | 数据治理、奖励器、模型、训练器与计算资源 | 需模型、数据与 GPU 预算 |
| 同一状态分叉探索多条路径 | 当前可先独立重跑不同尝试 | 完整状态快照、暂停/恢复、分叉和前缀共享仍在上游路线图 | 后续研究，非现成功能 |

完整状态快照、暂停/恢复、分叉和前缀共享仍列在上游 Roadmap；评测中断后继续集合中的任务不等于恢复进程与内存快照。身份、计费、多租户业务授权等需另外设计。

## 运行与验证

网页使用无依赖 HTML/CSS/JavaScript，内容从 research.json 加载，未连接模型或沙箱服务。仓库根目录执行：

```bash
python scripts/project_catalog.py check
python projects/018-orchard-agentic/scripts/verify_web.py
python scripts/build_site.py --output _site/orchard-preview-1
python -m http.server 8927 --bind 127.0.0.1 --directory _site/orchard-preview-1
```

预览 /018-orchard-agentic/。重新构建需另选空目录，构建器不会删除旧产物。文档由 scripts/build_docs.py 从同一份研究内容生成。

真正运行上游需另按[固定部署文档](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/orchard_env/docs/deployment.md)配置 Kubernetes、Calico、镜像仓库和服务。SDK 要求 Python 3.11+；模型接口、凭据、任务环境与训练 GPU 另外准备。本文未执行云资源创建。

## 来源与研究记录

- [研究笔记](notes.md)
- [固定文件来源与 SHA-256](research-evidence.json)
- [上游许可与来源声明](THIRD_PARTY_NOTICES.md)
- [项目与研究配方](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/README.md)
- [整体组件](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/docs/overview.md)
- [环境架构](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/orchard_env/docs/architecture.md)
- [HTTP API](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/orchard_env/docs/api.md)
- [部署前提](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/orchard_env/docs/deployment.md)
- [评测协议](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/orchard_eval/README.md)
- [OpenWebRL](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/projects/openwebrl.md)
- [OpenForge RL](https://github.com/microsoft/Orchard-Agentic/blob/bd8da32b3a075128700caab75bbc491fb6fdc16e/projects/openforge-rl.md)
- [论文第三版](https://arxiv.org/html/2605.15040v3)
- [Docker Engine](https://docs.docker.com/engine/)

本研究未实测集群并发、隔离强度、真实浏览器任务、论文成绩、训练和成本。技术沉淀及扩展场景是后续实施建议，不宣称已交付这些服务。网页验证和公开部署以相应 JSON 记录为准。
