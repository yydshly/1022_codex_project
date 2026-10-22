(() => {
  'use strict';
  const CHANNEL = 'render-atlas-live-v1';
  const $ = (id) => document.getElementById(id);
  const frame = $('live-frame');
  const controls = $('live-controls');
  const start = $('start-live');
  const stop = $('stop-live');
  const sceneSelect = $('live-scene');
  const requestedScene = new URLSearchParams(location.search).get('scene');
  if (Array.from(sceneSelect.options).some((option) => option.value === requestedScene)) sceneSelect.value = requestedScene;
  let session = '';
  let running = false;
  let ready = false;
  let updateScheduled = false;
  let pendingGroup = '';
  let currentState = null;
  let commandRevision = 0;
  const fields = {
    sunAzimuth: ['live-sun-azimuth', 'out-sun-azimuth', '°', 0],
    sunElevation: ['live-sun-elevation', 'out-sun-elevation', '°', 0],
    sunIntensity: ['live-sun-intensity', 'out-sun-intensity', '', 1],
    cameraAzimuth: ['live-camera-azimuth', 'out-camera-azimuth', '°', 0],
    cameraElevation: ['live-camera-elevation', 'out-camera-elevation', '°', 0],
    cameraDistance: ['live-camera-distance', 'out-camera-distance', '', 1],
  };
  const value = (id) => Number($(id).value);
  function labels() {
    for (const [input, output, unit, places] of Object.values(fields)) $(output).textContent = value(input).toFixed(places) + unit;
  }
  function status(text, kind = '') {
    $('live-status').textContent = text;
    $('live-indicator').dataset.state = kind;
  }
  function send(command) {
    if (ready && frame.contentWindow) frame.contentWindow.postMessage({ channel: CHANNEL, session, ...command, revision: ++commandRevision }, location.origin);
  }
  function sendGroup(group) {
    if (group === 'sun') send({ type: 'sun', azimuth: value('live-sun-azimuth'), elevation: value('live-sun-elevation'), intensity: value('live-sun-intensity') });
    else send({ type: 'camera', azimuth: value('live-camera-azimuth'), elevation: value('live-camera-elevation'), distance: value('live-camera-distance') });
  }
  function sync(state) {
    // A delayed acknowledgement must not overwrite a newer slider edit.
    if (state.commandRevision < commandRevision) return;
    currentState = state;
    $('live-camera-distance').min = state.cameraLimits[0];
    $('live-camera-distance').max = state.cameraLimits[1];
    $('live-camera-elevation').min = state.cameraElevationLimits[0];
    $('live-camera-elevation').max = state.cameraElevationLimits[1];
    $('live-detail-presets').hidden = state.detailLabels.length === 0;
    $('live-detail-a').textContent = state.detailLabels[0] || '';
    $('live-detail-b').textContent = state.detailLabels[1] || '';
    for (const [key, [input]] of Object.entries(fields)) if (document.activeElement !== $(input)) $(input).value = state[key];
    labels();
    $('pause-live').setAttribute('aria-pressed', String(state.paused));
    $('pause-live').textContent = state.paused ? '继续画面' : '暂停画面';
    $('live-cache-note').textContent = state.stale ? '太阳已改变：直接光与阴影正在按新参数显示；间接光仍是旧烘焙，可点击重烘焙。' : '当前太阳与烘焙参数一致。改动相机不会使静态间接光过期。';
    $('live-cache-note').dataset.stale = String(state.stale);
    $('live-frame-count').textContent = state.paused ? '画面已暂停' : 'WebGPU 正在实时绘制';
    $('live-frame-count').dataset.frame = state.frame;
    $('live-actual-state').textContent = `引擎已应用：太阳 ${state.sunAzimuth.toFixed(0)}° / ${state.sunElevation.toFixed(0)}°，强度 ${state.sunIntensity.toFixed(1)}；相机 ${state.cameraAzimuth.toFixed(0)}° / ${state.cameraElevation.toFixed(0)}°，距离 ${state.cameraDistance.toFixed(1)}。`;
    $('live-actual-state').dataset.state = JSON.stringify(state);
    const stats = state.sceneStats;
    $('live-scene-facts').textContent = `${state.sceneLabel} · ${stats.meshes} 个网格对象 · ${stats.instances.toLocaleString()} 个网格实例 · 约 ${(stats.triangles / 10000).toFixed(1)} 万三角形${stats.water ? ' · 原库浅水模拟运行中' : stats.waterKind === 'opaque-stream-material' ? ' · 原库溪流波纹材质运行中' : ''}（几何统计，非性能测试）`;
  }
  function launch() {
    ready = false;
    running = true;
    currentState = null;
    commandRevision = 0;
    controls.disabled = true;
    frame.hidden = false;
    $('live-placeholder').hidden = true;
    start.disabled = true;
    start.textContent = '正在准备画面…';
    stop.disabled = false;
    session = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    $('live-actual-state').textContent = '等待所选场景启动并回传实际参数。';
    delete $('live-actual-state').dataset.state;
    const hints = { cornell: 'Cornell Box · 观察天窗投影与红绿墙面的反弹光。', 'midsee-village': '完整海岸村庄 · 房屋、码头、植被与浅水模拟。', beach: '热带海滩 · 棕榈、灌木、波浪、泡沫和浮球。', forest: '针叶林与溪流 · 原始近景/远景树群、灌木、地表与不透明溪流波纹材质。' };
    $('live-scene-facts').textContent = hints[sceneSelect.value] + ' 首次启动需要生成场景、编译着色器和烘焙光照。';
    $('live-frame-count').textContent = '等待所选场景出帧';
    $('live-cache-note').textContent = '正在准备新场景及其初始光照。';
    $('live-cache-note').dataset.stale = 'false';
    $('live-detail-presets').hidden = true;
    frame.title = `原库 ${sceneSelect.selectedOptions[0].textContent} 的真实 WebGPU 渲染画面`;
    status('启动原库 · 正在检查 WebGPU', 'busy');
    frame.src = `live/index.html?scene=${encodeURIComponent(sceneSelect.value)}&session=${encodeURIComponent(session)}`;
  }
  start.addEventListener('click', launch);
  sceneSelect.addEventListener('change', () => {
    if (running) launch();
    else $('live-scene-facts').textContent = '已选择 ' + sceneSelect.selectedOptions[0].textContent + '，点击启动真实演示。';
  });
  stop.addEventListener('click', () => {
    running = false;
    session = '';
    ready = false;
    frame.src = 'about:blank';
    frame.hidden = true;
    $('live-placeholder').hidden = false;
    controls.disabled = true;
    stop.disabled = true;
    start.disabled = false;
    start.textContent = '重新启动演示';
    currentState = null;
    delete $('live-actual-state').dataset.state;
    $('live-actual-state').textContent = '画面已停止，启动后会重新回传引擎参数。';
    $('live-cache-note').textContent = '场景已停止。每次启动将按默认太阳重新准备光照。';
    $('live-cache-note').dataset.stale = 'false';
    status('已停止 · 再启动时会重新准备光照');
    $('live-frame-count').textContent = '画面已释放';
  });
  for (const [key, [input]] of Object.entries(fields)) $(input).addEventListener('input', () => {
    labels();
    pendingGroup = key.startsWith('sun') ? 'sun' : 'camera';
    if (updateScheduled) return;
    updateScheduled = true;
    requestAnimationFrame(() => { updateScheduled = false; sendGroup(pendingGroup); });
  });
  document.querySelectorAll('[data-sun-preset]').forEach((button) => button.addEventListener('click', () => {
    const presets = { high: [45, 75, 4], low: [110, 18, 4], dim: [45, 55, 0.7] };
    const values = presets[button.dataset.sunPreset];
    ['live-sun-azimuth', 'live-sun-elevation', 'live-sun-intensity'].forEach((id, index) => { $(id).value = values[index]; });
    labels(); sendGroup('sun');
  }));
  document.querySelectorAll('[data-camera-preset]').forEach((button) => button.addEventListener('click', () => {
    send({ type: 'cameraPreset', name: button.dataset.cameraPreset });
  }));
  $('reset-live').addEventListener('click', () => send({ type: 'reset' }));
  $('pause-live').addEventListener('click', () => send({ type: 'pause', value: !currentState?.paused }));
  $('rebake-live').addEventListener('click', () => {
    send({ type: 'rebake' });
    ready = false;
    controls.disabled = true;
    status('按当前太阳重烘焙间接光', 'busy');
  });
  window.addEventListener('message', (event) => {
    if (!running || event.source !== frame.contentWindow || event.origin !== location.origin || event.data?.channel !== CHANNEL || event.data.session !== session || event.data.scene !== sceneSelect.value) return;
    const message = event.data;
    if (message.type === 'progress') status(`${message.text} · ${message.elapsed || 0}s`, 'busy');
    else if (message.type === 'ready') {
      ready = true;
      controls.disabled = false;
      start.textContent = '演示运行中';
      status(`原库 WebGPU 已就绪 · ${message.state.sceneLabel}`, 'ready');
      sync(message.state);
    } else if (message.type === 'state') sync(message.state);
    else if (message.type === 'error') {
      ready = false;
      controls.disabled = true;
      start.disabled = false;
      start.textContent = '重试启动';
      status(message.text, 'error');
    }
  });
  labels();
})();
