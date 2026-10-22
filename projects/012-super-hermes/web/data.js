/* Research summaries are distinct from the unmodified upstream text in source-data.js. */
window.GUIDE = {
  revision: 'ffe2d10042041dcc23325f013e8b7e607e069952',
  repository: 'https://github.com/Cranot/super-hermes',
  scenarios: {
    memory: {title:'服务跑得越久，\n内存为什么越高？', tag:'内存与资源生命周期', desc:'怀疑缓存无上限、对象长期被引用或释放路径缺失；让 AI 沿创建、持有、退出路径检查相关代码，再用运行数据验证。', input:'相关单个文件 + 增长现象、请求模式与已有内存采样。', output:'可疑分配点与持有点、触发条件、修复代价，以及需要补采的证据。', skill:'scan', request:'检查 cache_fixture.py：哪些对象被长期保留？缓存有没有容量或淘汰机制？列出可疑行、触发条件，以及如何用内存快照验证。', command:'/prism-scan analyze cache_fixture.py focusing on unbounded memory retention', boundary:'本研究自建缓存案例有实测对比；未运行 Hermes 或验证 Skill 检出率。该库不内置运行时内存探针。'},
    code: {title:'这段代码看起来能跑，\n但边界情况安全吗？', tag:'最典型的场景', desc:'准备修改一个重要文件，想找出普通阅读容易忽略的失败路径、并发冲突和隐藏假设。', input:'单个代码文件 + 检查重点，例如线程安全。', output:'问题位置、触发条件、严重程度、可修复性，以及尚未覆盖的角度。', skill:'scan', request:'检查 circuit_breaker.py，重点关注线程安全：找出状态转换与锁之间的冲突，并列出触发条件。', command:'/prism-scan analyze circuit_breaker.py focusing on thread safety', boundary:'示例提问。真实并发漏洞及本地复现见下方案例。'},
    design: {title:'这个方案的目标，\n真的可以同时满足吗？', tag:'设计决策前', desc:'缓存、重试、数据同步或一份产品方案中，常常同时追求多个目标。用不同角度寻找隐藏假设与修改代价。', input:'一份有目标、约束和候选做法的设计说明。', output:'结构上的矛盾、未来变化可能暴露的问题，以及需要进一步验证的取舍。', skill:'three', request:'检查 cache-design.md，从结构、未来变化与目标冲突三个角度分析；对每个“不可能”结论说明成立条件。', command:'/prism-3way analyze cache-design.md', boundary:'场景示例，并非已实测报告。模型提出的目标冲突需要独立验证。'},
    research: {title:'刚打开一个项目，\n应该优先检查什么？', tag:'研究陌生项目', desc:'面对一个核心文件或设计文档，先列出值得追查的方向。选择真正有价值的角度，再进入深入扫描。', input:'选定的单个源文件或一份项目设计文档。', output:'可选的研究方向清单，例如错误传播、接口约定、维护风险；之后再选一个方向分析。', skill:'discover', request:'针对 routing.py 列出值得研究的不同角度；先帮我决定查什么，再按重点深入。', command:'/prism-discover analyze routing.py', boundary:'discover 只列方向，不直接完成审查。当前库不支持跨文件整库分析。'},
    gaps: {title:'报告已经很详细，\n还有什么没有被检查？', tag:'依赖分析结论前', desc:'已有审查集中在某个角度，想检查它的假设、遗漏和过度断言，并为后续分析留下记录。', input:'同一个待审查文件；若要明确复查已有报告，也一并提供。', output:'结构分析、自我复查、盲区报告，以及追加到 .prism-history.md 的记录。', skill:'reflect', request:'检查 circuit_breaker.py，说明这套分析优先看到了什么、没看到什么；把后续检查建议记录下来。', command:'/prism-reflect analyze circuit_breaker.py', boundary:'reflect 会按指令写入项目历史文件；完整执行依赖宿主 Agent 的读写工具。'}
  },
  skills: {
    scan: {name:'prism-scan', kind:'单次定向分析', title:'先为这个问题，设计一套检查方法。', desc:'读取材料与既往盲区，生成一段针对当前对象的分析指令，再按指令完成审查。', steps:['读文件与历史', '生成专用方法', '执行并列出问题'], output:'生成的分析指令 + 问题表（位置、触发问题、严重程度、可修复性）+ 简短盲区说明。', limit:'适合单个文件或一份材料的定向审查。可在提问中补充性能、安全等重点。'},
    full: {name:'prism-full', kind:'多轮分析与反驳', title:'先深入检查，再攻击自己的结论。', desc:'为当前材料设计 2–4 个分析轮次；后续轮次参考前面的输出，最后强制做一次反驳与修正。', steps:['设计分析轮次', '逐轮执行', '反驳与撤回误判'], output:'最终问题表、经复查保留的设计判断、撤回的结论，以及反驳后新增的发现。', limit:'适合关键文件与重要设计。文档将多轮组织在一次响应中；完整遵循程度取决于模型。'},
    three: {name:'prism-3way', kind:'结构 / 时间 / 目标冲突', title:'把同一个问题，从三个角度看一遍。', desc:'依次检查结构层次、未来变化，以及所追求性质之间的冲突，最后比较三个角度的共同与不同发现。', steps:['WHERE 看结构', 'WHEN 推演变化', 'WHY 查目标冲突'], output:'三个角度的分析、交叉支持的发现、独有视角，以及综合判断。', limit:'适合代码、方案或研究文档。角度由同一模型执行；相互一致并不能独立证明结论正确。'},
    discover: {name:'prism-discover', kind:'先决定研究方向', title:'还没开始分析，先找值得问的问题。', desc:'列出约 10–20 个真正不同的研究方向，并说明每个方向可能揭示什么，供用户选择下一步。', steps:['读取材料', '区分研究方向', '列出方向菜单'], output:'一份分析方向清单。然后用 scan 或 full 深入其中一个方向。', limit:'这一步只发现方向；不执行深入分析，也不生成分析模板。'},
    reflect: {name:'prism-reflect', kind:'自我复查与盲区记录', title:'把自己的分析，也当成待检查的材料。', desc:'完成结构分析，再检查刚才的输出隐藏了什么，最后给出盲区报告并追加到项目历史文件。', steps:['分析原始材料', '复查本次分析', '报告并保存盲区'], output:'结构分析 + 自我复查 + MAXIMIZED / SACRIFICED / RECOMMENDATIONS 报告 + .prism-history.md。', limit:'会指示 Agent 写文件。上游估计成本约为 scan 的 2–3 倍；本研究未验证模型费用。'}
  },
  lenses: {
    error_resilience: {title:'错误传播', desc:'沿着异常捕获、默认值与回调边界，检查丢失的错误信息如何影响后续决策。'},
    l12: {title:'结构权衡', desc:'通过提出判断、构造替代设计与反转假设，寻找具体问题和持续存在的设计权衡。'},
    optimize: {title:'性能成本', desc:'检查抽象边界隐藏了哪些分配、缓存、锁竞争或往返成本，要求提出具体代价。'},
    identity: {title:'接口与实际行为', desc:'比较命名、类型和文档作出的承诺，与代码实际行为；例如读取属性却改变状态。'},
    deep_scan: {title:'信息损失', desc:'追踪具体错误如何被变成模糊错误，并检查异步状态交接、搜索优先级和组合边界。'},
    claim: {title:'假设反转', desc:'把关于时间、资源、因果或使用方式的假设逐个反过来，推演会出现什么问题。'},
    simulation: {title:'长期演化', desc:'推演新人加入、依赖升级、作者离开、使用增长和安全审查等维护周期中的脆弱点。'}
  },
  mechanism: [
    {owner:'由宿主 Agent 读取', title:'把材料与目标放进上下文。', desc:'用户选定一个文件或方案。scan 首先查找项目的 .prism-history.md；不存在时，直接从当前材料开始。', path:'skills/prism-scan/SKILL.md', name:'INPUT / 当前材料', example:'artifact: circuit_breaker.py\nfocus: thread safety\nhistory: 未发现历史记录\n\n先检查状态转换与锁。', historical:'artifact: circuit_breaker.py\nfocus: 补查此前遗漏\nhistory: 已查线程安全；未查性能与可观测性\n\n把遗漏加入本次检查目标。'},
    {owner:'由模型生成检查方法', title:'为当前材料写一段专用指令。', desc:'scan 要求模型生成 75–200 个英文单词的分析方法，并且包含构造替代方案或反例的步骤，再把它展示出来。', path:'skills/prism-scan/SKILL.md', name:'GENERATED LENS / 教学示意', example:'逐条列出状态转换。\n标出读取和写入发生的位置。\n构造线程交错使旧判断失效。\n比较改变锁边界后的效果。', historical:'上次已检查线程安全。\n这次构造高负载和监听器阻塞情形。\n追踪吞吐与可观测性上的遗漏。\n比较不同接口设计的代价。'},
    {owner:'由底层模型执行', title:'按步骤推演，形成具体问题。', desc:'模型执行生成的方法，尝试构造失败条件、替代设计和反例，输出位置与严重程度。真正运行代码仍需宿主提供工具。', path:'skills/prism-scan/SKILL.md', name:'FINDINGS / 教学示意', example:'位置：state 属性\n触发：检查时间后插入一次新失败\n结果：旧判断把状态改成 HALF_OPEN\n验证：需要构造线程交错。', historical:'位置：锁内的监听器通知\n问题：慢回调可能延长锁的持有时间\n下一步：增加负载与延时测量。\n注：这是分析建议，尚未实测。'},
    {owner:'切换到 prism-reflect', title:'检查这套分析遗漏了什么。', desc:'reflect 将第一轮分析当作新的材料，要求质疑假设、列出被牺牲的视角，再建议该如何补查。完整流程另外包含结构分析。', path:'skills/prism-reflect/SKILL.md', name:'CONSTRAINT REPORT / 教学示意', example:'MAXIMIZED: 线程安全\nSACRIFICED: 性能、可观测性\nRECOMMENDATIONS:\n下一次聚焦吞吐与日志。', historical:'MAXIMIZED: 性能与可观测性\nSACRIFICED: 接口可用性、测试体验\nRECOMMENDATIONS:\n下次检查测试隔离与时钟注入。'},
    {owner:'宿主 Agent 通过工具写入', title:'把盲区留给下一次分析。', desc:'reflect 指示 Agent 把报告追加到 .prism-history.md；后续 scan 再读取它，调整关注重点。持久化的是文本，不是模型参数。', path:'skills/prism-reflect/SKILL.md', name:'.prism-history.md / 教学示意', example:'# Prism Constraint History\n### 日期 — circuit_breaker.py\n- Maximized: 线程安全\n- Sacrificed: 性能、可观测性\n- Recommendations: 下次补查', historical:'# Prism Constraint History\n### 上次：线程安全 → 留下性能遗漏\n### 本次：性能与可观测性 → 留下接口遗漏\n\n后续 scan 读取这些记录继续补查。'}
  ]
};
