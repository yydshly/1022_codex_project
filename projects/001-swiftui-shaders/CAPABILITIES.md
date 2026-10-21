# SwiftUIShaders 完整能力清单

研究固定版本：`6b644a8bd4f3131401bd6765990e476352d3cdef`。共 41 个公开修饰器。上游有 37 个动画封装，但其中 Shatter 不使用 time；实际为 36 个时间变化效果、3 个静态/参数驱动效果和 2 个交互效果。

[浏览器展示](web/standalone.html) · [研究说明](README.md) · [原生展示](native/README.md)

本文件由 `scripts/build_gallery.py` 从实际 Metal 签名与上游参数表生成。中文描述为本研究补充；每种效果都对应独立的原始算法。

## 总览

| 序号 | 效果 | 修饰器 | 分类 | 驱动 |
| --- | --- | --- | --- | --- |
| 01 | 极光 / Aurora | `bcsAurora` | 光影材质 | 时间 |
| 02 | 黑洞 / Black Hole | `bcsBlackHole` | 几何空间 | 时间 |
| 03 | 色彩分离 / Chromatic Split | `bcsChromaticSplit` | 色彩轮廓 | 时间 |
| 04 | 数据损坏 / Datamosh | `bcsDatamosh` | 故障解构 | 时间 |
| 05 | 粒化消散 / Disintegrate | `bcsDisintegrate` | 故障解构 | 时间 |
| 06 | 双色映射 / Duochrome | `bcsDuochrome` | 色彩轮廓 | 时间 |
| 07 | 重影回声 / Echo / Ghost | `bcsEcho` | 几何空间 | 时间 |
| 08 | 浮雕 / Emboss / Relief | `bcsEmboss` | 光影材质 | 静态 |
| 09 | 灵动光晕 / Ethereal Aura (v2) | `bcsEtherealAura` | 光影材质 | 时间 |
| 10 | 磨砂玻璃 / Frosted Glass | `bcsFrosted` | 光影材质 | 静态 |
| 11 | 几何螺旋 / Geometric Warp | `bcsGeometricWarp` | 几何空间 | 时间 |
| 12 | 数字故障 / Glitch | `bcsGlitch` | 故障解构 | 时间 |
| 13 | 引力井 / Gravity Wells | `bcsGravityWells` | 几何空间 | 时间 |
| 14 | 热浪 / Heat Shimmer | `bcsHeatShimmer` | 流体波纹 | 时间 |
| 15 | 全息镭射 / Holographic / Prismatic | `bcsHolographic` | 光影材质 | 时间 |
| 16 | 水墨晕染 / Ink Bleed / Domain Warp | `bcsInkBleed` | 流体波纹 | 时间 |
| 17 | 万花筒 / Kaleidoscope | `bcsKaleidoscope` | 几何空间 | 时间 |
| 18 | 液态金属 / Liquid Chrome | `bcsLiquidChrome` | 光影材质 | 时间 |
| 19 | 水面倒影 / Liquid Mirror | `bcsLiquidMirror` | 流体波纹 | 时间 |
| 20 | 连续涟漪 / Live Ripple | `bcsLiveRipple` | 流体波纹 | 时间 |
| 21 | 磁场 / Magnetic Field | `bcsMagneticField` | 流体波纹 | 时间 |
| 22 | 熔化 / Melt | `bcsMelt` | 故障解构 | 时间 |
| 23 | 有机呼吸 / Morph Breathe | `bcsMorphBreathe` | 流体波纹 | 时间 |
| 24 | 霓虹轮廓 / Neon Edge | `bcsNeonEdge` | 色彩轮廓 | 时间 |
| 25 | 立体马赛克 / Pixelate Mosaic | `bcsPixelateMosaic` | 故障解构 | 时间 |
| 26 | 像素风暴 / Pixelate Storm | `bcsPixelateStorm` | 故障解构 | 时间 |
| 27 | 等离子光 / Plasma | `bcsPlasma` | 光影材质 | 时间 |
| 28 | 心跳脉冲 / Pulse / Heartbeat | `bcsPulse` | 流体波纹 | 时间 |
| 29 | 交互透镜 / Refract Lens (Interactive) | `bcsRefractLens` | 触摸交互 | 交互 |
| 30 | 碎片散开 / Shatter | `bcsShatter` | 故障解构 | 参数 |
| 31 | 碎玻璃 / Shatter Glass | `bcsShatterGlass` | 光影材质 | 时间 |
| 32 | 冲击波 / Shockwave | `bcsShockwave` | 流体波纹 | 时间 |
| 33 | 烟雾显影 / Smoke Reveal | `bcsSmokeReveal` | 光影材质 | 时间 |
| 34 | 曝光反转 / Solarize | `bcsSolarize` | 色彩轮廓 | 时间 |
| 35 | 热成像 / Thermal | `bcsThermal` | 色彩轮廓 | 时间 |
| 36 | 等高线 / Topographic | `bcsTopographic` | 色彩轮廓 | 时间 |
| 37 | 触摸涟漪 / Touch Ripple | `bcsTouchRipple` | 触摸交互 | 交互 |
| 38 | 水下焦散 / Underwater Caustics | `bcsUnderwaterCaustics` | 流体波纹 | 时间 |
| 39 | 旋涡 / Vortex Spiral | `bcsVortex` | 几何空间 | 时间 |
| 40 | 波浪池 / Wave Pool | `bcsWavePool` | 流体波纹 | 时间 |
| 41 | 虫洞 / Wormhole | `bcsWormhole` | 几何空间 | 时间 |

## 公共修饰器参数

所有修饰器还接受 `maxSampleOffset: CGSize`，默认 `64×64`，表示向各轴偏移采样的最大距离。强位移需要增大此值；它是 SwiftUI 的采样边界声明。本浏览器预览不模拟 SwiftUI 的采样边界裁剪，使用完整图像采样。

## 完整效果与参数

### 01 · 极光 / Aurora

彩色光带缓慢掠过画面，像夜空中的极光。

原理：多层正弦光带、噪声扰动与亮度混合。

原始实现：[`bcs_aurora`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1558)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `intensity` | 强度 | `0.5` | 0.0 ～ 1.0 |
| `bands` | 光带数量 | `4.5` | 1.0 ～ 8.0 |
| `speed` | 速度 | `1.65` | 0.3 ～ 3.0 |
| `colorShift` | 色彩偏移 | `0.5` | 0.0 ～ 1.0 |

### 02 · 黑洞 / Black Hole

画面被中心引力拉弯，周围形成发光的吸积环。

原理：按径向距离改变采样坐标，叠加旋转光环与中心遮罩。

原始实现：[`bcs_blackHole`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L691)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `mass` | 中心质量 | `0.28` | 0.05 ～ 0.5 |
| `spin` | 旋转速度 | `2.5` | 0.0 ～ 5.0 |
| `distortion` | 扭曲程度 | `105` | 10.0 ～ 200.0 |
| `ringBrightness` | 光环亮度 | `1.0` | 0.0 ～ 2.0 |

### 03 · 色彩分离 / Chromatic Split

红绿蓝通道错开，制造棱镜边缘和光学色差。

原理：沿指定方向分别采样 RGB 通道，可按距中心的距离衰减。

原始实现：[`bcs_chromaticSplit`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L242)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `spread` | 分离距离 | `8.0` | 0.0 ～ 30.0 |
| `angle` | 方向角度 | `0.0` | 0.0 ～ 6.28 |
| `edgeOnly` | 边缘权重 | `0.5` | 0.0 ～ 1.0 |
| `animate` | 动画幅度 | `0.5` | 0.0 ～ 1.0 |

### 04 · 数据损坏 / Datamosh

图像块随机错位、拖抹，呈现视频解码故障的观感。

原理：随机块遮罩、采样偏移、通道分离与颜色量化。

原始实现：[`bcs_datamosh`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1898)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `blockCorruption` | 损坏比例 | `0.4` | 0.0 ～ 1.0 |
| `smearAmount` | 拖抹距离 | `30.0` | 0.0 ～ 60.0 |
| `colorBleed` | 颜色溢出 | `0.5` | 0.0 ～ 1.0 |
| `glitchRate` | 故障频率 | `2.0` | 0.5 ～ 5.0 |

### 05 · 粒化消散 / Disintegrate

画面沿噪声边界逐渐消散，留下发亮的燃烧边缘。

原理：噪声阈值决定透明度，并在阈值附近加入漂移和高光。

原始实现：[`bcs_disintegrate`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1739)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `threshold` | 阈值 | `0.0` | 0.0 ～ 1.0 |
| `edgeWidth` | 边缘宽度 | `0.12` | 0.05 ～ 0.3 |
| `driftAmount` | 漂移距离 | `25.0` | 0.0 ～ 50.0 |
| `direction` | 漂移方向 | `1.0` | 0.0 ～ 6.28 |

### 06 · 双色映射 / Duochrome

把明暗映射到两种色相，得到双色海报般的画面。

原理：以亮度为插值因子混合两种颜色，并调节对比度。

原始实现：[`bcs_duochrome`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1694)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `intensity` | 强度 | `0.5` | 0.0 ～ 1.0 |
| `hue1` | 暗部色相 | `0.5` | 0.0 ～ 1.0 |
| `hue2` | 亮部色相 | `0.5` | 0.0 ～ 1.0 |
| `contrast` | 对比度 | `1.25` | 0.5 ～ 2.0 |

### 07 · 重影回声 / Echo / Ghost

多层半透明轮廓沿一个方向展开，像视觉的回声。

原理：叠加多次偏移采样，以递减权重混合。

原始实现：[`bcs_echo`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L987)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `echoCount` | 重影数量 | `4.0` | 2.0 ～ 8.0 |
| `spread` | 分离距离 | `20.0` | 5.0 ～ 50.0 |
| `direction` | 漂移方向 | `0.785` | 0.0 ～ 6.28 |
| `fade` | 衰减 | `0.6` | 0.3 ～ 0.9 |

### 08 · 浮雕 / Emboss / Relief

细节呈现凸起或雕刻般的明暗，光线方向可以调节。

原理：沿光照方向比较相邻位置的亮度差。

原始实现：[`bcs_emboss`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L54)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `strength` | 强度 | `2.0` | 0.0 ～ 5.0 |
| `angle` | 方向角度 | `0.785` | 0.0 ～ 6.28 |
| `mixAmount` | 混合比例 | `0.8` | 0.0 ～ 1.0 |

### 09 · 灵动光晕 / Ethereal Aura (v2)

边缘呼吸、轻微液化，彩色光晕随时间起伏。

原理：边缘距离遮罩、噪声位移与周期性的光晕混合。

原始实现：[`bcs_etherealAura`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L609)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `auraWidth` | 光晕宽度 | `0.12` | 未指定 |
| `auraIntensity` | 光晕强度 | `1.0` | 未指定 |
| `pulseSpeed` | 脉冲速度 | `1.5` | 未指定 |
| `distortion` | 扭曲程度 | `8.0` | 未指定 |
| `hueShift` | 色相偏移 | `3.5` | 未指定 |

auraWidth：上游未指定范围；此滑块区间为本展示页的实验范围。 auraIntensity：上游未指定范围；此滑块区间为本展示页的实验范围。 pulseSpeed：上游未指定范围；此滑块区间为本展示页的实验范围。 distortion：上游未指定范围；此滑块区间为本展示页的实验范围。 hueShift：上游未指定范围；此滑块区间为本展示页的实验范围。

### 10 · 磨砂玻璃 / Frosted Glass

画面局部像蒙上霜雾，中心保留柔和的清晰窗口。

原理：噪声决定散射方向，五次邻域采样近似模糊。

原始实现：[`bcs_frosted`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L198)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `frostAmount` | 结霜程度 | `0.5` | 0.0 ～ 1.0 |
| `grainSize` | 霜晶尺度 | `10` | 1.0 ～ 20.0 |
| `clearRadius` | 清晰半径 | `0.5` | 0.0 ～ 1.0 |
| `clearSoftness` | 过渡柔度 | `0.5` | 0.0 ～ 1.0 |

### 11 · 几何螺旋 / Geometric Warp

画面卷入重复的螺旋，也可逐渐混入镜面对称。

原理：对数极坐标变换、循环缩放与扇区镜像。

原始实现：[`bcs_geometricWarp`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L2174)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `spiralTight` | 螺旋紧密度 | `3.0` | 1.0 ～ 8.0 |
| `zoomRepeat` | 重复缩放 | `1.0` | 0.3 ～ 2.0 |
| `rotation` | 旋转角度 | `0.0` | 0.0 ～ 6.28 |
| `blend` | 镜像混合 | `0.0` | 0.0 ～ 1.0 |

### 12 · 数字故障 / Glitch

间歇性的横向撕裂、扫描线和 RGB 错位。

原理：按时间和图像条带生成随机位移与通道偏移。

原始实现：[`bcs_glitch`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L432)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `intensity` | 强度 | `0.5` | 0.0 ～ 1.0 |
| `blockSize` | 图块大小 | `15.0` | 2.0 ～ 50.0 |
| `scanLines` | 扫描线 | `0.4` | 0.0 ～ 1.0 |
| `colorShift` | 色彩偏移 | `8.0` | 0.0 ～ 20.0 |

### 13 · 引力井 / Gravity Wells

多个移动的引力中心同时牵引、扭曲画面。

原理：叠加多个径向衰减的采样偏移场。

原始实现：[`bcs_gravityWells`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1431)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `wellStrength` | 引力强度 | `80.0` | 10.0 ～ 200.0 |
| `wellCount` | 引力井数量 | `3.0` | 1.0 ～ 5.0 |
| `orbitSpeed` | 轨道速度 | `0.8` | 0.1 ～ 3.0 |
| `warpFalloff` | 引力衰减 | `2.0` | 0.5 ～ 5.0 |

### 14 · 热浪 / Heat Shimmer

画面像隔着热空气一样轻微摇晃，上方可更明显。

原理：不同频率的正弦波叠加为采样位移。

原始实现：[`bcs_heatShimmer`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L87)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `amplitude` | 位移幅度 | `10` | 0.0 ～ 20.0 |
| `frequency` | 频率 | `16` | 1.0 ～ 30.0 |
| `speed` | 速度 | `2.75` | 0.5 ～ 5.0 |
| `verticalBias` | 顶部权重 | `0.5` | 0.0 ～ 1.0 |

### 15 · 全息镭射 / Holographic / Prismatic

彩虹光泽掠过图像，明亮区域像镭射卡纸一样反光。

原理：三个相位错开的正弦波生成彩虹，再按原图亮度叠加。

原始实现：[`bcs_holographic`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L120)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `intensity` | 强度 | `0.4` | 0.0 ～ 1.0 |
| `scale` | 纹理尺度 | `8.0` | 1.0 ～ 20.0 |
| `speed` | 速度 | `1.0` | 0.1 ～ 3.0 |
| `angleOffset` | 光带角度 | `0.785` | 0.0 ～ 6.28 |

### 16 · 水墨晕染 / Ink Bleed / Domain Warp

图像像湿纸上的颜料一样缓慢渗化、流动。

原理：多层分形噪声相互扰动，形成 domain warping 位移场。

原始实现：[`bcs_inkBleed`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L161)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `warpStrength` | 扭曲强度 | `15.0` | 0.0 ～ 50.0 |
| `scale` | 纹理尺度 | `4.0` | 1.0 ～ 10.0 |
| `speed` | 速度 | `0.5` | 0.1 ～ 2.0 |
| `detail` | 噪声层数 | `5.0` | 2.0 ～ 8.0 |

### 17 · 万花筒 / Kaleidoscope

原图被折叠成旋转、对称的放射状花纹。

原理：在极坐标中折叠角度，再映射回图像采样。

原始实现：[`bcs_kaleidoscope`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L805)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `segments` | 镜像分段 | `9.0` | 2.0 ～ 16.0 |
| `rotation` | 旋转角度 | `3.14` | 0.0 ～ 6.28 |
| `zoom` | 缩放 | `1.75` | 0.5 ～ 3.0 |
| `animateSpeed` | 自转速度 | `1.0` | 0.0 ～ 2.0 |

### 18 · 液态金属 / Liquid Chrome

表面像流动的水银，带有起伏的白色金属高光。

原理：噪声位移、由高度差估算法线、去饱和与镜面高光。

原始实现：[`bcs_liquidChrome`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L383)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `distortion` | 扭曲程度 | `15` | 0.0 ～ 30.0 |
| `chromeIntensity` | 金属强度 | `0.5` | 0.0 ～ 1.0 |
| `flowSpeed` | 流动速度 | `1.55` | 0.1 ～ 3.0 |
| `reflectionScale` | 反射尺度 | `5.5` | 1.0 ～ 10.0 |

### 19 · 水面倒影 / Liquid Mirror

画面下部变成有涟漪的倒影，反射边界平滑过渡。

原理：翻转局部纵坐标，叠加波纹并按深度衰减。

原始实现：[`bcs_liquidMirror`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1488)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `mirrorAxis` | 反射起点 | `0.55` | 0.3 ～ 0.7 |
| `ripple` | 涟漪幅度 | `12.0` | 2.0 ～ 30.0 |
| `speed` | 速度 | `1.5` | 0.5 ～ 3.0 |
| `depth` | 深度 | `0.5` | 0.0 ～ 1.0 |

### 20 · 连续涟漪 / Live Ripple

多个波源持续产生向外扩散的同心波纹。

原理：多波源的径向正弦位移叠加，并按距离衰减。

原始实现：[`bcs_liveRipple`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L281)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `amplitude` | 位移幅度 | `12.0` | 0.0 ～ 30.0 |
| `frequency` | 频率 | `25.0` | 5.0 ～ 60.0 |
| `speed` | 速度 | `4.0` | 1.0 ～ 10.0 |
| `damping` | 距离衰减 | `2.0` | 0.5 ～ 5.0 |
| `ringCount` | 波源数量 | `3.0` | 1.0 ～ 5.0 |

### 21 · 磁场 / Magnetic Field

图像沿弯曲的力线流动，呈现磁流体般的走势。

原理：模拟磁偶极场方向，用场向量和噪声改变采样坐标。

原始实现：[`bcs_magneticField`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1951)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `fieldStrength` | 磁场强度 | `40.0` | 5.0 ～ 80.0 |
| `lineCount` | 线条数量 | `8.0` | 3.0 ～ 20.0 |
| `fieldTurbulence` | 磁场扰动 | `0.5` | 0.0 ～ 1.0 |
| `polarity` | 磁极形态 | `0.0` | 0.0 ～ 1.0 |

### 22 · 熔化 / Melt

图像像被加热的蜡一样向下融化、滴落。

原理：按列生成噪声下垂量，并叠加暖色与边缘高光。

原始实现：[`bcs_melt`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L759)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `meltAmount` | 熔化距离 | `40.0` | 0.0 ～ 100.0 |
| `dripScale` | 滴流尺度 | `6.0` | 1.0 ～ 15.0 |
| `speed` | 速度 | `1.0` | 0.1 ～ 3.0 |
| `heat` | 暖色偏移 | `0.3` | 0.0 ～ 1.0 |

### 23 · 有机呼吸 / Morph Breathe

画面整体缓慢膨胀、收缩，并带有不规则起伏。

原理：周期性的径向变形叠加分形噪声扰动。

原始实现：[`bcs_morphBreathe`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1366)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `breatheDepth` | 呼吸幅度 | `28` | 5.0 ～ 50.0 |
| `breatheRate` | 呼吸频率 | `1.65` | 0.3 ～ 3.0 |
| `warpComplexity` | 扰动层数 | `4.5` | 1.0 ～ 8.0 |
| `organic` | 有机程度 | `0.5` | 0.0 ～ 1.0 |

### 24 · 霓虹轮廓 / Neon Edge

图像的轮廓变成流动的彩色霓虹线条。

原理：Sobel 亮度边缘检测、按边缘方向着色与亮度增强。

原始实现：[`bcs_neonEdge`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1142)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `edgeStrength` | 轮廓强度 | `5.5` | 1.0 ～ 10.0 |
| `glowAmount` | 发光强度 | `4.0` | 0.0 ～ 2.0 |
| `colorCycle` | 变色速度 | `1.0` | 0.0 ～ 3.0 |
| `mixOriginal` | 原图权重 | `1.0` | 0.0 ～ 1.0 |

glowAmount：上游默认值超出建议区间；滑块已扩展以保留原默认值。

### 25 · 立体马赛克 / Pixelate Mosaic

画面变成带斜面、间隙的方砖，并能动态聚合。

原理：网格量化采样、砖块偏移与程序化斜面明暗。

原始实现：[`bcs_pixelateMosaic`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1839)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `pixelSize` | 像素大小 | `20.0` | 4.0 ～ 60.0 |
| `bevel` | 斜面强度 | `0.6` | 0.0 ～ 1.0 |
| `animateAssemble` | 聚合动画 | `0.5` | 0.0 ～ 1.0 |
| `gap` | 砖块间隙 | `0.05` | 0.0 ～ 0.3 |

### 26 · 像素风暴 / Pixelate Storm

像素块脉冲、偏移，卷入旋转的像素风暴。

原理：网格采样、随机块偏移与极坐标旋转。

原始实现：[`bcs_pixelateStorm`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1202)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `pixelSize` | 像素大小 | `21` | 2.0 ～ 40.0 |
| `stormAmount` | 风暴强度 | `0.5` | 0.0 ～ 1.0 |
| `swirl` | 旋转强度 | `1.5` | 0.0 ～ 3.0 |
| `pulse` | 脉冲频率 | `1.5` | 0.0 ～ 3.0 |

### 27 · 等离子光 / Plasma

彩色能量波在原图上交错、流动。

原理：多组正弦场和噪声构造彩色干涉图案。

原始实现：[`bcs_plasma`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L927)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `intensity` | 强度 | `0.5` | 0.0 ～ 1.0 |
| `scale` | 纹理尺度 | `5.5` | 1.0 ～ 10.0 |
| `speed` | 速度 | `2.75` | 0.5 ～ 5.0 |
| `colorMode` | 配色模式 | `0.5` | 0.0 ～ 1.0 |

### 28 · 心跳脉冲 / Pulse / Heartbeat

画面按指定 BPM 律动，边缘同步闪动。

原理：周期性的尖峰波形驱动径向位移和边缘光。

原始实现：[`bcs_pulse`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L533)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `amplitude` | 位移幅度 | `15.0` | 0.0 ～ 30.0 |
| `bpm` | 每分钟心跳 | `72.0` | 30.0 ～ 180.0 |
| `sharpness` | 脉冲锐度 | `3.0` | 1.0 ～ 10.0 |
| `glowIntensity` | 边缘光 | `0.5` | 0.0 ～ 1.0 |

### 29 · 交互透镜 / Refract Lens (Interactive)

拖动玻璃球，让局部画面折射、放大并出现彩边。

原理：以交互点为中心计算球面折射、边缘扭曲和色散。

原始实现：[`bcs_refractLens`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L845)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `touchPos` | 交互位置 | `center` | 未指定 |
| `lensRadius` | 透镜半径 | `0.3` | 0.1 ～ 0.5 |
| `refraction` | 折射强度 | `2.0` | 1.0 ～ 3.0 |
| `aberration` | 色散距离 | `5.0` | 0.0 ～ 15.0 |
| `wobble` | 边缘起伏 | `0.5` | 0.0 ～ 1.0 |

### 30 · 碎片散开 / Shatter

画面沿不规则碎片分开，碎片带玻璃高光。

原理：Voronoi 单元确定碎片，按单元偏移和旋转采样。

原始实现：[`bcs_shatter`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1031)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `shardCount` | 碎片密度 | `16` | 3.0 ～ 30.0 |
| `explode` | 散开程度 | `0.5` | 0.0 ～ 1.0 |
| `rotationAmt` | 碎片转角 | `1.5` | 0.0 ～ 3.0 |
| `edgeGlow` | 裂缝发光 | `1.0` | 0.0 ～ 2.0 |

上游以动画包装器传入 `time`，但函数体不使用它。碎片散开程度由 `explode` 控制；只播放时间不会改变画面。

### 31 · 碎玻璃 / Shatter Glass

玻璃裂纹布满画面，裂缝处出现折射和棱镜彩边。

原理：Voronoi 最近与次近距离确定裂纹，叠加折射与色散。

原始实现：[`bcs_shatterGlass`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L2223)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `crackDensity` | 裂纹密度 | `8.0` | 3.0 ～ 15.0 |
| `glassRefraction` | 裂缝折射 | `10.0` | 0.0 ～ 20.0 |
| `prismStrength` | 棱镜强度 | `0.5` | 0.0 ～ 1.0 |
| `shatterSpread` | 碎片分离 | `0.0` | 0.0 ～ 1.0 |

### 32 · 冲击波 / Shockwave

明亮的冲击环周期性扩散，沿途拉动图像。

原理：按传播半径计算环形遮罩，再执行径向采样偏移。

原始实现：[`bcs_shockwave`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1250)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `waveSpeed` | 传播速度 | `200.0` | 50.0 ～ 500.0 |
| `ringWidth` | 波环宽度 | `30.0` | 5.0 ～ 60.0 |
| `strength` | 强度 | `40.0` | 5.0 ～ 80.0 |
| `repeatRate` | 重复间隔 | `2.0` | 0.5 ～ 5.0 |

### 33 · 烟雾显影 / Smoke Reveal

内容在流动的烟雾中显露，伴随柔和的光线。

原理：分形噪声构建烟雾密度，控制图像混合与光束亮度。

原始实现：[`bcs_smokeReveal`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L2124)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `smokeAmount` | 烟雾浓度 | `0.6` | 0.0 ～ 1.0 |
| `smokeScale` | 烟雾尺度 | `5.0` | 2.0 ～ 10.0 |
| `windSpeed` | 风速 | `1.5` | 0.5 ～ 3.0 |
| `smokeTurb` | 烟雾扰动 | `1.5` | 0.5 ～ 3.0 |

### 34 · 曝光反转 / Solarize

画面局部反相，出现强烈、超现实的色彩分区。

原理：按阈值和曲线对 RGB 通道执行非线性色彩映射。

原始实现：[`bcs_solarize`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1801)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `threshold` | 阈值 | `0.5` | 0.2 ～ 0.8 |
| `curveIntensity` | 曲线强度 | `1.5` | 0.0 ～ 3.0 |
| `colorSeparation` | 颜色分离 | `0.5` | 0.0 ～ 1.0 |
| `animate` | 动画幅度 | `0.5` | 0.0 ～ 1.0 |

### 35 · 热成像 / Thermal

明暗转为冷暖热力色带，并带有热空气扰动。

原理：按亮度映射伪彩色，再加入噪声位移；颜色不代表真实温度。

原始实现：[`bcs_thermal`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1312)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `intensity` | 强度 | `0.8` | 0.0 ～ 1.0 |
| `shimmer` | 热扰动 | `5.0` | 0.0 ～ 15.0 |
| `noiseSpeed` | 噪声速度 | `1.5` | 0.5 ～ 3.0 |
| `paletteShift` | 色带偏移 | `0.0` | 0.0 ～ 1.0 |

### 36 · 等高线 / Topographic

明暗层次变成密集等高线，像一张彩色地形图。

原理：把原图亮度分层，用周期阈值描出主次轮廓线。

原始实现：[`bcs_topographic`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L2070)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `lineCount` | 线条数量 | `20.0` | 5.0 ～ 40.0 |
| `lineWidth` | 线条宽度 | `0.05` | 0.01 ～ 0.15 |
| `colorize` | 着色比例 | `0.7` | 0.0 ～ 1.0 |
| `animate` | 动画幅度 | `0.3` | 0.0 ～ 1.0 |

### 37 · 触摸涟漪 / Touch Ripple

点击画面，从触点产生扩散后逐渐消退的水波。

原理：传播半径由 touchAge 决定，正弦波包络控制位移与衰减。

原始实现：[`bcs_touchRipple`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L330)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `touchPos` | 交互位置 | `center` | 未指定 |
| `touchAge` | 触摸经过时间 | `1.0` | 未指定 |
| `amplitude` | 位移幅度 | `15.0` | 0.0 ～ 30.0 |
| `frequency` | 频率 | `20.0` | 5.0 ～ 40.0 |
| `speed` | 速度 | `300.0` | 50.0 ～ 500.0 |
| `decay` | 时间衰减 | `2.0` | 0.5 ～ 4.0 |

touchAge：上游未指定范围；此滑块区间为本展示页的实验范围。

调用方必须在触摸后持续更新 `touchAge`；只设置一个固定值会得到相应时刻的静态波纹。本页支持点击、时间推进和手动调整。

### 38 · 水下焦散 / Underwater Caustics

游动的水光、波纹和淡蓝色深度感覆盖画面。

原理：多层周期场生成焦散亮纹，叠加水面位移和光束。

原始实现：[`bcs_underwaterCaustics`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L2011)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `causticScale` | 焦散尺度 | `6.0` | 2.0 ～ 15.0 |
| `causticIntensity` | 水光强度 | `1.0` | 0.0 ～ 2.0 |
| `waterDistortion` | 水面扭曲 | `12.0` | 0.0 ～ 30.0 |
| `waterDepth` | 水体深度 | `0.4` | 0.0 ～ 1.0 |

### 39 · 旋涡 / Vortex Spiral

图像围绕中心旋转、扭曲，中心与边缘转角不同。

原理：按径向距离指数衰减旋转角，重新映射采样坐标。

原始实现：[`bcs_vortex`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L491)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `twistAmount` | 扭转角度 | `3.0` | 0.0 ～ 10.0 |
| `radius` | 作用半径 | `0.5` | 0.1 ～ 1.0 |
| `speed` | 速度 | `0.5` | 0.1 ～ 3.0 |
| `falloff` | 距离衰减 | `2.0` | 0.5 ～ 5.0 |

### 40 · 波浪池 / Wave Pool

多个方向的波浪交叠，让画面像水面一样起伏。

原理：叠加不同方向和频率的正弦位移场。

原始实现：[`bcs_wavePool`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L574)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `amplitude` | 位移幅度 | `12` | 0.0 ～ 25.0 |
| `wavelength` | 波长 | `22` | 5.0 ～ 40.0 |
| `speed` | 速度 | `2.75` | 0.5 ～ 5.0 |
| `complexity` | 叠加波数 | `3.5` | 1.0 ～ 6.0 |

### 41 · 虫洞 / Wormhole

画面卷进带纵深与旋转感的隧道。

原理：径向透视式缩放、角度扭转与中心雾化。

原始实现：[`bcs_wormhole`](upstream/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L1624)。

| 参数 | 含义 | 上游默认 | 上游建议范围 |
| --- | --- | --- | --- |
| `depth` | 深度 | `4.5` | 1.0 ～ 8.0 |
| `speed` | 速度 | `1.65` | 0.3 ～ 3.0 |
| `twist` | 隧道扭转 | `2.5` | 0.0 ～ 5.0 |
| `radius` | 作用半径 | `0.3` | 0.1 ～ 0.5 |
