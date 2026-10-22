// Research-authored teaching example of OUR seven-step protocol, not a Hermes run.
window.INVESTIGATION = [
  {
    name:'定义问题', owner:'我们的七步协议 · 输入与范围', title:'先说清楚：什么现象，需要查到什么程度。',
    input:'现象：长期服务中，请求越多，内存越高。\n入口：cache_fixture.py；响应大小为 64 KiB。',
    instructions:['区分预期与实际，记录请求条件、影响范围和可用材料。','约定完成标准：解释增长路径并验证；本教学另比较有限缓存，但不推及真实服务。'],
    output:'问题：缓存服务的存活内存为何随不同 key 增长？\n范围：研究自建 Python 缓存，不含原生内存与跨文件引用。\n验收：有代码位置、触发条件、可反驳解释与运行对照。',
    why:'避免把含糊的“内存泄漏”直接当成根因，先确定调查对象与交付要求。',
    path:null, measurement:false,
    provenance:'问题定义、验收字段是本研究的协议设计；不是上游自动输入校验，也不是 Hermes 执行记录。'
  },
  {
    name:'建立事实基础', owner:'借鉴 scan · 先公开具体检查方法', title:'把“查内存”展开为分配、持有和退出路径。',
    input:'问题定义 + cache_fixture.py + 运行与采样入口。',
    instructions:['针对当前材料设计查法：追分配点、持有者、持有者寿命和淘汰条件。','读取相关代码，记录第 11 行分配、第 20 行入缓存；把代码事实与运行证据分开。'],
    output:'代码事实：每个未命中的 key 创建 64 KiB 响应；self.cache[key] 保存它。\n持有链：长期存活的 cache → key → 响应。\n缺口：仅凭代码还需验证对象是否一直保留、条件是否足够。',
    why:'沉淀的是“沿生命周期追踪”的通用动作；当前问题的具体查法由分析者结合材料展开。',
    path:'skills/prism-scan/SKILL.md', anchor:'step-1-generate-a-fresh-lens', measurement:false,
    provenance:'scan 要求先生成 75–200 个单词的定制方法，再执行；此处内存查法由研究者编写，未调用 Hermes。'
  },
  {
    name:'提出候选解释', owner:'我们的七步协议 · 将解释变成可检验假设', title:'不要看到内存上涨，就断言 GC 失效。',
    input:'分配与缓存持有事实；还没有排除其他原因。',
    instructions:['为合理候选写出支持依据、预测与推翻条件。','选择能区分候选的条件，而不是重复描述“内存变大”。'],
    output:'候选 A：无界缓存长期保留响应。预测：不同 key 增长，同 key 有界；清空缓存后响应释放。\n候选 B：响应另被其他对象持有。预测：清空缓存后仍保留。\n若重复同 key 也持续增长，候选 A 不足以解释现象。',
    why:'候选与反证条件让下一步有明确目标；这里的候选清单是我们的协议补充。',
    path:'skills/prism-full/SKILL.md', anchor:'phase-2-execute-the-pipeline--mandatory-adversarial-pass', measurement:false,
    provenance:'借鉴 full 主动推翻发现的要求；假设列表及本例内容由研究者编排。'
  },
  {
    name:'设计并执行检查', owner:'宿主 / 开发者 · 外接测量工具', title:'改变 key 或容量，用执行结果区分解释。',
    input:'候选 A/B、可检验预测和自建缓存代码。',
    instructions:['分别检查不同 key、重复 key、32 条 LRU；各组使用独立子进程，采样前执行 GC。','用 tracemalloc 记录存活分配，最后清空缓存检查响应分配行；记录预期与实际。'],
    output:'本研究确实执行了这些检查；数据见下方实测。', metrics:true,
    why:'这一步将代码推演与运行结果对照；原库没有内置本例测量器。',
    path:null, measurement:true,
    provenance:'检查、测量工具与运行由研究者完成。没有运行 Hermes 或模型；数值不代表 Skill 检出率。'
  },
  {
    name:'收敛并反驳根因', owner:'借鉴 full · 对抗复查与撤回过度结论', title:'让根因解释条件与传播路径，并寻找反例。',
    input:'三组实测、清空后响应分配增量为 0、代码持有链。',
    instructions:['比较预测与结果，排除“请求数本身造成增长”和本例响应还有其他长期引用的解释。','核对因果链和边界；若结果不符，回到候选或检查，不强行结案。'],
    output:'本例有证据支持：长期缓存无淘汰 → 新 key 响应一直可达 → 存活内存持续增长。\n反证检查：同 key 不持续增长；清空后响应分配增量归零。\n边界：没有测真实服务、原生内存或运行至 OOM。',
    why:'反驳帮助纠正结论；有限案例的证据只能支持有限范围的原因。',
    path:'skills/prism-full/SKILL.md', anchor:'phase-2-execute-the-pipeline--mandatory-adversarial-pass', measurement:true,
    provenance:'full 要求额外对抗复查。这里的因果解释和排除判断由研究者给出，不是模型输出。'
  },
  {
    name:'验证修复', owner:'我们的七步协议 · 仅修复任务适用', title:'原场景能改善，还要说明相关回归和代价。',
    input:'无界缓存的原因 + 最多 32 条 LRU 的替代实现。',
    instructions:['同样 800 个不同 key 比较前后；检查缓存条目与对象持有是否有界。','记录命中与容量相关检查，以及淘汰后需要重新生成响应的代价；没有覆盖的回归如实列出。'],
    output:'原场景：无上限约 50.126 MiB / 800 条；32 条 LRU 约 2.010 MiB / 32 条。\n相关检查：不同 key 的条目上限、无上限缓存重复 key 对照、清空后响应释放已测。\n未覆盖：真实业务语义、并发与过期策略等回归。\n只定位时可不改；这些结果不等于生产服务已修复。',
    why:'修复验收是我们补充的执行要求。代码改动和改善曲线不能代替未覆盖的业务回归。',
    path:null, measurement:true,
    provenance:'自建代码与有限缓存对照已运行；本步骤不是上游内置的修复和测试编排器。'
  },
  {
    name:'报告与沉淀', owner:'我们的九项报告 + 借鉴 reflect 的盲区历史', title:'交付能核查的结论，给下次留下可用线索。',
    input:'问题定义、代码路径、运行数据、反证结果和未覆盖范围。',
    instructions:['按九项报告交付，明确根因已有证据支持、候选待验证或尚未定位。','保存查法、适用条件与盲区；reflect 可追加侧重、遗漏和建议，完整案例另行归档。'],
    output:'01 结论状态：本自建案例根因已有证据支持。\n02 问题与影响：不同 key 增多导致存活内存增加。\n03 定位位置：cache_fixture.py:11 分配；:20 持有。\n04 触发条件：缓存长期存活、持续出现新 key。\n05 因果链：新 key → 响应入无界缓存 → 长期保留。\n06 证据：代码持有链、三组对照、清空后响应释放。\n07 其他解释：请求次数本身不足以解释；未检查真实服务其他来源。\n08 修复与验证：LRU 对照有界；生产业务回归未覆盖。\n09 局限与下一步：补充真实服务指标、原生内存与跨文件引用。',
    why:'把结论、证据、修复状态和局限放在同一报告中，才能交接、复核和复用。',
    path:'skills/prism-reflect/SKILL.md', anchor:'phase-4-growth--persist-constraint-knowledge', measurement:true,
    provenance:'九项报告是我们的协议；上游 reflect 保存的主要是侧重、遗漏和建议，不是完整故障档案或模型训练。'
  }
];
