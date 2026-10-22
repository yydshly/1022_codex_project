// This adapter is copied into the pinned upstream's .atlas/ directory before build.
// Scene, GI, shadows and frame composition are imported from the original library.
import GUI from 'lil-gui';
import type { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import type { Mesh, InstancedMesh } from 'three/webgpu';
import { initRenderer } from '../src/shared/render/renderer.ts';
import { createRenderPipeline, type SceneHost } from '../src/features/render-pipeline/index.ts';
import { createCornellScene, populateCornell } from '../src/widgets/world/cornellScene.ts';
import { staticInteriorVolume } from '../src/shared/gi/probes/index.ts';
import { onBootProgress } from '../src/shared/ui/bootProgress.ts';

const CHANNEL = 'render-atlas-live-v1';
const $ = (id: string) => document.getElementById(id)!;
const params = new URLSearchParams(location.search);
const labels: Record<string, string> = { cornell: 'Cornell Box', 'midsee-village': '海岸村庄', beach: '热带海滩', forest: '针叶林与溪流' };
const requestedScene = params.get('scene') || 'cornell';
const scene = Object.hasOwn(labels, requestedScene) ? requestedScene : 'cornell';
const village = scene === 'midsee-village';
const beach = scene === 'beach';
const forest = scene === 'forest';
const sceneLabel = labels[scene];
const session = params.get('session') || '';
const cameraLimits = village ? [8, 120] : beach ? [0.8, 100] : forest ? [0.8, 160] : [5, 24];
const cameraElevationLimits = beach || forest ? [-60, 85] : [-10, 75];
const cameraPresets: Record<string, number[]> = village
  ? { front: [0,17,46,0,2,-1], side: [46,16,0,0,2,-1], above: [15,24,16,0,3,-5], detailA: [12,6,13,2,3,-2], detailB: [15,18,8,0,6,-5] }
  : beach ? { front: [0,12,28,.4,-.7,0], side: [20,12,18,.4,-.7,0], above: [-4,24,8,.4,-.7,0], detailA: [-2,3.5,7.5,-1.5,-.6,1.5], detailB: [-1.5,3.2,-.8,3.2,3.6,-3.6] }
  : forest ? { front: [0,12,26,0,1,-.6], side: [22,10,14,0,1,-.6], above: [-4,22,5,0,0,-.6], detailA: [-.6,2.2,3,-3,.5,-1.6], detailB: [1.6,2.4,5,3,6.5,-2] }
  : { front: [0,2.3,11,0,2.3,1], side: [-5.510086,4.79494,11.363919,0,2.3,1], above: [0,9.342073,14.244214,0,2.3,1] };
const detailLabels = village ? ['码头近看', '屋顶近看'] : beach ? ['水面近看', '棕榈叶片'] : forest ? ['溪流近看', '树冠仰看'] : [];
let initialCamera: number[] = [];
let initialTarget: number[] = [];
let sceneStats: Record<string, unknown> = {};
let commandRevision = 0;
const defaults: Record<string, string> = {
  scene: 'cornell', settings: 'off', hud: '0', inspector: '0', bakeCache: '0',
  iters: '64', bakeSeconds: '4', rays: '16', probeIters: '64', probeRays: '16',
  sample: '0.25', lmDensity: '0.08', probeSpacing: '3', mover: '0',
  reflections: '0', probeSpecular: '0', fog: '0', glare: '0', motionBlur: '0',
  grain: '0', aa: 'fxaa', exposure: '1', warmup: '1', sun: '4',
  sunAz: '45', sunEl: '55',
};
defaults.scene = scene;
if (village) Object.assign(defaults, { lm: '2048', sample: '0.7', lmDensity: '0.12', probeSpacing: '8', bakeSeconds: '6', probeIters: '32' });
if (beach) Object.assign(defaults, { lm: '1024', sample: '0.5', lmDensity: '0.12', probeSpacing: '5', bakeSeconds: '6', probeIters: '32', van: '0' });
if (forest) Object.assign(defaults, { lm: '2048', sample: '0.7', lmDensity: '0.12', probeSpacing: '12', bakeSeconds: '6', probeIters: '32' });
for (const [key, value] of Object.entries(defaults)) if (!params.has(key)) params.set(key, value);
history.replaceState(null, '', `${location.pathname}?${params}`);

type EngineHooks = Window & {
  __probe: () => { sunIntensity: number; lightCfg: { azimuthDeg: number; elevationDeg: number; intensity: number }; camera: number[]; target: number[] };
  __camera: (...values: number[]) => void;
  __audit: { sun: (a: number, e: number, i: number) => void; pause: (value: boolean) => void; bakeStatus: () => unknown };
};
const engine = window as unknown as EngineHooks;
let renderer: Awaited<ReturnType<typeof initRenderer>>['renderer'];
let gui: GUI;
let host: Omit<SceneHost, 'controls' | 'skyIsBackground' | 'moverByDefault'> & { controls: OrbitControls };
let ready = false;
let failed = false;
let paused = false;
let bakedSun: number[] = [];
let bootStart = performance.now();
let deviceInfo: Record<string, unknown> = {};

function send(type: string, payload: Record<string, unknown> = {}) {
  if (parent !== window) parent.postMessage({ channel: CHANNEL, session, scene, type, ...payload }, location.origin);
}
function stage(text: string) {
  const villageStages: Record<string, string> = {
    'Village: rock and dirt textures': '读取村庄岩石与地面纹理', 'Village: headland terrain': '生成村庄海岸地形',
    'Village: sand layer maps': '读取沙滩分层纹理', 'Village: shore terrain surface': '生成海岸表面',
    'Village: shore rock variants': '生成岸边岩石变体', 'Village: placing the shore rocks': '布置海岸岩石',
    'Village: house and quay materials': '读取房屋、植被与码头材质', 'Village: raising the houses and the quay': '搭建房屋与码头',
    'Village: bathymetry': '采样水底地形与障碍物', 'Village: settling the water simulation': '预运行浅水模拟',
    'Village: water and backdrop': '装配水面与背景',
  };
  text = villageStages[text] || text;
  text = text.replace('Beach: rock and dirt textures', '读取海滩岩石与地面纹理').replace('Beach: sand layer maps', '读取沙滩分层纹理').replace('Beach: island', '生成海滩地形').replace('Beach: rocks', '布置海滩岩石').replace('Beach: bathymetry', '采样水底与障碍物').replace('Beach: settling the water simulation', '预运行海滩浅水模拟').replace(/Beach: palm (\d+) of (\d+)/, '生成棕榈 $1 / $2').replace(/Beach: undergrowth (\d+) of (\d+)/, '生成灌木 $1 / $2');
  text = text.replace(/Baking lightmap [\d.]+% · pass (\d+)/, '烘焙光照贴图 · 第 $1 轮（至少 32 轮）').replace('Baking lightmap', '烘焙光照贴图').replace(/pass (\d+)/, '第 $1 轮').replace('Baking probes', '烘焙空间探针').replace('Compiling shaders', '编译着色器').replace('Waiting for the first frame', '等待首帧').replace('Building the static BVH', '构建静态 BVH').replace('Resolving lightmap page', '合成光照贴图页').replace('Unwrapping lightmap UVs', '分配光照贴图 UV').replace('Seeding lightmap page', '布置光照页采样点');
  $('runtime-stage').textContent = text;
  $('runtime-loading').hidden = false;
  send('progress', { text, elapsed: Math.round((performance.now() - bootStart) / 1000) });
}
function fail(error: unknown) {
  if (failed) return;
  failed = true;
  ready = false;
  const text = error instanceof Error ? error.message : String(error);
  $('runtime-loading').hidden = true;
  $('runtime-error-panel').hidden = false;
  $('runtime-error').textContent = text;
  $('frame-label').textContent = 'WebGPU 启动失败';
  send('error', { text });
  console.error(error);
}
function state() {
  const s = engine.__probe();
  const [x, y, z] = s.camera.map((v, i) => v - s.target[i]);
  const distance = Math.hypot(x, y, z);
  const sun = [s.lightCfg.azimuthDeg, s.lightCfg.elevationDeg, s.lightCfg.intensity];
  return {
    sunAzimuth: sun[0], sunElevation: sun[1], sunIntensity: sun[2],
    cameraAzimuth: Math.atan2(x, z) * 180 / Math.PI,
    cameraElevation: Math.asin(y / distance) * 180 / Math.PI,
    cameraDistance: distance, camera: s.camera, target: s.target,
    paused, bakedSun, stale: sun.some((v, i) => Math.abs(v - bakedSun[i]) > 0.001),
    frame: renderer.info.frame, renderCalls: renderer.info.render.calls, computeCalls: renderer.info.compute.calls, commandRevision,
    device: deviceInfo, pipeline: 'render-pipeline', scene, sceneLabel, cameraLimits, cameraElevationLimits, detailLabels, sceneStats,
  };
}
function notify() {
  if (!ready || failed) return;
  const current = state();
  $('frame-label').textContent = `${paused ? '画面已暂停' : '真实 WebGPU'} · ${sceneLabel} · ${current.stale ? '间接光待重烘焙' : '烘焙与当前太阳一致'}`;
  send('state', { state: current });
}
function number(value: unknown, min: number, max: number) {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error('控制参数必须是有限数值');
  return Math.max(min, Math.min(max, value));
}
function sun(command: Record<string, unknown>) {
  engine.__audit.sun(number(command.azimuth, -180, 180), number(command.elevation, 5, 85), number(command.intensity, 0, 12));
}
function camera(command: Record<string, unknown>) {
  const a = number(command.azimuth, -180, 180) * Math.PI / 180;
  const e = number(command.elevation, cameraElevationLimits[0], cameraElevationLimits[1]) * Math.PI / 180;
  const r = number(command.distance, cameraLimits[0], cameraLimits[1]);
  const target = host.controls.target;
  engine.__camera(target.x + r * Math.cos(e) * Math.sin(a), target.y + r * Math.sin(e), target.z + r * Math.cos(e) * Math.cos(a), target.x, target.y, target.z);
}
window.addEventListener('message', (event) => {
  if (event.source !== parent || event.origin !== location.origin || event.data?.channel !== CHANNEL || event.data.session !== session) return;
  const command = event.data;
  if (!ready || failed) return;
  try {
    if (!Number.isSafeInteger(command.revision) || command.revision <= commandRevision) return;
    commandRevision = command.revision;
    if (command.type === 'sun') sun(command);
    else if (command.type === 'camera') camera(command);
    else if (command.type === 'pause') { paused = Boolean(command.value); engine.__audit.pause(paused); }
    else if (command.type === 'reset') {
      engine.__audit.sun(45, 55, 4);
      engine.__camera(...initialCamera, ...initialTarget);
    } else if (command.type === 'cameraPreset') {
      const values = cameraPresets[String(command.name)];
      if (values) engine.__camera(...values);
    } else if (command.type === 'rebake') {
      ready = false;
      bootStart = performance.now();
      stage('按当前太阳重新烘焙间接光');
      const controller = gui.controllersRecursive().find((item) => item.property === 'rebake');
      if (!controller) throw new Error('未找到原库的烘焙控制');
      controller.object[controller.property]();
    }
    notify();
  } catch (error) { fail(error); }
});
window.addEventListener('error', (event) => fail(event.error || event.message));
window.addEventListener('unhandledrejection', (event) => fail(event.reason));
document.addEventListener('visibilitychange', () => {
  if (ready) { paused = document.hidden; engine.__audit.pause(paused); notify(); }
});

onBootProgress((text) => stage(text));
async function boot() {
  stage('检查 WebGPU 与设备上限');
  if (!navigator.gpu) throw new Error('当前浏览器没有启用 WebGPU。请使用支持 WebGPU 的新版桌面浏览器。');
  const adapter = await navigator.gpu.requestAdapter();
  if (!adapter) throw new Error('没有找到可用的 WebGPU 适配器。');
  deviceInfo = {
    vendor: adapter.info?.vendor, architecture: adapter.info?.architecture,
    maxStorageBuffersPerShaderStage: adapter.limits.maxStorageBuffersPerShaderStage,
    maxComputeInvocationsPerWorkgroup: adapter.limits.maxComputeInvocationsPerWorkgroup,
    maxComputeWorkgroupSizeX: adapter.limits.maxComputeWorkgroupSizeX,
  };
  if (adapter.limits.maxStorageBuffersPerShaderStage < 14 || adapter.limits.maxComputeInvocationsPerWorkgroup < 1024 || adapter.limits.maxComputeWorkgroupSizeX < 1024) throw new Error('设备上限不足：原库要求每阶段至少 14 个存储缓冲、每工作组至少 1024 次计算调用，以及 X 维 1024 工作组大小。');
  ({ renderer } = await initRenderer());
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.25));
  renderer.setSize(innerWidth, innerHeight);
  renderer.domElement.tabIndex = 0;
  renderer.domElement.setAttribute('aria-label', '真实三维画面，可拖动旋转、滚轮缩放；也可使用展示页相机滑杆');
  gui = new GUI({ autoPlace: false });
  stage('读取原库 HDR 环境与蓝噪声纹理');
  const pipeline = await createRenderPipeline(renderer);
  let sceneOptions: SceneHost;
  if (village) {
    stage('生成村庄、海岸与水面模拟');
    const { createMidseeVillageScene } = await import('../src/widgets/world/midseeVillageScene.tsx');
    const original = await createMidseeVillageScene(renderer, pipeline.envTexture);
    host = original;
    sceneOptions = { ...original, skyIsBackground: false, moverByDefault: false, sunIntensity: 'environment', reflections: { denoisePasses: 1 } };
  } else if (beach) {
    stage('生成海滩、棕榈和浅水模拟');
    const { createBeachScene } = await import('../src/widgets/world/beachScene.ts');
    host = await createBeachScene(renderer, pipeline.envTexture);
    sceneOptions = { ...host, skyIsBackground: false, moverByDefault: false, sunIntensity: 'environment', reflections: { denoisePasses: 1 } };
  } else if (forest) {
    stage('读取森林纹理，生成针叶林、灌木和溪流');
    const { createForestScene } = await import('../src/widgets/world/forestScene.ts');
    host = await createForestScene(renderer);
    sceneOptions = { ...host, skyIsBackground: false, moverByDefault: false, sunIntensity: 'environment' };
  } else {
    host = createCornellScene(renderer);
    populateCornell(host.scene, host.sun);
    sceneOptions = { ...host, skyIsBackground: true, moverByDefault: false, interiorVolumes: [staticInteriorVolume(host.scene)] };
  }
  initialCamera = host.camera.position.toArray();
  initialTarget = host.controls.target.toArray();
  let meshes = 0, instances = 0, triangles = 0;
  host.scene.traverse((object) => {
    const mesh = object as Mesh;
    if (!mesh.isMesh) return;
    meshes++;
    const count = (mesh as InstancedMesh).isInstancedMesh ? (mesh as InstancedMesh).count : 1;
    instances += count;
    triangles += ((mesh.geometry.index?.count ?? mesh.geometry.attributes.position?.count ?? 0) / 3) * count;
  });
  sceneStats = { meshes, instances, triangles: Math.round(triangles), water: village || beach, waterKind: village || beach ? 'worker-shallow-water' : forest ? 'opaque-stream-material' : 'none', architecture: village ? 'react-three-fiber' : 'three' };
  host.controls.enableDamping = false;
  host.controls.minDistance = cameraLimits[0];
  host.controls.maxDistance = cameraLimits[1];
  host.controls.minPolarAngle = (90 - cameraElevationLimits[1]) * Math.PI / 180;
  host.controls.maxPolarAngle = (90 - cameraElevationLimits[0]) * Math.PI / 180;
  host.controls.addEventListener('end', notify);
  const ui = {
    setLoading: stage, showChrome: false, showError: fail,
    clearLoading() {
      if (failed) return;
      const s = engine.__probe();
      bakedSun = [s.lightCfg.azimuthDeg, s.lightCfg.elevationDeg, s.lightCfg.intensity];
      ready = true;
      $('runtime-loading').hidden = true;
      send('ready', { state: state(), elapsed: Math.round((performance.now() - bootStart) / 1000) });
      notify();
    },
  };
  await pipeline.run(sceneOptions, gui, ui);
  setInterval(notify, 1000);
}
boot().catch(fail);
