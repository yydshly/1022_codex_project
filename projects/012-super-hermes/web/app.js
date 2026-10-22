(() => {
  'use strict';
  const guide = window.GUIDE;
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const sourceUrl = (path, anchor = '') => `${guide.repository}/blob/${guide.revision}/${path}${anchor ? `#${anchor}` : ''}`;
  let selectedScenario = 'code';
  let selectedSkill = 'scan';
  let selectedStep = 0;
  let raceStep = 0;
  let investigationStep = 0;
  let currentDocument = '';
  let toastTimeout;
  const dialog = $('#source-dialog');

  function notify(message) {
    clearTimeout(toastTimeout);
    $('#toast').textContent = message;
    $('#toast').classList.add('visible');
    toastTimeout = setTimeout(() => $('#toast').classList.remove('visible'), 3000);
  }

  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const previous = document.activeElement;
        const area = document.createElement('textarea');
        area.value = text;
        area.style.cssText = 'position:fixed;left:-10000px;top:0';
        (dialog.open ? dialog : document.body).append(area);
        area.select();
        const copied = document.execCommand('copy');
        area.remove();
        if (previous instanceof HTMLElement) previous.focus({preventScroll:true});
        if (!copied) throw new Error('copy unavailable');
      }
      notify('已复制，可以粘贴到你的 AI 工具中。');
    } catch {
      notify('浏览器未允许复制，请选中文字复制，或下载原文件。');
    }
  }

  function updateTabs(selector, active, attribute) {
    $$(selector).forEach(button => {
      const selected = button.dataset[attribute] === String(active);
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    });
  }

  function selectScenario(id) {
    if (!guide.scenarios[id]) return;
    selectedScenario = id;
    const value = guide.scenarios[id];
    updateTabs('[data-scenario]', id, 'scenario');
    $('#scenario-panel').setAttribute('aria-labelledby', `scenario-${id}`);
    $('#scenario-title').replaceChildren(...value.title.split('\n').flatMap((line, i) => i ? [document.createElement('br'), document.createTextNode(line)] : [document.createTextNode(line)]));
    $('.scenario-story .tag').textContent = value.tag;
    for (const key of ['desc','input','output','request','command','boundary']) $(`#scenario-${key}`).textContent = value[key];
    $('#scenario-skill').textContent = `/${guide.skills[value.skill].name}`;
  }

  function selectSkill(id) {
    if (!guide.skills[id]) return;
    selectedSkill = id;
    const skill = guide.skills[id];
    updateTabs('[data-skill]', id, 'skill');
    $('#skill-panel').setAttribute('aria-labelledby', `skill-${id}`);
    for (const key of ['kind','title','desc','output','limit']) $(`#skill-${key}`).textContent = skill[key];
    $('#skill-id').textContent = skill.name;
    $('#skill-steps').replaceChildren(...skill.steps.map((value, index) => {
      const item = document.createElement('li');
      const number = document.createElement('span');
      number.textContent = `0${index + 1}`;
      item.append(number, document.createTextNode(value));
      return item;
    }));
    const path = `skills/${skill.name}/SKILL.md`;
    $('#download-skill').href = `assets/upstream/${path}`;
    $('#download-skill').download = `${skill.name}-SKILL.md`;
    $('#skill-upstream').href = sourceUrl(path);
  }

  function updateLens() {
    const lens = guide.lenses[$('#lens-select').value];
    $('#lens-desc').textContent = lens.desc;
  }

  function selectStep(index) {
    selectedStep = index;
    const step = guide.mechanism[index];
    updateTabs('[data-step]', index, 'step');
    $('#mechanism-detail').setAttribute('aria-labelledby', `step-${index}`);
    for (const key of ['owner','title','desc']) $(`#mechanism-${key}`).textContent = step[key];
    $('#context-name').textContent = step.name;
    $('#mechanism-example').textContent = $('#history-toggle').checked ? step.historical : step.example;
    $('#mechanism-source').href = sourceUrl(step.path);
  }

  function updateRace(step) {
    raceStep = step;
    $('#race-counter').textContent = `0${step} / 04`;
    $$('#race-timeline li').forEach(item => {
      const number = Number(item.dataset.race);
      item.classList.toggle('reached', number <= step);
      item.classList.toggle('current', number === step);
      if (number === step) item.setAttribute('aria-current', 'step');
      else item.removeAttribute('aria-current');
    });
    $('#race-state').textContent = step >= 3 ? 'HALF_OPEN · 允许试探' : 'OPEN · 暂停请求';
    $('.race-state').classList.toggle('danger', step >= 3);
    $('#race-next').disabled = step === 4;
    $('#race-next').firstChild.textContent = step === 4 ? '演示完成 ' : '下一步 ';
    $('#race-state').setAttribute('aria-label', `${step >= 3 ? '出现竞态。' : ''}当前状态：${$('#race-state').textContent}。步骤 ${step}，共四步。`);
  }

  function readDocument(path, title, evidence) {
    const content = window.UPSTREAM?.[path];
    if (typeof content !== 'string') {
      notify('当前原文未加载，请从资料包读取。');
      return;
    }
    currentDocument = path;
    $('#dialog-title').textContent = title || path.split('/').at(-1);
    $('#dialog-path').textContent = path;
    let marker;
    const match = evidence && typeof evidence.needle === 'string' ? content.indexOf(evidence.needle) : -1;
    if (match >= 0) {
      marker = document.createElement('mark');
      marker.className = 'source-evidence';
      marker.textContent = evidence.needle;
      $('#dialog-content').replaceChildren(document.createTextNode(content.slice(0, match)), marker,
        document.createTextNode(content.slice(match + evidence.needle.length)));
    } else $('#dialog-content').textContent = content;
    $('#dialog-content').scrollTop = 0;
    $('#dialog-source').href = sourceUrl(path, evidence?.line ? 'L' + evidence.line : '');
    $('#dialog-download').href = `assets/upstream/${path}`;
    $('#dialog-download').download = path.split('/').join('-');
    dialog.showModal();
    document.body.style.overflow = 'hidden';
    $('#close-dialog').focus();
    if (marker) marker.scrollIntoView({block:'center'});
  }

  document.addEventListener('study-source', event => {
    const evidence = event.detail;
    if (evidence && typeof evidence.path === 'string') readDocument(evidence.path, undefined, evidence);
  });
  document.addEventListener('study-copy', event => {
    if (typeof event.detail === 'string') copyText(event.detail);
  });

  function selectInvestigation(index) {
    investigationStep = index;
    const step = window.INVESTIGATION[index];
    updateTabs('[data-investigation]', index, 'investigation');
    $('#investigation-panel').setAttribute('aria-labelledby', `investigation-${index}`);
    for (const key of ['owner','title','input','why','provenance']) $(`#investigation-${key}`).textContent = step[key];
    $('#investigation-instructions').replaceChildren(...step.instructions.map(text => {
      const item = document.createElement('li');
      item.textContent = text;
      return item;
    }));
    if (step.metrics) {
      const report = window.MEMORY_CASE;
      const unbounded = report.cases[0].samples.at(-1);
      const bounded = report.cases[1].samples.at(-1);
      const repeated = report.controls.repeated_key.samples.at(-1);
      const mib = sample => (sample.traced_growth_bytes / 1048576).toFixed(3);
      $('#investigation-output').textContent = `本研究实测：每组 800 次请求，每条响应 64 KiB。\n不同 key + 无上限 → ${mib(unbounded)} MiB，${unbounded.entries} 条。\n同一个 key + 无上限 → ${mib(repeated)} MiB，${repeated.entries} 条。\n不同 key + 32 条 LRU → ${mib(bounded)} MiB，${bounded.entries} 条。\n清空缓存后，各组响应分配行的增量均为 0。\n度量：Python 跟踪的存活内存增量，非进程 RSS。`;
    } else $('#investigation-output').textContent = step.output;
    $('#investigation-source').hidden = !step.path;
    $('#investigation-measurement').hidden = !step.measurement;
    $('#investigation-count').textContent = `${String(index + 1).padStart(2, '0')} / ${String(window.INVESTIGATION.length).padStart(2, '0')}`;
    $('#investigation-prev').disabled = index === 0;
    $('#investigation-next').textContent = index === window.INVESTIGATION.length - 1 ? '从头查看 ↺' : '下一步 →';
  }
  $$('[data-investigation]').forEach(button => button.addEventListener('click', () => selectInvestigation(Number(button.dataset.investigation))));
  $('#investigation-prev').addEventListener('click', () => selectInvestigation(Math.max(0, investigationStep - 1)));
  $('#investigation-next').addEventListener('click', () => selectInvestigation((investigationStep + 1) % window.INVESTIGATION.length));
  $('#investigation-source').addEventListener('click', () => readDocument(window.INVESTIGATION[investigationStep].path));

  const memoryCases = window.MEMORY_CASE.cases;
  const memoryX = sample => 55 + sample.requests / 800 * 520;
  const memoryY = sample => 210 - sample.traced_growth_bytes / 1048576 * 3.6;
  const memorySeries = ['unbounded', 'bounded'];
  memorySeries.forEach((mode, i) => {
    $(`#memory-${mode}-path`).setAttribute('points', memoryCases[i].samples.map(sample => `${memoryX(sample)},${memoryY(sample)}`).join(' '));
  });
  function showMemorySample() {
    const index = Number($('#memory-sample').value);
    const requests = memoryCases[0].samples[index].requests;
    $('#memory-request-count').textContent = `${requests} 个请求`;
    $('#memory-sample').setAttribute('aria-valuetext', `${requests} 个请求`);
    memorySeries.forEach((mode, i) => {
      const sample = memoryCases[i].samples[index];
      const unit = document.createElement('small');
      unit.textContent = 'MiB';
      $(`#memory-${mode}-value`).replaceChildren(document.createTextNode(`${(sample.traced_growth_bytes / 1048576).toFixed(2)} `), unit);
      $(`#memory-${mode}-entries`).textContent = `${sample.entries} 条${i === 0 ? '，随新 key 增加' : '，上限 32 条'}`;
      $(`#memory-${mode}-point`).setAttribute('cx', memoryX(sample));
      $(`#memory-${mode}-point`).setAttribute('cy', memoryY(sample));
    });
    const x = memoryX(memoryCases[0].samples[index]);
    $('#memory-cursor').setAttribute('x1', x);
    $('#memory-cursor').setAttribute('x2', x);
  }
  $('#memory-sample').addEventListener('input', showMemorySample);

  dialog.addEventListener('close', () => {document.body.style.overflow = '';});
  $('#close-dialog').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {if (event.target === dialog) {
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  }});
  $('#copy-document').addEventListener('click', () => copyText(window.UPSTREAM[currentDocument]));
  $('#read-skill').addEventListener('click', () => readDocument(`skills/${guide.skills[selectedSkill].name}/SKILL.md`, `/${guide.skills[selectedSkill].name} · 完整原文`));
  $('#read-lens').addEventListener('click', () => readDocument(`skills/prism-scan/references/${$('#lens-select').value}.md`, `${guide.lenses[$('#lens-select').value].title} · 固定模板`));
  $$('[data-document]').forEach(button => button.addEventListener('click', () => readDocument(button.dataset.document)));
  $$('[data-copy]').forEach(button => button.addEventListener('click', () => copyText(button.dataset.copy)));
  $('#copy-scenario').addEventListener('click', () => copyText(guide.scenarios[selectedScenario].command));
  $('#scenario-detail').addEventListener('click', () => selectSkill(guide.scenarios[selectedScenario].skill));
  $$('[data-scenario]').forEach(button => button.addEventListener('click', () => selectScenario(button.dataset.scenario)));
  $$('[data-skill]').forEach(button => button.addEventListener('click', () => selectSkill(button.dataset.skill)));
  $$('[data-step]').forEach(button => button.addEventListener('click', () => selectStep(Number(button.dataset.step))));
  $('#lens-select').addEventListener('change', updateLens);
  $('#history-toggle').addEventListener('change', () => selectStep(selectedStep));
  $('#race-next').addEventListener('click', () => updateRace(Math.min(4, raceStep + 1)));
  $('#race-reset').addEventListener('click', () => updateRace(0));

  const mapDialog = $('#overview-map-dialog');
  const mapFrame = $('#map-image-frame');
  const mapImage = mapFrame.querySelector('img');
  const setMapNativeWidth = () => {
    if (mapImage.naturalWidth) mapFrame.style.setProperty('--map-native-width', mapImage.naturalWidth + 'px');
  };
  mapImage.addEventListener('load', setMapNativeWidth);
  const zoomMap = $('#zoom-overview-map');
  $('#open-overview-map').addEventListener('click', () => {
    setMapNativeWidth();
    mapFrame.classList.remove('is-zoomed');
    zoomMap.setAttribute('aria-pressed', 'false');
    zoomMap.textContent = '查看原尺寸';
    mapDialog.showModal();
    document.body.style.overflow = 'hidden';
    mapFrame.scrollTop = 0;
    mapFrame.scrollLeft = 0;
    $('#close-overview-map').focus();
  });
  $('#close-overview-map').addEventListener('click', () => mapDialog.close());
  mapDialog.addEventListener('close', () => {document.body.style.overflow = '';});
  mapDialog.addEventListener('click', event => {
    if (event.target !== mapDialog) return;
    const rect = mapDialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) mapDialog.close();
  });
  zoomMap.addEventListener('click', () => {
    const zoomed = mapFrame.classList.toggle('is-zoomed');
    zoomMap.setAttribute('aria-pressed', String(zoomed));
    zoomMap.textContent = zoomed ? '适应窗口' : '查看原尺寸';
  });

  // Roving tab focus follows the WAI-ARIA tab pattern; every control is also clickable.
  $$('[role="tablist"]').forEach(list => list.addEventListener('keydown', event => {
    const tabs = [...list.querySelectorAll('[role="tab"]')];
    const index = tabs.indexOf(document.activeElement);
    if (index < 0) return;
    const vertical = list.getAttribute('aria-orientation') === 'vertical';
    let next = index;
    if (event.key === (vertical ? 'ArrowDown' : 'ArrowRight')) next = (index + 1) % tabs.length;
    else if (event.key === (vertical ? 'ArrowUp' : 'ArrowLeft')) next = (index - 1 + tabs.length) % tabs.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = tabs.length - 1;
    else return;
    event.preventDefault();
    tabs[next].focus({preventScroll:true});
    tabs[next].click();
  }));

  $$('[data-source]').forEach(link => {link.href = sourceUrl(link.dataset.source, link.dataset.anchor || '');});
  const navLinks = $$('#section-nav a');
  const sections = $$('.observed');
  let pendingScroll = false;
  const updateNav = () => {
    $('.skill-list').setAttribute('aria-orientation', window.innerWidth <= 550 ? 'horizontal' : 'vertical');
    const top = window.innerWidth <= 760 ? 110 : 90;
    let active = sections[0];
    for (const section of sections) if (section.getBoundingClientRect().top <= top) active = section;
    navLinks.forEach(link => {
      const selected = link.hash === `#${active.id}`;
      link.classList.toggle('active', selected);
      if (selected) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    pendingScroll = false;
  };
  window.addEventListener('scroll', () => {if (!pendingScroll) {pendingScroll = true; requestAnimationFrame(updateNav);}}, {passive:true});
  window.addEventListener('resize', updateNav);
  selectScenario('code');
  selectSkill('scan');
  updateLens();
  selectStep(0);
  updateRace(0);
  showMemorySample();
  selectInvestigation(0);
  updateNav();
})();
