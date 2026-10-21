# 005 · Scene Card Studio：直接给大模型的创作规则

> 将核心场景卡、创作规则与审核方法提取成提示词。复制指令、提供照片和创作目标即可，无需安装原项目。

[在线网页](https://yydshly.github.io/1022_codex_project/005-scene-card-studio/) · [站点总导航](https://yydshly.github.io/1022_codex_project/) · [部署验证](deployment-verification.json)

| 信息 | 内容 |
| --- | --- |
| 上游与作者 | [swping999/scene-card-studio](https://github.com/swping999/scene-card-studio) |
| 研究版本 | v0.7.0，commit [`8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea`](https://github.com/swping999/scene-card-studio/tree/8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea) |
| 上游许可 | Apache-2.0；见 [许可证副本](LICENSE.scene-card-studio.txt) 与 [改写说明](NOTICE.md) |
| 收录日期 | 2026-10-21 |
| 验证环境 | Windows、PowerShell、Python 3.10.11；规则提取只需标准库 |
| 本次范围 | 提取、中文改写、完整规则与编译模板导出；补充 AI 生成理解总结图，未进行新的原图改图实验 |

![Scene Card Studio 理解总结：基于原图二次创作，把改图要求变成可复用、可检查的规则与流程，并展示四种效果及扩展场景与意义](assets/understanding-summary.png)

*本研究使用内置 ImageGen 生成；图中效果为参考上游样张的呈现，非新的改图实测，扩展场景为应用方向。完整请求见 [生成提示词](assets/understanding-summary-prompt.txt)，参考图、哈希与检查见 [总结图记录](study-guide.json)。原有[流程图](assets/overview.svg)保留，来源见 [图片说明](assets/README.md)。*

## 我们的理解

本质是基于原图做二次创作，也就是图生图／AI 改图。这个库把改图要求整理成可复用、可检查的规则和流程，实际成片由外部图像模型生成。

| 要点 | 简明说明 |
| --- | --- |
| 能力 | 组织照片二次创作，明确保留、改变和删除的范围，再组织叙事、构图、光色与材质要求。 |
| 输入 | 一张或多张原图，加上表达目标、修改范围、画幅和文字需求；场景语义由人或视觉大模型补齐。 |
| 如何处理 | 整理场景卡 → 选择叙事与表达 → 编译提示词 → 外部模型改图 → 对照检查、定向返修；需要文字时独立排版。 |
| 输出 | 外部模型输出成片；库组织场景卡、完整提示词、文件清单和审核记录，执行相应工具后还可产生排版文件。 |
| 使用场景 | 旅行纪念、家庭相册、社交内容与品牌视觉，以及多张作品统一、反复修改和团队交接。 |
| 可扩展方向 | 自定义风格模板、接入更多图像模型、批量处理与协作流程、嵌入相册或内容工具；这些是扩展方向，不代表已有完整产品实现。 |
| 意义 | 把“改得好看一点”变成具体且可追溯的决定，让要求可复用、结果可检查、过程可交接。 |

## 网页摘要

本质是基于原图做二次创作，可理解为“图生图／AI 改图”。核心价值是把改图要求整理成可复用、可检查的规则和流程；实际改图由外部图像模型执行。网页首屏与价值说明均采用这一表述。

[打开网页](web/index.html)：首页直接展示原图与成片；湖泊刺绣、海边人物水彩两组案例均包含输入原图、创作要求、三类规则、最终效果、结果观察和完整编译提示词。创作要求为场景卡的中文整理，非原始用户发言。效果区默认并列展示纤维刺绣、全画面水彩、选择性浮雕和国风诗意四种效果，无需展开或切换；浮雕与国风明确标注“仅成片，原图未公开”。共六张上游图片，未重新生图。

页面新增“一张图，读懂这个库”区域，总结能力、图生图原理、四种效果参考、可扩展场景和意义，支持放大与下载；总结图也作为项目导航封面。页面保留精简／完整／返修指令的复制与下载，以及 11 种叙事和 24 种表达的兼容筛选。案例原始记录和译写来源见 [cases.json](cases.json)；每组源图与成片的哈希均已核对原编译记录。

发布资源使用相对路径，先运行 `python projects/005-scene-card-studio/scripts/package_web.py`，再用根 `scripts/build_site.py` 汇总至 `/005-scene-card-studio/`。打包与副本检查已接入现有 Pages 工作流。2026-10-21 已发布到[正式网页](https://yydshly.github.io/1022_codex_project/005-scene-card-studio/)，内容提交 `224b0fe`，[构建与部署成功](https://github.com/yydshly/1022_codex_project/actions/runs/39619790319)；线上 35 个文件（项目资源及总导航）均 HTTP 200 且字节一致，七项摘要、指定引导图与主要交互通过浏览器检查。

[四种效果总览](assets/web-preview-effects-restored.png) · [完整案例桌面预览](assets/web-preview-inputs.png) · [完整案例手机预览](assets/web-preview-inputs-mobile.png) · [网页验证记录](web-verification.json)

网页修改后的检查：

```powershell
python projects/005-scene-card-studio/scripts/package_web.py --check
python projects/005-scene-card-studio/scripts/verify_web.py
node --check projects/005-scene-card-studio/web/app.js
```

## 怎么用

1. 日常先复制 [精简指令](prompts/00-quick-use.zh-CN.txt)；复杂任务再用 [完整创作指令](prompts/01-direct-use.zh-CN.txt)，或把文件作为附件交给能看图的大模型。
2. 上传照片，按 [需求模板](prompts/02-request-template.zh-CN.txt) 说明目标。未定的可留空，由模型从可见信息出发给保守建议。
3. 想用具体风格时，从 [11 种叙事与 24 种表达规则](prompts/03-creative-rules.zh-CN.md) 选相关条目附上，不必一次提交整套规则。
4. 成片需要修改时，提供原图、当前成片和前一版提示词，使用 [对照审核与定向返修](prompts/04-review-and-retry.zh-CN.txt)。

只有生图功能的工具，可直接使用 [十模块生图模板](prompts/05-image-prompt-template.zh-CN.txt)；只有看图和文本功能的模型输出创作方案与提示词。需要工具才能生成画面。

例如上传湖边照片后可以说：

> 想表达安静的湖边停留。选择记忆地图＋纤维地景；保留小船形状、磨损、山脊轮廓和前后层次，允许把表面统一转换成刺绣；仅删除我明确指出的杂物。单张 4:5 竖图，无字，给出实际生图指令。

这是一条用法示例，须以实际照片核实主体，不是本次实测请求或生成证据。

## 原始规则在哪里

| 文件 | 内容与性质 |
| --- | --- |
| [中文通用版](prompts/01-direct-use.zh-CN.txt) | 普通对话改写，无命令行依赖 |
| [中文规则指南](prompts/03-creative-rules.zh-CN.md) | 机制与材质摘要、兼容表；非逐句完整翻译 |
| [原始规则 JSON](rules/upstream-rules.json) | 从固定 commit 的真实常量完整导出，保留各系统不同的 `source-led`、全部 Profile 内容、别名和审核标准 |
| [全部编译模板 JSON](rules/compiled-templates.json) | 调用上游编译器生成，覆盖全部兼容组合的单图与双图分支，带十模块与完整英文指令 |
| [精选原始模板](prompts/extracted/README.md) | 五组常用组合，替换 `{{字段}}` 后可直接使用 |
| [上游原文快照](upstream/skills/scene-card-studio/SKILL.md) | 原 Skill 与参考文档的未修改副本 |
| [来源与哈希](SOURCE.json) | 固定版本、实际代码与快照的哈希、导出参数 |
| [检查结果](verification.json) | 组合覆盖、编译一致性与文件完整性检查 |

`full-watercolor-memory` 是全水彩的兼容别名，不计入 24 个规范表达。原始模板使用符号场景卡，占位文件仅满足编译器的存在／哈希要求；导出不含占位文件路径、源哈希或假的成片审核记录。

## 提取后保留与缺少的能力

保留：观察与解释分层、保留／变化／删除规则、系统与材质分离、十模块提示词、五项审核和多图连续性检查。

自然语言不会自动提供精确尺寸校验、文件哈希绑定、版本持久化、SVG 排版和软件硬性拦截。文字准确性、主体保真与输出规格仍需实际工具和看图检查。没有排版工具时只交付正文与版面说明。

中文版将 CLI 和清单操作改为对话步骤，在既有授权内直接推进，关键事实、修改范围或新增工具授权不明确时才澄清。具体改写见 [NOTICE.md](NOTICE.md)。未进行与普通直接改图的受控对比，不能声称提高画质或成功率。

## 重新提取与检查

日常使用不需要运行。重新导出时，在仓库根目录执行：

```powershell
git clone https://github.com/swping999/scene-card-studio.git _upstream/scene-card-studio
git -C _upstream/scene-card-studio checkout 8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea
python projects/005-scene-card-studio/scripts/extract_rules.py --upstream _upstream/scene-card-studio
python projects/005-scene-card-studio/scripts/extract_rules.py --upstream _upstream/scene-card-studio --check
python scripts/project_catalog.py check
```

脚本拒绝不匹配的提交或参与提取的代码修改。检查各兼容组合的输出数量、来源模式、十模块与完整指令的一致性，并逐字节核对导出。

上游本地 `direct` 流程此前已验证：未补语义为 `needs-semantic-direction`，完整卡片为 `prompt-ready`，均未生图。详见 [研究笔记](notes.md)。

[上游编译器](https://github.com/swping999/scene-card-studio/blob/8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea/src/moments_to_pages/prompt_compiler.py) · [表达规则源码](https://github.com/swping999/scene-card-studio/blob/8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea/src/moments_to_pages/expression_profiles.py) · [返回总索引](../../README.md#项目索引)
