# 11 种叙事系统与 24 种表达方案

来源：Scene Card Studio v0.7.0，commit `8ced16f3ebd84be0ce8e29658ffd9d080f5e72ea`。本文件为中文选择摘要；完整英文规则见 [JSON](../rules/upstream-rules.json)，许可与修改见 [NOTICE](../NOTICE.md)。每次只选一种机制与一种兼容表达。

## 叙事机制

| ID | 名称 | 组织规则 | 上游多图方式 |
| --- | --- | --- | --- |
| `cinematic-storyboard` | 电影序列 | 景别、真实光源、动作与时间关系；多图保持连续，不凭空补事件 | 逐张 |
| `memory-atlas` | 记忆地图 | 以实际地点、方向、距离和空间关系组织记忆；无依据不加路线、地名或归来故事 | 融合 |
| `family-archive` | 家庭纪事 | 以已知人物、物件和日常动作建立关系；不推断亲属、传承或年代 | 融合 |
| `minimal-editorial` | 安静静物 | 主体层级、负空间、光影和真实材料；避免无依据道具和奢华广告化 | 逐张 |
| `editorial-sequence` | 编辑节奏 | 以尺度、密度、对比和停顿组织阅读；不擅自重排用户时间线 | 逐张 |
| `field-log` | 现场日志 | 保持动作和环境语境可观察，不戏剧化重演或摆拍 | 逐张 |
| `museum-catalogue` | 博物馆图录 | 结构、尺度、接合、磨损和修复可检查；元数据只用已知内容 | 逐张 |
| `travel-journal` | 旅行日志 | 以实际路径、车站、门槛、票据和停留组织旅程；不补目的地、日期和道具 | 融合 |
| `journey-taxonomy` | 地点分类 | 在一个主场景中区分可见地形、水、植被、天气、主体和移动线索，缺项省略 | 融合 |
| `street-reportage` | 街头纪实 | 保留人数、姿态、交通与事件方向，裁切强化动作，不编造冲突和紧迫感 | 逐张 |
| `fashion-editorial` | 服装编辑 | 姿态、面料、服装结构、景别与裁切张力；保留身份、解剖、衣缝和配饰 | 逐张 |

单图始终是一张独立成片。直接使用版对多图采用逐张保守默认；需要融合时由用户明确选定或授权。

## 表达方案

| Profile | 中文名称 | 创作与失败检查 |
| --- | --- | --- |
| `source-led` | 沿用源图 | 从源图决定构图、光色和材料；不同系统有各自具体规则 |
| `rain-nocturne` | 雨夜镜头 | 合理冷环境光与暖实景光、湿面反射、自然表面；雨夜变化须授权，不滥用霓虹 |
| `quiet-window-light` | 安静窗光 | 单一可信窗光、几何阴影、非对称构图与触感；避免数字辉光和 CGI 光洁 |
| `watercolor-contour` | 摄影＋水彩地形 | 摄影锚点融入水彩地理与铅笔轮廓；材料和空间应有依据 |
| `watercolor-chronicle` | 全画面水彩 | 人物、皮肤、建筑与环境统一透明水彩和纸纹；不能留摄影脸或粘贴边缘 |
| `graphite-paper` | 石墨档案纸 | 纪实人物与石墨研究、描图纸、织物线索建立关系；避免等格拼贴和人物褐色滤镜 |
| `heritage-portrait` | 银盐手工着色 | 保持年龄、身份、衣服和姿态，细纸纹、克制银盐层次与少量着色；不换古装或伪造身世 |
| `monochrome-reportage` | 黑白纪实 | 原始明度转详细黑白和细银盐颗粒，不压黑脸部与关键暗部 |
| `dream-logic` | 单规则梦境 | 锁定身份、解剖和数量，仅执行一条授权空间变化，共用光源；避免随机漂浮道具 |
| `mineral-ink-memory` | 矿物水墨 | 墨色、矿物蓝绿与土色组织深度，保持主体、地形和方向；不加虚构山水与印章 |
| `impasto-light-study` | 厚涂光线 | 原图支持的光路主导，亮部结构厚涂、次要区域安静；避免全图等厚和数字发光 |
| `pixel-diary` | 像素日记 | 一套网格、尺度、色阶和边缘簇，保持轮廓与空间；不用 UI、摄影块和混合像素尺度 |
| `risograph-route` | 孔版路线 | 两三种源图油墨、网点、叠印和少量套印偏差，方向信息有依据；不编票据地图或贴纸板 |
| `gouache-place-study` | 水粉地点 | 哑光不透明形状群重绘可辨认地点；避免透明水彩、摄影孤岛与装裱样机 |
| `cyanotype-archive` | 蓝晒档案 | 普鲁士蓝、纸白与接触印相逻辑，保持尺度轮廓；不虚构标本、标签与档案编号 |
| `paper-relief-landscape` | 纸浮雕 | 连续纸层、统一纸厚、光源、深度和接触阴影；不做白边贴纸和分割拼块 |
| `sculpted-place-diorama` | 微缩地景 | 原地理关系重建立体体积和真实阴影；交付是模型质感图像，不是 3D 几何文件 |
| `threaded-landscape` | 纤维刺绣 | 连续织物底、统一纤维尺度，远景平织、结构刺绣、气氛针毡、局部凸起；无流苏毛线球和摄影残片 |
| `autochrome-memory` | 早期彩色 | 克制早期彩色摄影材料感，保持身份和场景，不虚构年代与服饰 |
| `pixel-ink-memory` | 像素水墨·实验 | 近景像素、远景水墨共享色板、光线和深度，不对半硬切 |
| `travel-zine` | 旅行 Zine | 一个主导节点、稀疏且有依据的路线、安静纸面和留白；不自动补票据邮票和手写字 |
| `chinese-photo-editorial` | 水墨摄影编辑 | 摄影锚点、克制墨色与无涂布纸；不自动补竹、山、印、书法或古装 |
| `chinese-ink-poetry` | 国风诗意 | 主体和实际环境保留，只让源图周边过渡成墨与纸，用户诗句独立后期排字 |
| `selective-material-relief` | 选择性浮雕 | 主体摄影、授权环境连续浅浮雕，保持光向、透视、接触和可信材质边界 |

兼容别名 `full-watercolor-memory` 指向 `watercolor-chronicle`，不另计数。

## 代码导出的兼容关系

<!-- COMPATIBILITY:START -->
| 系统 | 可用表达 |
| --- | --- |
| `cinematic-storyboard` | `source-led`、`rain-nocturne` |
| `memory-atlas` | `source-led`、`watercolor-contour`、`watercolor-chronicle`、`dream-logic`、`mineral-ink-memory`、`impasto-light-study`、`pixel-diary`、`risograph-route`、`gouache-place-study`、`paper-relief-landscape`、`sculpted-place-diorama`、`threaded-landscape`、`autochrome-memory`、`pixel-ink-memory`、`travel-zine`、`chinese-photo-editorial`、`chinese-ink-poetry`、`selective-material-relief` |
| `family-archive` | `source-led`、`graphite-paper`、`watercolor-chronicle`、`heritage-portrait`、`cyanotype-archive`、`autochrome-memory`、`threaded-landscape`、`travel-zine`、`chinese-photo-editorial`、`chinese-ink-poetry`、`selective-material-relief` |
| `minimal-editorial` | `source-led`、`quiet-window-light`、`impasto-light-study`、`chinese-photo-editorial`、`chinese-ink-poetry` |
| `editorial-sequence` | `source-led` |
| `field-log` | `source-led`、`cyanotype-archive` |
| `museum-catalogue` | `source-led`、`watercolor-chronicle`、`heritage-portrait`、`cyanotype-archive`、`chinese-photo-editorial`、`chinese-ink-poetry` |
| `travel-journal` | `source-led`、`watercolor-chronicle`、`mineral-ink-memory`、`impasto-light-study`、`pixel-diary`、`risograph-route`、`gouache-place-study`、`paper-relief-landscape`、`sculpted-place-diorama`、`threaded-landscape`、`autochrome-memory`、`travel-zine`、`chinese-photo-editorial`、`chinese-ink-poetry`、`selective-material-relief` |
| `journey-taxonomy` | `source-led`、`watercolor-chronicle`、`mineral-ink-memory`、`impasto-light-study`、`pixel-diary`、`risograph-route`、`gouache-place-study`、`paper-relief-landscape`、`sculpted-place-diorama`、`threaded-landscape`、`autochrome-memory`、`pixel-ink-memory`、`travel-zine`、`chinese-ink-poetry`、`selective-material-relief` |
| `street-reportage` | `source-led`、`monochrome-reportage`、`cyanotype-archive` |
| `fashion-editorial` | `source-led`、`dream-logic` |
<!-- COMPATIBILITY:END -->

## 共通要求

保留／变化／删除写具体属性；全介质转换保持统一，局部转换明确边界。装饰、路线、资料与类别须有实际依据，缺项省略。默认不生成可见文字，事实性元数据不编造。用材料、工艺和叙事机制描述表达，不依赖具名艺术家模仿或照搬第三方构图、配色、贴纸和标题位置。原图与成片实际对照后再判断效果。
