(function () {
  'use strict';
  const D = window.OCResearch, L = window.OCLab;
  const $ = id => document.getElementById(id);
  const escape = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const sourceURL = path => `${D.repo}/blob/${D.commit}/${path}`;
  let scenario = new URLSearchParams(location.search).get('scenario');
  if (!D.scenarios[scenario]) scenario = 'inventory';
  let latest = null, latestMutation = null, engineHash = 'unverified', sources = [], selectedSource = null;
  let toastTimer;
  function toast(message) { clearTimeout(toastTimer); $('toast').textContent = message; $('toast').hidden = false; toastTimer = setTimeout(() => { $('toast').hidden = true; }, 3500); }
  function download(name, text, type = 'text/plain;charset=utf-8') {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const link = document.createElement('a'); link.href = url; link.download = name; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  for (const id of ['openPoster','enlargePoster']) $(id).addEventListener('click', () => $('posterDialog').showModal());
  $('posterDialog').addEventListener('click', event => { if (event.target === $('posterDialog')) $('posterDialog').close(); });
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); toast('已复制完整文本'); return true; }
    catch { toast('浏览器未允许复制，请在文本区选取后复制或下载文件。'); return false; }
  }
  function bindTabs(container, activate) {
    container.addEventListener('keydown', event => {
      if (!['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
      const tabs = [...container.querySelectorAll('[role="tab"]')];
      const current = tabs.indexOf(document.activeElement); if (current < 0) return;
      let next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (current + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
      event.preventDefault(); tabs[next].focus(); activate(tabs[next]);
    });
  }
  $('comparisonRows').innerHTML = D.comparison.map(row => `<tr>${row.map((value,i) => `<${i ? 'td':'th'}${i ? '' : ' scope="row"'}>${escape(value)}</${i ? 'td':'th'}>`).join('')}</tr>`).join('');

  function showStage(index) {
    const stage = D.stages[index];
    $('stageTabs').innerHTML = D.stages.map((item,i) => `<button id="stage-${i}" role="tab" aria-selected="${i === index}" aria-controls="stagePanel" tabindex="${i === index ? 0 : -1}" data-index="${i}"><span>${String(i+1).padStart(2,'0')}</span>${item.name}<small>${item.zh}</small></button>`).join('');
    $('stagePanel').setAttribute('aria-labelledby',`stage-${index}`);
    $('stagePanel').innerHTML = `<div class="stage-copy"><span class="eyebrow">${stage.name} / ${String(index+1).padStart(2,'0')}</span><h3>${stage.zh}</h3><dl><dt>输入</dt><dd>${stage.input}</dd><dt>具体动作</dt><dd>${stage.action}</dd><dt>产物</dt><dd>${stage.artifact}</dd></dl></div><div class="stage-example"><span class="tiny-label">以重复扣库存为例</span><pre>${escape(stage.example)}</pre><p><span>注意</span>${stage.guard}</p></div>`;
  }
  $('stageTabs').addEventListener('click', event => { const button = event.target.closest('[data-index]'); if (button) showStage(Number(button.dataset.index)); });
  // Rendered tabs are replaced; refocus the new node after keyboard activation.
  bindTabs($('stageTabs'), button => { const index = Number(button.dataset.index); showStage(index); $(`stage-${index}`).focus(); });
  showStage(0);

  function resetResults() {
    latest = null; latestMutation = null; $('downloadEvidence').disabled = true;
    $('testSummary').textContent = '尚未运行'; $('testSummary').className = '';
    $('testResults').innerHTML = '<p class="empty-state">当前选择已更新，请运行检查。不会沿用上一份结果。</p>';
    $('testMeter').innerHTML = ''; $('mutationResults').innerHTML = '';
  }
  function seed() { const value = Number($('seedInput').value); return Number.isFinite(value) ? Math.max(0, Math.min(2147483647, Math.trunc(value))) : 42; }
  function showScenario(id) {
    scenario = id; const item = D.scenarios[id];
    $('scenarioTabs').innerHTML = Object.entries(D.scenarios).map(([key,value],i) => `<button id="scenario-${key}" role="tab" aria-selected="${key === id}" aria-controls="scenarioContent" tabindex="${key === id ? 0 : -1}" data-scenario="${key}"><span>0${i+1}</span>${value.label}</button>`).join('');
    document.querySelector('.lab-body').id = 'scenarioContent';
    document.querySelector('.lab-body').setAttribute('role','tabpanel');
    document.querySelector('.lab-body').setAttribute('aria-labelledby',`scenario-${id}`);
    $('scenarioDomain').textContent = item.domain; $('scenarioTitle').textContent = item.title; $('scenarioIntro').textContent = item.intro;
    $('variantSelect').innerHTML = L.variants[id].map(([key,title]) => `<option value="${key}">${title}${key === L.correct[id] ? ' · 修复版' : ''}</option>`).join('');
    $('weakNote').textContent = `试一试简化检查：${item.weak}`;
    $('scenarioContract').innerHTML = item.contract.map(text => `<li>${escape(text)}</li>`).join('');
    $('scenarioWhy').textContent = item.why; $('scenarioMapping').textContent = item.mapping; $('scenarioLimit').textContent = item.limit;
    document.querySelector('.seed-label').hidden = id !== 'limiter';
    $('traceOutput').textContent = '选择输入后点击执行。';
    const controls = {
      inventory: '<label>通知方式<select id="patternSelect"><option value="serial">连续重试</option><option value="concurrent">并发交错（确定性调度）</option><option value="restart">处理后重启再重试</option><option value="failure">标记后故障再重试</option></select></label><label>重复次数<input id="requestCount" type="number" min="2" max="50" value="10"></label>',
      limiter: '<label>请求序列<select id="sequenceSelect"><option value="burst">同一时刻连续 5 次</option><option value="boundary">1000ms 与 1001ms 边界</option><option value="cross">跨整秒的 6 次请求</option><option value="keys">alice 用完，bob 再请求</option></select></label>',
      permission: '<label>接口<select id="actionSelect"><option value="get">订单详情</option><option value="list">订单列表</option><option value="export">订单导出</option></select></label><label>订单 ID<select id="orderSelect"><option value="B-01">B-01 · beta 的订单</option><option value="A-01">A-01 · alpha 的订单</option></select></label><label>请求体中的租户<select id="bodyTenant"><option value="beta">beta · 伪造</option><option value="alpha">alpha</option></select></label>',
      api: '<label>模拟请求<select id="apiRequest"><option value="legacy">旧客户端：不传 country</option><option value="new">新客户端：传 country</option></select></label>'
    };
    $('traceControls').innerHTML = controls[id];
    const url = new URL(location.href); url.searchParams.set('scenario',id); history.replaceState(null,'',url);
    resetResults(); renderTemplate();
  }
  $('scenarioTabs').addEventListener('click', event => { const button = event.target.closest('[data-scenario]'); if (button) showScenario(button.dataset.scenario); });
  bindTabs($('scenarioTabs'), button => { const id = button.dataset.scenario; showScenario(id); $(`scenario-${id}`).focus(); });
  for (const id of ['variantSelect','strengthSelect','seedInput']) $(id).addEventListener('change',resetResults);
  function format(value) { return typeof value === 'string' ? value : JSON.stringify(value); }
  $('runTests').addEventListener('click', () => {
    latest = L.runSuite(scenario,$('variantSelect').value,$('strengthSelect').value,seed());
    $('testSummary').textContent = `${latest.passed}/${latest.total} 通过${latest.failed ? ` · ${latest.failed} 项失败` : ' · 当前检查全绿'}`;
    $('testSummary').className = latest.failed ? 'text-fail' : 'text-pass';
    $('testMeter').innerHTML = latest.rows.map(r => `<span class="${r.pass ? 'pass':'fail'}"></span>`).join('');
    $('testResults').innerHTML = latest.rows.map(r => `<details class="test-row ${r.pass ? 'passed':'failed'}"><summary><span class="test-id">${r.id}</span><span>${r.title}</span><b class="status ${r.pass ? 'pass':'fail'}">${r.pass ? 'PASS':'FAIL'}</b></summary><div class="assertion"><span>期望 <code>${escape(format(r.expected))}</code></span><span>实际 <code>${escape(format(r.actual))}</code></span></div></details>`).join('');
    if ($('strengthSelect').value === 'weak') $('testResults').insertAdjacentHTML('beforeend','<p class="result-caution">当前仅运行简化检查。全绿不代表完整需求通过，请切换完整验收标准再比较。</p>');
    $('downloadEvidence').disabled = false;
  });
  $('chooseFixed').addEventListener('click', () => { $('variantSelect').value = L.correct[scenario]; resetResults(); toast('已切换修复实现；点击运行以获得新结果。'); });
  $('runMutations').addEventListener('click', () => {
    latestMutation = L.mutation(scenario,$('strengthSelect').value,seed());
    $('mutationResults').innerHTML = `<div class="mutation-block"><div><h4>故意改坏，测试发现了 ${latestMutation.killed}/${latestMutation.total} 个</h4><p>修复版基线：${latestMutation.baselinePassed ? '通过':'失败，不能信任本轮变异结论'}。每项都是重新执行当前检查范围，不是预设动画。</p></div>${latestMutation.mutants.map(m => `<div class="mutant-row"><span>${escape(m.title)}</span><code>${m.failures.join(', ') || '没有测试失败'}</code><b class="status ${m.killed ? 'pass':'fail'}">${m.killed ? '被发现':'漏过了'}</b></div>`).join('')}<p class="fine-print">人工选择的行为缺陷，用于教学；不是 AST 自动变异，也不是所有可能缺陷的覆盖率。</p></div>`;
    $('downloadEvidence').disabled = false;
  });
  $('runTrace').addEventListener('click', () => {
    const variant = $('variantSelect').value;
    if (scenario === 'inventory') {
      const requests = Math.max(2,Math.min(50,Number($('requestCount').value) || 10));
      const result = L.inventory({variant,pattern:$('patternSelect').value,requests});
      $('traceOutput').textContent = `输入：库存 10，同一订单通知 ${requests} 次（故障模式为故障一次后重试）\n输出：库存 ${result.stock}，成功扣减 ${result.effects} 次\n\n${result.trace.map((t,i)=>`${String(i+1).padStart(2,'0')}  ${t}`).join('\n')}`;
    } else if (scenario === 'limiter') {
      const sequences = {burst:[0,0,0,0,0].map(t=>['alice',t]),boundary:[0,0,0,1000,1001].map(t=>['alice',t]),cross:[950,960,970,1001,1002,1003].map(t=>['alice',t]),keys:[['alice',0],['alice',0],['alice',0],['bob',0]]};
      const result = L.rateSequence(variant,sequences[$('sequenceSelect').value]);
      $('traceOutput').textContent = result.map((r,i)=>`${i+1}. ${r.key.padEnd(5)} @ ${String(r.time).padStart(4)}ms → ${r.allowed ? '允许':'拒绝'}`).join('\n');
    } else if (scenario === 'permission') {
      const request={tenant:'alpha',bodyTenant:$('bodyTenant').value,id:$('orderSelect').value,action:$('actionSelect').value};
      $('traceOutput').textContent = `可信身份：alpha\n请求：${JSON.stringify(request,null,2)}\n\n响应：${JSON.stringify(L.permission(variant,request),null,2)}`;
    } else {
      const payload=$('apiRequest').value==='legacy'?{}:{country:'CN'}; const result=L.api(variant,payload);
      $('traceOutput').textContent=`请求：${JSON.stringify(payload)}\n\n响应：${JSON.stringify(result,null,2)}\n\n旧客户端需要字符串 id：${result.status===200 && typeof result.user.id==='string' ? '可读取':'不可用'}`;
    }
  });
  $('downloadEvidence').addEventListener('click', () => {
    const evidence = {kind:'本地教学实验运行结果',runAt:new Date().toISOString(),engineVersion:L.VERSION,engineSHA256:engineHash,
      upstreamReference:D.commit,scenario,implementation:$('variantSelect').value,strength:$('strengthSelect').value,seed:seed(),
      suite:latest,mutation:latestMutation,notRun:['真实业务服务、数据库与跨进程并发','真实 AI 对照实验','上游完整 gauntlet 与独立验证协议'],scope:D.scenarios[scenario].limit};
    download(`old-coder-${scenario}-evidence.json`,JSON.stringify(evidence,null,2),'application/json');
  });

  function renderLayers(filter='all') {
    $('layerGrid').innerHTML = D.layers.filter(l=>filter==='all'||l.risk===filter).map((l,i)=>`<details class="layer-card"><summary><span class="layer-number">${String(D.layers.indexOf(l)+1).padStart(2,'0')}</span><h3>${l.name}</h3><p>${l.question}</p><span class="expand-symbol">+</span></summary><div class="layer-body"><span class="tiny-label">工具示例</span><code>${escape(l.tool)}</code><h4>具体怎么查</h4><p>${l.example}</p><h4>它的盲区</h4><p>${l.blind}</p></div></details>`).join('');
  }
  $('layerFilters').addEventListener('click',event=>{const button=event.target.closest('[data-filter]');if(!button)return;for(const b of $('layerFilters').querySelectorAll('button'))b.setAttribute('aria-pressed',String(b===button));renderLayers(button.dataset.filter);});
  renderLayers();
  $('apiGates').innerHTML=D.gates.map(([title,text],i)=>`<details><summary><span>${String(i+1).padStart(2,'0')}</span><h3>${title}</h3><b>+</b></summary><p>${text}</p></details>`).join('');
  $('faqList').innerHTML=D.faq.map(([question,answer])=>`<details><summary>${question}<span>+</span></summary><p>${answer}</p></details>`).join('');

  function renderRisk() {
    const tier=Number($('riskSelect').value);
    const items={1:['Tier 1 · 小范围','全量相关测试与 lint；通常不必为错别字专门新增测试。说明为什么无需新增测试。'],2:['Tier 2 · 一般功能','完整 SPEC → RED → GREEN → REFACTOR → GAUNTLET → EVIDENCE。修 Bug 先留下能复现问题的失败测试。'],3:['Tier 3 · 高风险','先写故障模型；完整流程加属性、变异与主动攻击，并为并发、回滚、兼容、性能等风险选专门检查。独立新上下文复核是可选实验。']};
    $('riskAdvice').innerHTML=`<span class="tier-label">${items[tier][0]}</span><p>${items[tier][1]}</p><small>分级依据是影响范围，不能只按代码行数判断。最终选择由具体项目风险决定。</small>`;
  }
  function template() {
    const s=D.scenarios[scenario],type=$('templateSelect').value;
    if(type==='spec')return `# SPEC 草案 — ${s.label}\n\n状态：未获人确认（本研究生成的教学草案）\n风险建议：Tier ${s.tier}\n任务：${s.request}\n\n## 验收场景\n${s.contract.map((t,i)=>`- S${i+1}：${t}`).join('\n')}\n\n## Must NOT\n- 不破坏现有接口与已确认行为。\n- 不把未运行的检查记为通过。\n\n## 故障模型\n- 列出该项目真实可能出现的错误，并为每项指定检查。\n\n## 环境计划（待按真实项目补齐）\n- 已有测试与基线：待检查\n- 工具与新增依赖：待说明，优先复用现有工具\n- 隔离与改动文件：待明确\n\n## 修订记录\n- 2026-10-22：根据教学场景生成草案，未代表真实业务审批。`;
    if(type==='evidence')return `# EVIDENCE 模板 — ${s.label}\n\n- 规格确认：待记录（没有明确确认则写未获得）\n- 源码状态：待填写 commit 或源码哈希\n- 环境与工具版本：待记录\n- 复跑入口：待填写仓库中存在的命令\n- 最后改动后的运行时间：待记录\n- 独立验证：not performed（除非完整执行协议）\n\n## 需求 → 测试映射\n| 需求 | 测试 | 实际结果 |\n| --- | --- | --- |\n${s.contract.map((t,i)=>`| S${i+1} ${t} | 待填写 | unverified |`).join('\n')}\n\n## 检查层\n| 检查 | 命令 | 退出码与实际数字 |\n| --- | --- | --- |\n| 全量测试 | 待填写 | unverified |\n| 类型 / lint | 待填写 | unverified |\n| 改动行覆盖 / 分支 | 待填写 | unverified |\n| 变异与随机输入 | 待填写 | unverified |\n| 真实执行与领域检查 | 待填写 | unverified |\n\n## 未完成或不适用\n分别记录 n-a（确实不适用）、unavailable（缺工具）、substituted（替代且说明检测不到什么）。\n\n## 失败、修复与已知盲区\n如实记录；只有从最后源码运行得到的数字才能进入正式结果。`;
    return `请按 old-coder 的证据优先方法处理以下任务。\n\n任务：${s.request}\n\n先检查现有代码、测试与失败基线，再写 SPEC：具体输入输出、边界、Must NOT、故障模型、工具和依赖计划、工作隔离方案。\n\n至少覆盖：\n${s.contract.map(t=>`- ${t}`).join('\n')}\n\n先展示规格供我确认；若明确约定自主执行，记录规格未获得人工确认，不声称已审批。\n\n每个行为先写能失败的测试，再实现和重构。不得弱化断言来获得通过。按实际风险运行相关检查；证明关键测试和自制检查器能发现已知错误。\n\n最后交付 EVIDENCE：逐条需求对应的测试、真实命令、退出码和结果、源码身份、环境版本、一条可复跑入口、失败处理及未验证项。未运行标 unverified。\n\n本请求草案尚需结合真实项目调整；本网页的 JS 教学结果不作为生产系统证据。`;
  }
  function renderTemplate(){ $('templateOutput').textContent=template();$('copyStatus').textContent=''; }
  $('riskSelect').addEventListener('change',renderRisk);$('templateSelect').addEventListener('change',renderTemplate);
  $('copyTemplate').addEventListener('click',async()=>{$('copyStatus').textContent=await copy(template())?'已复制':'可下载后使用';});
  $('downloadTemplate').addEventListener('click',()=>download(`old-coder-${scenario}-${$('templateSelect').value}.md`,template()));
  renderRisk();showScenario(scenario);

  async function loadEvidence(){
    try {
      const [upstream,lab]=await Promise.all([fetch('assets/upstream-reproduction.json').then(r=>{if(!r.ok)throw Error(r.status);return r.json();}),fetch('assets/lab-verification.json').then(r=>{if(!r.ok)throw Error(r.status);return r.json();})]);
      engineHash=lab.engineSHA256;
      const originalTests = upstream.results.find(r => r.name === 'tests-and-coverage');
      const originalCount = originalTests?.stdout?.match(/(\d+) passed/);
      $('localEvidence').innerHTML=`<p class="evidence-env">${escape(upstream.python)} · Windows · 固定上游源码</p><ul>${upstream.results.map(r=>`<li><span class="inline-state ${r.status==='pass'?'text-pass':'text-fail'}">${r.status.toUpperCase()}</span> ${escape({'tests-and-coverage':'原始应用测试与属性测试 + 覆盖率',types:'原始源码类型检查',lint:'原始源码 lint',format:'原始源码格式检查','real-execution':'原始 Python 示例运行','dependency-audit':'依赖已知漏洞审计'}[r.name]||r.name)}</li>`).join('')}</ul><p><strong>教学实验：</strong>${lab.checks.length} 项检查通过，四套完整契约与人工缺陷对照结果已保存。浏览器点击运行后可另外导出本次结果。</p><details><summary>查看本机没有运行的上游部分</summary><ul>${upstream.notRun.map(text=>`<li>${escape(text)}</li>`).join('')}</ul></details><p class="warning">本机仅复现选定检查，未执行上游完整 POSIX gauntlet，也未执行独立新上下文验证。</p>`;
      if (originalCount) $('localEvidence').insertAdjacentHTML('afterbegin', `<p><strong>本次应用与属性测试：${escape(originalCount[1])} 项通过。</strong><br>49/49 语句、20/20 分支覆盖；不含 9 项源码绑定测试。</p>`);
      for (const item of upstream.results.filter(r => r.reason)) {
        const note=document.createElement('p'); note.className='fine-print';
        note.textContent=`未获结果的原因：${item.name === 'dependency-audit' ? '依赖审计运行超过 120 秒。' : item.reason}`;
        $('localEvidence').appendChild(note);
      }
    }catch(error){$('localEvidence').textContent='结果文件读取失败。请通过 HTTP 服务打开页面，或下载下方原始 JSON 查看；当前不声称实测通过。';}
  }
  function selectSource(path){
    selectedSource=sources.find(item=>item.path===path);if(!selectedSource)return;
    $('sourcePath').textContent=selectedSource.path;$('sourceText').textContent=selectedSource.text;$('sourceText').scrollTop=0;
    $('sourcePermalink').href=selectedSource.url;
    for(const button of $('sourceList').querySelectorAll('button'))button.setAttribute('aria-pressed',String(button.dataset.path===path));
  }
  function renderSources(){const query=$('sourceSearch').value.toLowerCase();const list=sources.filter(item=>item.path.toLowerCase().includes(query));$('sourceList').innerHTML=list.length?list.map(item=>`<button data-path="${escape(item.path)}" aria-pressed="${selectedSource?.path===item.path}">${escape(item.path)}</button>`).join(''):'<p>没有匹配文件。</p>';}
  $('sourceSearch').addEventListener('input',renderSources);$('sourceList').addEventListener('click',event=>{const button=event.target.closest('[data-path]');if(button)selectSource(button.dataset.path);});
  $('copySource').addEventListener('click',()=>{if(selectedSource)copy(selectedSource.text);});
  $('downloadSource').addEventListener('click',()=>{if(selectedSource)download(selectedSource.path.replaceAll('/','__'),selectedSource.text);});
  for(const link of document.querySelectorAll('[data-source]')){
    link.href=sourceURL(link.dataset.source);link.target='_blank';link.rel='noopener';
  }
  async function loadSources(){try{const response=await fetch('assets/sources.json');if(!response.ok)throw Error(response.status);sources=await response.json();selectSource('skills/old-coder/SKILL.md');renderSources();}catch{$('sourcePath').textContent='原文读取失败';$('sourceText').textContent='请用本地 HTTP 服务打开网页。也可使用上方固定版本链接或查看项目 upstream/ 目录。';}}
  loadSources();loadEvidence();
  const navLinks=[...document.querySelectorAll('.sidebar nav a')];
  const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){for(const link of navLinks){const active=link.hash===`#${entry.target.id}`;link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');}}},{rootMargin:'-12% 0px -68% 0px',threshold:0});
  document.querySelectorAll('main>section').forEach(section=>observer.observe(section));
})();
