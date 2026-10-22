# 图片与资料来源

| 文件 | 内容与替代文字 | 来源与说明 |
| --- | --- | --- |
| `super-hermes-diagnosis-v3.png` | 最新总结：5 个 Skill、7 份模板、模型与 Skill 及证据分工、七步定位协议、循环与修复条件、九项报告、验证边界和复用价值 | 2026-10-22 内置 ImageGen 新生成；971 × 1619；七步与完整报告为研究提炼，非原库自动执行器；旧图保留 |
| `seven-step-imagegen-prompt.txt` | 七步流程与能力总结图完整生成提示词 | 实际发送给内置 ImageGen 的内容；生成记录与哈希见 `../seven-step-image.json` |
| `super-hermes-understanding-v2.png` | 上一版理解总结：Skill 本质、能力、原理、六步归纳、逐步约束与产物、软约束边界、复用价值 | 2026-10-22 内置 imagegen 生成；1086 × 1448；旧版六步为当时跨文件归纳，现行协议以七步版为准 |
| `understanding-imagegen-prompt.txt` | 上一版理解图的完整生成提示词 | 实际发送给内置 imagegen 的内容；生成记录与哈希见 `../understanding-image.json` |
| `super-hermes-overview.png` | Super Hermes 全量总览：步骤、5 个 Skill、规范、7 份视角、角色与历史反馈、限制与扩展 | 2026-10-22 使用内置 ImageGen 生成；原始 941 × 1672 PNG；固定版本依据、研究归纳与未验证范围在图中标注 |
| `overview-imagegen-prompt.txt` | 全景图的完整生成指令 | 本次实际发送给内置 ImageGen 的提示词，不是上游 Skill 原文 |
| `cover.png` | Super Hermes 研究网页：AI 深度审查 Skill 包的定位、输入输出与能力规模 | 2026-10-22 本地浏览器真实首屏截图；不是 Hermes 原生界面或模型运行结果 |
| `capabilities.png` | 五个 Skill 的职责、完整原文入口与七份固定分析模板 | 本研究静态网页真实截图 |
| `mobile.png` | 手机宽度下的 Super Hermes 研究网页 | 本研究静态网页真实截图 |
| `analysis-method.png` | 流程、交付规范、检查角度三类约束与提示词执行边界 | 2026-10-22 新增方法提炼区的真实截图 |
| `memory-case.png` | 无上限缓存的可疑代码、对象持有原因与 LRU 修改前后内存曲线 | 2026-10-22 研究网页真实截图；代码和测量为研究自建，没有运行 Hermes 或模型 |
| `guided-investigation.png` | 从现象到结果教学中的“生成查法”：具体指令、输入、产物和阶段作用 | 2026-10-22 网页真实截图；教学内容按上游规则编写，不是 Hermes 分析记录 |
| `rulebook.png` | 完整规则区展开“构造动作”规则，展示指令、作用、产物与来源 | 2026-10-22 研究网页真实截图；不是 Hermes 执行结果 |

网页首屏的棱镜、流程形状与图标由本研究以 SVG / CSS 绘制；新全景图由 ImageGen 依照研究内容绘制。没有使用上游标志或第三方图片。全景图和首屏截图均放入 `web/assets/`；登记表与根站点总导航使用新全景图。

原始生成文件保留于生成工具返回的 D 盘目录，项目内原图与网页副本字节一致。尺寸、字节数、SHA-256、提示词路径和固定上游 SHA 见 `../overview-image.json`。图中“共用分析思路”是研究者归纳，五个 Skill 的阶段不同；扩展分层与允许证据不足的做法为研究建议。

上游 Markdown、代码与示例保存在 `web/assets/upstream/`，逐文件来源、固定版本与哈希见 `../SOURCE.json`。使用上游 MIT 许可，并保留其完整声明。`web/assets/race-reproduction.json` 是本次运行脚本输出；界面上的逐步线程演示是依据此过程编排的预设示意。
