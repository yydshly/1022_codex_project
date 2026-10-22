(() => {
  'use strict';
  const data = window.RESEARCH_DATA || { papers: [], answers: [], downloads: [] };
  const $ = (selector) => document.querySelector(selector);
  const create = (tag, className, text) => { const el = document.createElement(tag); if (className) el.className = className; if (text !== undefined) el.textContent = text; return el; };
  const paths = {
    tested: { title: '我们实际跑通的内容生产路径', label: '研究扩展 + 原生聊天接口', steps: [['Europe PMC', '关键词检索开放文献，保存候选与检索记录'], ['期刊原始 PDF', '下载三篇论文，检查文件头与 SHA-256'], ['Open Notebook', '上传、提取、保存全文；选定来源组成上下文'], ['MiniMax API', '原生 provider + 本轮推理参数适配'], ['研究归档', '完整回答、失败记录、来源对照与质量核查']], status: '已产生结果', note: '两份完整回答已保存，后续补充原文精读。本页发布静态成果；Open Notebook 原版在线应用的用户访问入口仍未打通。' },
    upstream: { title: 'Auto Paper Digest 原库的编排路径', label: '原库面向 AI 论文榜单', steps: [['Hugging Face', '收集日榜 / 周榜论文，获取 arXiv 标识'], ['arXiv PDF', 'Python 下载论文并登记处理状态'], ['NotebookLM', '通过登录会话与浏览器自动化提交资料和生成'], ['产物下载', '按工作流获取 NotebookLM 生成的内容'], ['归档与发布', '本地周报、门户展示及独立发布流程']], status: '本轮未跑通', note: '水生毒理学检索来自我们的扩展。NotebookLM 路线未生成解读、视频或幻灯片，不能把替代路线的产出计入原库成功。' }
  };
  const panel = $('#architecture-panel');
  function showArchitecture(key) {
    const path = paths[key]; panel.replaceChildren(); panel.setAttribute('aria-labelledby', 'architecture-' + key);
    const label = create('div', 'flow-label'); label.append(create('strong', '', path.title), create('span', '', path.label));
    const steps = create('div', 'flow-steps'); path.steps.forEach((step, i) => { const block = create('div', 'flow-step'); block.append(create('span', 'step-num', String(i + 1).padStart(2, '0')), create('h3', '', step[0]), create('p', '', step[1])); steps.append(block); });
    const result = create('div', 'flow-result'); result.append(create('span', 'flow-pill', path.status), create('span', '', path.note)); panel.append(label, steps, result);
    document.querySelectorAll('[data-architecture]').forEach((b) => { const active = b.dataset.architecture === key; b.setAttribute('aria-selected', String(active)); b.tabIndex = active ? 0 : -1; });
  }
  document.querySelectorAll('[data-architecture]').forEach((button) => button.addEventListener('click', () => showArchitecture(button.dataset.architecture)));
  function arrowTabs(container) { container.addEventListener('keydown', (event) => { if (!['ArrowRight','ArrowLeft','ArrowDown','ArrowUp','Home','End'].includes(event.key)) return; const buttons = [...container.querySelectorAll('[role="tab"]')]; const index = buttons.indexOf(document.activeElement); if (index < 0) return; event.preventDefault(); let next = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : (index + (['ArrowRight','ArrowDown'].includes(event.key) ? 1 : -1) + buttons.length) % buttons.length; buttons[next].click(); buttons[next].focus(); }); }
  arrowTabs($('.segmented')); showArchitecture('tested');

  const reportTabs = $('#report-tabs');
  let selectedReport = null;
  function showReport(report, index) {
    selectedReport = report;
    $('#report-kicker').textContent = report.kicker;
    $('#report-title').textContent = report.title;
    $('#report-summary').textContent = report.summary;
    $('#report-origin').textContent = '2026.10.22 · 研究代理原文精读 · ' + report.characters.toLocaleString('zh-CN') + ' 字符（含引用与格式） · 非历史 MiniMax 输出';
    const facts = $('#report-facts'); facts.replaceChildren();
    report.facts.forEach((fact) => facts.append(create('span', '', fact)));
    const article = $('#report-content'); article.innerHTML = report.html;
    article.setAttribute('aria-labelledby', 'report-tab-' + index);
    const toc = $('#report-toc'); toc.replaceChildren();
    report.toc.forEach((item) => { const a = create('a', '', item.title); a.href = '#' + item.id; toc.append(a); });
    $('#report-standalone').href = report.standalone;
    $('#report-download').href = report.download;
    $('#report-evidence').href = report.evidenceDownload;
    const figures = $('#report-figures'); figures.replaceChildren();
    (report.figures || []).forEach((item) => { const figure = create('figure'); const a = create('a'); a.href = 'assets/papers/' + item.paper + '.pdf#page=' + item.page; a.target = '_blank'; a.rel = 'noopener'; const img = create('img'); img.src = item.src; img.alt = item.caption; img.loading = 'lazy'; a.append(img); figure.append(a, create('figcaption', '', item.caption + ' · PDF 第 ' + item.page + ' 页 · 原论文作者 / CC BY')); figures.append(figure); });
    $('.report-figure-section').hidden = !report.figures.length;
    reportTabs.querySelectorAll('button').forEach((b, i) => { const active = i === index; b.setAttribute('aria-selected', String(active)); b.tabIndex = active ? 0 : -1; });
  }
  (data.reports || []).forEach((report, i) => {
    const b = create('button'); b.type = 'button'; b.id = 'report-tab-' + i; b.setAttribute('role', 'tab'); b.setAttribute('aria-controls', 'report-content');
    b.append(create('span', 'report-tab-index', String(i + 1).padStart(2, '0')), create('strong', '', report.shortTitle), create('small', '', report.tabNote));
    b.addEventListener('click', () => { showReport(report, i); history.replaceState(null, '', '#report-' + report.id); }); reportTabs.append(b);
  });
  arrowTabs(reportTabs);
  function reportFromHash() {
    const hash = decodeURIComponent(location.hash.slice(1));
    const index = (data.reports || []).findIndex((r) => hash === 'report-' + r.id || hash.startsWith(r.id + '-s'));
    if (index >= 0 && selectedReport !== data.reports[index]) showReport(data.reports[index], index);
    if (hash.startsWith('report-')) $('#deep-reports').scrollIntoView();
    else if (index >= 0) document.getElementById(hash)?.scrollIntoView();
  }
  if (data.reports?.length) { showReport(data.reports[0], 0); requestAnimationFrame(reportFromHash); }
  window.addEventListener('hashchange', reportFromHash);

  let currentAnswer = null;
  const answerTabs = $('#answer-tabs');
  const isTruncated = (answer) => /trunc|length|截断|不完整/i.test((answer.status || '') + ' ' + (answer.id || ''));
  function showAnswer(answer, index) {
    currentAnswer = answer; const limited = isTruncated(answer);
    $('#answer-status').textContent = limited ? '原版截断 · 失败记录' : '完整返回 · 模型原文'; $('#answer-status').classList.toggle('limited', limited);
    $('#answer-length').textContent = Number(answer.characters || (answer.content || '').length).toLocaleString('zh-CN') + ' 字符 · 含 Markdown';
    const article = $('#answer-content'); article.innerHTML = answer.html || ''; if (!answer.html) { const pre = create('div', '', answer.content || '未找到回答文件。'); pre.style.whiteSpace = 'pre-wrap'; article.append(pre); } article.scrollTop = 0; article.setAttribute('aria-labelledby', 'answer-tab-' + index);
    const notes = $('#answer-notes'); notes.replaceChildren(); notes.append(create('strong', '', limited ? '这次未计为成功解读' : '阅读前的核对提示'));
    const list = create('ul'); const noteTexts = answer.notes && answer.notes.length ? answer.notes : limited ? ['原版请求以 length 结束，正文中途截断。保留它是为了说明参数适配的依据。'] : ['原文保留生成时的内容与错误。Cyprinodon variegatus 的中文俗名不可靠，请以拉丁学名为准。']; noteTexts.forEach((note) => list.append(create('li', '', note))); notes.append(list);
    $('#download-answer').href = answer.download || '#'; $('#download-answer').setAttribute('download', (answer.id || 'answer') + '.md');
    answerTabs.querySelectorAll('button').forEach((b, i) => { const active = i === index; b.setAttribute('aria-selected', String(active)); b.tabIndex = active ? 0 : -1; });
  }
  (data.answers || []).forEach((answer, index) => { const b = create('button'); b.type = 'button'; b.id = 'answer-tab-' + index; b.setAttribute('role', 'tab'); b.setAttribute('aria-controls', 'answer-content'); b.setAttribute('aria-selected', String(index === 0)); b.title = answer.title; const shortTitles = {single:'单篇论文解读',synthesis:'三篇综合比较',truncated:'首次截断记录'}; b.append(create('span', '', shortTitles[answer.id] || answer.title), create('small', '', isTruncated(answer) ? '原始失败记录' : index === 0 ? '单一来源 · 全文上下文' : '三个来源 · 综合比较')); b.addEventListener('click', () => showAnswer(answer, index)); answerTabs.append(b); });
  arrowTabs(answerTabs);
  if (data.answers && data.answers.length) showAnswer(data.answers[0], 0); else { $('#answer-content').textContent = '研究数据文件未加载。请确认 data.js 与本页位于同一目录。'; $('#copy-answer').disabled = true; $('#download-answer').removeAttribute('href'); }
  let toastTimer; function toast(message) { const el = $('#toast'); el.textContent = message; el.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('show'), 2600); }
  $('#copy-answer').addEventListener('click', async () => { if (!currentAnswer) return; const text = currentAnswer.content || ''; try { if (!navigator.clipboard || !window.isSecureContext) throw new Error('Use local copy'); await navigator.clipboard.writeText(text); toast('已复制模型原文'); } catch { const area = create('textarea'); area.value = text; area.style.position = 'fixed'; area.style.opacity = '0'; document.body.append(area); area.focus(); area.select(); const copied = document.execCommand('copy'); area.remove(); $('#copy-answer').focus(); toast(copied ? '已复制模型原文' : '浏览器未允许复制，可下载 Markdown 原文'); } });
  $('#print-answer').addEventListener('click', () => window.print());

  (data.papers || []).forEach((paper, index) => {
    const card = create('article', 'paper-card'); card.id = 'paper-' + paper.id; const number = create('div', 'paper-index', String(index + 1).padStart(2, '0')); number.append(create('small', '', String(paper.year)));
    const info = create('div'); info.append(create('h3', '', paper.title), create('p', 'paper-focus', [paper.organism, paper.focus].filter(Boolean).join(' · ')));
    const meta = create('div', 'paper-meta'); const mib = paper.bytes ? (paper.bytes / 1048576).toFixed(1) + ' MiB PDF' : '原始 PDF'; [paper.id, mib, paper.chars ? Number(paper.chars).toLocaleString('zh-CN') + ' 提取字符' : '', paper.license || 'CC BY'].filter(Boolean).forEach((item) => meta.append(create('span', '', item))); info.append(meta);
    const sourceIds = { PMC13162690: 'source:vhshfa8xv8wi6xozjagl', PMC11851982: 'source:bezlz9t8sr5pu12stjfu', PMC10819493: 'source:i8m54onbhh6bq0q0w7sd' }; const source = create('p', 'paper-source'); source.append(document.createTextNode('原生来源 ID  '), create('code', '', paper.source_id || sourceIds[paper.id] || '见证据文件')); info.append(source);
    if (paper.titleEn || paper.authors || paper.sha256) { const detail = create('details', 'paper-detail'); detail.append(create('summary', '', '完整题名、作者与文件校验')); if (paper.titleEn) detail.append(create('p', '', paper.titleEn)); if (paper.authors) detail.append(create('p', '', '作者：' + (Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors))); if (paper.doi) detail.append(create('p', '', 'DOI：' + paper.doi)); if (paper.sha256) { const hash = create('p', 'paper-hash'); hash.append(document.createTextNode('SHA-256：'), create('code', '', paper.sha256)); detail.append(hash); } info.append(detail); }
    const links = create('div', 'paper-links'); if (paper.pdf) { const pdf = create('a', 'button', '下载 PDF ↓'); pdf.href = paper.pdf; pdf.setAttribute('download', paper.id + '.pdf'); links.append(pdf); }
    if (paper.doi) { const doi = create('a', '', '查看期刊原文 ↗'); doi.href = paper.doi.startsWith('http') ? paper.doi : 'https://doi.org/' + paper.doi; doi.target = '_blank'; doi.rel = 'noopener noreferrer'; links.append(doi); }
    card.append(number, info, links); $('#paper-list').append(card);
  });

  const checks = [
    ['文献检索', 'Europe PMC 返回 916 条记录，保存前 30 条候选。数字只对应本次检索式与查询时点。', 'passed', '已验证'],
    ['下载与同一性', '3 份公开原始 PDF 检查文件头与 SHA-256；云端导入文件与本地下载一致。', 'passed', '已验证'],
    ['文本提取', '提取 50,134 / 61,337 / 59,970 字符；历史文本有空格丢失与重复标题；精读直接参考原 PDF 并核对关键图页，未校验全部提取字符和公式。', 'limited', '有边界'],
    ['原生模型问答', '通过 /api/chat/context → /api/chat/execute 调用模型。适配后两次 finish_reason=stop，完整原文保留。', 'passed', '已验证'],
    ['原文精读与图表', '新增 3 篇精读及 1 篇综合报告，目视核对关键图页并标出统计、样本与机制证据问题；未重跑原始实验数据。', 'limited', '有边界'],
    ['原版默认参数', '首次问答 finish_reason=length，最终正文仅 350 字符。不计入两份完整结果。', 'blocked', '未跑通'],
    ['NotebookLM 路线', '企业 API 缺许可；个人 HTTP/RPC 返回地区不支持。原 APD 路线没有生成本页展示的解读。', 'blocked', '未跑通'],
    ['向量检索与媒体', '本次使用来源全文，embedding、音频与视频均未生成；未验证对应效果。', 'blocked', '未测试'],
    ['用户网页入口', '云机内 UI / API 正常，认证保留；原生预览与隧道没有得到可用地址。当前只读结果页不代表原应用部署成功。', 'blocked', '未跑通']
  ];
  function renderChecks(filter) { const body = $('#verification-rows'); body.replaceChildren(); const rows = checks.filter((row) => filter === 'all' || row[2] === filter); rows.forEach((row) => { const tr = create('tr'); tr.append(create('td', '', row[0]), create('td', '', row[1])); const td = create('td'); td.append(create('span', 'status-label ' + row[2], row[3])); tr.append(td); body.append(tr); }); $('#verification-count').textContent = rows.length + ' 条记录'; document.querySelectorAll('[data-filter]').forEach((b) => { const active = b.dataset.filter === filter; b.classList.toggle('active', active); b.setAttribute('aria-pressed', String(active)); }); }
  document.querySelectorAll('[data-filter]').forEach((b) => b.addEventListener('click', () => renderChecks(b.dataset.filter))); renderChecks('all');
  (data.downloads || []).forEach((file) => { const offlineArchive = window.location.protocol === 'file:' && /research-archive\.zip$/.test(file.href); const link = create(offlineArchive ? 'div' : 'a', offlineArchive ? 'offline-archive' : ''); if (!offlineArchive) { link.href = file.href; link.setAttribute('download', ''); } link.append(create('span', 'file-type', (file.type || file.href.split('.').pop() || 'FILE').toUpperCase()), create('span', '', offlineArchive ? '当前已是离线档案，无需再次下载' : file.title), create('span', 'file-arrow', offlineArchive ? '✓' : '↓')); $('#download-list').append(link); });
  const navigation = [...document.querySelectorAll('.sidebar nav a')];
  if ('IntersectionObserver' in window) { const observer = new IntersectionObserver((entries) => { const visible = entries.filter((entry) => entry.isIntersecting).sort((a,b) => a.boundingClientRect.top - b.boundingClientRect.top); if (!visible.length) return; const id = visible[0].target.id; navigation.forEach((link) => { const active = link.getAttribute('href') === '#' + id; link.classList.toggle('active', active); if (active) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current'); }); }, { rootMargin: '-15% 0px -60% 0px', threshold: 0 }); document.querySelectorAll('section.section-anchor').forEach((section) => observer.observe(section)); }
})();
