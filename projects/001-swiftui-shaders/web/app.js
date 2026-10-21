import { ShaderRenderer } from './renderer.js';

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const showcaseValues = {
  Holographic: { intensity: 0.65, scale: 12, speed: 1.2 },
  Disintegrate: { threshold: 0.48 },
  Duochrome: { intensity: 0.9, hue1: 0.58, hue2: 0.09 },
  Frosted: { frostAmount: 0.95, clearRadius: 0.14, clearSoftness: 0.2, grainSize: 16 },
  TouchRipple: { touchAge: 0.48, amplitude: 28, decay: 0.8 },
  NeonEdge: { glowAmount: 1.2, mixOriginal: 0.45 },
  ShatterGlass: { shatterSpread: 0.3 },
  Topographic: { colorize: 0.9, lineCount: 28 },
};
const state = {
  effects: [], selected: null, values: new Map(), touch: [0.5, 0.5],
  time: 1.7, playing: !matchMedia('(prefers-reduced-motion: reduce)').matches,
  compare: false, split: 0.5, material: 'cover', renderer: null,
  thumbRenderer: null, thumbEpoch: 0, rippleStart: null, lastFrame: null,
  source: null, sourceEpoch: 0, cards: new Map(), errors: [], ready: false,
};

function valuesFor(effect, showcase = false) {
  const values = Object.fromEntries(effect.params.filter(p => p.type === 'float').map(p => [p.label, p.default]));
  return showcase ? { ...values, ...showcaseValues[effect.id] } : values;
}

function currentValues() { return state.values.get(state.selected.id); }
function number(value) { return Number(value.toFixed(3)).toString(); }
function mode(effect) { return effect.category === '触摸交互' ? '触摸交互' : effect.timeUsed ? '自动动画' : effect.animated ? '参数驱动' : '静态效果'; }

let toastTimer;
function toast(message) {
  $('#toast').textContent = message;
  $('#toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 2600);
}

function reportError(error, effect = state.selected) {
  const message = `${effect?.name || '渲染器'}：${error.message}`;
  state.errors.push(message);
  console.error(message);
  $('#preview-error').textContent = `此预览未能渲染。\n${message}`;
  $('#preview-error').hidden = false;
  $('#render-status').textContent = '渲染遇到错误 · 可继续查看参数与源码';
}

function updateCode() {
  const effect = state.selected;
  const values = currentValues();
  const args = effect.params.map(param => {
    const value = param.type === 'point'
      ? `UnitPoint(x: ${number(state.touch[0])}, y: ${number(state.touch[1])})`
      : number(values[param.label]);
    return `    ${param.label}: ${value}`;
  });
  $('#swift-code').textContent = `.${effect.modifier}(\n${args.join(',\n')}\n)`;
}

function scalarControl(param, { label = param.name, value, min, max, step, onInput, suffix = '' }) {
  const div = document.createElement('div');
  div.className = 'control';
  const id = `param-${param.label}${suffix}`;
  div.innerHTML = `<div class="control-header"><label for="${id}">${label}<small>${param.label}${suffix}</small></label><output for="${id}">${number(value)}</output></div><input id="${id}" type="range" min="${min}" max="${max}" step="${step}" value="${value}"><div class="range-labels"><span>${number(min)}</span><span>${number(max)}</span></div>`;
  if (param.rangeNote) {
    const note = document.createElement('p');
    note.className = 'range-note';
    note.textContent = param.rangeNote;
    div.append(note);
  }
  div.querySelector('input').addEventListener('input', event => {
    const next = Number(event.target.value);
    div.querySelector('output').textContent = number(next);
    onInput(next);
    $('#preset-label').textContent = '自定义参数';
    updateCode();
    render();
  });
  return div;
}

function buildControls() {
  const controls = $('#controls');
  controls.replaceChildren();
  const values = currentValues();
  for (const param of state.selected.params) {
    if (param.type === 'point') {
      const group = document.createElement('div');
      group.className = 'control point-control';
      const box = document.createElement('div');
      box.className = 'point-controls';
      for (let axis = 0; axis < 2; axis++) {
        box.append(scalarControl(param, { label: axis ? '触点 Y' : '触点 X', value: state.touch[axis], min: 0, max: 1, step: 0.001,
          suffix: axis ? '.y' : '.x', onInput: value => { state.touch[axis] = value; } }));
      }
      group.append(box);
      controls.append(group);
    } else {
      const min = Math.min(param.min ?? param.uiMin, param.default);
      const max = Math.max(param.max ?? param.uiMax, param.default);
      const range = max - min;
      controls.append(scalarControl(param, { value: values[param.label], min, max,
        step: range <= 1 ? 0.001 : range <= 10 ? 0.01 : 0.1,
        onInput: value => { values[param.label] = value; if (param.label === 'touchAge') state.rippleStart = null; } }));
    }
  }
}

function selectEffect(id, { scroll = false, replaceHash = true } = {}) {
  const effect = state.effects.find(item => item.id === id) || state.effects.find(item => item.id === 'Holographic');
  state.selected = effect;
  state.rippleStart = null;
  $('#preview-error').hidden = Boolean(state.renderer);
  if (!state.values.has(effect.id)) state.values.set(effect.id, valuesFor(effect));
  $('#effect-name').replaceChildren(document.createTextNode(`${effect.name} `));
  const english = document.createElement('span');
  english.textContent = effect.title;
  $('#effect-name').append(english);
  $('#effect-kind').textContent = mode(effect);
  $('#effect-description').textContent = effect.description;
  $('#principle').textContent = effect.principle;
  $('#metal-code').textContent = effect.metalSource;
  $('#source-link').href = `https://github.com/krispuckett/SwiftUIShaders/blob/6b644a8bd4f3131401bd6765990e476352d3cdef/Sources/SwiftUIShaders/Shaders/SwiftUIShaders.metal#L${effect.line}`;
  $('#preview').setAttribute('aria-label', `${effect.name}实时预览${effect.category === '触摸交互' ? '；使用方向键移动触点，空格触发涟漪' : ''}`);
  $('#stage-hint').textContent = effect.id === 'RefractLens' ? '拖动透镜探索画面 · 也可用方向键移动触点'
    : effect.id === 'TouchRipple' ? '点击任意位置激起涟漪 · 空格可从当前触点触发'
    : effect.id === 'Shatter' ? '调节「散开程度」展开碎片 · 此算法不使用时间参数'
    : effect.timeUsed ? '光影随时间变化，试试调节右侧参数' : '静态效果 · 调节参数观察细节变化';
  const interaction = effect.category === '触摸交互';
  $('#interaction-note').hidden = !interaction;
  $('#interaction-note').textContent = effect.id === 'TouchRipple'
    ? '原生接入时请绑定 touchPos，并在点击后持续更新 touchAge。这里可点击预览，或直接拖动 touchAge 观察波前。'
    : '原生接入时请将 DragGesture 的位置归一化，再传给 touchPos。这里支持拖动与方向键。';
  $('#preset-label').textContent = JSON.stringify(currentValues()) === JSON.stringify(valuesFor(effect)) ? '上游默认值' : '已调整参数';
  for (const button of $$('.effect-option')) {
    const selected = button.dataset.id === effect.id;
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  }
  for (const [key, card] of state.cards) {
    card.classList.toggle('selected', key === effect.id);
    card.setAttribute('aria-pressed', String(key === effect.id));
  }
  const option = $(`.effect-option[data-id="${effect.id}"]`);
  if (option) {
    const list = $('#effect-list');
    if (list.scrollHeight > list.clientHeight + 5) list.scrollTop = option.offsetTop - list.offsetTop - 130;
    else if (list.scrollWidth > list.clientWidth) list.scrollLeft = option.offsetLeft - 30;
  }
  buildControls();
  updateCode();
  render();
  if (replaceHash) history.replaceState(null, '', `#effect=${effect.id}`);
  if (scroll) $('#workspace').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
}

function buildCatalog() {
  for (const effect of state.effects) {
    const button = document.createElement('button');
    button.className = 'effect-option';
    button.dataset.id = effect.id;
    button.setAttribute('aria-pressed', 'false');
    button.innerHTML = `<span class="effect-number">${String(effect.index).padStart(2, '0')}</span><div><strong>${effect.name}</strong><small>${effect.title}</small></div><span class="tiny-dot" aria-hidden="true"></span>`;
    button.addEventListener('click', () => selectEffect(effect.id));
    $('#effect-list').append(button);

    const card = document.createElement('button');
    card.className = 'effect-card';
    card.dataset.id = effect.id;
    card.setAttribute('aria-label', `探索${effect.name}，${effect.title}，${mode(effect)}`);
    card.setAttribute('aria-pressed', 'false');
    card.innerHTML = `<div class="card-image"><canvas width="180" height="240" aria-label="${effect.name}的展示预设效果"></canvas><span class="card-index">${String(effect.index).padStart(2, '0')}</span><span class="card-kind">${mode(effect)}</span></div><div class="card-body"><div><strong>${effect.name}</strong><span class="card-arrow" aria-hidden="true">↗</span></div><small>${effect.title}</small><span class="card-category">${effect.category}</span></div>`;
    card.addEventListener('click', () => {
      state.values.set(effect.id, valuesFor(effect, true));
      selectEffect(effect.id, { scroll: true });
      $('#preset-label').textContent = '展示预设';
    });
    state.cards.set(effect.id, card);
    $('#gallery-grid').append(card);
  }
}

function buildVisualModules() {
  const examples = ['Holographic', 'NeonEdge', 'Kaleidoscope', 'InkBleed', 'Datamosh', 'Disintegrate', 'TouchRipple', 'RefractLens'];
  for (const id of examples) {
    const effect = state.effects.find(item => item.id === id);
    const module = document.createElement('article');
    module.className = 'example-module';
    const image = document.createElement('img');
    image.src = globalThis.SHADER_VISUAL_ASSETS?.[id] || `./assets/effects/${id}.png`;
    image.alt = `${effect.name}：同一原创封面的真实 WebGL 移植效果`;
    image.width = 600;
    image.height = 800;
    image.loading = 'lazy';
    const body = document.createElement('div');
    body.className = 'example-module-body';
    const title = document.createElement('h4');
    title.textContent = effect.name;
    const type = document.createElement('span');
    type.textContent = effect.category;
    const description = document.createElement('p');
    description.textContent = effect.description;
    const button = document.createElement('button');
    button.dataset.exploreEffect = id;
    button.dataset.previewTime = '1.7';
    button.textContent = '在实验区体验 ↗';
    body.append(title, type, description, button);
    module.append(image, body);
    $('#example-modules').append(module);
  }
  for (const link of $$('[data-download-visual], [data-open-visual]')) {
    const key = link.dataset.downloadVisual || link.dataset.openVisual;
    if (key === 'OverviewSVG') link.href = $('#overview-image').src;
    else if (globalThis.SHADER_VISUAL_ASSETS?.[key]) link.href = globalThis.SHADER_VISUAL_ASSETS[key];
  }
}

function filterCatalog() {
  const query = $('#search').value.trim().toLowerCase();
  const category = $('#category').value;
  let count = 0;
  for (const effect of state.effects) {
    const haystack = `${effect.name} ${effect.title} ${effect.modifier} ${effect.description} ${effect.category} ${effect.params.map(p => `${p.label} ${p.name}`).join(' ')}`.toLowerCase();
    const visible = (!query || haystack.includes(query)) && (category === 'all' || effect.category === category);
    $(`.effect-option[data-id="${effect.id}"]`).hidden = !visible;
    state.cards.get(effect.id).hidden = !visible;
    if (visible) count++;
  }
  $('#list-count').textContent = count;
  $('#gallery-count').textContent = `${count} / 41`;
  $('#empty').hidden = count > 0;
}

function render() {
  if (!state.renderer || !state.source || !state.selected) return;
  try {
    const rect = $('#canvas-wrap').getBoundingClientRect();
    const values = { ...currentValues() };
    if (state.selected.id === 'TouchRipple' && state.rippleStart !== null) {
      // Use the same pause/seek clock as all other previews.
      const age = state.time >= state.rippleStart ? state.time - state.rippleStart : state.time + 30 - state.rippleStart;
      values.touchAge = age;
    }
    state.renderer.draw(state.selected, values, { width: rect.width || 300, height: rect.height || 400,
      scale: Math.min(devicePixelRatio, 1.5), time: state.time, touch: state.touch,
      compare: state.compare ? state.split : -1 });
    $('#time-label').textContent = `00:${state.time.toFixed(1).padStart(4, '0')}`;
    $('#timeline').value = state.time;
  } catch (error) { reportError(error); }
}

async function renderThumbnails() {
  if (!state.thumbRenderer || !state.source) return;
  const epoch = ++state.thumbEpoch;
  for (const effect of state.effects) {
    if (epoch !== state.thumbEpoch) return;
    const card = state.cards.get(effect.id);
    try {
      state.thumbRenderer.draw(effect, valuesFor(effect, true), { width: 180, height: 240, time: 1.7 });
      card.querySelector('canvas').getContext('2d').drawImage(state.thumbRenderer.canvas, 0, 0);
      card.dataset.rendered = 'true';
    } catch (error) {
      state.errors.push(`${effect.id}: ${error.message}`);
      console.error(effect.id, error);
      const note = document.createElement('span');
      note.className = 'card-error';
      note.textContent = '此效果渲染失败，可查看源码';
      card.querySelector('.card-image').append(note);
    }
    await new Promise(requestAnimationFrame);
  }
  if (epoch === state.thumbEpoch) {
    $('#render-status').innerHTML = `<i class="status-dot"></i>WebGL 2 · ${$$('.effect-card[data-rendered=true]').length} / 41 种效果已就绪`;
    state.ready = true;
    $('#workspace').setAttribute('aria-busy', 'false');
  }
}

async function setMaterial(source, label, key = null) {
  const epoch = ++state.sourceEpoch;
  ++state.thumbEpoch;
  state.ready = false;
  $('#workspace').setAttribute('aria-busy', 'true');
  const image = new Image();
  image.src = source;
  try { await image.decode(); }
  catch {
    if (epoch === state.sourceEpoch) {
      state.ready = Boolean(state.source);
      $('#workspace').setAttribute('aria-busy', 'false');
      toast('图片无法读取，请选择其他图片。');
    }
    return;
  }
  if (epoch !== state.sourceEpoch) return;
  const texture = document.createElement('canvas');
  texture.width = 600;
  texture.height = 800;
  const ctx = texture.getContext('2d');
  ctx.fillStyle = '#172219';
  ctx.fillRect(0, 0, 600, 800);
  const scale = Math.max(600 / image.naturalWidth, 800 / image.naturalHeight);
  ctx.drawImage(image, (600 - image.naturalWidth * scale) / 2, (800 - image.naturalHeight * scale) / 2, image.naturalWidth * scale, image.naturalHeight * scale);
  state.source = texture;
  for (const card of state.cards.values()) delete card.dataset.rendered;
  state.material = key || 'upload';
  $('#stage-caption').textContent = label;
  for (const button of $$('[data-material]')) {
    const active = button.dataset.material === key;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  }
  state.renderer?.setImage(texture);
  state.thumbRenderer?.setImage(texture);
  render();
  await renderThumbnails();
}

function triggerPoint(event) {
  const rect = $('#preview').getBoundingClientRect();
  const point = [Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)),
    Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height))];
  if (state.compare) {
    state.split = point[0];
    $('#compare-divider').style.left = `${state.split * 100}%`;
    render();
    return;
  }
  state.touch = point;
  if (state.selected.id === 'TouchRipple') {
    state.rippleStart = state.time;
  }
  if (state.selected.category === '触摸交互') {
    for (let axis = 0; axis < 2; axis++) {
      const input = document.getElementById(`param-touchPos.${axis ? 'y' : 'x'}`);
      input.value = state.touch[axis];
      input.closest('.control').querySelector('output').textContent = number(state.touch[axis]);
    }
    updateCode();
  }
  render();
}

function updatePlayButton() {
  $('#play').textContent = state.playing ? 'Ⅱ' : '▷';
  $('#play').setAttribute('aria-label', state.playing ? '暂停动画' : '播放动画');
  $('#play').title = state.playing ? '暂停动画' : '播放动画';
}

function bindEvents() {
  $('#search').addEventListener('input', filterCatalog);
  $('#category').addEventListener('change', filterCatalog);
  for (const button of $$('[data-explore-effect]')) button.addEventListener('click', () => {
    const effect = state.effects.find(item => item.id === button.dataset.exploreEffect);
    state.values.set(effect.id, valuesFor(effect, true));
    if (button.dataset.previewTime) {
      state.time = Number(button.dataset.previewTime);
      state.touch = [0.5, 0.5];
    }
    selectEffect(effect.id, { scroll: true });
    $('#preset-label').textContent = '展示预设';
  });
  $('#play').addEventListener('click', () => { state.playing = !state.playing; updatePlayButton(); });
  $('#timeline').title = '30 秒预览循环，可拖动查看指定时间';
  $('#timeline').addEventListener('input', event => { state.time = Number(event.target.value); state.rippleStart = null; render(); });
  $('#reset').addEventListener('click', () => {
    state.values.set(state.selected.id, valuesFor(state.selected));
    state.touch = [0.5, 0.5];
    selectEffect(state.selected.id);
    toast('已恢复上游原始默认值');
  });
  $('#showcase').addEventListener('click', () => {
    state.values.set(state.selected.id, valuesFor(state.selected, true));
    selectEffect(state.selected.id);
    $('#preset-label').textContent = '展示预设';
  });
  $('#compare').addEventListener('click', () => {
    state.compare = !state.compare;
    state.split = 0.5;
    $('#compare').setAttribute('aria-pressed', String(state.compare));
    $('#compare-divider').hidden = !state.compare;
    $('#compare-divider').style.left = '50%';
    for (const label of $$('.split-label')) label.hidden = !state.compare;
    if (state.compare) toast('左侧为原图，右侧为效果；拖动分界线调整对比');
    render();
  });
  $('#download').addEventListener('click', () => {
    if (!state.renderer || !state.source) { toast('渲染器尚未就绪'); return; }
    render();
    const link = document.createElement('a');
    link.download = `SwiftUIShaders-${state.selected.id}.png`;
    link.href = $('#preview').toDataURL('image/png');
    link.click();
    toast('已导出当前预览');
  });
  $('#copy').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText($('#swift-code').textContent); toast('SwiftUI 调用代码已复制'); }
    catch { const range = document.createRange(); range.selectNodeContents($('#swift-code')); const selection = getSelection(); selection.removeAllRanges(); selection.addRange(range); toast('请复制已选中的代码'); }
  });
  for (const button of $$('[data-material]')) button.addEventListener('click', () => {
    const key = button.dataset.material;
    const names = { cover: 'THE SHAPE OF SILENCE / 原创测试封面', flower: 'IN FULL BLOOM / 原创植物插画', type: 'MAKE SOME WAVES / 原创文字海报' };
    setMaterial(`./assets/sample-${key}.svg`, names[key], key);
  });
  $('#upload').addEventListener('change', async event => {
    const file = event.target.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    try { await setMaterial(url, `${file.name} / 本地图片 · 居中裁切为 3:4`); }
    finally { URL.revokeObjectURL(url); event.target.value = ''; }
  });
  const canvas = $('#preview');
  let dragging = false;
  canvas.addEventListener('pointerdown', event => {
    dragging = true;
    canvas.setPointerCapture(event.pointerId);
    triggerPoint(event);
  });
  canvas.addEventListener('pointermove', event => { if (dragging) triggerPoint(event); });
  canvas.addEventListener('pointerup', () => { dragging = false; });
  canvas.addEventListener('pointercancel', () => { dragging = false; });
  canvas.addEventListener('keydown', event => {
    const keys = { ArrowLeft: [-0.02, 0], ArrowRight: [0.02, 0], ArrowUp: [0, -0.02], ArrowDown: [0, 0.02] };
    if (event.code === 'Space') {
      event.preventDefault();
      if (state.selected.id === 'TouchRipple') state.rippleStart = state.time;
      else { state.playing = !state.playing; updatePlayButton(); }
    } else if (keys[event.key] && state.selected.category === '触摸交互') {
      event.preventDefault();
      state.touch = state.touch.map((value, i) => Math.min(1, Math.max(0, value + keys[event.key][i])));
      buildControls(); updateCode();
    }
    render();
  });
  new ResizeObserver(render).observe($('#canvas-wrap'));
  addEventListener('hashchange', () => {
    const id = new URLSearchParams(location.hash.slice(1)).get('effect');
    if (id) selectEffect(id, { replaceHash: false });
  });
  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault(); state.playing = false; updatePlayButton();
    reportError(new Error('GPU 上下文已丢失，请刷新页面恢复预览。'));
  });
}

function animate(now) {
  if (state.lastFrame !== null && state.playing && !document.hidden) {
    state.time = (state.time + Math.min((now - state.lastFrame) / 1000, 0.1)) % 30;
    render();
  }
  state.lastFrame = now;
  requestAnimationFrame(animate);
}

async function init() {
  try {
    let manifest = globalThis.SHADER_MANIFEST;
    if (!manifest) {
      const response = await fetch('./shaders.json');
      if (!response.ok) throw new Error(`特效数据读取失败 (${response.status})`);
      manifest = await response.json();
    }
    state.effects = manifest.shaders;
    buildCatalog();
    buildVisualModules();
    try {
      state.renderer = new ShaderRenderer($('#preview'));
      state.thumbRenderer = new ShaderRenderer(document.createElement('canvas'));
    } catch (error) { reportError(error); }
    bindEvents();
    const id = new URLSearchParams(location.hash.slice(1)).get('effect') || 'Holographic';
    const holographic = state.effects.find(effect => effect.id === 'Holographic');
    state.values.set('Holographic', valuesFor(holographic, true));
    selectEffect(id, { replaceHash: !location.hash || location.hash.startsWith('#effect=') });
    if (state.selected.id === 'Holographic') $('#preset-label').textContent = '展示预设';
    updatePlayButton();
    requestAnimationFrame(animate);
    await setMaterial('./assets/sample-cover.svg', 'THE SHAPE OF SILENCE / 原创测试封面', 'cover');
    // Small diagnostic surface for repeatable compile/render tests, without
    // introducing a separate testing implementation of the effect algorithms.
    window.shaderLab = { state, selectEffect, render, valuesFor, showcaseValues, ShaderRenderer };
    $('#workspace').setAttribute('aria-busy', 'false');
  } catch (error) { reportError(error); $('#workspace').setAttribute('aria-busy', 'false'); }
}

init();
