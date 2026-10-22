# 003 · Algorithmic Sublime Poster

> 从海报风格规范出发，研究以情绪与艺术意图引导AI创作：结合像素、点云、数据连接等视觉语言组织提示词，用实际图片、视频和返修沉淀可复用方法。

![情绪与艺术意图引导AI创作研究总览：源库三组海报效果、21个情绪起点、风格规则、图片视频探索与可复用Skill](assets/research/emotion-art-research-overview-v3.png)

*最新第三版研究总览，2026-10-22通过内置imagegen制作。图中案例为依据原件的AI概览合成；源库温暖人物、彩珠动物与数字连接三组参照共同说明主体、计算结构和排版的关系。实际原件与准确指令见下方案例及[总览图来源记录](assets/research/overview-manifest.json)。*

**本轮研究收束：**先读[研究总结与后续复用问题](research-summary.md)，再按具体任务查看图片、视频或Skill记录。核心是用艺术意图统领画面，把情绪与风格转成可执行要求并检查实际结果；现有案例未证明Skill优于同样完整的直接提示词，也未证明稳定的观众情绪命中。

[网页复盘入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#research-summary)提供对照导航；[核心理解与案例索引](assets/research/working-understanding.md)和[研究复盘模板](assets/research/revisit-template.txt)可直接交给后续AI。当前资料已够本轮研究使用，之后针对具体问题重访，不再以增加风格数量作为完成目标。

| 信息 | 内容 |
| --- | --- |
| 原项目 | [https://github.com/xianxie6/algorithmic-sublime-poster](https://github.com/xianxie6/algorithmic-sublime-poster) |
| 作者 / 组织 | [xianxie6](https://github.com/xianxie6) |
| 研究版本 | [`846fac0a9fc247b480f71c9846c83815d2edfe41`](https://github.com/xianxie6/algorithmic-sublime-poster/tree/846fac0a9fc247b480f71c9846c83815d2edfe41)，2026-09-01 的初始提交；2026-10-21 核对时为 main HEAD |
| 上游许可 | 该提交没有独立 `LICENSE`，不能假定为 MIT 等许可；示例媒体另有 [NOTICE](assets/NOTICE.upstream.md) |
| 收录日期 | 2026-10-21 |
| 研究进度 | 以 [项目登记表](../catalog.json) 为准 |
| Web 展示 | [公开展示](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/)；**已部署并验证（2026-10-22）**。本地构建步骤见下方[复现与运行](#复现与运行) |

## 研究主线与能力边界

本研究关注**用艺术意图统领作品，用具体视觉与听觉要求指导模型实现，再依据实际结果校准**。先明确希望观众感到什么、作品想表达什么，再选择主体关系或事件，继承需要延续的风格，组织完整提示词与参考素材。像素、点云、字符、扫描、数据连接、光色和构图是实现手段；进入视频后，还要安排动作因果、时间、镜头与声音。

源库将“算法崇高 / Algorithmic Sublime”编辑海报的经验写成设计Skill和风格手册。用户提供主题或图片，使用它的AI据此组织主体、计算隐喻、转换区域、构图、标题与颜色，再调用宿主可用的图像生成工具。源库的核心是**设计规范 + 结构化提示词 + 生成后检查**，不包含自研模型、训练代码、绘图引擎或自动情绪评分。

我们在此基础上扩展了情绪档案、跨媒介艺术方向、真实图片与视频试跑、审查返修及[emotion-art-direction Skill](skill-guide.md)。源库的实体数据融合仍作为主风格保留；摄影、诗性实体转化、水墨留白、有机曲线装饰是我们另选或探索的表达方向。实际生成依赖相应模型与工具，网页负责组织和展示既有结果。

网页以“情绪档案 → 主体与原风格 → 可执行要求 → 成图校准”为核心流程，提供7组21份情绪起点、主副情绪组合、表达力度、自由补充、返修依据与JSON/TXT导出。原风格固定规则持续保留；早期四个情绪与材料起点、七张花朵成图的三组对照继续作为研究展示。另增加三份风格档案与六张人物／产品作品，支持固定规则、可变项、禁用倾向、定制指令与档案导出；并保留早期鲸鱼作品和三组作者案例，在折叠的算法说明中提供 **13 种同源 Canvas 实时样式**、5 种动态动作与静态对照、4 种版式、指针扰动、滚动转化、PNG 导出和提示词联动。网页使用原创 HTML/CSS/JavaScript，没有搬运上游执行代码。

其中，作者案例是图像模型生成的既有结果；折叠区的13种实时扩展实验是本研究编写的浏览器程序，另有独立调用模型生成的图片和视频案例。13 种实时样式不等于上游自带 13 个算法，也不能作为图像模型生成效果的实测。定位方法、定制方式与本轮实际指令见 [情绪驱动的艺术方向](art-direction.md)；早期修正见 [visual-quality.md](visual-quality.md)，算法说明见 [extensions.md](extensions.md)。

## 研究成果与执行记录

以下记录区分源库既有示例、我们实际生成的媒体与代码预演。每个案例保留准确指令和已知偏差；新增情绪档案不代表已逐一生成并验证。

实际应用Skill组织并生成[短片《给你留个座》](skill-film-trial.md)：先确定“局促—邀请—接受—可以停留”，再组织写实影像规则、动作/空间/声音与两张参考图角色。一次Seedance 2.0图像参考视频生成，实际原片1902×1092、24fps、10.048秒，估算240积分、实际300；[网页新入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#skill-film)保留准确指令、Skill读取哈希、原片、实际抽帧和审片偏差。可见邀请、走近与最终落座；坐稳后停留很短，动作接触与情绪余味仍需校准。未完成听觉审片，未证明情绪稳定命中。

按用户原有风格完成[同一红木椅的实体与数据融合三情绪对照](chair-data-trial.md)：锁定真实实体、沿结构组织的计算转化与模块化标题“在场”，再用安心、孤独、不安定制光色、距离和数据关系。3次首轮ImageGen生成加1次孤独尺度返修，全部原图与准确指令保留；[网页主对照](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#skill-trial)可放大、下载、比较摄影分支及真实返修前后。孤独整椅人工粗框由约47%降至27%；风格延续有可见依据，情绪仍有相邻解读。

前轮实际应用Skill，换用朱红色木椅，生成[安心、孤独、不安三种摄影方向](skill-trial.md)。4次调用得到1张身份参考和3张成图，原件保留；现明确标为[摄影分支历史对照](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#chair-photo-trial)。它展示了情绪空间差异，却未延续用户原主风格，本轮已针对这一点重新生成。

新增可复用Skill [emotion-art-direction](skills/emotion-art-direction/SKILL.md)，以情绪与艺术意图为起点，按需读取21份情绪档案、原主风格和3份旁支、图片/视频/返修模板与实际案例。已放入本机Skill目录，另提供[独立安装包](assets/skills/emotion-art-direction.zip)与[使用说明](skill-guide.md)。网页增加[Skill下载与调用入口](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#emotion-skill)，准确历史指令、原始媒体和观察边界随包保留。

新增[以情绪与艺术意图为核心的提示词总纲](prompt-template-guide.md)，提供图片、视频、定向返修三份可编辑模板，结合《风有形》、香水瓶孤独与尺度返修、《留一点位置》实际案例。可载入事后整理的复用方案，分别查看准确历史指令，并复制或下载当前草稿。完整JSON还包含21份情绪档案、原有主风格5条固定规则及3份旁支档案，供后续AI整体读取。[进入创作模板](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#intent-template)。

此前的 [实际AI短片《留一点位置》](ai-film-direction.md)：一次Seedance 2.0文字生成视频，保留未经修改的模型原片、原始声音、实际指令和审片偏差。10.048秒、1902×1092、24fps，通过“独处—移伞邀请—同伞同行”表达从疏离到被接纳。生成前估算240积分，实际返回300；差异已告知并记录。旧片继续独立保留，原件与深链接不变；代码预演折叠保留。[直接播放旧AI原片](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#ai-film)。本片没有独立观众情绪评测。

补充 [动态情绪V2与观看返修流程](motion-revision.md)：保留三条首版片，实际重做三条优化片，调整人物比例、姿态对齐、距离驱动步态、减速停步、接地与声音。网页增加同一时刻切换V1/V2、三片同步对照、单独听某一片、按版本保存个人复盘及针对性返修指令。没有新增模型调用或情绪命中统计。

新增 [动态情绪对照《候光》](motion-emotions.md)：同一雨夜场景的孤独、不安、希望三条12秒有声影片。两张新增AI素材加人物逐帧动画、镜头、雨、水波、光影和原创合成声音制作；网页支持选片、静音/有声比较、定格、分镜定位及下载。对应视频模型导演指令作为尚未执行的草案提供。没有调用视频模型，也没有验证观众情绪成功率。[直接播放](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#motion-emotions)。

新增 [情绪引导的实际生成验证](emotion-validation.md)：8次内置ImageGen调用，1张中性主体图、6张首轮作品、1张定向返修；展示同主体换情绪、同情绪换主体和返修前后三种对照。实际指令、来源、偏差、原图与个人观图记录均可查看或下载。结果支持视觉配方与定向尺度返修可执行，未证明目标情绪稳定命中；温柔与参照重叠、母风格标题偏差等问题如实保留。

新增 [从情绪档案到作品与视频](motion-direction.md)，说明单幅、系列、视频的场景、交付和风格积累方法，并实际制作《夜香 · 给孤独一个回应》15秒有声概念片。网页可播放、拖动时间、定位三个分镜、同步查看要求和下载影片与方案。成片由一张新增ImageGen关键画面加动态合成制作；没有调用视频模型，也不代表上游具备视频生成能力。直接打开 [视频演示](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#motion-demo)。

- [x] 固定上游提交，核对完整文件树、流程、风格手册、入口配置和素材声明。
- [x] 检查三组作者前后对比，区分保留目标、实际观察与角色重设计。
- [x] 以静态网页展示能力、效果、原理、场景和意义。
- [x] 使用可复现的素材打包、目录检查与整站构建流程。
- [x] 按上游规范及本研究艺术方向手工组织指令，使用内置 ImageGen 工具实际生成或编辑 14 张原创成图，保存原图、完整指令、哈希和轮次；其中 7 张花朵成图用于三组方向对照，另新增 6 张跨主体风格探索。工具未返回模型版本；未自动执行上游 Skill。
- [ ] 对作者的原始输入进行受控复跑，测试主体保真、标题准确率与生成成功率。

## 复现与运行

已验证环境：Windows、Python 3.10.11、Node.js 22.15.0；网页无需 npm、构建框架、CDN、API Key 或后端。Python 打包与整站构建只使用标准库，Node.js 仅用于检查 JavaScript 语法。

在仓库根目录执行：

```powershell
python projects/003-algorithmic-sublime-poster/scripts/prepare_intent_guide.py
python projects/003-algorithmic-sublime-poster/scripts/package_emotion_skill.py
python projects/003-algorithmic-sublime-poster/scripts/package_emotion_skill.py --check
python projects/003-algorithmic-sublime-poster/scripts/package_web.py
python projects/003-algorithmic-sublime-poster/scripts/package_web.py --check
python scripts/project_catalog.py check
node --check projects/003-algorithmic-sublime-poster/web/app.js
node --check projects/003-algorithmic-sublime-poster/web/extensions.js
node --check projects/003-algorithmic-sublime-poster/web/art-gallery.js
node --check projects/003-algorithmic-sublime-poster/web/direction-studio.js
node --check projects/003-algorithmic-sublime-poster/web/style-profiles.js
node --check projects/003-algorithmic-sublime-poster/web/emotion-library.js
node --check projects/003-algorithmic-sublime-poster/web/motion-study.js
node --check projects/003-algorithmic-sublime-poster/web/emotion-validation.js
node --check projects/003-algorithmic-sublime-poster/web/motion-emotions.js
node --check projects/003-algorithmic-sublime-poster/web/motion-review.js
node --check projects/003-algorithmic-sublime-poster/web/ai-film.js
node --check projects/003-algorithmic-sublime-poster/web/skill-film.js
node --check projects/003-algorithmic-sublime-poster/web/intent-template.js
node --check projects/003-algorithmic-sublime-poster/web/skill-trial.js
node --check projects/003-algorithmic-sublime-poster/web/chair-data.js
python scripts/build_site.py --output _site/poster-preview
python projects/003-algorithmic-sublime-poster/scripts/serve_web.py --directory _site/poster-preview --port 8033
```

访问 [本地项目展示](http://127.0.0.1:8033/003-algorithmic-sublime-poster/) 和 [本地总导航](http://127.0.0.1:8033/)。输出目录必须为空；重复构建时更换目录名，不需要删除已有产物。

素材原件仅在 `assets/` 登记和维护，打包脚本按其 `FILES` 清单逐字节复制至被忽略的 `web/assets/`；具体数量以本次 `--check` 输出为准，检查会核对副本与原件完全一致。创作模板源定义在 `scripts/prepare_intent_guide.py`，该脚本生成独立MD/TXT与整合JSON；改模板或情绪/旁支档案后先运行它，再更新Skill包。椅子试跑的登记与数据整理见[摄影分支](skill-trial.md)、[实体数据融合](chair-data-trial.md)及[新短片](skill-film-trial.md)，Skill版本保持不变。部署工作流再由根汇总器复制完整 `web/`。静态资源使用相对路径，兼容 `/1022_codex_project/003-algorithmic-sublime-poster/` 子路径。网页播放已有视频不需要密钥；重新生成视频需要已授权的外部生成服务。

打包后的 `web/index.html` 也适用于支持本地文件的普通浏览器；此前内置浏览器只允许 HTTP/HTTPS，历史检查通过本地 HTTP 服务完成，详见[验证记录](verification.md)。本次公开发布状态另行核验，不能以本地检查代替。受浏览器剪贴板限制时，可手动复制已选中的指令，或下载 `.txt`。扩展实验支持本地 PNG/JPEG/WebP 读取，文件只在浏览器内存中处理，没有上传服务或图像模型接口。图像取样需使用允许 Canvas 读取像素的本地 HTTP 服务。

优先查看 [情绪定位与定制流程](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#extensions)。算法实验默认折叠；仍可直接进入 [实时扩展画布](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#extension-stage)。上方的“当前样式”可以连续切换 13 种；下面可调密度、比例、速度、动作与版式，或展开“13 种同源效果图谱”。

本轮 [四种情绪并排对照](assets/direction-emotions-preview.png) 和 [手机流程](assets/direction-mobile-preview.png) 可直接查看。早期已保存 [桌面首屏](assets/web-preview.png) 与 [手机首屏](assets/web-preview-mobile.png)；完整检查结果见 [verification.md](verification.md)。

原 Skill 的实际复现条件是：宿主能够读取 Skill，并提供图像生成或图片编辑工具。早期十四张原创成图的指令按上游规范手工编排，没有安装或自动执行上游Skill；之后另实际读取并应用本研究扩展的emotion-art-direction，完成红木椅图片与《给你留个座》短片生成。两类执行记录分别保留，均未验证原图保真或稳定成功率；视频另依赖相应生成服务。

## 实现拆解

| 上游文件 | 提供的内容 | 本页如何展示 |
| --- | --- | --- |
| [`SKILL.md`](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/SKILL.md) | 理解输入、三个主要转换方向、标题、氛围、强度、调用工具与检查要求 | 能力说明、流程交互和局限 |
| [`references/style-system.md`](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/references/style-system.md) | 视觉 DNA、构图、三档强度、适应性配色、提示词顺序和失败模式 | 机制示意与提示词构建器 |
| [`agents/openai.yaml`](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/agents/openai.yaml) | 显示名、简介和默认提示 | 入口配置说明 |
| `examples/*.png` | 三组作者提供的输入与输出对照 | 展示结果、完整对照与案例解读 |

流程是：**理解素材与识别特征 → 组织设计约束 → 调用外部图像模型 → 检查与针对性修正**。字符、粒子、扫描线等由模型绘制，不是这个仓库对输入执行物理扫描、三维仿真或真实数据编码。

提示词实验室按“交付比例 → 素材角色 → 主体特征 → 计算隐喻与方向 → 构图 → 标题与排版 → 光色材质 → 保留与避免事项”组织文字。输入只用于本地字符串组合，以 `textContent` 写入页面；复制与下载均由用户点击触发。

实时实验独立实现在 `web/extensions.js`：将图片缩放到 320 × 420 的离屏画布后采样颜色和透明度，根据选定样式重绘为 1200 × 760 的海报。不同样式采用字符、色块、点、网格、条带、三角切片或软边纹理；动画移动这些实际样本。“带入提示词”将对应视觉要求写入提示词实验室，真实 AI 成图仍需另行调用图像模型。

### 能力与效果

一套集中于“实体与计算系统发生联系”的美学，支持以下方向：

1. **局部数据分解**：实体边缘逐渐成为字母、像素、粒子或点云。
2. **系统包围**：人物或物体进入信息空间、屏幕隧道或数据场。
3. **分析标本**：网格、坐标与扫描结构穿过实体。

克制、标准和强故障控制视觉密度；深色科技、明亮天空、温暖人物与动作场景调整氛围。它们是同一视觉体系内的变体。留白、覆盖比例等是提示目标，不是由前端或上游程序精确执行的图像参数。

### 案例观察

![作者的南瓜服儿童前后对比：左为照片，右为奶油色背景、橙色像素消散与大号中文标题组成的海报](assets/03-pumpkin-before-after.png)

*源库作者原始示例，左为输入素材与请求，右为输出；与README上方的AI研究总览示意分开。主体、构图与细节可能被重新生成，本研究未复跑作者原始输入。三组原件均见[素材声明与来源](assets/README.md)。*

| 案例 | 展示出的能力 | 保留的边界 |
| --- | --- | --- |
| 彩珠动物 | 黑底与青蓝数据场、轮廓消散、大标题构图 | 画面被重新生成，数据字符不是实际编码计算 |
| 原创数字英雄 | 伸手动作成为横向轴线，数据线连接人物、空间网格与右侧标题；见[作者原始对照](assets/02-original-web-hero-before-after.png) | 示例记录了改为原创角色，标题也从原请求调整；不属于原角色保真转换成功 |
| 南瓜服儿童 | 暖色、奶油纸张、少量坐标与局部像素化 | 人物与手势细节有变化，不能证明身份完全一致 |

### 场景与意义

研究方法适合有明确情绪或艺术方向的创作：海报与封面把感受落实到主体关系、光色和留白；系列作品锁定识别中心与风格规则；视频把感受组织为事件、回应和结尾余味。提示词模板与Skill将这些判断连同准确历史指令、原件和返修依据保存，便于后续AI复用。以下场景为依据风格和实验推导的建议，不是已核实的客户案例。

| 场景建议 | 适用原因 | 实际使用时的边界 |
| --- | --- | --- |
| 科技传播、文章封面、活动概念 | 给“人、物与系统”这样的抽象关系一个具体视觉形式 | 正式发布需检查产品外形、文字与素材授权 |
| 自然、文化与展览主题 | 大留白和扫描隐喻适合表现观察、生命和编码 | 装饰数据不等于真实科研信息 |
| 人物与品牌情绪提案 | 以暖色和边缘转化服务于身份、记忆或成长主题 | 脸、手、姿态和身份一致性需复核 |
| 系列视觉与跨主体创作 | 先固定风格规则，再改变主体、情绪及其具体表达 | 换情绪不能无意替换原风格；跨主体一致性仍需逐张检查 |
| 短片概念与导演方案 | 用可见事件、动作和时间表达关系变化，结合声音提出完整要求 | 实际视频中的受力、回应、节奏与声音需分别审查；代码预演不能替代模型成片 |
| 设计教学、风格探索与评审 | 可对照提示词选择，并在同一素材上实时比较 13 种程序效果 | 浏览器处理与图像模型成图是两条路径；模型结果仍需单独生成与检查 |

目前可复用的价值是把模糊审美转成明确条件，积累可讨论、可修改的过程；能节省多少时间、改善多少生成质量或观众感受，仍待更深入验证。

## 研究结论

1. 源库提供海报风格规范；我们的研究进一步整理为情绪与艺术意图引导的图片、视频和Skill方法。实际生成仍依赖相应模型与工具。
2. 像素、点云、数据线等应与主体形成方向和语义联系；人物、空间、排版与留白共同组织画面，不能只概括为粒子效果。
3. 图片案例出现了空间与光色差异，尺度返修有可见改进；两条真实AI短片出现了邀请与回应。风格、接触、节奏和相邻情绪解读仍有偏差，两片声音尚未完成听审。
4. Skill由使用它的AI推理并组织提示词和审查。向同一模型提供同样完整的直接提示词、素材与参数，可以形成相同生成输入；本轮没有证明Skill独立收益或稳定情绪命中，跨模型与独立观众反馈也待验证。
5. 精确文字、主体保真、分层交付、矢量排版与印刷色彩流程仍需额外工作。源库作者示例没有提供稳定复现和成功率基准，本研究也未受控复跑其原输入。
6. 当前没有独立上游 LICENSE；保留媒体 NOTICE，将示例用于明确署名的研究评论与效果展示。没有把它们声明为可商用素材包，也没有引入上游执行代码。

后续从具体问题重访，保留固定条件，记录完整实际指令、输入角色、模型/参数、原件、失败和返修。只有要判断因果或稳定性时，再安排匹配对照、重复采样和独立观看；详见[研究收束与复用清单](research-summary.md)。

## 图片说明

图片文件、来源、授权和说明见 [assets/README.md](assets/README.md)。新增截图应配有替代文字和简短图注。

## 研究记录与来源

- [研究笔记](notes.md)
- [原始仓库](https://github.com/xianxie6/algorithmic-sublime-poster)
- [返回总索引](../../README.md#项目索引)

本目录为独立研究记录。第三方代码、图片及其他材料遵循其各自许可；引入时补充来源与必要声明。

## 风格档案与对应作品

核心入口增加 [情绪引导档案](emotion-guide.md)：7组21个起点，每份包含目标／避免感受、故事、光色构图、计算转化、跑偏与返修要求。支持检索、主副情绪组合、表达力度、自由补充、指令复制和JSON/TXT导出，并可载入原风格编辑器，保留主体、标题与识别中心。完整档案数据可供后续AI读取使用；新增档案不代表已有独立成图。

原有 Algorithmic Sublime 作为默认主档案保留：五条固定规则、温暖人物／深色科技／横向动作三份指导配方，以及可编辑的意图、计算隐喻、识别中心、区域、语言、光色、画幅与强度。可复制指令与下载主档案 JSON，作者原图只作风格参照。详见 [原有风格的定制与引导](original-style.md)。

诗性实体转化、水墨留白、有机曲线装饰归入折叠的跨风格旁支。每份用人物和无品牌香水瓶各生成一张，比较规则如何跨主体延续，也记录实际执行偏差。详见 [旁支档案研究](style-profiles.md)，或打开 [风格展厅](https://yydshly.github.io/1022_codex_project/003-algorithmic-sublime-poster/#style-profiles)。网页不执行实时生成。
