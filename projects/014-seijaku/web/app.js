import { projects, capabilities, principles, comparisons, research, sources, SEIJAKU_COMMIT, useCases } from './content.js';

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escape = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const external = 'target="_blank" rel="noopener noreferrer"';
let selectedProject = 'seijaku';
let selectedChapter = '';
let frame = null;
let loadingTimer;

function markTabs(container, selected) {
  container.querySelectorAll('[role="tab"]').forEach((button) => {
    const on = button === selected;
    button.setAttribute('aria-selected', String(on));
    button.tabIndex = on ? 0 : -1;
  });
}

function wireTabKeys(container, orientation = 'horizontal') {
  container.addEventListener('keydown', (event) => {
    if (!event.target.matches('[role="tab"]')) return;
    const tabs = [...container.querySelectorAll('[role="tab"]')];
    const index = tabs.indexOf(event.target);
    const previous = orientation === 'vertical' ? ['ArrowUp', 'ArrowLeft'] : ['ArrowLeft'];
    const next = orientation === 'vertical' ? ['ArrowDown', 'ArrowRight'] : ['ArrowRight'];
    let target;
    if (next.includes(event.key)) target = (index + 1) % tabs.length;
    if (previous.includes(event.key)) target = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') target = 0;
    if (event.key === 'End') target = tabs.length - 1;
    if (target === undefined) return;
    event.preventDefault();
    tabs[target].click();
    tabs[target].focus();
  });
}

function demoURL() { return projects[selectedProject].live + selectedChapter; }

function updateChapters() {
  const project = projects[selectedProject];
  $('#chapter-nav').innerHTML = project.chapters.map(([hash, label]) => `<button type="button" data-chapter="${hash}" aria-pressed="${hash === selectedChapter}">${escape(label)}</button>`).join('');
  $('#chapter-nav').setAttribute('aria-label', `${project.name} 体验章节`);
  $('#demo-external').href = demoURL();
}

function stopDemo(announce = true) {
  clearTimeout(loadingTimer);
  if (frame) frame.remove();
  frame = null;
  $('#frame-host').hidden = true;
  $('#demo-poster').hidden = false;
  $('#demo-stop').disabled = true;
  $('#demo-fullscreen').disabled = true;
  if (announce) $('#demo-status').textContent = '体验已结束 · 原库画面和声音已卸载，可再次启动';
}

function startDemo() {
  stopDemo(false);
  const project = projects[selectedProject];
  frame = document.createElement('iframe');
  frame.title = `${project.name} 作者官方在线体验`;
  frame.allow = 'fullscreen';
  frame.allowFullscreen = true;
  frame.referrerPolicy = 'strict-origin-when-cross-origin';
  frame.src = demoURL();
  const activeFrame = frame;
  frame.addEventListener('load', () => {
    if (frame !== activeFrame) return;
    clearTimeout(loadingTimer);
    $('#demo-status').textContent = `${project.name} 在线页面已打开 · 按上方与画面内指引操作`;
  });
  $('#frame-host').append(frame);
  $('#frame-host').hidden = false;
  $('#demo-poster').hidden = true;
  $('#poster-name').textContent = `走进 ${project.name}`;
  $('#demo-stop').disabled = false;
  $('#demo-fullscreen').disabled = !document.fullscreenEnabled;
  $('#demo-status').textContent = `正在加载 ${project.name} 官方页面…`;
  loadingTimer = setTimeout(() => {
    if (frame !== activeFrame) return;
    stopDemo(false);
    $('#poster-name').textContent = `${project.name} 载入未完成`;
    $('#demo-status').textContent = '官方页面未及时载入 · 可重试，或使用“独立打开”访问原库';
  }, 25000);
}

function chooseProject(id) {
  if (!projects[id]) return;
  stopDemo(false);
  selectedProject = id;
  selectedChapter = '';
  const project = projects[id];
  markTabs($('.project-tabs'), $(`[data-project="${id}"]`));
  $('#demo-panel').setAttribute('aria-labelledby', `project-${id}`);
  $('#demo-name').textContent = project.name;
  $('#demo-description').textContent = project.description;
  $('#poster-name').textContent = `走进 ${project.name}`;
  $('#demo-preview').src = project.preview;
  $('#demo-preview').alt = project.alt;
  $('#demo-instructions').textContent = project.controls;
  $('#demo-status').textContent = '尚未启动 · 已切换官方预览，点击“启动原库”体验';
  updateChapters();
}

function chooseChapter(hash, start = false) {
  selectedChapter = hash;
  updateChapters();
  if (frame) {
    frame.src = demoURL();
    $('#demo-status').textContent = '正在转到所选章节 · 可在画面内继续滚动';
  } else if (start) startDemo();
  else $('#demo-status').textContent = '章节已选择 · 点击“启动原库”从该章节进入';
}

$$('[data-project]').forEach((button) => button.addEventListener('click', () => chooseProject(button.dataset.project)));
$('#chapter-nav').addEventListener('click', (event) => {
  const button = event.target.closest('[data-chapter]');
  if (button) chooseChapter(button.dataset.chapter);
});
$('#demo-start').addEventListener('click', startDemo);
$('#demo-stop').addEventListener('click', () => { stopDemo(); $('#demo-start').focus(); });
$('#demo-fullscreen').addEventListener('click', async () => {
  try { await $('#demo-stage').requestFullscreen(); }
  catch { $('#demo-status').textContent = '当前环境无法全屏，可使用“独立打开”继续体验'; }
});
wireTabKeys($('.project-tabs'));
updateChapters();

const capabilityTabs = $('#capability-tabs');
capabilityTabs.innerHTML = capabilities.map((item, index) => `<button type="button" id="cap-${item.id}" role="tab" aria-selected="${index === 0}" aria-controls="capability-detail" tabindex="${index === 0 ? 0 : -1}" data-cap="${item.id}"><span>${item.number}</span>${escape(item.title)}</button>`).join('');
function showCapability(id) {
  const item = capabilities.find((entry) => entry.id === id);
  if (!item) return;
  markTabs(capabilityTabs, $(`[data-cap="${id}"]`));
  const panel = $('#capability-detail');
  panel.setAttribute('aria-labelledby', `cap-${id}`);
  panel.innerHTML = `<p class="detail-kicker">${item.number} / ${escape(item.tag)}</p><h3>${escape(item.title)}</h3><div class="detail-grid"><div><span>看见什么</span><p>${escape(item.effect)}</p></div><div><span>如何实现</span><p>${escape(item.mechanism)}</p></div><div><span>可以用在哪里</span><p>${escape(item.value)}</p></div><div><span>理解边界</span><p class="boundary">${escape(item.boundary)}</p></div></div><div class="detail-actions"><button type="button" data-open-cap="${id}">在原库中体验 ↗</button><a href="${item.source}" ${external}>查看固定版本源码 ↗</a></div>`;
}
capabilityTabs.addEventListener('click', (event) => {
  const button = event.target.closest('[data-cap]');
  if (button) showCapability(button.dataset.cap);
});
$('#capability-detail').addEventListener('click', (event) => {
  const button = event.target.closest('[data-open-cap]');
  if (!button) return;
  const item = capabilities.find((entry) => entry.id === button.dataset.openCap);
  chooseProject('seijaku');
  chooseChapter(item.chapter, true);
  $('#experience').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
});
wireTabKeys(capabilityTabs, 'vertical');
showCapability('walk');

$('#pipeline').innerHTML = principles.map((item, index) => `<button type="button" id="step-${index}" role="tab" aria-selected="${index === 0}" aria-controls="pipeline-detail" tabindex="${index === 0 ? 0 : -1}" data-step="${index}"><span>0${index + 1}</span><strong>${escape(item.title)}</strong><small>${escape(item.subtitle)}</small></button>`).join('');
function showStep(index) {
  markTabs($('#pipeline'), $(`[data-step="${index}"]`));
  $('#pipeline-detail').setAttribute('aria-labelledby', `step-${index}`);
  $('#pipeline-detail').innerHTML = `<strong>0${index + 1} / ${escape(principles[index].subtitle)}</strong>${escape(principles[index].detail)}`;
}
$('#pipeline').addEventListener('click', (event) => {
  const button = event.target.closest('[data-step]');
  if (button) showStep(Number(button.dataset.step));
});
wireTabKeys($('#pipeline'));
showStep(0);

function renderComparison(filter) {
  const rows = comparisons.filter((row) => filter === 'all' || row.category === filter);
  $('#comparison-body').innerHTML = rows.map((row) => `<tr data-category="${row.category}"><td>${escape(row.name)}<span class="category-tag ${row.category}">${escape(row.label)}</span></td><td>${escape(row.kage)}</td><td>${escape(row.sublevel)}</td><td>${escape(row.seijaku)}</td><td>${escape(row.verdict)}</td></tr>`).join('');
  $$('[data-filter]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.filter === filter)));
  $('#comparison-status').textContent = `显示 ${rows.length} / ${comparisons.length} 项对比 · 窄屏可在表格内横向滚动`;
}
$$('[data-filter]').forEach((button) => button.addEventListener('click', () => renderComparison(button.dataset.filter)));
renderComparison('all');

$('#use-cases').innerHTML = useCases.map(([title, value, condition], index) => `<article class="use-case"><span>0${index + 1}</span><h3>${escape(title)}</h3><p>${escape(value)}</p><small>落地还需要<br>${escape(condition)}</small></article>`).join('');

$('#research-tabs').innerHTML = research.map((item, index) => `<button type="button" id="research-${item.id}" role="tab" aria-selected="${index === 0}" aria-controls="research-detail" tabindex="${index === 0 ? 0 : -1}" data-research="${item.id}">${escape(item.title)}<small>${escape(item.priority)}</small></button>`).join('');
function showResearch(id) {
  const item = research.find((entry) => entry.id === id);
  if (!item) return;
  markTabs($('#research-tabs'), $(`[data-research="${id}"]`));
  $('#research-detail').setAttribute('aria-labelledby', `research-${id}`);
  $('#research-detail').innerHTML = `<p class="detail-kicker">${escape(item.priority)} / PROPOSED MODULE</p><h3>${escape(item.title)}</h3><dl><dt>输入</dt><dd>${escape(item.input)}</dd><dt>输出</dt><dd>${escape(item.output)}</dd><dt>最小实验</dt><dd>${escape(item.experiment)}</dd><dt>沉淀价值</dt><dd>${escape(item.value)}</dd><dt>当前边界</dt><dd>${escape(item.boundary)}</dd></dl><a class="text-link" href="${item.source}" ${external}>阅读这项机制的源码 ↗</a>`;
}
$('#research-tabs').addEventListener('click', (event) => {
  const button = event.target.closest('[data-research]');
  if (button) showResearch(button.dataset.research);
});
wireTabKeys($('#research-tabs'), 'vertical');
showResearch('environment');

$('#sources-list').innerHTML = sources.map((item) => `<a class="source-item" href="${item.url}" ${external}><div><strong>${escape(item.title)}</strong><small>${escape(item.meta)}</small></div><span aria-hidden="true">↗</span></a>`).join('');
$('#download-research').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify({ project: 'Seijaku', date: '2026-10-22', sourceCommit: SEIJAKU_COMMIT, status: 'research proposals; not extracted modules', capabilities, comparisons, research, sources }, null, 2)], { type: 'application/json;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'seijaku-research-plan.json';
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  $('#download-status').textContent = '研究清单已生成，包含对比结论、源码链接和最小实验。';
});

const sections = $$('main section[id]').filter((section) => $(`.site-header nav a[href="#${section.id}"]`));
const observer = new IntersectionObserver((entries) => {
  const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
  if (!visible) return;
  $$('.site-header nav a').forEach((link) => {
    const current = link.hash === `#${visible.target.id}`;
    link.classList.toggle('current', current);
    if (current) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}, { rootMargin: '-15% 0px -65% 0px', threshold: 0 });
sections.forEach((section) => observer.observe(section));
window.addEventListener('pagehide', () => stopDemo(false));
