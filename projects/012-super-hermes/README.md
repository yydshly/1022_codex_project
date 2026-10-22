# 012 · Super Hermes · 多 Skill 问题定位与审查

> 用 5 个 Markdown Skill 与 7 份分析模板组织 AI 问题定位和方案审查：规定检查动作、顺序、反驳与报告，模型结合材料完成分析，宿主提供工具、运行证据检验判断。我们将方法提炼为七步定位协议和九项报告，供不同项目复用；上游代码分析主要限定单文件。

[在线网页](https://yydshly.github.io/1022_codex_project/012-super-hermes/) · [打开本地网页](web/index.html) · [七步流程与能力总结图](assets/super-hermes-diagnosis-v3.png) · [七步协议与九项报告](web/assets/problem-diagnosis-protocol.txt) · [流程、规范与角度提炼](analysis-method.md) · [研究笔记](notes.md) · [来源与文件校验](SOURCE.json) · [上游仓库](https://github.com/Cranot/super-hermes)

![Super Hermes 能力总结：多个分析 Skill、七步定位协议、逐步要求与产物、九项结论报告、验证要求和我们的复用价值](assets/super-hermes-diagnosis-v3.png)

*使用内置 ImageGen 绘制，971 × 1619。完整展示输入、七步要求、③–⑤循环、条件修复、九项报告、三种结论状态和验证边界。七步协议及完整报告是我们的提炼与扩展，并非上游内置七阶段执行器。网页支持放大、原尺寸查看与下载。来源与哈希见 [seven-step-image.json](seven-step-image.json)，完整提示词见 [生成请求](assets/seven-step-imagegen-prompt.txt)。[上一版理解图](assets/super-hermes-understanding-v2.png)和[初版全景图](assets/super-hermes-overview.png)保留。*

## 我们的理解与七步协议

**用多个 Skill 组织问题定位：模型完成分析与判断，Skill 约定可见的动作和产物，证据检验结论。** Skill 把排查经验写成自然语言规范，不等于能够锁定模型内部思维，也不能保证每步执行或结论正确。

我们的通用流程为：**定义问题 → 建立事实基础 → 提出候选解释 → 设计并执行检查 → 收敛并反驳根因 → 验证修复 → 报告与沉淀**。第 3–5 步循环收敛；第 6 步仅在任务包含修复时适用。每一步在网页中列出输入、具体要求、产物与边界，并用内存案例逐步讲解。

输入至少包含问题现象、预期与实际、触发条件和材料入口；按需补充环境、最近变更、日志、复现、操作范围与完成标准。最终按九项报告交付：**结论状态、问题与影响、定位位置、触发条件、因果链、证据、其他解释、修复与验证、局限与下一步**。结论允许为根因已有证据支持、候选待验证或尚未定位。

这一流程不局限内存泄漏，可为不同项目替换领域清单、材料与工具。原库代码分析主要限定单文件；跨项目协议、完整报告、阶段校验与修复验收属于我们的设计，不能冒称上游已经自动实现。可下载 [完整输入、步骤、报告与验证要求](web/assets/problem-diagnosis-protocol.txt)。

## 什么场景使用

| 用户遇到的问题 | 建议入口 | 输入与产出 |
| --- | --- | --- |
| 服务内存随请求持续增长，怀疑缓存或资源持有问题 | `prism-scan` | 相关代码与现象 → 可疑分配点、持有点、触发条件与验证建议 |
| 单个关键文件能跑，但担心并发、失败路径和边界问题 | `prism-scan` | 文件与重点 → 定制分析方法、具体问题表和盲区说明 |
| 一个核心文件或方案需要更深入复查 | `prism-full` | 材料 → 多轮分析、反驳、自我修正与最终报告 |
| 想从结构、长期变化与目标冲突三个角度评估方案 | `prism-3way` | 文件或方案 → 三个角度的分析与综合判断 |
| 刚研究一个文件，还不知道值得查什么 | `prism-discover` | 材料 → 约 10–20 个研究方向；不执行深入审查 |
| 已有报告，需要检查遗漏并为下次补查留记录 | `prism-reflect` | 材料 → 结构分析、自我复查、约束报告与历史记录 |

网页提供五种场景切换、五个 Skill 的分工和完整原文、七份模板阅读、运行原理步骤与历史切换、内存增长实测曲线、并发问题逐步演示、扩展分层和下载资料。场景提问是研究者整理的使用示例；网页不调用模型，也没有上传或在线分析入口。

## 支持哪些能力

上游提供 5 个 Skill 和 7 份固定分析模板。Skill 是 Markdown 指令，Hermes 提供加载与工具，模型完成分析。

- `prism-scan` 根据当前材料与历史盲区生成新分析方法；不会自动把七份模板逐个都跑一遍。
- 七份固定模板覆盖错误传播、结构权衡、性能成本、接口与实际行为、信息损失、假设反转、长期演化，可通过支持系统提示词的工具单独使用。
- `prism-full` 强制反驳自己的发现，包括撤回过度判断。
- `prism-reflect` 指示宿主读写项目内 `.prism-history.md`；下次 scan 会参考此前遗漏。
- 代码审查目前明确限定单文件，不能据此宣称已有跨文件整库分析。

技能与模板原文完整保存在 [web/assets/upstream/skills/](web/assets/upstream/skills/)，未改写。网页中的中文解释和能力名称是本研究整理。

## 原理

### 完整通用步骤与规则

网页的“通用步骤与完整规则”逐份核对固定版本的 **5 个 Skill + 7 份固定模板**，合并相同动作后整理为 **69 条**：12 条通用动作、27 条入口专属、26 条固定视角与 4 条实现边界。数量和分组为研究者归纳，README 另补运行说明。

每条包含原文动作的中文概括、如何指导 AI、应留下的产物、应用示例和使用边界，并关联原文件和行号。网页可搜索、按分组与来源筛选、展开或收起当前结果、查看高亮原文、复制单条与下载全表。

- [完整中文规则 TXT](web/assets/super-hermes-rules.txt)
- [结构化规则与来源 JSON](web/assets/super-hermes-rules.json)
- 编写内容位于 [rulebook_content.py](scripts/rulebook_content.py)；修改后运行 `python projects/012-super-hermes/scripts/build_rulebook.py`，再执行网页校验。

通用流程统一见上面的七步协议；逐条规则仍按上游原文职责归类，不表示每个 Skill 执行全部步骤。中文解释、应用示例与使用边界不是上游原文；对预设守恒律、多角色一致等规则明确标注需要额外核查。正文覆盖由研究者人工核对，静态校验只确认原文哈希、来源位置和导出一致性，不冒称自动验证语义完整性。

网页“从现象到定位结果”统一为七步教学，与通用协议对应，每一步展示输入、给 AI 的具体要求、产物、作用及适用的上游原文。内存实测附在设计检查和修复验证中，九项报告附在最后一步；这是研究者教学示例，没有把它记为单个 Skill 已自动实现的流程。

方法沉淀在三个位置：**Skill 的通用规则、本次生成的具体检查方法、历史中的分析盲区。** 其中完整故障报告、修复与测试证据需要额外归档。详见 [带案例的方法说明](analysis-method.md)。

最值得复用的是三类约束：**流程规定先做什么、每轮接收什么；规范规定交付字段、反驳与盲区说明；角度把结构、时间、目标冲突等领域变成具体检查动作。** 详见 [方法提炼](analysis-method.md) 和 [我们的七步定位协议](web/assets/problem-diagnosis-protocol.txt)。这些限制主要由提示词引导，执行强度依赖宿主和模型。

1. **读取上下文**：材料、用户重点及可选的 `.prism-history.md`。
2. **设计方法**：scan 生成 75–200 个单词的定制分析指令；full 自行设计 2–4 个轮次。
3. **执行分析**：构造替代方案或失败条件，形成位置、问题、严重程度和设计权衡等输出。
4. **复查结论或遗漏**：full 反驳自己的发现；reflect 再分析第一轮输出，说明侧重与盲区。
5. **留下历史**：reflect 指示 Agent 追加约束报告，下一次 scan 再读取。

这是提示词与上下文层的工作流。“三个专家”是模型角色安排；“长期成长”是文本记录进入后续上下文。实际工具调用、完整遵循程度及输出质量由宿主 Agent 与底层模型决定。本研究没有训练或修改模型。

## 具体场景：辅助定位内存持续增长

把“服务内存随请求增长”的现象和相关代码交给 AI，用 scan 指定内存持有、缓存淘汰与资源生命周期重点。上游 [optimize 模板](web/assets/upstream/skills/prism-scan/references/optimize.md) 明确要求检查分配、缓存行为和具体成本。由此可以展开内存问题审查，但库本身没有提供内存探针或经过验证的内存泄漏检出率。

网页首个案例用本研究自建的 [缓存代码](web/assets/memory-demo/cache_fixture.py) 展示完整过程：

1. **现象**：800 个不同请求，每条响应 64 KiB，内存随请求数量持续增长。
2. **定位**：第 11 行创建响应；第 20 行把响应放进长期缓存，没有容量限制和淘汰路径。仍被引用的对象不会被垃圾回收释放。
3. **检验**：每个采样点执行 GC，通过 tracemalloc 跟踪分配；无上限版本留下约 50.13 MiB、800 条缓存。清空缓存后，该响应分配行的增量归零。
4. **修改与代价**：改成最多 32 条的 LRU 缓存，同样 800 个请求约 2.01 MiB；被淘汰的数据之后需要重新生成。

这属于无界对象持有，常被称为逻辑内存泄漏；数值是 Python 跟踪的存活内存相对空缓存的增量，不是进程 RSS。两组各在独立子进程执行，原始数据见 [memory-reproduction.json](web/assets/memory-reproduction.json)。

```powershell
python projects/012-super-hermes/scripts/reproduce_memory.py
```

**证据范围**：问题代码、定位说明、LRU 修改与实测均为本研究补充，没有实际调用 Hermes 或模型。这个案例确认了缺陷机制与修改效果，不证明 Super Hermes 能独立检出它，也不测量相对普通 AI 的增益。网页采样器只浏览已记录数据。

## 真实验证：示例并发漏洞

上游 `examples/circuit_breaker.py` 明确标注故意包含设计缺陷；保存的 AI 分析报告指出 `state` 属性的无锁状态转换。本研究使用固定版本原始代码，复现了一种确定的线程交错：

1. 线程 A 检查旧失败时间，判断已满足 30 秒等待条件。
2. 暂停 A，在主线程执行 `_on_failure()`，把失败时间刷新到现在。
3. 恢复 A；它不重新检查时间，直接在第 49 行把状态改为 `HALF_OPEN`。
4. 结果：新失败后不足 30 秒，熔断器已允许试探请求。

脚本通过 `sys.settrace` 控制交错，避免依赖随机调度。测试对象是上游代码，演示不替换其状态机实现。

```powershell
python projects/012-super-hermes/scripts/reproduce_race.py
```

[真实执行记录](web/assets/race-reproduction.json) 包含 Python 版本、平台、时间、固定 SHA、等待配置和结果。网页中的下一步按钮只播放预设线程顺序。这个复现支持一个具体漏洞存在，不是对模型整体检出率或 Skill 增益的评测。本轮没有实际运行 Hermes、在线模型调用或对比实验。

## 可扩展能力

| 层次 | 可做的事情 | 当前状态 |
| --- | --- | --- |
| 直接使用 | 指定安全/性能等重点；选择固定模板；依据历史补查 | 上游已有指令支持 |
| 修改 Skill | 团队检查标准、领域专用模板、证据与复现报告格式 | 本研究建议，需修改提示词并评估 |
| 额外开发 | PR/CI 审查运行器、跨文件依赖检索、结构化盲区存储、自动验证与评测 | 当前包没有完整实现 |

推荐先在本研究库形成“固定版本 → 单文件报告 → 独立复现 → 记录未验证项”的最小流程，再考虑跨项目自动化。

## 运行网页

网页采用无依赖 HTML、CSS、JavaScript，所有阅读数据本地保存；没有 CDN、第三方字体、分析统计或 API 密钥。可直接用浏览器打开 [web/index.html](web/index.html)。也可在仓库根目录预览：

```powershell
python -m http.server 7872 --bind 127.0.0.1 --directory projects/012-super-hermes/web
```

访问 <http://127.0.0.1:7872/>，按 `Ctrl+C` 停止。

```powershell
python projects/012-super-hermes/scripts/verify_web.py
python scripts/project_catalog.py check
```

根汇总器会自动复制本项目 `web/`，兼容 `/1022_codex_project/012-super-hermes/`，无需新增前端依赖。现有 Pages 工作流在汇总前运行本项目资源与原文完整性检查；2026-10-22 已发布至 [正式入口](https://yydshly.github.io/1022_codex_project/012-super-hermes/)；[Pages 构建与部署](https://github.com/yydshly/1022_codex_project/actions/runs/39776656381)成功。43 个项目发布文件均 HTTP 200 且与本地发布版本逐字节一致，总导航摘要和指定引导图已核验。详见 [部署记录](deployment-verification.json)。

## 在 Hermes 中使用上游 Skill

下面为上游文档的使用方法，本轮没有安装或运行：

```text
hermes skills install Cranot/super-hermes/skills/prism-scan
# 安装后在 Hermes 新会话中使用，确保文件路径有效：
/prism-scan analyze circuit_breaker.py focusing on thread safety
```

其余 Skill 单独安装。独立固定模板可作为其他工具的系统提示词，但完整 Skill 的迁移还需适配加载方式、工具名称、读写权限与会话编排。

## 版本、许可与边界

| 信息 | 记录 |
| --- | --- |
| 上游 | [Cranot/super-hermes](https://github.com/Cranot/super-hermes) |
| 固定 commit | `ffe2d10042041dcc23325f013e8b7e607e069952`，提交日期 2026-07-27 |
| 原始许可 | MIT，完整保留于 [上游 LICENSE](web/assets/upstream/LICENSE) |
| 本次材料 | 18 个上游文件，含 5 个 Skill、7 个模板、README、许可、安装脚本和三个示例文件 |
| 本地复现 | Windows，Python 3.10.11；仅标准库 |
| 语法检查 | Node.js 22.15.0；无 npm 依赖 |
| 研究日期 | 2026-10-22，Asia/Shanghai |

需要刷新快照时执行 `python projects/012-super-hermes/scripts/capture_source.py`，使用系统 curl 保持 HTTPS 验证，固定 SHA，不安装技能。`SOURCE.json` 保存逐文件 URL、字节数和 SHA-256；脚本还生成离线原文数据和 [资料 ZIP](web/assets/super-hermes-study-kit.zip)，重取快照会更新它们。

上游的 9.x 深度评分来自作者的 AI 评审，没有标准化外部基准。提示词要求推导的“守恒律”和“不可能三角”应当逐项核查，不能把输出形式当成数学证明。追加历史也没有后续质量提高的保证。

[网页验证记录](verification.json) · [编号路径与文件验证](http-verification.json) · [研究笔记](notes.md) · [返回总索引](../../README.md#项目索引)
