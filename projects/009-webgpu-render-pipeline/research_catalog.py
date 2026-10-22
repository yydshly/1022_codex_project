"""Curated capability records. Claims describe source evidence, not a runtime acceptance test."""

CATEGORIES = [
    ("pipeline", "渲染管线", "WebGPU 计算、场景组织与画面合成"),
    ("gi", "全局光照", "表面光照缓存与三维空间探针"),
    ("lightmap", "光照贴图与流送", "烘焙、质量控制和按需显存使用"),
    ("lighting", "光源、阴影与反射", "直接光、遮挡和镜面响应"),
    ("water", "海水与流体", "主场景浅水系统与独立物理水实验"),
    ("nature", "植被、地形与材质", "程序化形体、叶片透光与分层表面"),
    ("sky", "天空与大气", "物理天空、云影、雾和空气透视"),
    ("post", "镜头与后期", "稳定画面、曝光、运动与艺术调色"),
    ("tools", "诊断与研究工具", "逐层看图、定位画质问题和测量成本"),
    ("integration", "集成与使用边界", "场景接口、组件接入和复现条件"),
]

# title | visible effect | mechanism | availability | boundary | source | search anchor | scenes | example parameters
ROWS = {
"pipeline": """
WebGPU 渲染与计算|在浏览器中同时渲染场景并运行光照计算|WebGPURenderer、storage buffer 与 compute dispatch|主管线|无 WebGL 降级；还需满足程序申请的设备上限|src/shared/render/renderer.ts|requiredLimits|all|gputime=1
TSL 与 WGSL 着色器|材质、光照和计算过程可组合扩展|Three.js 节点表达式配合手写 WGSL 函数|主管线|依赖 r182 及定制补丁，跨版本迁移需检查节点行为|src/shared/gi/surfel/surfelIntegratePass.ts|wgslFn|all|
MRT 多缓冲输出|可以分别观察颜色、法线、速度和深度|一次场景通道写入多个渲染附件供后续步骤共享|主管线|每个附件增加内存与带宽成本|src/shared/render/frameGraph.ts|setMRT|all|split=normal
统一画面合成|间接光、反射、水面和后期按顺序组成最终画面|FrameGraph 组织渲染目标与节点链，变化时重建图|主管线|这是项目内部帧流程，未提供通用引擎插件契约|src/shared/render/frameGraph.ts|class FrameGraph|all|
静态与动态几何分离|移动物体可参与部分遮挡和追踪|分别管理静态 BVH 与动态几何加速数据|主管线|实时探针更新当前以静态几何为主，不能概括为任意动态 GI|src/shared/gi/surfel/dynamicBvh.ts|export |cornell,corridor-lights|
实例化绘制与运动向量|树、花和建筑细节重复出现时降低对象组织成本|InstancedMesh、MultiInstances 与上一帧变换记录|按场景|正确 TAA 还依赖定制 Three.js 的实例速度修复|src/shared/fiber/MultiInstances.tsx|export |midsee-village,forest|
水面独立叠加通道|水可读取已画好的水底颜色与深度|Overlay 层在主体光照合成后绘制，屏幕纹理供水材质读取|按场景|水的光学着色与主体 GI 存在专门的排除和接入规则|src/shared/render/frameGraph.ts|onScreenTextures|beach,midsee-village|
线性光照与统一输出转换|降低颜色重复转换和重复曝光造成的偏差|材质色彩空间、HDR 计算和末端 tone mapping 分开处理|主管线|参考图与实测必须统一曝光、调色和输出转换|src/shared/render/outputStage.ts|export |all|lookOutput=linear
""",
"gi": """
Surfel 表面光照采样|阴影区域仍可获得环境与反弹光的层次|把表面离散为带位置、法线和辐照信息的小型采样单元|主管线|采样密度和射线数量会影响启动时间与细节质量|src/shared/gi/bake/lightmapSurfels.ts|export |all|sample=0.1
基于 BVH 的光线求交|采样光线能找到墙体、地面和其他表面|在 WebGPU 计算中遍历空间层级，避免逐个测试所有三角形|主管线|计算着色器追踪不代表已接入硬件 RT 管线|src/shared/gi/surfel/sceneBvh.ts|export |all|
间接光迭代与缓存|逐步累积表面之间的反弹照明|Surfel 积分器读取场景光源和已有辐照缓存，迭代更新|主管线|依赖近似缓存及收敛过程，不是逐像素无偏路径追踪|src/shared/gi/surfel/surfelIntegratePass.ts|export |cornell|iters=64&rays=32
三维光照探针体积|没有光照 UV 的物体也能获得位置相关的环境补光|规则空间网格保存方向辐照，着色时对周边探针加权|主管线|低密度探针不能替代所有表面细节；接收对象由材质规则选择|src/shared/gi/probes/probeVolume.ts|class ProbeVolume|all|probeSpacing=2
DDGI 风格方向编码|物体朝向不同，接收的间接光也不同|探针以八面体贴图保存方向辐照及距离矩|主管线|借鉴 DDGI 存储与采样，不等同于完整 RTXGI 产品|src/shared/gi/probes/probeVolume.ts|DDGI storage|cornell,corridor|
探针遮挡权重与偏移|减少隔着墙取得错误亮光|距离均值、二阶矩、Chebyshev 权重和法线/视线偏移|主管线|属于漏光抑制近似；参数过大也会改变细节|src/shared/gi/probes/probeVolume.ts|chebyshev|corridor,leak-room|probeVisibility=1
探针分类与重定位|降低落在实体内部的无效采样影响|追踪周边几何，为探针设置有效状态和位移|主管线|复杂薄壁与边界仍需用漏光实验验证|src/shared/gi/probes/probeClassify.ts|export |corridor,leak-room|probeClassify=1
室内外探针分层|室内物体优先使用合适的室内光照|根据室内容积标记探针和接收点的层掩码|按场景|需场景提供 interiorVolumes，不会自动理解任意建筑室内|src/shared/gi/probes/probeLayers.ts|export |corridor,corridor-lights|probeLayers=1
探针渐进实时更新|太阳改变后，探针补光可逐步跟随|保留探针方向 Surfel，按每帧射线预算刷新|可选|probeLive 默认关闭；响应以秒收敛；不自动重算静态 Lightmap|src/shared/gi/probes/probeLive.ts|class ProbeLiveUpdate|sky,cornell|probeLive=1&probeRayBudget=8192
实时 Surfel GI 路径|研究按当前视角持续更新的间接光|每帧分配、积分并解析活动 Surfel，和静态烘焙路径并存|历史路径|surfelGi 默认关闭；pipeline=legacy 是另一条旧管线入口|src/features/render-pipeline/index.ts|url.flag('surfelGi'|cornell|surfelGi=1
""",
"lightmap": """
自动分配光照 UV 与图表|建筑表面能对应到自己的光照贴图区域|按几何和表面特征拆 chart、打包到 atlas 页|主管线|不等于支持所有导入模型；退化、复杂和实例化几何需检查|src/shared/gi/bake/lightmapUv.ts|export |all|split=lightmap
按世界尺寸控制光照密度|近看墙面和阴影时可获得更细的照明纹理|以米/texel 指定目标密度，场景大时增加 atlas 页|主管线|0.03 比 0.1 更细，内存和烘焙代价也更高|src/features/render-pipeline/staticLight.ts|DEFAULT_METRES_PER_TEXEL|corridor,midsee-village|lmDensity=0.05
稀疏采样与可见性传播|用较少 Surfel 覆盖更多贴图像素|按世界采样步距建点，再沿追踪得到的链接传播|主管线|跨表面传播可能产生误差，项目配有漏光定位工具|src/shared/gi/bake/filterLinks.ts|export |corridor,leak-room|sample=0.1&filterLinks=1
表面约束的填洞与去噪|降低烘焙噪点、空白与薄壁漏光|按表面归属、法线、可见性链接限制滤波和填充|主管线|精度仍受射线数量和几何分辨率影响|src/shared/gi/bake/holeFill.ts|export |leak-room|leak=1
Chart 边缘扩张与隔离|降低 UV 接缝处的暗线和邻区串光|给每个图表单独填充边界 texel|主管线|它处理纹理过滤边界，不会修复错误几何或错误 UV|src/shared/gi/bake/chartPadding.ts|export |lod-scale|
烘焙结果持久化|重复打开场景时可跳过已有光照积分|二进制缓存与配套清单保存 atlas、Surfel 和探针|主管线|写入流程依赖开发服务插件；不能假设静态托管可直接回写|src/shared/gi/bake/persistedBake.ts|export |all|bakeCache=0
光照来源与陈旧状态检查|修改环境后能知道缓存是否仍匹配|记录环境、太阳和传输设置的 provenance，再比较当前条件|主管线|提示过期不会自动完成全场景重烘焙|src/shared/gi/bake/lightingProvenance.ts|export |sky|bakeCache=0
每个 Chart 独立 Mip 金字塔|远处读取较粗光照，近处保留细节|逐 chart 降采样并切成带边框的 tile|主管线|独立金字塔用于隔离不同表面；不是完整材质虚拟纹理系统|src/shared/gi/lod/chartPyramids.ts|export |lod-scale|vtTile=64
按可见需求驻留光照 Tile|有限 GPU 工作池服务当前镜头需要的光照细节|反馈通道收集请求，页表指向驻留页或同 chart 粗级 tail|主管线|仍需保留完整数据的 CPU 内存，不是网络按需下载|src/shared/gi/lod/tileResidency.ts|export |lod-scale,midsee-village|vtPool=16
CPU 到 GPU 的分块上传|镜头变化时逐步送入需要的光照页|当前代码将半精度 tile 存在 tab 内存，通过 writeTexture 上传|主管线|旧虚拟纹理文档还写着全量 GPU store，当前代码已前进；不承诺总内存恒定|src/shared/gi/lod/tilePool.ts|device.queue.writeTexture|lod-scale|vtUploadKiB=1024
""",
"lighting": """
太阳方向与强度控制|调整光照朝向、阴影方向与明暗|DirectionalLight 与太阳方位角、高度角控制|主管线|静态间接光仍保留烘焙时条件，变化后应检查缓存状态|src/features/render-pipeline/sun.ts|function setupSun|all|sunAz=-60&sunEl=10
太阳能量从环境图估计|HDR 天空与直接太阳光更协调|从环境贴图提取太阳方向/能量供解析光源使用|按场景|受环境图内容和场景主机配置影响|src/features/lighting-pipeline/sunFromEnvironment.ts|export |beach,forest|sun=2
接触硬化软阴影|遮挡物附近阴影较硬，离开后更柔和|PCSS 风格遮挡搜索与半影滤波，太阳视直径参与计算|主管线|基于阴影贴图的近似；受分辨率和滤波预算限制|src/shared/render/softSunShadow.ts|U_SUN_ANGULAR_DIAMETER_DEG|all|shadowFilter=soft&sunDisc=0.533
接收面修正与阴影范围适配|减少斜面条纹与阴影精度浪费|接收面导数补偿和相机范围拟合|可选|shadowFit 默认关闭；偏移需要按场景验证|src/features/render-pipeline/sun.ts|shadowFit.enabled|all|shadowFit=1&shadowFilter=receiverPlane
移动彩色光源与阴影|走廊里彩灯移动，照明和阴影随之变化|专门场景逐帧更新多个解析光源|按场景|演示动态直接光，不代表所有静态反弹光都实时更新|src/widgets/world/corridorLightsScene.ts|export |corridor-lights|scene=corridor-lights&lightMotion=0
短射线接触遮蔽|墙脚、椅脚和物体接触更有重量感|对近距离几何发射短光线，只调制间接光|可选|默认关闭；不能当作完整远距离阴影|src/shared/gi/contact/contactOcclusionPass.ts|DEFAULT_CONTACT_SETTINGS|corridor|contact=1
场景射线反射|低粗糙度表面可反映屏幕外几何|根据 G-buffer 方向追踪静态/动态 BVH，并对命中点着色|主管线|有最大粗糙度、射线节点预算和更新间隔|src/shared/gi/reflect/reflectionPass.ts|DEFAULT_REFLECTION_SETTINGS|cornell,sky|reflections=0
反射降噪与粗糙表面补充|降低反射噪点并给较粗表面环境响应|空间降噪，以及光照探针方向采样作为粗糙反射补充|主管线|探针补充是近似，不等同于逐像素精确镜面反射|src/features/render-pipeline/index.ts|probeSpecular|cornell|probeSpecular=0
反射缓存与局部代理体积|以分时更新的反射探针研究可控成本反射|捕获、过滤、发布、版本状态和盒/球代理体积|可选|通过 reflections=cached 选择；当前默认仍走另一条反射路径|src/shared/gi/reflect/cache/reflectionCache.ts|export |sky,cornell|reflections=cached
""",
"water": """
浅水高度与流速求解|浪接近岸边和障碍物时发生变化|二维浅水方程在高度/流速网格上推进|按场景|高度场流体，不是任意三维体积流体或完整海洋数值模型|src/entities/water/shallowWater.ts|export |beach,midsee-village|
水底地形与障碍物采样|水深和岸线跟随底部及障碍形状|将水底与障碍几何烘焙为 bathymetry 高度数据|按场景|精度受格点尺寸与几何覆盖限制|src/entities/water/bathymetry.ts|export |beach,midsee-village|
水面折射与水下成像|透过水面看见位置偏移的水底|主场景重建深度和折射路径，实验室进一步追踪水下几何|按场景|主场景与实验室算法不同，不能用实验室能力概括所有水面|src/entities/water/index.ts|Snell refraction|beach,midsee-village|
随路径长度的吸收与散射|浅水透明、深水更有颜色和厚度|逐 RGB 通道 Beer–Lambert 衰减与散射项|按场景|颜色由光学系数、路径和底色共同决定|src/entities/water/index.ts|Beer|beach,midsee-village|
Fresnel 天空反射与太阳闪光|掠视时更像镜子，顺光看到水面亮点|Fresnel 混合天空与透射，结合太阳 GGX 响应|按场景|主场景天空反射与实验室的几何反射需要分别理解|src/entities/water/index.ts|fresnel|beach,midsee-village|
水底焦散图案|水下沙地出现流动的明亮纹理|主水面材质生成并调制焦散近似|按场景|主场景焦散是视觉近似，不能宣称全物理光子传输|src/entities/water/index.ts|caustic|beach,midsee-village|
持续泡沫场与湿沙|泡沫随水流漂移并逐渐消散，岸边留下湿润痕迹|Ping-pong 纹理保存泡沫、湿度和撞击源|按场景|需要多帧状态推进；冻结模拟后不再按真实时间演变|src/entities/water/index.ts|persistent foam field|beach,midsee-village|
浪花与喷溅粒子|岸线或撞击处出现抛出的细小水滴|根据水面状态和泡沫源驱动喷溅粒子|按场景|视觉粒子表现，不是每滴水都参与完整流体求解|src/entities/water/spray.ts|export |beach,midsee-village|spray=0
独立 Worker 水模拟|重水模拟可从页面主线程移走|Worker 使用自己的 WebGPU device，异步传回状态|按场景|线程与 GPU 数据传递仍有开销，需要目标设备实测|src/entities/water/simHost.ts|export |beach,midsee-village|
漂浮球交互样例|球会随局部水高与斜率浮动|独立 Worker 计算示例球受力，主线程应用姿态|按场景|是特定物体样例，不能视为通用刚体物理引擎|src/entities/ball/index.ts|export |beach|
风浪频谱与 FFT 微细节|独立水实验室里可观察多尺度海面起伏|方向频谱与波分量控制几何，逆 FFT 产生细尺度表面场|实验室|通过 labs/water 的 physicalWater 路径接入，主场景仍使用另一套水入口|src/entities/water/physicalWater.ts|new OceanDetail|water-ocean|wind=8
几何反射与波面追踪|独立实验中水面可反射测试物体|平面反射、波面反射通道和表面射线求交共同工作|实验室|代价与近似需要单独验证；不能推断所有主场景已使用|src/entities/water/physicalWater.ts|WaveReflectionPass|water-pool,water-ocean|
水体体积光与光学诊断|实验室可单独查看水下散射与光线路径|水体射线步进、表面交点和多种诊断视图|实验室|属于独立光学研究模块，未完成跨设备验收|src/entities/water/volumeLight.ts|waterSolarScatter|water-pool|waterInspect=1
""",
"nature": """
叶片生化光学|不同叶片具有不同反射色与透射色|PROSPECT 风格板层模型，把色素/结构参数转换为光谱再转 RGB|按场景|是渲染模型实现，未完成植物实验数据拟合验证|src/entities/foliage/leafOptics.ts|function leafOptics|beach|
薄叶透光与表面反光|逆光时叶片发亮，正面保留表面光泽|薄叶 BSDF、方向透射和 GGX 角质层响应|按场景|屏幕合成、光线命中和叶材质的透射路径并不完全相同|src/shared/render/foliage/leafMaterial.ts|export |beach,forest|
程序化叶脉与微表面|近看叶片有脉络凹凸与光泽差异|在叶片局部空间生成表面纹理和光学变化|按场景|细节表达取决于相机距离、纹理分辨率和光照|src/entities/foliage/leafSurface.ts|export |beach|
程序化棕榈与树干|形成叶冠、环状叶痕、裂缝和风化细节|几何构建结合统一高度场导出的颜色、法线与粗糙度|按场景|形体是程序化资产，不是通用植物扫描或建模编辑器|src/entities/palm/trunkSurface.ts|export |beach|
针叶树与灌木生成|森林里可布置多种树形和灌木层次|ez-tree、分枝生长、针束和实例化几何|按场景|不同植物走不同生成模块，参数并非统一编辑器|src/entities/conifer/index.ts|export |forest|
风动植被与顶点运动|叶片随风摆动，TAA 可跟随形变|顶点位移与前后帧运动记录组合|按场景|自定义形变必须同步速度，否则可能出现拖影和闪烁|src/shared/render/vertexMotion.ts|export |beach,forest|
多层沙地与湿润过渡|干沙、湿沙、贝壳和风纹自然交替|按地形条件混合贴图、法线、粗糙度和层间细节|按场景|部分贴图来自上游资源，复用需逐项确认素材权利|src/entities/island/sandMaterial.ts|export |beach|
抗重复地形表面采样|大面积地面降低明显的平铺重复|分层表面、分块噪声与变化采样|按场景|属于材质采样方法，不包含完整地形编辑与植被散布工具|src/shared/render/terrain/layerSampler.ts|export |beach,forest|
自适应地形与程序化岩石|森林与海岛有起伏、岩壁、石块和溪流|高度场、局部自适应网格和程序化岩石构建|按场景|场景专用的建模代码，不是通用开放世界流送系统|src/entities/grove/adaptiveMesh.ts|export |forest,beach|
村庄建筑与陈设组件|台地房屋、钟楼、咖啡馆、船和植物可组合成场景|多个 React 预制组件共享材质和实例化几何|按场景|村庄标注开发中；组件运行还依赖未打包的 R3F 定制源码|src/entities/village/VillagePrefab.tsx|export |midsee-village|
""",
"sky": """
物理大气与天空 LUT|天空随太阳高度和观察高度改变颜色|计算透射、多次散射和天空视图查找表|按场景|默认是否开启由场景是否提供 sky 决定|src/shared/render/sky/atmosphereLuts.ts|export |sky|scene=sky
Rayleigh 与 Mie 散射|出现蓝天、暖色低太阳和近太阳泛白|空气与气溶胶散射系数、相函数和光线积分|按场景|参数化地球大气模型，未宣称天文或气象计算精度|src/shared/render/sky/scatteringMarch.ts|export |sky|sunEl=2
空气透视|远处物体对比减弱并向天空颜色融合|沿视线估算空气透射与入射散射|按场景|效果强度可以艺术放大；aerialScale 不是实际距离测量|src/shared/render/sky/aerialPerspective.ts|export |sky|aerialScale=400
体积云与云层光照|能看到厚薄不同、具有内部明暗的云|程序化密度、射线步进和云层光照采样|按场景|属于有限云层模型，分辨率和步数影响细节与耗时|src/shared/render/sky/cloudLayer.ts|export |sky|cloudCoverage=0.55
移动云影|地面与场景表面随云移动出现遮光变化|云密度生成太阳透射图，作用于直接光|按场景|烘焙的静态间接光不会跟每一帧云影完整重算|src/shared/render/sky/cloudShadowMap.ts|export |sky|clouds=1
天空作为环境照明与反射来源|天空变化能传递到环境反射|生成天空环境纹理并接入渲染与烘焙来源|按场景|需要更新静态间接光时仍须明确发起重烘焙|src/shared/render/sky/skyEnvironment.ts|export |sky|skyEnvironment=1
Froxel 体积雾|光穿过有密度变化的空气，远景产生空间层次|视锥体素保存散射/透射，沿视线合成并做时间积累|按场景|不同场景可默认关闭；不是实体烟火流体模拟|src/shared/render/atmosphere/volumetricFog.ts|export |beach,forest|fog=1
""",
"post": """
TAA 时间抗锯齿|减少几何边缘、植被和高光的闪烁|相机抖动、速度重投影、历史裁剪与累积|主管线|依赖准确运动向量；快速运动和遮挡变化仍有拖影风险|src/shared/render/temporalAA.ts|class TemporalAANode|all|aa=taa
FXAA 与关闭抗锯齿对照|可对比单帧平滑与原始像素边缘|在 TAA、FXAA 和 none 三种模式间选择|可选|用于成本/画质对照，不承诺每种模式质量一致|src/shared/render/frameGraph.ts|type Antialiasing|all|aa=fxaa
自动曝光与手动曝光|从暗处看向亮处时逐步适应亮度|测光、时间适应、手动曝光与曝光补偿分开控制|主管线|截图比较需等适应稳定或固定曝光|src/shared/render/exposure.ts|DEFAULT_EXPOSURE|all|exposure=1&exposureEV=-1
艺术 Look 调色|控制对比、饱和度、暗部和色彩平衡|在正确阶段应用艺术调整，部分参数单独作用于间接光|主管线|美术增益会改变物理响应；并非所有旋钮都是末端后期|src/shared/render/look.ts|class ArtisticLook|all|look=0&indirectEV=1
Neutral、AgX 与线性输出|同一 HDR 场景可采用不同高光压缩方式|选择末端输出转换，避免重复 tone mapping|主管线|线性输出主要用于诊断，不代表可直接和显示图比较|src/shared/render/look.ts|TONE_MAPPING|all|lookOutput=agx
镜头眩光与胶片颗粒|高亮向邻域扩散，画面带少量颗粒质感|眩光扩散合成，tone mapping 后叠加显示空间噪声|按场景|截图比较应关闭颗粒；眩光不是完整镜头光学仿真|src/features/render-pipeline/postStages.ts|class PostStages|all|glare=0&grain=0
速度驱动运动模糊|相机或物体运动时出现随方向的拖曳|根据运动向量、快门角度和积分时间采样|可选|默认关闭；开启不等于自动得到准确摄影曝光|src/shared/render/motionBlur.ts|DEFAULT_MOTION_BLUR|all|motionBlur=1&shutter=0.5
摄影机与镜头预设|不同传感器与焦距改变取景范围|使用 ALEXA、VENICE、IMAX 等参数预设设置 FOV 和快门|可选|预设不是认证相机模拟；代码没有完整景深、镜片像差与传感器仿真|src/features/render-pipeline/cineCamera.ts|export |midsee-village|cine=alexa35-32
""",
"tools": """
左右分屏查看中间层|直接对照最终画面和光照/法线等缓冲|SplitView 在同一视角输出所选中间结果|可选|分屏是诊断结果，不是不同渲染引擎的画质排名|src/shared/render/frameGraph.ts|SplitView|all|split=baked
漏光阶段追踪|定位烘焙在哪一步把黑处变亮|保存原始、去噪、填洞、padding 和发布阶段的数据|可选|leak=1 会改变缓存与捕获流程，应与基线分开测量|src/shared/gi/bake/leakStages.ts|export |leak-room,corridor|leak=1&split=leak
封闭房间与毫米级开缝标尺|用本应全黑的室内检查漏光，再打开真实缝隙|专门几何夹具和 gap 参数建立可解释参照|按场景|几何标尺是测试场景，仍需检查追踪和采样设置|src/widgets/world/leakRoomScene.ts|export |leak-room|scene=leak-room&gap=1
光照 Tile 驻留实验室|同时看场景与实际 GPU 光照工作池|LOD lab 显示 tile、mip、占用和相关参数|可选|这是光照缓存调试，不是通用模型 LOD 预览器|src/widgets/lod-lab/index.ts|export |lod-scale,midsee-village|lodLab=1
GPU 通道计时与绘制统计|知道时间花在何处、哪些对象被重复绘制|可选 timestamp queries、每通道审计和 draw count hooks|可选|计时本身有开销；不同 CPU/GPU 列不能混当总帧时间|src/features/render-pipeline/audit.ts|export |all|gputime=1
CPU 帧循环与启动阶段诊断|区分构建场景、烘焙、编译和首帧瓶颈|bootStage、动画循环计时、作者的启动检查脚本|可选|作者历史数据不直接代表当前机器或发布构建|src/shared/ui/bootProgress.ts|export |midsee-village|
可重复相机与冻结画面|相同机位比较参数前后的差别|场景相机预设、still 参数与截图脚本|可选|仍需关闭颗粒、固定曝光并处理 TAA 收敛|src/app/home/catalog.ts|still=1|all|still=1&grain=0&aa=none
浏览器自动检查脚本|为反射、TAA、软阴影和水模拟提供回归入口|Playwright 打开参数化场景、读取诊断钩子并截图比较|可选|脚本存在不表示本次已全部运行，部分脚本引用缺失资源|scripts/check-water-sim.mjs|import |water-pool|
GUI 设置与研究配置|保存每个场景的参数组合，恢复研究视角|lil-gui 控制面板配合开发服务器设置插件|按场景|增加查询参数可能绕过保存的配置，比较前须统一来源|src/app/guiSettings.ts|export |all|hud=0
渲染技术阅读页|比较 RDR2、Lumen 等管线的取舍|独立静态说明页组织作者技术研究|独立资料|是研究资料，提及的商业引擎能力不等于本项目已实现|src/widgets/pipeline/PipelinePage.tsx|export |pipeline-doc|
""",
"integration": """
可替换场景主机接口|把不同场景插入同一套光照与渲染流程|SceneHost 交付 scene、camera、sun、更新函数和可选设置|主管线|接入新场景仍需标记静态性、光照接收和室内容积|src/features/render-pipeline/host.ts|SceneHost|all|
React Three Fiber 场景组件|以组件描述建筑、岩石和其他预制体|自定义 scene root、StaticGroup 和 MultiInstances 连接 WebGPU 场景|集成待补|定制 R3F vendor 和部分 React 依赖未随固定版本完整提交|src/shared/fiber/sceneRoot.tsx|export |midsee-village,fiber-lab|
Three.js 定制修复说明|改善实例 TAA 稳定性和部分 CPU 提交开销|r182 分支回移运动向量修复，并维护影子材质等补丁|集成待补|文档记录了依赖，但 vendor/three 不在本库树中|docs/lessons-three-fork.md|## What exists|all|
参数化场景与相机接入|同一应用可以选择不同场景与观察配置|URL 查询选择主场景，各场景读取自己的 cam 等参数|按场景|不同场景支持的参数不同；独立实验室路径仍需补入口|src/app/main.ts|params.get('scene')|all|scene=beach
""",
}

SCENES = [
    {"id":"cornell","title":"Cornell Box","kind":"参考场景","route":"/?hud=1","focus":"彩色墙面反弹光、移动物体、探针与烘焙分层","cameras":[],"source":"src/widgets/world/cornellScene.ts","note":"未指定 scene 时的默认参考场景。","checks":"先用 split=baked 看反弹光，再对比 surfelGi=1。"},
    {"id":"beach","title":"热带海滩","kind":"主场景","route":"/?scene=beach","focus":"浅水、沙地、棕榈、树皮、叶片透光、浪花","cameras":["shore","rocks","water","surf","eye","leaves","trunkLit","shrub","sunward","van"],"source":"src/widgets/world/beachScene.ts","note":"已接入真实演示，使用 entities/water/index.ts 主场景水实现；固定源码缺少房车 GLB，展示设 van=0。","checks":"分别看 leaves、trunkLit 和 water，避免仅用远景判断材质。"},
    {"id":"forest","title":"针叶林与溪流","kind":"主场景","route":"/?scene=forest","focus":"自适应地形、程序化树木、群落阴影与溪流","cameras":["hero","wide","trail","stream","ledge","canopy","rim"],"source":"src/widgets/world/forestScene.ts","note":"已接入真实演示，保留近远景植被；溪流为不透明波纹材质，区别于海滩浅水模拟。","checks":"对比 canopy、stream 与 rim，记录 TAA 是否闪烁。"},
    {"id":"corridor","title":"封闭走廊","kind":"参考场景","route":"/?scene=corridor","focus":"室内外探针分层、墙体漏光、地面与长椅接触","cameras":["hero","wide","bench","panels","floor","deep"],"source":"src/widgets/world/corridorScene.ts","note":"可用 lmDensity=0.1 与 0.03 观察光照密度差异。","checks":"从 floor/bench 检查接触处，再用 leak=1 追踪阶段。"},
    {"id":"corridor-lights","title":"走廊动态彩灯","kind":"专用实验","route":"/?scene=corridor-lights","focus":"三个移动彩灯、实时直接光和阴影","cameras":["hero","bench","deep"],"source":"src/widgets/world/corridorLightsScene.ts","note":"静态照明设置与普通走廊不同，不能把两场景当作单参数 A/B。","checks":"暂停 lightMotion=0，分别控制每个灯的启用和强度。"},
    {"id":"midsee-village","title":"地中海村庄","kind":"开发中场景","route":"/?scene=midsee-village","focus":"台地建筑、钟楼、咖啡馆、海湾、船和植物","cameras":["front","side","rear","quay","roofs"],"source":"src/widgets/world/midseeVillageScene.tsx","note":"作者标注开发中；本研究已将该完整场景接入上方真实演示，历史截图另行标明。","checks":"先选 front，再查看 quay/roofs；关注启动时间与光照页占用。"},
    {"id":"village-light","title":"单栋房屋轻量夹具","kind":"专用实验","route":"/?scene=village-light","focus":"同一建筑材质与光照问题的低成本定位","cameras":[],"source":"src/widgets/world/villageLightScene.tsx","note":"降低场景内容量，适合区分材质编译与全村几何成本。","checks":"配合 lodLab=1 和 bakedOnly=1 定位贴图、页表和补光。"},
    {"id":"sky","title":"天空、大气与云","kind":"专用实验","route":"/?scene=sky&cam=objects","focus":"午间、黄金时刻、落日、暮光、云影与高空视角","cameras":["objects","sunward","zenith","horizon"],"source":"src/widgets/world/skyLabScene.tsx","note":"太阳与反射可即时变化；静态间接光使用 GUI 的 bake light from this sky 更新。","checks":"对比 sunEl=45、10、2、-4；分别关闭 clouds 与 aerial。"},
    {"id":"lod-scale","title":"光照 LOD 比例尺","kind":"专用实验","route":"/?scene=lod-scale&cam=overview","focus":"格栅细影、不同尺寸房屋、长墙、mip 与 tile 接缝","cameras":["overview","eye","grazing","glow","pergola","ladder","wall","far"],"source":"src/widgets/world/lodScaleScene.tsx","note":"这是光照纹理 LOD 夹具，不是通用几何 LOD 系统。","checks":"lod=0 对比虚拟纹理，再用 vtPool=4 或 vtEvict=all 压缩工作池。"},
    {"id":"leak-room","title":"全封闭漏光房间","kind":"专用实验","route":"/?scene=leak-room&cam=contact","focus":"封闭室内应为零光照，开缝后应恢复真实光线","cameras":["contact","inside","floor","outside"],"source":"src/widgets/world/leakRoomScene.ts","note":"gap 的单位是毫米；房间正确全黑不意味着贴图缺失。","checks":"比较 gap=0、1、20；使用 leak=1 逐阶段核对。"},
    {"id":"water-pool","title":"物理水实验室 · 水池","kind":"独立实验室","route":"/labs/water/?scene=pool","focus":"折射、反射、焦散、体积散射与测试物体","cameras":[],"source":"src/labs/water/main.ts","note":"调用 physicalWater.ts；catalog 声明了此路径，但固定树未找到对应 HTML 入口或路径接线，需先补接。","checks":"补齐入口后用红柱、水下石块和水上球观察光学路径。"},
    {"id":"water-ocean","title":"物理水实验室 · 海面","kind":"独立实验室","route":"/labs/water/?scene=ocean","focus":"风浪频谱、FFT 微细节、较大振幅水面","cameras":[],"source":"src/labs/water/main.ts","note":"海面有独立风速、水深和波幅设置；固定树未找到该实验室的 HTML 接线。","checks":"补接入口后逐项改变 wind，结合 FFT/反射诊断看响应。"},
    {"id":"fiber-lab","title":"React Three Fiber 实验室","kind":"独立实验室","route":"/labs/fiber/","focus":"定制 R3F、React 19 与 WebGPU 场景接入","cameras":[],"source":"src/labs/fiber/main.tsx","note":"固定版本缺少 vendor、部分包声明和对应 HTML 入口；此处为作者声明路径。","checks":"补齐入口、vendor/react-three-fiber 和 React 依赖后再启动。"},
    {"id":"pipeline-doc","title":"渲染管线技术阅读页","kind":"独立资料","route":"/pipeline","focus":"RDR2、Lumen、Alan Wake、Cyberpunk 的研究与本项目设计","cameras":[],"source":"src/widgets/pipeline/PipelinePage.tsx","note":"有说明组件但未找到 /pipeline 接线；商业引擎技术讨论不自动计入本项目实现。","checks":"先补 src/app/pipeline.tsx 的页面入口，再分清技术比较与实际实现。"},
]

PIPELINE = [
    {"step":"01","title":"构建与标记场景","text":"几何、材质、相机、太阳、静态性与室内容积组成 SceneHost。"},
    {"step":"02","title":"准备光照缓存","text":"分配光照 UV、构建 BVH；读取已有烘焙，或采样 Surfel 与探针后保存。"},
    {"step":"03","title":"读取表面与空间光照","text":"静态 chart 读按需驻留的 Lightmap；未使用 chart 的接收对象从空间探针取得补光。"},
    {"step":"04","title":"更新实时通道","text":"更新直接光、阴影、动态几何、反射与需要的云影；可选地渐进刷新探针。"},
    {"step":"05","title":"水面、空气与合成","text":"使用主体颜色/深度绘制水，按配置加入空气透视与体积雾。实际顺序由 FrameGraph 管理。"},
    {"step":"06","title":"稳定与输出画面","text":"抗锯齿、可选运动模糊、曝光、艺术 Look、眩光、输出转换与颗粒。"},
]

LIMITATIONS = [
    {"title":"静态间接光不会自动跟随一切变化","text":"默认是预计算 Lightmap 与探针；probeLive 和 surfelGi 默认关闭。太阳、天空、建筑变化后需检查缓存并按需重烘焙。","severity":"核心取舍"},
    {"title":"主场景水与物理水实验室是两条实现","text":"海滩/村庄导入 water/index.ts；labs/water 导入 physicalWater.ts。FFT、几何波面反射和体积光应按接入点单独描述。","severity":"能力范围"},
    {"title":"WebGPU 可用仍不足以保证启动","text":"渲染器申请每阶段 14 个 storage buffer、1024 线程工作组等上限，并明确拒绝 WebGL 降级；目标设备须逐项验证。","severity":"设备条件"},
    {"title":"原始缺失依赖需按固定版本准备","text":"原始快照未入库定制 Three.js/R3F，且缺 React 等直接依赖。本研究已用固定 fork 与锁文件跑通 Cornell Box、完整村庄、海滩与森林；其他场景和独立实验室仍需各自验证。","severity":"复现条件"},
    {"title":"声明的实验室路径尚缺页面接线","text":"固定树只有主应用 index.html，未找到 labs/water、labs/fiber 和 /pipeline 对应 HTML 或路由装配。源模块存在，但目录里的路径不能当作已经跑通的入口。","severity":"入口完整性"},
    {"title":"没有仓库级许可证与完整素材授权清单","text":"GitHub license 返回 null，固定树未发现 LICENSE/COPYING；本研究保存来源与署名，避免把公开源码当作已获自由商用授权。","severity":"来源记录"},
    {"title":"作者目标与历史数字不是本次测量","text":"120 FPS 是文档中的设计目标；另有 1600×900、约 60 FPS 和分钟级冷启动的历史记录。没有统一硬件基线，当前不作性能保证。","severity":"证据范围"},
    {"title":"旧文档会落后于最新代码","text":"虚拟纹理说明仍写全量 GPU store，当前 tilePool 已把 tile 存在 CPU 并分块上传。研究以固定代码和接入路径为准。","severity":"版本差异"},
    {"title":"完整引擎能力仍需另建","text":"未找到可交付的统一关卡编辑、通用刚体物理、联网多人、动画资产管线、任意资产自动导入和跨设备验收；不能由已有示例推导出这些能力。","severity":"产品边界"},
]
