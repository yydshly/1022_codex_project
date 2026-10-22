# 能力清单

本清单把固定版本分解为 **89 项研究条目、10 类能力**。计数是本研究的信息组织方式，不是上游官方功能数量。

每项均核对源码存在与接入条件；现已运行 Cornell Box、完整村庄、海滩与森林的指定主管线配置，仍不能据此声明全部能力、画质或性能已验收。`主管线` 表示主路径有接入；`按场景` 表示依赖场景配置；`可选` 需启用；`实验室` 为独立实现；`历史路径` 与 `集成待补` 不应作为默认交付能力。

[交互检索](web/index.html#capabilities) · [场景地图](SCENES.md) · [技术原理](ARCHITECTURE.md) · [全部参数定位](PARAMETERS.md)

## 渲染管线（8 项）

WebGPU 计算、场景组织与画面合成

### pipeline-01 · WebGPU 渲染与计算

- **画面或使用效果**：在浏览器中同时渲染场景并运行光照计算。
- **原理**：WebGPURenderer、storage buffer 与 compute dispatch。
- **接入状态**：主管线；**边界**：无 WebGL 降级；还需满足程序申请的设备上限。
- **适用入口**：all。
- **源码证据**：[src/shared/render/renderer.ts:63](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/renderer.ts#L63)。
- **参数示例**：`?gputime=1`（需接在正确场景路径后，不会在本研究页执行）。

### pipeline-02 · TSL 与 WGSL 着色器

- **画面或使用效果**：材质、光照和计算过程可组合扩展。
- **原理**：Three.js 节点表达式配合手写 WGSL 函数。
- **接入状态**：主管线；**边界**：依赖 r182 及定制补丁，跨版本迁移需检查节点行为。
- **适用入口**：all。
- **源码证据**：[src/shared/gi/surfel/surfelIntegratePass.ts:4](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/surfel/surfelIntegratePass.ts#L4)。

### pipeline-03 · MRT 多缓冲输出

- **画面或使用效果**：可以分别观察颜色、法线、速度和深度。
- **原理**：一次场景通道写入多个渲染附件供后续步骤共享。
- **接入状态**：主管线；**边界**：每个附件增加内存与带宽成本。
- **适用入口**：all。
- **源码证据**：[src/shared/render/frameGraph.ts:192](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/frameGraph.ts#L192)。
- **参数示例**：`?split=normal`（需接在正确场景路径后，不会在本研究页执行）。

### pipeline-04 · 统一画面合成

- **画面或使用效果**：间接光、反射、水面和后期按顺序组成最终画面。
- **原理**：FrameGraph 组织渲染目标与节点链，变化时重建图。
- **接入状态**：主管线；**边界**：这是项目内部帧流程，未提供通用引擎插件契约。
- **适用入口**：all。
- **源码证据**：[src/shared/render/frameGraph.ts:99](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/frameGraph.ts#L99)。

### pipeline-05 · 静态与动态几何分离

- **画面或使用效果**：移动物体可参与部分遮挡和追踪。
- **原理**：分别管理静态 BVH 与动态几何加速数据。
- **接入状态**：主管线；**边界**：实时探针更新当前以静态几何为主，不能概括为任意动态 GI。
- **适用入口**：cornell, corridor-lights。
- **源码证据**：[src/shared/gi/surfel/dynamicBvh.ts:30](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/surfel/dynamicBvh.ts#L30)。

### pipeline-06 · 实例化绘制与运动向量

- **画面或使用效果**：树、花和建筑细节重复出现时降低对象组织成本。
- **原理**：InstancedMesh、MultiInstances 与上一帧变换记录。
- **接入状态**：按场景；**边界**：正确 TAA 还依赖定制 Three.js 的实例速度修复。
- **适用入口**：midsee-village, forest。
- **源码证据**：[src/shared/fiber/MultiInstances.tsx:5](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/fiber/MultiInstances.tsx#L5)。

### pipeline-07 · 水面独立叠加通道

- **画面或使用效果**：水可读取已画好的水底颜色与深度。
- **原理**：Overlay 层在主体光照合成后绘制，屏幕纹理供水材质读取。
- **接入状态**：按场景；**边界**：水的光学着色与主体 GI 存在专门的排除和接入规则。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/shared/render/frameGraph.ts:92](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/frameGraph.ts#L92)。

### pipeline-08 · 线性光照与统一输出转换

- **画面或使用效果**：降低颜色重复转换和重复曝光造成的偏差。
- **原理**：材质色彩空间、HDR 计算和末端 tone mapping 分开处理。
- **接入状态**：主管线；**边界**：参考图与实测必须统一曝光、调色和输出转换。
- **适用入口**：all。
- **源码证据**：[src/shared/render/outputStage.ts:12](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/outputStage.ts#L12)。
- **参数示例**：`?lookOutput=linear`（需接在正确场景路径后，不会在本研究页执行）。


## 全局光照（10 项）

表面光照缓存与三维空间探针

### gi-01 · Surfel 表面光照采样

- **画面或使用效果**：阴影区域仍可获得环境与反弹光的层次。
- **原理**：把表面离散为带位置、法线和辐照信息的小型采样单元。
- **接入状态**：主管线；**边界**：采样密度和射线数量会影响启动时间与细节质量。
- **适用入口**：all。
- **源码证据**：[src/shared/gi/bake/lightmapSurfels.ts:64](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/lightmapSurfels.ts#L64)。
- **参数示例**：`?sample=0.1`（需接在正确场景路径后，不会在本研究页执行）。

### gi-02 · 基于 BVH 的光线求交

- **画面或使用效果**：采样光线能找到墙体、地面和其他表面。
- **原理**：在 WebGPU 计算中遍历空间层级，避免逐个测试所有三角形。
- **接入状态**：主管线；**边界**：计算着色器追踪不代表已接入硬件 RT 管线。
- **适用入口**：all。
- **源码证据**：[src/shared/gi/surfel/sceneBvh.ts:14](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/surfel/sceneBvh.ts#L14)。

### gi-03 · 间接光迭代与缓存

- **画面或使用效果**：逐步累积表面之间的反弹照明。
- **原理**：Surfel 积分器读取场景光源和已有辐照缓存，迭代更新。
- **接入状态**：主管线；**边界**：依赖近似缓存及收敛过程，不是逐像素无偏路径追踪。
- **适用入口**：cornell。
- **源码证据**：[src/shared/gi/surfel/surfelIntegratePass.ts:73](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/surfel/surfelIntegratePass.ts#L73)。
- **参数示例**：`?iters=64&rays=32`（需接在正确场景路径后，不会在本研究页执行）。

### gi-04 · 三维光照探针体积

- **画面或使用效果**：没有光照 UV 的物体也能获得位置相关的环境补光。
- **原理**：规则空间网格保存方向辐照，着色时对周边探针加权。
- **接入状态**：主管线；**边界**：低密度探针不能替代所有表面细节；接收对象由材质规则选择。
- **适用入口**：all。
- **源码证据**：[src/shared/gi/probes/probeVolume.ts:81](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/probes/probeVolume.ts#L81)。
- **参数示例**：`?probeSpacing=2`（需接在正确场景路径后，不会在本研究页执行）。

### gi-05 · DDGI 风格方向编码

- **画面或使用效果**：物体朝向不同，接收的间接光也不同。
- **原理**：探针以八面体贴图保存方向辐照及距离矩。
- **接入状态**：主管线；**边界**：借鉴 DDGI 存储与采样，不等同于完整 RTXGI 产品。
- **适用入口**：cornell, corridor。
- **源码证据**：[src/shared/gi/probes/probeVolume.ts:77](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/probes/probeVolume.ts#L77)。

### gi-06 · 探针遮挡权重与偏移

- **画面或使用效果**：减少隔着墙取得错误亮光。
- **原理**：距离均值、二阶矩、Chebyshev 权重和法线/视线偏移。
- **接入状态**：主管线；**边界**：属于漏光抑制近似；参数过大也会改变细节。
- **适用入口**：corridor, leak-room。
- **源码证据**：[src/shared/gi/probes/probeVolume.ts:282](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/probes/probeVolume.ts#L282)。
- **参数示例**：`?probeVisibility=1`（需接在正确场景路径后，不会在本研究页执行）。

### gi-07 · 探针分类与重定位

- **画面或使用效果**：降低落在实体内部的无效采样影响。
- **原理**：追踪周边几何，为探针设置有效状态和位移。
- **接入状态**：主管线；**边界**：复杂薄壁与边界仍需用漏光实验验证。
- **适用入口**：corridor, leak-room。
- **源码证据**：[src/shared/gi/probes/probeClassify.ts:13](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/probes/probeClassify.ts#L13)。
- **参数示例**：`?probeClassify=1`（需接在正确场景路径后，不会在本研究页执行）。

### gi-08 · 室内外探针分层

- **画面或使用效果**：室内物体优先使用合适的室内光照。
- **原理**：根据室内容积标记探针和接收点的层掩码。
- **接入状态**：按场景；**边界**：需场景提供 interiorVolumes，不会自动理解任意建筑室内。
- **适用入口**：corridor, corridor-lights。
- **源码证据**：[src/shared/gi/probes/probeLayers.ts:4](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/probes/probeLayers.ts#L4)。
- **参数示例**：`?probeLayers=1`（需接在正确场景路径后，不会在本研究页执行）。

### gi-09 · 探针渐进实时更新

- **画面或使用效果**：太阳改变后，探针补光可逐步跟随。
- **原理**：保留探针方向 Surfel，按每帧射线预算刷新。
- **接入状态**：可选；**边界**：probeLive 默认关闭；响应以秒收敛；不自动重算静态 Lightmap。
- **适用入口**：sky, cornell。
- **源码证据**：[src/shared/gi/probes/probeLive.ts:42](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/probes/probeLive.ts#L42)。
- **参数示例**：`?probeLive=1&probeRayBudget=8192`（需接在正确场景路径后，不会在本研究页执行）。

### gi-10 · 实时 Surfel GI 路径

- **画面或使用效果**：研究按当前视角持续更新的间接光。
- **原理**：每帧分配、积分并解析活动 Surfel，和静态烘焙路径并存。
- **接入状态**：历史路径；**边界**：surfelGi 默认关闭；pipeline=legacy 是另一条旧管线入口。
- **适用入口**：cornell。
- **源码证据**：[src/features/render-pipeline/index.ts:693](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/index.ts#L693)。
- **参数示例**：`?surfelGi=1`（需接在正确场景路径后，不会在本研究页执行）。


## 光照贴图与流送（10 项）

烘焙、质量控制和按需显存使用

### lightmap-01 · 自动分配光照 UV 与图表

- **画面或使用效果**：建筑表面能对应到自己的光照贴图区域。
- **原理**：按几何和表面特征拆 chart、打包到 atlas 页。
- **接入状态**：主管线；**边界**：不等于支持所有导入模型；退化、复杂和实例化几何需检查。
- **适用入口**：all。
- **源码证据**：[src/shared/gi/bake/lightmapUv.ts:5](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/lightmapUv.ts#L5)。
- **参数示例**：`?split=lightmap`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-02 · 按世界尺寸控制光照密度

- **画面或使用效果**：近看墙面和阴影时可获得更细的照明纹理。
- **原理**：以米/texel 指定目标密度，场景大时增加 atlas 页。
- **接入状态**：主管线；**边界**：0.03 比 0.1 更细，内存和烘焙代价也更高。
- **适用入口**：corridor, midsee-village。
- **源码证据**：[src/features/render-pipeline/staticLight.ts:26](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/staticLight.ts#L26)。
- **参数示例**：`?lmDensity=0.05`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-03 · 稀疏采样与可见性传播

- **画面或使用效果**：用较少 Surfel 覆盖更多贴图像素。
- **原理**：按世界采样步距建点，再沿追踪得到的链接传播。
- **接入状态**：主管线；**边界**：跨表面传播可能产生误差，项目配有漏光定位工具。
- **适用入口**：corridor, leak-room。
- **源码证据**：[src/shared/gi/bake/filterLinks.ts:16](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/filterLinks.ts#L16)。
- **参数示例**：`?sample=0.1&filterLinks=1`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-04 · 表面约束的填洞与去噪

- **画面或使用效果**：降低烘焙噪点、空白与薄壁漏光。
- **原理**：按表面归属、法线、可见性链接限制滤波和填充。
- **接入状态**：主管线；**边界**：精度仍受射线数量和几何分辨率影响。
- **适用入口**：leak-room。
- **源码证据**：[src/shared/gi/bake/holeFill.ts:98](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/holeFill.ts#L98)。
- **参数示例**：`?leak=1`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-05 · Chart 边缘扩张与隔离

- **画面或使用效果**：降低 UV 接缝处的暗线和邻区串光。
- **原理**：给每个图表单独填充边界 texel。
- **接入状态**：主管线；**边界**：它处理纹理过滤边界，不会修复错误几何或错误 UV。
- **适用入口**：lod-scale。
- **源码证据**：[src/shared/gi/bake/chartPadding.ts:2](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/chartPadding.ts#L2)。

### lightmap-06 · 烘焙结果持久化

- **画面或使用效果**：重复打开场景时可跳过已有光照积分。
- **原理**：二进制缓存与配套清单保存 atlas、Surfel 和探针。
- **接入状态**：主管线；**边界**：写入流程依赖开发服务插件；不能假设静态托管可直接回写。
- **适用入口**：all。
- **源码证据**：[src/shared/gi/bake/persistedBake.ts:2](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/persistedBake.ts#L2)。
- **参数示例**：`?bakeCache=0`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-07 · 光照来源与陈旧状态检查

- **画面或使用效果**：修改环境后能知道缓存是否仍匹配。
- **原理**：记录环境、太阳和传输设置的 provenance，再比较当前条件。
- **接入状态**：主管线；**边界**：提示过期不会自动完成全场景重烘焙。
- **适用入口**：sky。
- **源码证据**：[src/shared/gi/bake/lightingProvenance.ts:3](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/lightingProvenance.ts#L3)。
- **参数示例**：`?bakeCache=0`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-08 · 每个 Chart 独立 Mip 金字塔

- **画面或使用效果**：远处读取较粗光照，近处保留细节。
- **原理**：逐 chart 降采样并切成带边框的 tile。
- **接入状态**：主管线；**边界**：独立金字塔用于隔离不同表面；不是完整材质虚拟纹理系统。
- **适用入口**：lod-scale。
- **源码证据**：[src/shared/gi/lod/chartPyramids.ts:3](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/lod/chartPyramids.ts#L3)。
- **参数示例**：`?vtTile=64`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-09 · 按可见需求驻留光照 Tile

- **画面或使用效果**：有限 GPU 工作池服务当前镜头需要的光照细节。
- **原理**：反馈通道收集请求，页表指向驻留页或同 chart 粗级 tail。
- **接入状态**：主管线；**边界**：仍需保留完整数据的 CPU 内存，不是网络按需下载。
- **适用入口**：lod-scale, midsee-village。
- **源码证据**：[src/shared/gi/lod/tileResidency.ts:3](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/lod/tileResidency.ts#L3)。
- **参数示例**：`?vtPool=16`（需接在正确场景路径后，不会在本研究页执行）。

### lightmap-10 · CPU 到 GPU 的分块上传

- **画面或使用效果**：镜头变化时逐步送入需要的光照页。
- **原理**：当前代码将半精度 tile 存在 tab 内存，通过 writeTexture 上传。
- **接入状态**：主管线；**边界**：旧虚拟纹理文档还写着全量 GPU store，当前代码已前进；不承诺总内存恒定。
- **适用入口**：lod-scale。
- **源码证据**：[src/shared/gi/lod/tilePool.ts:34](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/lod/tilePool.ts#L34)。
- **参数示例**：`?vtUploadKiB=1024`（需接在正确场景路径后，不会在本研究页执行）。


## 光源、阴影与反射（9 项）

直接光、遮挡和镜面响应

### lighting-01 · 太阳方向与强度控制

- **画面或使用效果**：调整光照朝向、阴影方向与明暗。
- **原理**：DirectionalLight 与太阳方位角、高度角控制。
- **接入状态**：主管线；**边界**：静态间接光仍保留烘焙时条件，变化后应检查缓存状态。
- **适用入口**：all。
- **源码证据**：[src/features/render-pipeline/sun.ts:124](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/sun.ts#L124)。
- **参数示例**：`?sunAz=-60&sunEl=10`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-02 · 太阳能量从环境图估计

- **画面或使用效果**：HDR 天空与直接太阳光更协调。
- **原理**：从环境贴图提取太阳方向/能量供解析光源使用。
- **接入状态**：按场景；**边界**：受环境图内容和场景主机配置影响。
- **适用入口**：beach, forest。
- **源码证据**：[src/features/lighting-pipeline/sunFromEnvironment.ts:17](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/lighting-pipeline/sunFromEnvironment.ts#L17)。
- **参数示例**：`?sun=2`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-03 · 接触硬化软阴影

- **画面或使用效果**：遮挡物附近阴影较硬，离开后更柔和。
- **原理**：PCSS 风格遮挡搜索与半影滤波，太阳视直径参与计算。
- **接入状态**：主管线；**边界**：基于阴影贴图的近似；受分辨率和滤波预算限制。
- **适用入口**：all。
- **源码证据**：[src/shared/render/softSunShadow.ts:38](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/softSunShadow.ts#L38)。
- **参数示例**：`?shadowFilter=soft&sunDisc=0.533`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-04 · 接收面修正与阴影范围适配

- **画面或使用效果**：减少斜面条纹与阴影精度浪费。
- **原理**：接收面导数补偿和相机范围拟合。
- **接入状态**：可选；**边界**：shadowFit 默认关闭；偏移需要按场景验证。
- **适用入口**：all。
- **源码证据**：[src/features/render-pipeline/sun.ts:141](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/sun.ts#L141)。
- **参数示例**：`?shadowFit=1&shadowFilter=receiverPlane`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-05 · 移动彩色光源与阴影

- **画面或使用效果**：走廊里彩灯移动，照明和阴影随之变化。
- **原理**：专门场景逐帧更新多个解析光源。
- **接入状态**：按场景；**边界**：演示动态直接光，不代表所有静态反弹光都实时更新。
- **适用入口**：corridor-lights。
- **源码证据**：[src/widgets/world/corridorLightsScene.ts:6](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/corridorLightsScene.ts#L6)。
- **参数示例**：`?scene=corridor-lights&lightMotion=0`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-06 · 短射线接触遮蔽

- **画面或使用效果**：墙脚、椅脚和物体接触更有重量感。
- **原理**：对近距离几何发射短光线，只调制间接光。
- **接入状态**：可选；**边界**：默认关闭；不能当作完整远距离阴影。
- **适用入口**：corridor。
- **源码证据**：[src/shared/gi/contact/contactOcclusionPass.ts:25](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/contact/contactOcclusionPass.ts#L25)。
- **参数示例**：`?contact=1`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-07 · 场景射线反射

- **画面或使用效果**：低粗糙度表面可反映屏幕外几何。
- **原理**：根据 G-buffer 方向追踪静态/动态 BVH，并对命中点着色。
- **接入状态**：主管线；**边界**：有最大粗糙度、射线节点预算和更新间隔。
- **适用入口**：cornell, sky。
- **源码证据**：[src/shared/gi/reflect/reflectionPass.ts:44](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/reflect/reflectionPass.ts#L44)。
- **参数示例**：`?reflections=0`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-08 · 反射降噪与粗糙表面补充

- **画面或使用效果**：降低反射噪点并给较粗表面环境响应。
- **原理**：空间降噪，以及光照探针方向采样作为粗糙反射补充。
- **接入状态**：主管线；**边界**：探针补充是近似，不等同于逐像素精确镜面反射。
- **适用入口**：cornell。
- **源码证据**：[src/features/render-pipeline/index.ts:697](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/index.ts#L697)。
- **参数示例**：`?probeSpecular=0`（需接在正确场景路径后，不会在本研究页执行）。

### lighting-09 · 反射缓存与局部代理体积

- **画面或使用效果**：以分时更新的反射探针研究可控成本反射。
- **原理**：捕获、过滤、发布、版本状态和盒/球代理体积。
- **接入状态**：可选；**边界**：通过 reflections=cached 选择；当前默认仍走另一条反射路径。
- **适用入口**：sky, cornell。
- **源码证据**：[src/shared/gi/reflect/cache/reflectionCache.ts:50](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/reflect/cache/reflectionCache.ts#L50)。
- **参数示例**：`?reflections=cached`（需接在正确场景路径后，不会在本研究页执行）。


## 海水与流体（13 项）

主场景浅水系统与独立物理水实验

### water-01 · 浅水高度与流速求解

- **画面或使用效果**：浪接近岸边和障碍物时发生变化。
- **原理**：二维浅水方程在高度/流速网格上推进。
- **接入状态**：按场景；**边界**：高度场流体，不是任意三维体积流体或完整海洋数值模型。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/shallowWater.ts:46](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/shallowWater.ts#L46)。

### water-02 · 水底地形与障碍物采样

- **画面或使用效果**：水深和岸线跟随底部及障碍形状。
- **原理**：将水底与障碍几何烘焙为 bathymetry 高度数据。
- **接入状态**：按场景；**边界**：精度受格点尺寸与几何覆盖限制。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/bathymetry.ts:14](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/bathymetry.ts#L14)。

### water-03 · 水面折射与水下成像

- **画面或使用效果**：透过水面看见位置偏移的水底。
- **原理**：主场景重建深度和折射路径，实验室进一步追踪水下几何。
- **接入状态**：按场景；**边界**：主场景与实验室算法不同，不能用实验室能力概括所有水面。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/index.ts:550](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/index.ts#L550)。

### water-04 · 随路径长度的吸收与散射

- **画面或使用效果**：浅水透明、深水更有颜色和厚度。
- **原理**：逐 RGB 通道 Beer–Lambert 衰减与散射项。
- **接入状态**：按场景；**边界**：颜色由光学系数、路径和底色共同决定。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/index.ts:210](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/index.ts#L210)。

### water-05 · Fresnel 天空反射与太阳闪光

- **画面或使用效果**：掠视时更像镜子，顺光看到水面亮点。
- **原理**：Fresnel 混合天空与透射，结合太阳 GGX 响应。
- **接入状态**：按场景；**边界**：主场景天空反射与实验室的几何反射需要分别理解。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/index.ts:704](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/index.ts#L704)。

### water-06 · 水底焦散图案

- **画面或使用效果**：水下沙地出现流动的明亮纹理。
- **原理**：主水面材质生成并调制焦散近似。
- **接入状态**：按场景；**边界**：主场景焦散是视觉近似，不能宣称全物理光子传输。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/index.ts:73](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/index.ts#L73)。

### water-07 · 持续泡沫场与湿沙

- **画面或使用效果**：泡沫随水流漂移并逐渐消散，岸边留下湿润痕迹。
- **原理**：Ping-pong 纹理保存泡沫、湿度和撞击源。
- **接入状态**：按场景；**边界**：需要多帧状态推进；冻结模拟后不再按真实时间演变。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/index.ts:365](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/index.ts#L365)。

### water-08 · 浪花与喷溅粒子

- **画面或使用效果**：岸线或撞击处出现抛出的细小水滴。
- **原理**：根据水面状态和泡沫源驱动喷溅粒子。
- **接入状态**：按场景；**边界**：视觉粒子表现，不是每滴水都参与完整流体求解。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/spray.ts:61](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/spray.ts#L61)。
- **参数示例**：`?spray=0`（需接在正确场景路径后，不会在本研究页执行）。

### water-09 · 独立 Worker 水模拟

- **画面或使用效果**：重水模拟可从页面主线程移走。
- **原理**：Worker 使用自己的 WebGPU device，异步传回状态。
- **接入状态**：按场景；**边界**：线程与 GPU 数据传递仍有开销，需要目标设备实测。
- **适用入口**：beach, midsee-village。
- **源码证据**：[src/entities/water/simHost.ts:22](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/simHost.ts#L22)。

### water-10 · 漂浮球交互样例

- **画面或使用效果**：球会随局部水高与斜率浮动。
- **原理**：独立 Worker 计算示例球受力，主线程应用姿态。
- **接入状态**：按场景；**边界**：是特定物体样例，不能视为通用刚体物理引擎。
- **适用入口**：beach。
- **源码证据**：[src/entities/ball/index.ts:9](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/ball/index.ts#L9)。

### water-11 · 风浪频谱与 FFT 微细节

- **画面或使用效果**：独立水实验室里可观察多尺度海面起伏。
- **原理**：方向频谱与波分量控制几何，逆 FFT 产生细尺度表面场。
- **接入状态**：实验室；**边界**：通过 labs/water 的 physicalWater 路径接入，主场景仍使用另一套水入口。
- **适用入口**：water-ocean。
- **源码证据**：[src/entities/water/physicalWater.ts:162](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/physicalWater.ts#L162)。
- **参数示例**：`?wind=8`（需接在正确场景路径后，不会在本研究页执行）。

### water-12 · 几何反射与波面追踪

- **画面或使用效果**：独立实验中水面可反射测试物体。
- **原理**：平面反射、波面反射通道和表面射线求交共同工作。
- **接入状态**：实验室；**边界**：代价与近似需要单独验证；不能推断所有主场景已使用。
- **适用入口**：water-pool, water-ocean。
- **源码证据**：[src/entities/water/physicalWater.ts:20](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/physicalWater.ts#L20)。

### water-13 · 水体体积光与光学诊断

- **画面或使用效果**：实验室可单独查看水下散射与光线路径。
- **原理**：水体射线步进、表面交点和多种诊断视图。
- **接入状态**：实验室；**边界**：属于独立光学研究模块，未完成跨设备验收。
- **适用入口**：water-pool。
- **源码证据**：[src/entities/water/volumeLight.ts:17](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/water/volumeLight.ts#L17)。
- **参数示例**：`?waterInspect=1`（需接在正确场景路径后，不会在本研究页执行）。


## 植被、地形与材质（10 项）

程序化形体、叶片透光与分层表面

### nature-01 · 叶片生化光学

- **画面或使用效果**：不同叶片具有不同反射色与透射色。
- **原理**：PROSPECT 风格板层模型，把色素/结构参数转换为光谱再转 RGB。
- **接入状态**：按场景；**边界**：是渲染模型实现，未完成植物实验数据拟合验证。
- **适用入口**：beach。
- **源码证据**：[src/entities/foliage/leafOptics.ts:267](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/foliage/leafOptics.ts#L267)。

### nature-02 · 薄叶透光与表面反光

- **画面或使用效果**：逆光时叶片发亮，正面保留表面光泽。
- **原理**：薄叶 BSDF、方向透射和 GGX 角质层响应。
- **接入状态**：按场景；**边界**：屏幕合成、光线命中和叶材质的透射路径并不完全相同。
- **适用入口**：beach, forest。
- **源码证据**：[src/shared/render/foliage/leafMaterial.ts:206](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/foliage/leafMaterial.ts#L206)。

### nature-03 · 程序化叶脉与微表面

- **画面或使用效果**：近看叶片有脉络凹凸与光泽差异。
- **原理**：在叶片局部空间生成表面纹理和光学变化。
- **接入状态**：按场景；**边界**：细节表达取决于相机距离、纹理分辨率和光照。
- **适用入口**：beach。
- **源码证据**：[src/entities/foliage/leafSurface.ts:25](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/foliage/leafSurface.ts#L25)。

### nature-04 · 程序化棕榈与树干

- **画面或使用效果**：形成叶冠、环状叶痕、裂缝和风化细节。
- **原理**：几何构建结合统一高度场导出的颜色、法线与粗糙度。
- **接入状态**：按场景；**边界**：形体是程序化资产，不是通用植物扫描或建模编辑器。
- **适用入口**：beach。
- **源码证据**：[src/entities/palm/trunkSurface.ts:32](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/palm/trunkSurface.ts#L32)。

### nature-05 · 针叶树与灌木生成

- **画面或使用效果**：森林里可布置多种树形和灌木层次。
- **原理**：ez-tree、分枝生长、针束和实例化几何。
- **接入状态**：按场景；**边界**：不同植物走不同生成模块，参数并非统一编辑器。
- **适用入口**：forest。
- **源码证据**：[src/entities/conifer/index.ts:11](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/conifer/index.ts#L11)。

### nature-06 · 风动植被与顶点运动

- **画面或使用效果**：叶片随风摆动，TAA 可跟随形变。
- **原理**：顶点位移与前后帧运动记录组合。
- **接入状态**：按场景；**边界**：自定义形变必须同步速度，否则可能出现拖影和闪烁。
- **适用入口**：beach, forest。
- **源码证据**：[src/shared/render/vertexMotion.ts:8](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/vertexMotion.ts#L8)。

### nature-07 · 多层沙地与湿润过渡

- **画面或使用效果**：干沙、湿沙、贝壳和风纹自然交替。
- **原理**：按地形条件混合贴图、法线、粗糙度和层间细节。
- **接入状态**：按场景；**边界**：部分贴图来自上游资源，复用需逐项确认素材权利。
- **适用入口**：beach。
- **源码证据**：[src/entities/island/sandMaterial.ts:25](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/island/sandMaterial.ts#L25)。

### nature-08 · 抗重复地形表面采样

- **画面或使用效果**：大面积地面降低明显的平铺重复。
- **原理**：分层表面、分块噪声与变化采样。
- **接入状态**：按场景；**边界**：属于材质采样方法，不包含完整地形编辑与植被散布工具。
- **适用入口**：beach, forest。
- **源码证据**：[src/shared/render/terrain/layerSampler.ts:29](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/terrain/layerSampler.ts#L29)。

### nature-09 · 自适应地形与程序化岩石

- **画面或使用效果**：森林与海岛有起伏、岩壁、石块和溪流。
- **原理**：高度场、局部自适应网格和程序化岩石构建。
- **接入状态**：按场景；**边界**：场景专用的建模代码，不是通用开放世界流送系统。
- **适用入口**：forest, beach。
- **源码证据**：[src/entities/grove/adaptiveMesh.ts:3](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/grove/adaptiveMesh.ts#L3)。

### nature-10 · 村庄建筑与陈设组件

- **画面或使用效果**：台地房屋、钟楼、咖啡馆、船和植物可组合成场景。
- **原理**：多个 React 预制组件共享材质和实例化几何。
- **接入状态**：按场景；**边界**：村庄标注开发中；组件运行还依赖未打包的 R3F 定制源码。
- **适用入口**：midsee-village。
- **源码证据**：[src/entities/village/VillagePrefab.tsx:28](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/entities/village/VillagePrefab.tsx#L28)。


## 天空与大气（7 项）

物理天空、云影、雾和空气透视

### sky-01 · 物理大气与天空 LUT

- **画面或使用效果**：天空随太阳高度和观察高度改变颜色。
- **原理**：计算透射、多次散射和天空视图查找表。
- **接入状态**：按场景；**边界**：默认是否开启由场景是否提供 sky 决定。
- **适用入口**：sky。
- **源码证据**：[src/shared/render/sky/atmosphereLuts.ts:51](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/sky/atmosphereLuts.ts#L51)。
- **参数示例**：`?scene=sky`（需接在正确场景路径后，不会在本研究页执行）。

### sky-02 · Rayleigh 与 Mie 散射

- **画面或使用效果**：出现蓝天、暖色低太阳和近太阳泛白。
- **原理**：空气与气溶胶散射系数、相函数和光线积分。
- **接入状态**：按场景；**边界**：参数化地球大气模型，未宣称天文或气象计算精度。
- **适用入口**：sky。
- **源码证据**：[src/shared/render/sky/scatteringMarch.ts:11](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/sky/scatteringMarch.ts#L11)。
- **参数示例**：`?sunEl=2`（需接在正确场景路径后，不会在本研究页执行）。

### sky-03 · 空气透视

- **画面或使用效果**：远处物体对比减弱并向天空颜色融合。
- **原理**：沿视线估算空气透射与入射散射。
- **接入状态**：按场景；**边界**：效果强度可以艺术放大；aerialScale 不是实际距离测量。
- **适用入口**：sky。
- **源码证据**：[src/shared/render/sky/aerialPerspective.ts:36](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/sky/aerialPerspective.ts#L36)。
- **参数示例**：`?aerialScale=400`（需接在正确场景路径后，不会在本研究页执行）。

### sky-04 · 体积云与云层光照

- **画面或使用效果**：能看到厚薄不同、具有内部明暗的云。
- **原理**：程序化密度、射线步进和云层光照采样。
- **接入状态**：按场景；**边界**：属于有限云层模型，分辨率和步数影响细节与耗时。
- **适用入口**：sky。
- **源码证据**：[src/shared/render/sky/cloudLayer.ts:46](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/sky/cloudLayer.ts#L46)。
- **参数示例**：`?cloudCoverage=0.55`（需接在正确场景路径后，不会在本研究页执行）。

### sky-05 · 移动云影

- **画面或使用效果**：地面与场景表面随云移动出现遮光变化。
- **原理**：云密度生成太阳透射图，作用于直接光。
- **接入状态**：按场景；**边界**：烘焙的静态间接光不会跟每一帧云影完整重算。
- **适用入口**：sky。
- **源码证据**：[src/shared/render/sky/cloudShadowMap.ts:24](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/sky/cloudShadowMap.ts#L24)。
- **参数示例**：`?clouds=1`（需接在正确场景路径后，不会在本研究页执行）。

### sky-06 · 天空作为环境照明与反射来源

- **画面或使用效果**：天空变化能传递到环境反射。
- **原理**：生成天空环境纹理并接入渲染与烘焙来源。
- **接入状态**：按场景；**边界**：需要更新静态间接光时仍须明确发起重烘焙。
- **适用入口**：sky。
- **源码证据**：[src/shared/render/sky/skyEnvironment.ts:27](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/sky/skyEnvironment.ts#L27)。
- **参数示例**：`?skyEnvironment=1`（需接在正确场景路径后，不会在本研究页执行）。

### sky-07 · Froxel 体积雾

- **画面或使用效果**：光穿过有密度变化的空气，远景产生空间层次。
- **原理**：视锥体素保存散射/透射，沿视线合成并做时间积累。
- **接入状态**：按场景；**边界**：不同场景可默认关闭；不是实体烟火流体模拟。
- **适用入口**：beach, forest。
- **源码证据**：[src/shared/render/atmosphere/volumetricFog.ts:44](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/atmosphere/volumetricFog.ts#L44)。
- **参数示例**：`?fog=1`（需接在正确场景路径后，不会在本研究页执行）。


## 镜头与后期（8 项）

稳定画面、曝光、运动与艺术调色

### post-01 · TAA 时间抗锯齿

- **画面或使用效果**：减少几何边缘、植被和高光的闪烁。
- **原理**：相机抖动、速度重投影、历史裁剪与累积。
- **接入状态**：主管线；**边界**：依赖准确运动向量；快速运动和遮挡变化仍有拖影风险。
- **适用入口**：all。
- **源码证据**：[src/shared/render/temporalAA.ts:120](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/temporalAA.ts#L120)。
- **参数示例**：`?aa=taa`（需接在正确场景路径后，不会在本研究页执行）。

### post-02 · FXAA 与关闭抗锯齿对照

- **画面或使用效果**：可对比单帧平滑与原始像素边缘。
- **原理**：在 TAA、FXAA 和 none 三种模式间选择。
- **接入状态**：可选；**边界**：用于成本/画质对照，不承诺每种模式质量一致。
- **适用入口**：all。
- **源码证据**：[src/shared/render/frameGraph.ts:28](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/frameGraph.ts#L28)。
- **参数示例**：`?aa=fxaa`（需接在正确场景路径后，不会在本研究页执行）。

### post-03 · 自动曝光与手动曝光

- **画面或使用效果**：从暗处看向亮处时逐步适应亮度。
- **原理**：测光、时间适应、手动曝光与曝光补偿分开控制。
- **接入状态**：主管线；**边界**：截图比较需等适应稳定或固定曝光。
- **适用入口**：all。
- **源码证据**：[src/shared/render/exposure.ts:24](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/exposure.ts#L24)。
- **参数示例**：`?exposure=1&exposureEV=-1`（需接在正确场景路径后，不会在本研究页执行）。

### post-04 · 艺术 Look 调色

- **画面或使用效果**：控制对比、饱和度、暗部和色彩平衡。
- **原理**：在正确阶段应用艺术调整，部分参数单独作用于间接光。
- **接入状态**：主管线；**边界**：美术增益会改变物理响应；并非所有旋钮都是末端后期。
- **适用入口**：all。
- **源码证据**：[src/shared/render/look.ts:74](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/look.ts#L74)。
- **参数示例**：`?look=0&indirectEV=1`（需接在正确场景路径后，不会在本研究页执行）。

### post-05 · Neutral、AgX 与线性输出

- **画面或使用效果**：同一 HDR 场景可采用不同高光压缩方式。
- **原理**：选择末端输出转换，避免重复 tone mapping。
- **接入状态**：主管线；**边界**：线性输出主要用于诊断，不代表可直接和显示图比较。
- **适用入口**：all。
- **源码证据**：[src/shared/render/look.ts:37](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/look.ts#L37)。
- **参数示例**：`?lookOutput=agx`（需接在正确场景路径后，不会在本研究页执行）。

### post-06 · 镜头眩光与胶片颗粒

- **画面或使用效果**：高亮向邻域扩散，画面带少量颗粒质感。
- **原理**：眩光扩散合成，tone mapping 后叠加显示空间噪声。
- **接入状态**：按场景；**边界**：截图比较应关闭颗粒；眩光不是完整镜头光学仿真。
- **适用入口**：all。
- **源码证据**：[src/features/render-pipeline/postStages.ts:34](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/postStages.ts#L34)。
- **参数示例**：`?glare=0&grain=0`（需接在正确场景路径后，不会在本研究页执行）。

### post-07 · 速度驱动运动模糊

- **画面或使用效果**：相机或物体运动时出现随方向的拖曳。
- **原理**：根据运动向量、快门角度和积分时间采样。
- **接入状态**：可选；**边界**：默认关闭；开启不等于自动得到准确摄影曝光。
- **适用入口**：all。
- **源码证据**：[src/shared/render/motionBlur.ts:50](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/motionBlur.ts#L50)。
- **参数示例**：`?motionBlur=1&shutter=0.5`（需接在正确场景路径后，不会在本研究页执行）。

### post-08 · 摄影机与镜头预设

- **画面或使用效果**：不同传感器与焦距改变取景范围。
- **原理**：使用 ALEXA、VENICE、IMAX 等参数预设设置 FOV 和快门。
- **接入状态**：可选；**边界**：预设不是认证相机模拟；代码没有完整景深、镜片像差与传感器仿真。
- **适用入口**：midsee-village。
- **源码证据**：[src/features/render-pipeline/cineCamera.ts:3](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/cineCamera.ts#L3)。
- **参数示例**：`?cine=alexa35-32`（需接在正确场景路径后，不会在本研究页执行）。


## 诊断与研究工具（10 项）

逐层看图、定位画质问题和测量成本

### tools-01 · 左右分屏查看中间层

- **画面或使用效果**：直接对照最终画面和光照/法线等缓冲。
- **原理**：SplitView 在同一视角输出所选中间结果。
- **接入状态**：可选；**边界**：分屏是诊断结果，不是不同渲染引擎的画质排名。
- **适用入口**：all。
- **源码证据**：[src/shared/render/frameGraph.ts:59](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/render/frameGraph.ts#L59)。
- **参数示例**：`?split=baked`（需接在正确场景路径后，不会在本研究页执行）。

### tools-02 · 漏光阶段追踪

- **画面或使用效果**：定位烘焙在哪一步把黑处变亮。
- **原理**：保存原始、去噪、填洞、padding 和发布阶段的数据。
- **接入状态**：可选；**边界**：leak=1 会改变缓存与捕获流程，应与基线分开测量。
- **适用入口**：leak-room, corridor。
- **源码证据**：[src/shared/gi/bake/leakStages.ts:4](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/gi/bake/leakStages.ts#L4)。
- **参数示例**：`?leak=1&split=leak`（需接在正确场景路径后，不会在本研究页执行）。

### tools-03 · 封闭房间与毫米级开缝标尺

- **画面或使用效果**：用本应全黑的室内检查漏光，再打开真实缝隙。
- **原理**：专门几何夹具和 gap 参数建立可解释参照。
- **接入状态**：按场景；**边界**：几何标尺是测试场景，仍需检查追踪和采样设置。
- **适用入口**：leak-room。
- **源码证据**：[src/widgets/world/leakRoomScene.ts:7](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/leakRoomScene.ts#L7)。
- **参数示例**：`?scene=leak-room&gap=1`（需接在正确场景路径后，不会在本研究页执行）。

### tools-04 · 光照 Tile 驻留实验室

- **画面或使用效果**：同时看场景与实际 GPU 光照工作池。
- **原理**：LOD lab 显示 tile、mip、占用和相关参数。
- **接入状态**：可选；**边界**：这是光照缓存调试，不是通用模型 LOD 预览器。
- **适用入口**：lod-scale, midsee-village。
- **源码证据**：[src/widgets/lod-lab/index.ts:14](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/lod-lab/index.ts#L14)。
- **参数示例**：`?lodLab=1`（需接在正确场景路径后，不会在本研究页执行）。

### tools-05 · GPU 通道计时与绘制统计

- **画面或使用效果**：知道时间花在何处、哪些对象被重复绘制。
- **原理**：可选 timestamp queries、每通道审计和 draw count hooks。
- **接入状态**：可选；**边界**：计时本身有开销；不同 CPU/GPU 列不能混当总帧时间。
- **适用入口**：all。
- **源码证据**：[src/features/render-pipeline/audit.ts:37](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/audit.ts#L37)。
- **参数示例**：`?gputime=1`（需接在正确场景路径后，不会在本研究页执行）。

### tools-06 · CPU 帧循环与启动阶段诊断

- **画面或使用效果**：区分构建场景、烘焙、编译和首帧瓶颈。
- **原理**：bootStage、动画循环计时、作者的启动检查脚本。
- **接入状态**：可选；**边界**：作者历史数据不直接代表当前机器或发布构建。
- **适用入口**：midsee-village。
- **源码证据**：[src/shared/ui/bootProgress.ts:1](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/ui/bootProgress.ts#L1)。

### tools-07 · 可重复相机与冻结画面

- **画面或使用效果**：相同机位比较参数前后的差别。
- **原理**：场景相机预设、still 参数与截图脚本。
- **接入状态**：可选；**边界**：仍需关闭颗粒、固定曝光并处理 TAA 收敛。
- **适用入口**：all。
- **源码证据**：[src/app/home/catalog.ts:194](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/app/home/catalog.ts#L194)。
- **参数示例**：`?still=1&grain=0&aa=none`（需接在正确场景路径后，不会在本研究页执行）。

### tools-08 · 浏览器自动检查脚本

- **画面或使用效果**：为反射、TAA、软阴影和水模拟提供回归入口。
- **原理**：Playwright 打开参数化场景、读取诊断钩子并截图比较。
- **接入状态**：可选；**边界**：脚本存在不表示本次已全部运行，部分脚本引用缺失资源。
- **适用入口**：water-pool。
- **源码证据**：[scripts/check-water-sim.mjs:32](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/scripts/check-water-sim.mjs#L32)。

### tools-09 · GUI 设置与研究配置

- **画面或使用效果**：保存每个场景的参数组合，恢复研究视角。
- **原理**：lil-gui 控制面板配合开发服务器设置插件。
- **接入状态**：按场景；**边界**：增加查询参数可能绕过保存的配置，比较前须统一来源。
- **适用入口**：all。
- **源码证据**：[src/app/guiSettings.ts:8](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/app/guiSettings.ts#L8)。
- **参数示例**：`?hud=0`（需接在正确场景路径后，不会在本研究页执行）。

### tools-10 · 渲染技术阅读页

- **画面或使用效果**：比较 RDR2、Lumen 等管线的取舍。
- **原理**：独立静态说明页组织作者技术研究。
- **接入状态**：独立资料；**边界**：是研究资料，提及的商业引擎能力不等于本项目已实现。
- **适用入口**：pipeline-doc。
- **源码证据**：[src/widgets/pipeline/PipelinePage.tsx:12](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/pipeline/PipelinePage.tsx#L12)。


## 集成与使用边界（4 项）

场景接口、组件接入和复现条件

### integration-01 · 可替换场景主机接口

- **画面或使用效果**：把不同场景插入同一套光照与渲染流程。
- **原理**：SceneHost 交付 scene、camera、sun、更新函数和可选设置。
- **接入状态**：主管线；**边界**：接入新场景仍需标记静态性、光照接收和室内容积。
- **适用入口**：all。
- **源码证据**：[src/features/render-pipeline/host.ts:11](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/features/render-pipeline/host.ts#L11)。

### integration-02 · React Three Fiber 场景组件

- **画面或使用效果**：以组件描述建筑、岩石和其他预制体。
- **原理**：自定义 scene root、StaticGroup 和 MultiInstances 连接 WebGPU 场景。
- **接入状态**：集成待补；**边界**：定制 R3F vendor 和部分 React 依赖未随固定版本完整提交。
- **适用入口**：midsee-village, fiber-lab。
- **源码证据**：[src/shared/fiber/sceneRoot.tsx:20](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/shared/fiber/sceneRoot.tsx#L20)。

### integration-03 · Three.js 定制修复说明

- **画面或使用效果**：改善实例 TAA 稳定性和部分 CPU 提交开销。
- **原理**：r182 分支回移运动向量修复，并维护影子材质等补丁。
- **接入状态**：集成待补；**边界**：文档记录了依赖，但 vendor/three 不在本库树中。
- **适用入口**：all。
- **源码证据**：[docs/lessons-three-fork.md:15](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/docs/lessons-three-fork.md#L15)。

### integration-04 · 参数化场景与相机接入

- **画面或使用效果**：同一应用可以选择不同场景与观察配置。
- **原理**：URL 查询选择主场景，各场景读取自己的 cam 等参数。
- **接入状态**：按场景；**边界**：不同场景支持的参数不同；独立实验室路径仍需补入口。
- **适用入口**：all。
- **源码证据**：[src/app/main.ts:83](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/app/main.ts#L83)。
- **参数示例**：`?scene=beach`（需接在正确场景路径后，不会在本研究页执行）。
