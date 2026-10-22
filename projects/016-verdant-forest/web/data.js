'use strict';
window.FOREST_RESEARCH = {
  commit: 'bb724d84fb683b8f1dea790c3e56f2ffadeb051e',
  repository: 'https://github.com/Leonxlnx/verdant-forest',
  capabilities: [
    {icon:'↗', title:'走进森林', text:'自由移动、升降和转向，支持鼠标、键盘与触屏。镜头可以贴近林下，也可以升到树冠。'},
    {icon:'♧', title:'生成自然结构', text:'树干、分枝、弯曲叶片与蕨类由规则生成，叠加枯木、苔藓、落叶与野花。'},
    {icon:'≈', title:'让环境动起来', text:'顶点着色器计算树枝摆动、叶片颤动与草丛起伏；阴影使用相应的几何变形。'},
    {icon:'◷', title:'组织镜头与输出', text:'内置五镜头、30 秒导览。捕获模式按指定时间渲染，再由配套脚本逐帧采集和编码。'}
  ],
  gallery: [
    {title:'贴近林下', tag:'01 / UNDERSTORY', src:'assets/upstream/forest-floor.png', alt:'林下视角：紫色野花、蕨类、草丛与高大的树干，远处有薄雾', text:'观察花草前景、树干遮挡，以及从近到远的颜色变化。', caption:'8.0 s · flowers-and-ferns · 1280 × 720。作者保存的真实浏览器 WebGL 逐帧采样；未做图像增强。'},
    {title:'升到树冠', tag:'02 / CANOPY', src:'assets/upstream/canopy-start.png', alt:'25 秒树冠镜头：从高处观察立体树冠与林间地表', text:'抬高镜头后，树冠仍有体积，林下地表也保持绿色覆盖。', caption:'25.0 s · canopy-reveal · 1280 × 720。来自上游 frame-0750.png；文件名中的帧序号使用 30 fps 采样编号。'},
    {title:'看向远方', tag:'03 / DEPTH', src:'assets/upstream/canopy.png', alt:'28 秒树冠镜头：近景枝叶、成片树冠和逐渐淡入天际的远景树林', text:'近处枝叶清晰，远处以简化树冠、覆盖色与雾维持纵深。', caption:'28.0 s · canopy-reveal · 1280 × 720。来自上游 frame-0840.png；静态帧不代表实时性能。'}
  ],
  shots: [
    {name:'林间小径', time:'00 — 08 s', duration:8},
    {name:'野花与蕨类', time:'08 — 14 s', duration:6},
    {name:'阳光下的树林', time:'14 — 20 s', duration:6},
    {name:'苔藓与枯木', time:'20 — 25 s', duration:5},
    {name:'树冠展开', time:'25 — 30 s', duration:5}
  ],
  labs: [
    {id:'terrain', label:'起伏地形', english:'PROCEDURAL TERRAIN', title:'用多层噪声，叠出自然起伏。', text:'在网格的每个位置计算高度，把大尺度坡地和小尺度凹凸叠加。树木落地时也读取实际地形高度，避免树根悬空。', range:'起伏强度', min:0,max:100,initial:48,unit:'%',ends:['平缓','起伏明显'], insight:'本页用几组不同频率的波形演示叠加。上游实际使用多层噪声 fbm，并对地形三角形插值，统一植被落点和地面高度。', source:'app/forest/math.ts#L2-L29'},
    {id:'geometry',label:'立体枝叶',english:'CURVED LEAF GEOMETRY',title:'把一片叶子，做成曲面。',text:'改变顶点位置，让叶片有中脊、弯曲、杯状凹陷和扭转。观察角度变化时，真实几何带来不同的轮廓与受光。',range:'叶片弯曲程度',min:0,max:100,initial:65,unit:'%',ends:['平展','弯曲 / 扭转'],insight:'本页放大一片 96 三角形的教学叶片。上游乔木的叶片按细节层级使用 8 / 4 / 2 个三角形；蕨类和灌木有各自的植物几何。',source:'app/forest/trees.js#L229-L290'},
    {id:'instances',label:'批量成林',english:'SHARED GEOMETRY / INSTANCING',title:'少量树形，组成整片森林。',text:'重复使用共享的植物网格。每个实例只改变位置、朝向、缩放和色调；按空间分区组织，再对可见区域更新。',range:'摆放的实例数',min:16,max:160,initial:96,unit:' 株',ends:['16 株','160 株'],insight:'这里用三种简化树形重复摆放。上游先生成八个乔木变体，使用 InstancedMesh 复用；随机流和空间规则同时保证重复性与自然分布。',source:'app/forest/vegetation.ts#L14-L103'},
    {id:'wind',label:'风动着色',english:'TIME + POSITION → VERTEX OFFSET',title:'时间流动，枝叶轻轻摆动。',text:'把时间、植株位置和顶点高度带入波形函数。同一株植物共同摆动，不同位置错开相位，叶尖再叠加细小颤动。',range:'示意风力',min:0,max:100,initial:50,unit:'%',ends:['静止','明显摆动'],insight:'本页用 Canvas 画简化草木。原版在 GPU 顶点着色器中完成位移，深度材质也使用相应逻辑，让阴影与叶片一起动。',source:'app/forest/materials.ts#L22-L100'},
    {id:'lod',label:'远近取舍',english:'DISTANCE → LEVEL OF DETAIL',title:'把细节，留给你看得见的地方。',text:'近处保留细致叶片，远处减少几何复杂度并维持树冠覆盖。更远的草逐渐降低密度，远景树林再切换专门的共享池。',range:'分区中心水平距离',min:0,max:100,initial:12,unit:' m',ends:['近处 0 m','远处 100 m'],insight:'这里对应桌面、quality=1 的乔木分区示例：24 m 内高细节，24–56 m 中细节，之后低细节。移动端、植物类型和质量系数会改变阈值。',source:'app/forest/vegetation.ts#L223-L255'}
  ],
  pipeline: [
    {symbol:'△',title:'几何与材质',text:'真实枝叶搭配树皮、地面、石块材质，输出颜色与场景深度。',label:'Geometry / PBR'},
    {symbol:'☀',title:'太阳与阴影',text:'方向光和天空补光建立明暗；树冠阴影决定地面和空气哪里能见光。',label:'Directional light / Shadows'},
    {symbol:'∴',title:'接触与空气',text:'屏幕空间遮蔽加强根部接触感；沿视线采样累积空气中的单次散射。',label:'Contact occlusion / Scattering'},
    {symbol:'◐',title:'合成与色调',text:'将空气与遮蔽合回场景，加入远景薄雾、色调映射和冷暖分离。',label:'Composite / ACES / sRGB'}
  ],
  values: [
    {tag:'01 / EXPERIENCE',title:'自然主题的沉浸展示',text:'让访客通过移动和观察建立空间感。适合自然主题展览、品牌概念页和视觉叙事原型。',reuse:'植物层次、自由镜头、林间光影',cost:'需要自己的内容、加载策略与目标设备优化'},
    {tag:'02 / ENGINEERING',title:'Web 3D 场景的技术样本',text:'把程序化建模、实例化、细节层级和后处理放在同一套可读代码中，便于逐层理解取舍。',reuse:'模块划分、共享网格、距离细节、资源清理',cost:'需要独立测量 CPU / GPU 成本和交互帧率'},
    {tag:'03 / CREATION',title:'可重复的镜头与画面',text:'固定随机种子和明确时间采样，方便在相同镜头下检查材质变化，或探索自然场景短片。',reuse:'确定性场景、五镜头编排、逐帧采集方式',cost:'视频仍需采集和编码；24 fps 播放不等于实时渲染'}
  ],
  sources: [
    ['项目说明与运行范围','README.md'],['场景与资源生命周期','app/forest/engine.ts'],['地形与确定性随机','app/forest/math.ts'],['乔木生成与叶片几何','app/forest/trees.js'],['蕨类与灌木建模','app/forest/botanical-refinement.js'],['摆放、实例化与 LOD','app/forest/vegetation.ts'],['风动、树皮与材质','app/forest/materials.ts'],['体积光与接触遮蔽','app/forest/volumetrics.ts'],['五镜头与时间采样','app/forest/cinematic.ts'],['光照与场景范围','app/forest/config.ts'],['浏览器截图记录','artifacts/browser-approved-review/capture-report-0.json'],['1080p 影片验证记录','artifacts/upgrade-capture-run.json'],['纹理与依赖来源声明','public/credits.txt']
  ]
};
