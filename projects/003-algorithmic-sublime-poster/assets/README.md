# 图片与来源

本次网页素材打包清单共160项；下文各实验中的累计数量保留为对应研究阶段的记录，不代表当前总数。素材接入打包与公开部署成功分别核验。

| 文件 | 用途 / 图注 | 来源与许可 |
| --- | --- | --- |
| `01-beverage-before-after.png` | 作者原始对比：彩珠动物素材 → 深色科技海报；2390 × 1810 | [固定版本原件](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/examples/01-beverage-before-after.png)，xianxie6 发布的工作流示例 |
| `02-original-web-hero-before-after.png` | 作者原始对比：现有角色动作 → 原创数字纤维英雄；2988 × 1026 | [固定版本原件](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/examples/02-original-web-hero-before-after.png)，含角色改编上下文 |
| `03-pumpkin-before-after.png` | 作者原始对比：南瓜服儿童 → 温暖人物海报；2784 × 1728；曾用作项目封面，现保留为源库案例原件 | [固定版本原件](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/examples/03-pumpkin-before-after.png)，xianxie6 发布的工作流示例 |
| `NOTICE.upstream.md` | 原样保留的媒体声明 | [上游 NOTICE.md](https://github.com/xianxie6/algorithmic-sublime-poster/blob/846fac0a9fc247b480f71c9846c83815d2edfe41/NOTICE.md) |
| `web-preview.png` | 本地网页桌面首屏，1265 × 712 截图；浏览器视口 1280 × 720 | 本研究的浏览器实拍，2026-10-21；画面内的作者示例仍遵循上述 NOTICE |
| `web-preview-mobile.png` | 本地网页手机首屏，375 × 812 截图；浏览器视口 390 × 844 | 本研究的浏览器实拍，2026-10-21；画面内的作者示例仍遵循上述 NOTICE |
| `study-flower.svg` | 13 种样式共用的橙金花朵与绿色叶片，透明底，480 × 620 | 本研究原创矢量绘制，用于实际像素采样；不来自图像模型 |
| `extension-previews/*.png` | 13 种实际浏览器导出，均为 1200 × 760；原色、密度 68、转化 100%、静态、单主体海报 | 本研究原创程序处理原创花朵，逐图说明和链接见 [扩展记录](../extensions.md) |
| `extension-previews/manifest.json` | 导出设置、13 张图的名称与 SHA-256 | 本地浏览器实际运行后登记，无图像后处理 |
| `extensions-preview.png` | 13 种实时扩展实验的桌面网页实拍 | 本地运行的 Canvas 页面，2026-10-21；源素材为原创花朵 |
| `extensions-mobile.png` | 手机宽度的画布、样式选择和参数控件实拍 | 本地运行的 Canvas 页面，2026-10-21；源素材为原创花朵 |

本研究未修改原始图片文件。网页只以 CSS 隐藏截图左侧来展示输出，也可切换完整对照或放大阅读。机制示意、页面排版与交互为本研究原创 HTML/CSS/JavaScript。

上游未提供独立 LICENSE。NOTICE 明确：这些示例可能包含用户图片、第三方虚构角色或其他素材；示例的存在不代表获得原素材的复用授权或商业使用权。本地保留署名与声明，用于研究评论与能力展示，不将其作为自由授权素材分发。

原件与网页副本 SHA-256：

```text
8ed9d590cd917d55f0736120d31f0cf399332788b6a9ea71cb5b7c0dcfa6f68c  01-beverage-before-after.png
c699ef273f899ebb7ba01cd59d50e9043cf1ae9b3982590ce6186033e69ce71e  02-original-web-hero-before-after.png
3270826d034940675400d5cd574d31627660a595f04f762a7666f43ac00013c0  03-pumpkin-before-after.png
```

运行 `python projects/003-algorithmic-sublime-poster/scripts/package_web.py` 生成 `web/assets/`，再用 `--check` 检查逐字节一致；网页副本不重复提交。脚本复制三张作者示例、NOTICE 和原创 SVG；实时图谱在浏览器中计算，13 张导出图作为研究证据保留，不重复放入网页包。上游来源登记见 [sources.json](sources.json)。

## 本次实际生成的原创海报

- [风有形](warm-bloom-poster.png)：橙色花朵、暖光、象牙纸与局部花瓣转化；[实际指令](warm-bloom-prompt.txt)。
- [向蓝而生](blue-whale-poster.png)：蓝色天空、鲸鱼与后缘玻璃晶体；[实际指令](blue-whale-prompt.txt)。

两张均在 2026-10-21 使用内置 ImageGen 工具从文字生成，每张一次、未经后期修改，1122 × 1402。未使用作者输入图片，不是上游已有素材。具体模型版本未由工具返回。完整来源和 SHA-256 见 [generated-posters.json](generated-posters.json)。生成指令按上游规范手工组织，未自动执行 Skill。

[新版展厅截图](creative-preview.png) 为浏览器实拍；生成海报、程序输出、作者示例分别标注来源。

## 情绪与艺术方向对照（本轮新增 6 张）

### 理解汇总图

[understanding-overview.png](understanding-overview.png) 将艺术意图、视觉要求、模型生成与检查修正串成闭环，引用四种情绪的成图，并概括使用场景和后续价值。2026-10-21 使用内置 ImageGen 工具生成，未经后期修改；具体模型版本未返回。完整指令见 [understanding-overview-prompt.txt](understanding-overview-prompt.txt)，尺寸、SHA-256、参考图角色和来源见 [understanding-overview.json](understanding-overview.json)。这是生成式信息图，缩略插图可能被模型重新绘制，不能作为逐像素复现证据。

原始输出在 [directions/](directions/manifest.json)，来源、共同编辑参考、尺寸、哈希与轮次均记录在清单。每张一次内置 ImageGen 调用，1122 × 1402，无后期，模型版本未返回。原有 warm-bloom-poster.png 为共同参考，不涉及第三方照片的身份保真测试。每张配有原始英文提示词 TXT。

网页使用七张花朵图做三组设计对照，另保留鲸鱼图。截图：[情绪](direction-emotions-preview.png)、[材料](direction-materials-preview.png)、[强度](direction-strength-preview.png)、[手机](direction-mobile-preview.png)。截图未经图像编辑。

## 风格档案与跨主体作品（新增 6 张）

[styles/profiles.json](styles/profiles.json) 是三份创作档案的原始定义：[诗性实体转化、水墨留白、有机曲线装饰](../style-profiles.md)。每种各有一张人物、一张产品，均为内置 ImageGen 实际输出，1122 × 1402、每张一次调用、无修订与后期，具体模型版本未返回。虚构人物与无品牌产品由文字生成，水墨与曲线版本分别参考对应的诗性版本重新诠释。不是上游素材、内置风格或训练权重。

六张 PNG、逐张实际英文指令、输入角色和 SHA-256 均在 [生成记录](styles/manifest.json) 登记。界面中的中文结构化配方另用于定制与复用。样例说明和执行偏差见 [风格研究记录](../style-profiles.md)。

网页实拍：[人物三风格](style-profiles-portrait-preview.png)、[香水瓶三风格](style-profiles-product-preview.png)、[档案详情](style-profile-detail-preview.png)、[手机](style-profile-mobile-preview.png)。截图无后期。当时打包脚本复制 36 个原始文件，包括这些新作品、实际指令、档案与生成记录；截图仅作研究证据，不放入网页包。

## 原有风格主档案恢复

[original-style-customization-preview.png](original-style-customization-preview.png) 是1280×720视口下的原风格定制与作者南瓜案例参照；[original-style-mobile-preview.png](original-style-mobile-preview.png) 为390×844视口下的手机参照与编辑流程。2026-10-21本地浏览器直接截图，无后期。画面内作者原图仅以CSS裁切输出区域，保留原图文件，来源与许可仍见本文件开头及NOTICE。工作法见 [原风格定制记录](../original-style.md)。

## 情绪引导档案（原创文字数据）

[emotions/profiles.json](emotions/profiles.json) 为本研究编写的7组21份创作指导档案，含目标／避免感受、故事、视觉要求、跑偏与返修、评审问题、表达力度与可读词汇。不是上游内置情绪模型，也没有逐项生成新的效果图。四份历史参照沿用 directions 中原始PNG与生成记录，角色在页面逐张说明。

新增网页实拍：[情绪核心入口](emotion-library-preview.png)、[孤独配方详情](emotion-profile-solitude-preview.png)、[手机版](emotion-library-mobile-preview.png)。截图由本地浏览器直接输出，无图像后期。当时打包脚本复制37个素材文件，新增的是完整情绪JSON数据；截图只作研究证据。

## 情绪影像《夜香》（新增1张关键画面与15秒影片）

motion/night-signal-keyframe.png 是内置ImageGen实际生成的1672×941原创关键画面，完整英文指令与一次调用、无修订的记录见 [motion/manifest.json](motion/manifest.json)。原图未经修改；工具未返回模型版本。主体为虚构无品牌香水瓶，没有使用第三方人物、商品照片或外部音乐。

[night-signal.mp4](motion/night-signal.mp4) 为本研究编写合成器实际制作的15秒、1280×720、24fps有声概念片。制作包括画幅适配、慢推镜头、冷暖调色、沿瓶身的信号、中文标题与原创程序合成声音，由FFmpeg导出H.264/AAC。未调用视频模型，也不表示上游海报库提供视频生成能力。制作方式与复现见 [影像说明](../motion-direction.md)。

三张JPEG从最终MP4的2、7.5、12.5秒直接提取，用于网页分镜定位。完整JSON、VTT字幕、原关键画面与实际指令、MP4、三张JPEG、素材清单共9个文件加入打包，总数46。文件大小与SHA-256在清单登记。关键画面的额外山景、开口和暖色反射已如实记录。

网页实拍：[实际视频入口](motion-study-preview.png)、[手机视频流程](motion-mobile-preview.png)、[作品用途与流程](creative-works-preview.png)。均为本地浏览器直接截图，无后期；仅作研究证据，不进入网页素材包。

## 情绪引导实际验证（新增8张原始PNG）

2026-10-21至22，本研究使用内置ImageGen共8次实际调用，全部结果保留：1张中性参考、6张首轮成图、1张定向返修。每张1122×1402，原工具PNG原样复制，无代码滤镜、调色、裁切或压缩；模型版本与种子未返回。本轮没有调用视频模型。

| 文件 | 内容与来源角色 |
| --- | --- |
| [00-bottle-reference.png](validation/00-bottle-reference.png) | 新生成的中性灰底瓶身身份参考，无标题或数据 |
| [01-bottle-control.png](validation/01-bottle-control.png) | 同一瓶身与母风格，仅省略情绪、故事与光色构图配方；仍由模型自动选择气氛 |
| [02-bottle-solitude.png](validation/02-bottle-solitude.png) | 孤独要求的首轮输出，主体尺度仍偏大 |
| [03-bottle-tender.png](validation/03-bottle-tender.png) | 温柔要求的首轮输出，实际仍偏暖金产品广告 |
| [04-bottle-pressure.png](validation/04-bottle-pressure.png) | 压迫要求的首轮输出，有空间挤压，也存在其他解读 |
| [05-person-solitude.png](validation/05-person-solitude.png) | 共享孤独视觉语法的虚构成年人物，文字生成 |
| [06-shelter-solitude.png](validation/06-shelter-solitude.png) | 共享孤独视觉语法的玻璃候车亭，文字生成 |
| [07-bottle-solitude-repaired.png](validation/07-bottle-solitude-repaired.png) | 以首轮完整香水图为编辑目标，仅针对主体尺度返修；非像素锁定 |

每张同名的-prompt.txt保存完整实际英文指令；[manifest.json](validation/manifest.json) 登记输入、轮次、原图大小、SHA-256与指令哈希；[protocol.json](validation/protocol.json) 和 [repair-plan.json](validation/repair-plan.json) 分别在生成及修正前记录计划；[study.json](validation/study.json) 提供完整观察与局限。

尺度粗框为作者人工估计，网页以CSS叠加显示，不改变原图，也不代表情绪分数。实验分析见 [emotion-validation.md](../emotion-validation.md)。新增20个素材与记录进入打包，当前总数66。

网页实拍：[同主体对照](validation-subject-preview.png)、[跨主体对照](validation-transfer-preview.png)、[返修前后](validation-repair-preview.png)、[手机流程](validation-mobile-preview.png)。均为浏览器直接输出、无后期，作为研究证据保留。


## 动态情绪对照《候光》（2张AI素材、3条有声影片）

2026-10-22，内置ImageGen实际调用2次：rain-shelter-plate.png（1672×941海岸雨亭场景），walker-sprites.png（1983×793 RGBA透明四姿态人物）。两个同名-prompt.txt为实际完整指令；原图按字节保存。模型版本与种子未返回。没有视频模型调用。

[孤独](motion-emotions/solitude.mp4)、[不安](motion-emotions/unease.mp4)、[希望](motion-emotions/hope.mp4) 均为本研究编排制作的12秒、1280×720、24fps影片，含人物二维素材动画、雨、水波、反射、光、镜头、稀疏连线和原创合成声音。封面JPEG从最终MP4的8.8秒直接提取；两人复用同一人物外观，动作自然度有限。

[motion-emotions/study.json](motion-emotions/study.json) 为制作方案；三份-video-direction.txt明确标记为后续视频模型输入草案、尚未执行。[manifest.json](motion-emotions/manifest.json) 保存来源与全部14个媒体/方案文件的哈希；连同清单共15个文件加入打包，总数81。详细原理、使用场景、局限与复现见 [motion-emotions.md](../motion-emotions.md)。

网页实拍：[桌面](motion-emotions-desktop-preview.png)、[手机](motion-emotions-mobile-preview.png)、[正常预览](motion-emotions-preview.png)。由浏览器直接输出，无后期；作为研究证据保留，不加入网页素材包。


## 动态情绪V2与观看复盘（新增12个文件）

[motion-emotions/v2/](motion-emotions/v2/manifest.json) 保留三条V2实际成片、从各最终MP4提取的3张8.8秒封面、3份尚未执行的视频模型导演指令、study.json、motion-metrics.json与manifest.json。无新增模型调用，复用原先2张ImageGen素材。V1原片和原始素材按字节保持不变，当前媒体打包总数93。

V2改善人物比例、姿态对齐、按距离推进的步态与脚步声、减速停步、接触阴影、衰减反射和后层雨线。人物仍为二维素材，两个角色来自同一原图，以身高和衣色区分；不代表自然演员表演、独立身份生成或真实三维景深。详见 [优化说明](../motion-revision.md)。

网页新增同步三片对照、单独选择一片声音、同秒切换V1/V2、个人复盘与返修指令草案。观众输入只在页内存放，可手动导出，未形成独立盲评或情绪成功率统计。

新增网页实拍：[同秒对照](motion-v2-comparison-preview.png)、[复盘与返修](motion-v2-review-preview.png)、[手机对照](motion-v2-mobile-preview.png)，均由浏览器直接输出、无后期，仅作研究证据。

## 视频模型原片《留一点位置》（新增11个文件）

2026-10-22，通过ChatArt技能实际调用一次Seedance 2.0文字生成视频，任务1034571；无图片、音频或视频参考输入。输入仅为本研究编写的虚构成年人物故事与导演要求。上游海报库没有生成此视频，原风格与作者素材的声明继续独立保留。

| 文件 | 来源与角色 |
| --- | --- |
| [shared-space-original.mp4](ai-film/shared-space-original.mp4) | [服务实际返回](https://files.chatartpro.com/web-video/20261021/6ad9035fbacd5.mp4)的原始字节；1902×1092、24fps、10.048秒、H.264/AAC、32kHz双声道；9,590,694字节 |
| [shared-space-prompt.txt](ai-film/shared-space-prompt.txt) | 实际提交的完整中文导演指令，与请求内容逐字核对 |
| [request.json](ai-film/request.json) / [provider-result.json](ai-film/provider-result.json) | 实际请求与完成结果，排除凭据；估算240积分，服务返回实际300，保留差异 |
| [plan.json](ai-film/plan.json) / [study.json](ai-film/study.json) / [review.json](ai-film/review.json) | 原计划、实际媒体信息与作者观察，区分目标、执行和未知项 |
| [2秒](ai-film/shared-space-02.jpg) / [5秒](ai-film/shared-space-05.jpg) / [8秒](ai-film/shared-space-08.jpg) | 直接从实际原片提取的JPEG：靠近、目光回应、同伞前行；仅作为定位用图，不代替视频 |
| [manifest.json](ai-film/manifest.json) | 以上10个文件的大小与SHA-256，以及原始视频来源 |

原片SHA-256为`da91ec9d5ed4b2cd66ea3bbeaf59ac5c5cbed4d47da9c3dd00060a9c0a08798c`。原片没有重新编码、画面加工、代码动画或另配声音。服务未提供权重版本与种子；本研究未进行听觉审片、独立观众评测或稳定成功率实验。详见[实际视频研究](../ai-film-direction.md)。

新增11个媒体与记录文件加入网页包，总数104。浏览器截图[AI原片展示](ai-film-web-preview.png)、[手机展示](ai-film-mobile-preview.png)与[展开实际提示词](ai-film-prompt-preview.png)为直接实拍，无后期，作为研究证据另存，不加入网页素材包。提示词截图展示原片抽帧、完整实际指令及其艺术意图段落。

## 情绪与艺术意图提示词包（新增5个指导文件，复用现有媒体）

2026-10-22，本研究原创整理[完整创作总纲MD](intent/guide.md)、[图片模板](intent/image-template.txt)、[视频模板](intent/video-template.txt)、[返修模板](intent/repair-template.txt)与[整合JSON](intent/templates.json)。由`scripts/prepare_intent_guide.py`生成；不调用模型，也不生成或修改图片与视频。

JSON整合原有21份情绪档案和3份旁支档案，并保存原主风格5条固定规则、3组实际案例与事后整理的中文复用方案。原情绪数据和旁支数据在对应命名空间内按内容原样保留；案例准确历史指令单独链接，复用方案不冒充实际提交内容。

网页复用`warm-bloom-poster.png`、`validation/07-bottle-solitude-repaired.png`、`ai-film/shared-space-05.jpg`；三图分别为已有图像生成输出、实际返修输出和AI视频5秒抽帧。来源及媒体声明沿用本文件前文，同时将已有`generated-posters.json`加入网页包以提供完整来源。新增网页素材共6项，总数110；没有新媒体生成。

直接浏览器截图：[核心理解](intent-template-preview.png)、[图片与视频案例](intent-cases-preview.png)、[手机模板](intent-mobile-preview.png)。截图无后期，仅作研究证据，不加入网页包。具体工作法见[提示词总纲说明](../prompt-template-guide.md)。

## 可复用Skill安装包

[emotion-art-direction.zip](skills/emotion-art-direction.zip)是完整独立Skill，源码在项目的`skills/emotion-art-direction/`，共49个文件、16,758,957字节。由本研究原创整理，包含入口、元数据、按需读取的档案与模板，以及既有实际案例原件；没有新增模型调用。构建过程和逐文件哈希见[清单](skills/emotion-art-direction.json)。

包内使用已有花朵原图、中性产品参考、首轮与返修香水图、AI短片原始MP4与2/5/8秒抽帧，四份准确实际指令按字节复制。没有加入上游第三方示例图片、账号凭据或生成服务配置。案例媒体来源、制作方式和限制在Skill的references/provenance.md与media-provenance.json中登记。

安装包和清单两项加入网页素材，总数112。新增浏览器实拍[Skill入口](emotion-skill-preview.png)、[手机入口](emotion-skill-mobile-preview.png)，截图无后期，不加入网页包。安装与调用见[Skill说明](../skill-guide.md)。

## 实际应用Skill：朱红色木椅三方向

2026-10-22，实际应用已安装的emotion-art-direction，内置ImageGen调用4次，生成1张主体身份参考与安心、孤独、不安三张方向成图。四张PNG都是1122×1402工具原件，按字节复制，无图像后期；模型版本与种子未返回。主体为本轮原创文字描述的无品牌木椅，三图都以新生成的reference.png作身份参考，无第三方主体照片。

[reference.png](skill-trial/reference.png)、[safe.png](skill-trial/safe.png)、[solitude.png](skill-trial/solitude.png)、[unease.png](skill-trial/unease.png)及四份同名-prompt.txt保留实际输出和准确提交文本。[protocol.json](skill-trial/protocol.json)登记生成前方案与读取的Skill文件哈希；[execution.json](skill-trial/execution.json)登记真实提交内容；[review.json](skill-trial/review.json)是作者观察、人工粗框与未执行返修建议；[study.json](skill-trial/study.json)用于展示；[manifest.json](skill-trial/manifest.json)记录工具原件路径及12个文件的SHA-256。共13项加入网页素材包，当前总数125。

本轮没有修改Skill源码、安装副本或下载包。每方向一次、全部保留；无无Skill对照、重复采样或独立观众，不把作者的观察写成情绪成功率。详细方法与局限见[实际试跑](../skill-trial.md)。

浏览器实拍[三图对照](skill-trial-preview.jpg)与[手机对照](skill-trial-mobile-preview.jpg)由本地浏览器直接输出，无后期；仅作研究证据，不进入网页素材包。

## 红木椅：固定原有实体数据融合风格

2026-10-22，实际应用emotion-art-direction，3次内置ImageGen首轮生成加1次孤独尺度返修，得到4张1122×1402原始PNG。[safe.png](chair-data/safe.png)、[solitude.png](chair-data/solitude.png)、[unease.png](chair-data/unease.png)为三个首轮，[solitude-repaired.png](chair-data/solitude-repaired.png)为一次真实模型返修；全部原件按字节保存，无代码滤镜、缩放、裁切或文字后期，模型与种子未知。

三次首轮共同附上前轮[椅子身份图](skill-trial/reference.png)与[作者示例截图](03-pumpkin-before-after.png)，后者仅借鉴右侧成品的实体计算转化、模块化大字与疏密语法，不复制儿童、服装或原标题。作者素材的第三方声明继续适用，见[NOTICE](NOTICE.upstream.md)。返修只以孤独首轮完整海报为编辑目标。

三份同名-prompt.txt与[solitude-repair-prompt.txt](chair-data/solitude-repair-prompt.txt)保留准确实际提交文本；[protocol.json](chair-data/protocol.json)、[execution.json](chair-data/execution.json)、[review.json](chair-data/review.json)、[study.json](chair-data/study.json)、[manifest.json](chair-data/manifest.json)分别登记方案/固定规则、真实提交、作者观察、网页数据、原件路径与12项哈希。新增13项进入网页包，总数138。前轮摄影素材未覆盖，Skill与安装包未修改。详细过程和局限见[研究说明](../chair-data-trial.md)。

## Skill驱动短片《给你留个座》（新增13项）

2026-10-22，实际应用emotion-art-direction读取入口、视频模板、安心档案与已有视频案例，再通过ChatArt Skill一次调用Seedance 2.0，任务1035011。采用`i2v / omni_reference`，两张实际参考分别为已有[椅子身份图](skill-trial/reference.png)与[窗边红椅光色材料图](skill-trial/safe.png)；不把任一参考锁为首帧。人物是本轮文字描述的虚构成年角色，无第三方人物照片。

[original.mp4](skill-film/original.mp4)保留[服务实际返回](https://files.chatartpro.com/web-video/20261022/6ad98f464e239.mp4)的原始字节：1902×1092、24fps、10.048秒、H.264/AAC、32kHz双声道，共5,943,163字节。SHA-256为`2915b267338007d877c3a5313ebfafdb9c5a294f39f907357aa5bbf78236d7fa`。没有重新编码、调色、代码动画、拼接或另配声音。请求1080p/16:9/10秒/有声；估算240积分，服务实际300，差异记录且没有自动追加生成。

[prompt.txt](skill-film/prompt.txt)为本次准确实际提交文本，[request.json](skill-film/request.json)保留去凭据请求；[brief.json](skill-film/brief.json)是原艺术意图、参数、素材角色与授权，[skill-use.json](skill-film/skill-use.json)保存实际读取文件哈希及意图转译。媒体、来源/消耗、作者观察与展示数据分别在[media.json](skill-film/media.json)、[provider-result.json](skill-film/provider-result.json)、[review.json](skill-film/review.json)、[study.json](skill-film/study.json)。[2秒](skill-film/frame-02.jpg)、[5秒](skill-film/frame-05.jpg)、[9秒](skill-film/frame-09.jpg)JPEG均直接从原片提取，作为实际定位帧；[manifest.json](skill-film/manifest.json)登记12个文件大小与SHA-256。

新增13项进入网页包，与此前138项合计151。旧片、图片原件及Skill安装包不变。实际邀请、走近与落座可见，坐稳后的结尾停留极短；没有听觉审片、独立观众评测或稳定命中率测试，不能把含音轨当作声音内容已验证。方法、原计划与实际偏差见[本次研究说明](../skill-film-trial.md)。

## 本轮研究收束与重复分析资料（新增2项）

2026-10-22，依据当前研究、实际作品及用户反馈，原创整理[核心理解与案例索引](research/working-understanding.md)和[给AI的研究复盘模板](research/revisit-template.txt)。两份文件是事后方法笔记与复用模板，分别说明Skill/助手/模型职责、情绪到视听要求的转译、直接提示词的等价输入边界、实际发现与未验证事项，以及下一次研究的六步问题。不是既有作品的历史生成指令，也没有新增媒体生成或改写历史请求。

两项按原文字节进入网页包，总数153；笔记中的素材链接使用相对路径，所引媒体、准确指令、Skill目录与49文件安装包保持原件。浏览器截图另存为研究证据，不进入素材包。

网页提供MD下载与TXT原文查看。新TXT采用UTF-8 BOM，保证缺少charset响应头时直接打开仍能显示中文；该编码处理仅用于本次复用模板。

## 一张图总结本轮理解

[情绪引导AI创作总览PNG](research/emotion-art-research-overview.png)于2026-10-22通过内置imagegen一次合成，1536×1024，2,136,062字节，无图像后期，按字节保留工具输出。内容包括源库海报能力、提示词与素材驱动的原理、21个情绪起点与已探索风格、配合例子、图片/视频/Skill探索、已有沉淀和待验证价值。

4张视觉输入分别为作者[南瓜示例](03-pumpkin-before-after.png)、研究者[红椅摄影图](skill-trial/safe.png)、[孤独返修海报](chair-data/solitude-repaired.png)与[实际视频5秒帧](skill-film/frame-05.jpg)。作者示例声明继续见[NOTICE](NOTICE.upstream.md)。生成图中的插图是概览合成，不保证为原件逐字节裁切，图内及报告均说明实际证据以原件和历史记录为准；没有新增椅子图或视频实验。

首版之后又通过内置imagegen作一次文字标注修订，明确“源库风格参照 / AI合成概览”、全部案例的概览性质及情绪标题。[第二版PNG](research/emotion-art-research-overview-v2.png)和首版保留；工具输出原件均未经过代码图像后期。

随后按用户要求，使用第二版为编辑目标，并实际提供全部三张源库作者对照原件，新增[第三版最终PNG](research/emotion-art-research-overview-v3.png)。1024×1536，温暖人物、彩珠动物、数字连接三组参照完整纳入；黑红英雄的横向“人物→伸手→数据线→标题”关系放大为画廊主要视觉。[本版准确指令](research/overview-source-examples-prompt.txt)与四项输入角色/哈希已记录。案例仍属依据原件的AI概览合成，不能将其称为原作逐字节裁切。

本图的[初版生成指令](research/overview-prompt.txt)、[标注修订指令](research/overview-revision-prompt.txt)、[输入角色与SHA-256清单](research/overview-manifest.json)随图保存。三次总览图工具调用没有新增椅子图片或视频实验。三版PNG、三份准确指令及清单共七项研究资料，现已接入网页素材包，与此前153项合计160项；其中第三版作为研究引导图，初版与第二版继续保留。既有媒体、Skill和历史提示词保持原件；此处说明打包集成状态，不代表公开部署已验证成功。

## 公开部署验证（2026-10-22）

`public-home-20261022.jpg`与`public-mobile-20261022.jpg`为GitHub Pages公开页面的真实浏览器截图，无图像后期；`deployment-verification.json`保存32个页面文件与160项素材的公网大小、SHA-256、视频范围请求及交互检查结果。三者仅为研究验证记录，不计入160项网页素材。画面内的源库示例继续按上述来源声明使用。
