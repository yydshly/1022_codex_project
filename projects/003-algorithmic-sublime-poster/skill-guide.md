# 可复用Skill：emotion-art-direction

[Skill入口](skills/emotion-art-direction/SKILL.md)将这套方法变成AI可以按任务读取的工作指引：先明确情绪与艺术意图，再结合风格规则和实际案例，构造图片、视频或返修提示词。由本研究原创整理；没有引入上游执行代码，也没有把海报库包装成视频模型。

[计划公开Skill入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#emotion-skill)：**本次发布验证中**。研究全貌见[第三版总览图](assets/research/emotion-art-research-overview-v3.png)和[研究总结](research-summary.md)；图中案例为AI概览合成，准确历史指令与媒体原件另外保存。

它承接的是整个研究方法：情绪与艺术意图明确创作方向，风格规则规定如何表达，再选择像素、点云、数据连接、光色、构图或视频事件等手段组织prompt。源库贡献实体与计算结构融合的海报规范；本Skill、21份情绪起点、其他风格旁支与跨图片/视频模板是我们的扩展。选择写实摄影就组织摄影要求，继承原海报家族就带入实体、计算关系与模块化排版；实际生成由宿主相应模型与工具完成。

## 调用

本次已安装到当前环境的`D:/codex/home/skills/emotion-art-direction/`。之后可显式调用，例如：

```text
请使用 $emotion-art-direction，为一张展览海报明确情绪与艺术方向。
希望观众感到自由而不轻浮，主体是候鸟；保留写实材质和大留白。
结合合适的风格规则与案例，给出完整图像生成提示词。
```

```text
请使用 $emotion-art-direction，为一条10秒短片构造生成提示词。
主题是从紧张到安心，保留克制的写实风格。
先明确情绪走向与转机事件，再安排动作、摄影和声音。
```

本Skill默认整理艺术方向与提示词。用户要求实际生成时，再使用宿主可用的相应工具与已有授权，不会因调用本Skill自动产生付费生成任务。现有意图足够明确时继续工作，只有影响核心方向的缺失才集中澄清。

## 包内内容

| 内容 | 读取方式 |
| --- | --- |
| SKILL.md与agents/openai.yaml | 短入口、适用范围和界面调用信息；保留默认自动匹配 |
| 21份情绪档案 | 先看情绪索引，再只读相关的一两份；可以继续自定义 |
| 原主风格与3份旁支 | 明确固定规则、可变项和评审依据；按用户方向选择，不给所有作品强加粒子、数据和标题 |
| 图片、视频、返修模板 | 按媒介或返修任务读取所需分支，不一次加载所有模板 |
| 3组实际案例 | 花朵、产品尺度返修与AI共伞短片，带准确历史指令、事后复用方案和执行偏差 |
| 媒体原件与来源清单 | 4张PNG、1条实际AI原始视频和3张抽帧JPEG；媒体与实际指令按字节保留 |

所有引用在Skill目录内可解析。安装包不依赖本仓库目录、当前本地网站、账号凭据或固定Windows盘符。用户未选择算法崇高家族时，可以采用写实无字、水墨等其他规则。

## 迁移与维护

下载[ZIP安装包](assets/skills/emotion-art-direction.zip)或从[网页Skill入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#emotion-skill)下载，解压后保留顶层目录。在Codex中，将该目录放入`CODEX_HOME/skills`；未设置CODEX_HOME时放入`~/.codex/skills`。

项目源码在`skills/emotion-art-direction/`。入口与界面元数据在该目录维护；模板、情绪、风格、案例参考由`scripts/package_emotion_skill.py`从既有指导包生成。先更新指导包，再打包：

```powershell
python projects/003-algorithmic-sublime-poster/scripts/prepare_intent_guide.py
python projects/003-algorithmic-sublime-poster/scripts/package_emotion_skill.py
python projects/003-algorithmic-sublime-poster/scripts/package_emotion_skill.py --check
python projects/003-algorithmic-sublime-poster/scripts/package_web.py
```

另加`--install`可安装一个新副本，或核对已安装副本完全一致；发现已存在的不同内容时会停止并保留原文件。不会静默覆盖用户在本机的修改。安装包和项目源码分别记录在[构建清单](assets/skills/emotion-art-direction.json)，媒体来源另在Skill内登记。

已通过Skill Creator结构校验、所有本地引用校验、原件与准确指令哈希核对、下载包解压校验和本机副本一致性检查。这些验证说明结构与资源可用，没有据此声称已完成跨模型前测、生成质量评分或观众情绪命中测试。

## 实际应用记录

新增[Skill驱动短片《给你留个座》](skill-film-trial.md)：实际读取入口、视频模板、安心档案和已有视频案例，再将“可以停留”转译成拉出座位、手势邀请、走近并实际落座。一次Seedance 2.0图像参考生成，保留2张输入的角色、准确提示词、原片与[Skill使用证据](assets/skill-film/skill-use.json)；[网页入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#skill-film)分别展示原计划与实际观察。落座确实发生，结尾停留偏短；尚未听觉审片，不能把含音轨写成声音质量已验证。

本次选择写实剧情影像规则，没有把图片海报的实体数据融合强加到视频中。新案例保存在项目与网页，未重打包进现有49文件Skill包；所读文件与安装包版本保持不变。它是一次真实执行案例，没有无Skill对照或独立观众，不能据此推出Skill独立增益。

较早用当前安装版完成[红木椅摄影分支试跑](skill-trial.md)，但用户指出其没有延续原有实体数据融合风格。之后实际完成[固定原风格的三情绪海报](chair-data-trial.md)：锁定红木椅、实体与计算结构、模块化标题“在场”，再定制情绪和具体画面要求。首轮三张，孤独方向追加一次尺度返修；准确指令、原件、偏差与前轮摄影对照在[网页主对照](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#skill-trial)展示。Skill与安装包版本保持不变，读取文件哈希随实验记录保留。

延续已有系列时，创作总纲应显式带入该系列的固定风格规则。换主体或情绪不应自动换掉这套规则；风格是否保留与情绪是否传达分别检查。

这是当前对话里的真实功能试跑，支持完整艺术配方能落实为可见差异；没有无Skill对照、独立代理前测、跨模型试跑或独立观众评测，不能据此给Skill独立增益或情绪命中率下结论。

## 本轮收束与后续复用

本轮的[研究总结](research-summary.md)整理了原库与研究扩展的边界、情绪/艺术意图/风格/手段的层级、真实案例和保留问题。[核心理解与案例索引](assets/research/working-understanding.md)可整份交给后续AI；[研究复盘模板](assets/research/revisit-template.txt)用于带着具体问题重访。两份资料位于项目中，不改动当前Skill目录、安装版或ZIP，也不需要本地网站才能理解。

Skill是使用它的AI的工作指引：由AI理解任务、按需读取参考、明确艺术方向、组织提示词，并对实际结果审片与返修。情绪词不是自动映射到画面的公式；风格规则也不是必须给所有作品叠加粒子。完整的直接提示词可以承载相同要求；若实际提交的提示词、素材、模型与参数相同，生成端不会因上游是否读过Skill而获得额外能力，输出仍可能受随机性影响。现有执行记录没有验证Skill相对同样完整直接提示词的因果收益。

后续使用时，先带入当前任务和需要继承的风格，再选一个有关案例。重点保留“意图—具体要求—实际输出—偏差—定向修改”的链路；不要把事后整理的复用方案写成准确历史指令，也不要用计划或代码预演替代未发生的生成。视频需分别检查事件回应、接触连续性、结尾时间和声音；未听过原片时继续标明音频未审。

六个复用问题是：研究对象实际提供什么；本次要解决什么具体问题；哪些规则继承、哪些变量改变；什么最小真实验证足够；实际证据与未检查项是什么；达到什么条件就收束、出现什么问题才重访。详表见[研究总结](research-summary.md#下一次研究的六个问题)。当前研究先保留资料，不再泛扩风格；以后根据具体偏差或新任务补充，而不是为目录数量继续生成。
