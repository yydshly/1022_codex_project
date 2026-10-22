# 场景与观察路线

共 14 个研究入口：主场景、测试夹具、独立实验室及阅读页分开登记。这里给出上游服务启动后的相对路由，不是已部署演示链接。

本地图来自固定版本场景入口及 `src/app/home/catalog.ts`。相机名以各场景实际支持为准，不把共享的 `cam` 参数当作所有场景都支持相同机位。

## Cornell Box · 参考场景

- 入口：`/?hud=1`。
- 看什么：彩色墙面反弹光、移动物体、探针与烘焙分层。
- 相机：使用默认相机或实验室内置控制。
- 建议观察：先用 split=baked 看反弹光，再对比 surfelGi=1。
- 范围：未指定 scene 时的默认参考场景。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/cornellScene.ts)。

## 热带海滩 · 主场景

- 入口：`/?scene=beach`。
- 看什么：浅水、沙地、棕榈、树皮、叶片透光、浪花。
- 相机：shore, rocks, water, surf, eye, leaves, trunkLit, shrub, sunward, van。
- 建议观察：分别看 leaves、trunkLit 和 water，避免仅用远景判断材质。
- 范围：已接入真实演示，使用 entities/water/index.ts 主场景水实现；固定源码缺少房车 GLB，展示设 van=0。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/beachScene.ts)。

## 针叶林与溪流 · 主场景

- 入口：`/?scene=forest`。
- 看什么：自适应地形、程序化树木、群落阴影与溪流。
- 相机：hero, wide, trail, stream, ledge, canopy, rim。
- 建议观察：对比 canopy、stream 与 rim，记录 TAA 是否闪烁。
- 范围：已接入真实演示，保留近远景植被；溪流为不透明波纹材质，区别于海滩浅水模拟。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/forestScene.ts)。

## 封闭走廊 · 参考场景

- 入口：`/?scene=corridor`。
- 看什么：室内外探针分层、墙体漏光、地面与长椅接触。
- 相机：hero, wide, bench, panels, floor, deep。
- 建议观察：从 floor/bench 检查接触处，再用 leak=1 追踪阶段。
- 范围：可用 lmDensity=0.1 与 0.03 观察光照密度差异。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/corridorScene.ts)。

## 走廊动态彩灯 · 专用实验

- 入口：`/?scene=corridor-lights`。
- 看什么：三个移动彩灯、实时直接光和阴影。
- 相机：hero, bench, deep。
- 建议观察：暂停 lightMotion=0，分别控制每个灯的启用和强度。
- 范围：静态照明设置与普通走廊不同，不能把两场景当作单参数 A/B。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/corridorLightsScene.ts)。

## 地中海村庄 · 开发中场景

- 入口：`/?scene=midsee-village`。
- 看什么：台地建筑、钟楼、咖啡馆、海湾、船和植物。
- 相机：front, side, rear, quay, roofs。
- 建议观察：先选 front，再查看 quay/roofs；关注启动时间与光照页占用。
- 范围：作者标注开发中；本研究已将该完整场景接入上方真实演示，历史截图另行标明。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/midseeVillageScene.tsx)。

## 单栋房屋轻量夹具 · 专用实验

- 入口：`/?scene=village-light`。
- 看什么：同一建筑材质与光照问题的低成本定位。
- 相机：使用默认相机或实验室内置控制。
- 建议观察：配合 lodLab=1 和 bakedOnly=1 定位贴图、页表和补光。
- 范围：降低场景内容量，适合区分材质编译与全村几何成本。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/villageLightScene.tsx)。

## 天空、大气与云 · 专用实验

- 入口：`/?scene=sky&cam=objects`。
- 看什么：午间、黄金时刻、落日、暮光、云影与高空视角。
- 相机：objects, sunward, zenith, horizon。
- 建议观察：对比 sunEl=45、10、2、-4；分别关闭 clouds 与 aerial。
- 范围：太阳与反射可即时变化；静态间接光使用 GUI 的 bake light from this sky 更新。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/skyLabScene.tsx)。

## 光照 LOD 比例尺 · 专用实验

- 入口：`/?scene=lod-scale&cam=overview`。
- 看什么：格栅细影、不同尺寸房屋、长墙、mip 与 tile 接缝。
- 相机：overview, eye, grazing, glow, pergola, ladder, wall, far。
- 建议观察：lod=0 对比虚拟纹理，再用 vtPool=4 或 vtEvict=all 压缩工作池。
- 范围：这是光照纹理 LOD 夹具，不是通用几何 LOD 系统。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/lodScaleScene.tsx)。

## 全封闭漏光房间 · 专用实验

- 入口：`/?scene=leak-room&cam=contact`。
- 看什么：封闭室内应为零光照，开缝后应恢复真实光线。
- 相机：contact, inside, floor, outside。
- 建议观察：比较 gap=0、1、20；使用 leak=1 逐阶段核对。
- 范围：gap 的单位是毫米；房间正确全黑不意味着贴图缺失。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/world/leakRoomScene.ts)。

## 物理水实验室 · 水池 · 独立实验室

- 入口：`/labs/water/?scene=pool`。
- 看什么：折射、反射、焦散、体积散射与测试物体。
- 相机：使用默认相机或实验室内置控制。
- 建议观察：补齐入口后用红柱、水下石块和水上球观察光学路径。
- 范围：调用 physicalWater.ts；catalog 声明了此路径，但固定树未找到对应 HTML 入口或路径接线，需先补接。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/labs/water/main.ts)。

## 物理水实验室 · 海面 · 独立实验室

- 入口：`/labs/water/?scene=ocean`。
- 看什么：风浪频谱、FFT 微细节、较大振幅水面。
- 相机：使用默认相机或实验室内置控制。
- 建议观察：补接入口后逐项改变 wind，结合 FFT/反射诊断看响应。
- 范围：海面有独立风速、水深和波幅设置；固定树未找到该实验室的 HTML 接线。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/labs/water/main.ts)。

## React Three Fiber 实验室 · 独立实验室

- 入口：`/labs/fiber/`。
- 看什么：定制 R3F、React 19 与 WebGPU 场景接入。
- 相机：使用默认相机或实验室内置控制。
- 建议观察：补齐入口、vendor/react-three-fiber 和 React 依赖后再启动。
- 范围：固定版本缺少 vendor、部分包声明和对应 HTML 入口；此处为作者声明路径。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/labs/fiber/main.tsx)。

## 渲染管线技术阅读页 · 独立资料

- 入口：`/pipeline`。
- 看什么：RDR2、Lumen、Alan Wake、Cyberpunk 的研究与本项目设计。
- 相机：使用默认相机或实验室内置控制。
- 建议观察：先补 src/app/pipeline.tsx 的页面入口，再分清技术比较与实际实现。
- 范围：有说明组件但未找到 /pipeline 接线；商业引擎技术讨论不自动计入本项目实现。
- [固定版本源码](https://github.com/vibegameengine/web-starter-kit-webgpu-pipline/blob/ca576b601bf84527102f1768372aa8cd96a3c55a/src/widgets/pipeline/PipelinePage.tsx)。
