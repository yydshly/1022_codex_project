"use strict";
(() => {
  const data = window.OIL_TONE_DATA;
  if (!data) return;
  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  const escape = value => String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const state = { group: "A", search: "", stage: 0, revision: 0, view: "annotated", source: "SKILL.md" };
  const commitRoot = `${data.meta.repo}/blob/${data.meta.sha}/skills/oil-tone/`;
  let toastTimer;
  function toast(message) {
    const box = $("#toast");
    box.textContent = message;
    box.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => box.classList.remove("visible"), 2600);
  }
  async function copy(text, message = "已复制，可粘贴查看") {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const field = document.createElement("textarea");
        field.value = text;
        field.style.cssText = "position:fixed;left:-10000px;top:0";
        document.body.append(field);
        field.select();
        const success = document.execCommand("copy");
        field.remove();
        if (!success) throw new Error("Clipboard unavailable");
      }
      toast(message);
    } catch (_) { toast("复制未完成，请选择正文复制或下载文件"); }
  }
  function download(text, filename, type = "text/markdown;charset=utf-8") {
    const url = URL.createObjectURL(new Blob([text], {type}));
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function selectTab(buttons, selected) {
    buttons.forEach(button => {
      const active = button === selected;
      button.setAttribute("aria-selected", String(active));
      button.tabIndex = active ? 0 : -1;
    });
  }
  function keyboardTabs(container) {
    container.addEventListener("keydown", event => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      const buttons = $$("[role=tab]", container);
      const index = buttons.indexOf(document.activeElement);
      if (index < 0) return;
      event.preventDefault();
      const next = event.key === "Home" ? 0 : event.key === "End" ? buttons.length - 1
        : (index + (event.key === "ArrowRight" ? 1 : -1) + buttons.length) % buttons.length;
      buttons[next].focus();
      buttons[next].click();
    });
  }

  function renderStages() {
    const list = $("#stage-tabs");
    list.innerHTML = data.stages.map((stage, index) => `<button type="button" class="stage-tab" role="tab" id="stage-${index}" aria-controls="stage-panel" aria-selected="${index === state.stage}" tabindex="${index === state.stage ? 0 : -1}" data-stage="${index}"><span class="stage-number">${stage.n}</span><strong>${escape(stage.title)}</strong></button>`).join("");
    list.addEventListener("click", event => {
      const button = event.target.closest("[data-stage]");
      if (!button) return;
      state.stage = Number(button.dataset.stage);
      selectTab($$("[role=tab]", list), button);
      renderStagePanel();
    });
    keyboardTabs(list);
    renderStagePanel();
  }
  function renderStagePanel() {
    const stage = data.stages[state.stage];
    $("#stage-panel").setAttribute("aria-labelledby", `stage-${state.stage}`);
    $("#stage-panel").innerHTML = `<div><span class="owner-badge ${stage.owner === "Python 程序" ? "program" : ""}">${escape(stage.owner)}</span><h3>${stage.n} / ${escape(stage.title)}</h3><p class="stage-file">${escape(stage.file)}</p></div><div><p class="stage-description">${escape(stage.action)}</p><div class="stage-io"><span><b>INPUT</b>${escape(stage.input)}</span><span class="io-arrow" aria-hidden="true">→</span><span><b>OUTPUT</b>${escape(stage.output)}</span></div><p class="boundary">${escape(stage.boundary)}</p></div>`;
  }

  function renderFilters() {
    $("#rule-filters").innerHTML = [{id:"all",title:"全部",count:23}, ...data.groups].map(group => `<button type="button" class="rule-filter" aria-pressed="${state.group === group.id}" data-group="${group.id}">${group.id === "all" ? "全部" : group.title}<span>${group.count}</span></button>`).join("");
    $("#rule-filters").addEventListener("click", event => {
      const button = event.target.closest("[data-group]");
      if (!button) return;
      state.group = button.dataset.group;
      $$("[data-group]").forEach(item => item.setAttribute("aria-pressed", String(item.dataset.group === state.group)));
      renderRules();
    });
    $("#rule-search").addEventListener("input", event => {
      state.search = event.target.value.toLocaleLowerCase().trim();
      if (state.search) {
        state.group = "all";
        $$("[data-group]").forEach(item => item.setAttribute("aria-pressed", String(item.dataset.group === "all")));
      }
      renderRules();
    });
    renderRules();
  }
  function renderRules() {
    const visible = data.rules.filter(rule => (state.group === "all" || rule.group === state.group) && (!state.search || Object.values(rule).join(" ").toLocaleLowerCase().includes(state.search)));
    $("#rule-count").textContent = `显示 ${visible.length} 条 / 共 23 条 · 展开条目查看原文与示例`;
    $("#rule-empty").hidden = visible.length > 0;
    $("#rule-grid").innerHTML = visible.map(rule => `<details class="rule-card" id="rule-${rule.id}"><summary><span class="rule-id">${rule.id}</span><h3>${escape(rule.title)}</h3><span class="line-label">L${rule.line}</span></summary><div class="rule-body"><dl><div><dt>判断条件</dt><dd>${escape(rule.trigger)}</dd></div><div><dt>编辑动作</dt><dd>${escape(rule.action)}</dd></div><div><dt>适用边界</dt><dd>${escape(rule.boundary)}</dd></div></dl><div class="rule-example"><p><span>原表达</span>${escape(rule.before)}</p><p><span>处理示意</span>${escape(rule.after)}</p></div><div class="rule-source"><blockquote>${escape(rule.source.replace(/^\s*(?:\d+\.|-)\s*/, ""))}</blockquote><a href="${commitRoot}SKILL.md#L${rule.line}" target="_blank" rel="noopener noreferrer">查看上游第 ${rule.line} 行 ↗</a></div></div></details>`).join("");
  }
  function openRule(id) {
    state.group = "all";
    state.search = "";
    $("#rule-search").value = "";
    $$("[data-group]").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.group === "all")));
    renderRules();
    const card = $(`#rule-${id}`);
    if (!card) return;
    card.open = true;
    card.scrollIntoView({block:"center",behavior:reducedMotion() ? "auto" : "smooth"});
    $("summary", card).focus({preventScroll:true});
  }
  const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function annotatedParagraph(paragraph) {
    const edits = data.revisions.filter(revision => paragraph.includes(revision.quote))
      .map(revision => ({...revision,start:paragraph.indexOf(revision.quote)})).sort((a,b) => a.start-b.start);
    let cursor = 0;
    let html = "";
    edits.forEach(edit => {
      html += escape(paragraph.slice(cursor, edit.start));
      html += `<button type="button" class="edit-mark ${edit.id - 1 === state.revision ? "active" : ""}" data-revision="${edit.id - 1}" aria-pressed="${edit.id - 1 === state.revision}" aria-label="修改 ${edit.id}：${escape(edit.title)}">${escape(edit.quote)}<sup>${String(edit.id).padStart(2,"0")}</sup></button>`;
      cursor = edit.start + edit.quote.length;
    });
    return html + escape(paragraph.slice(cursor));
  }
  function renderPlain(text, annotated = false) {
    const headings = new Set(["能力：简单，但不随意", "体验：快，但不止于快", "怎样导出笔记", "这次导出用了多长时间", "使用前需要了解的限制"]);
    return text.split("\n\n").map((paragraph, index) => {
      if (index === 0) return `<h3>${annotated ? annotatedParagraph(paragraph) : escape(paragraph)}</h3>`;
      if (headings.has(paragraph)) return `<h4>${annotated ? annotatedParagraph(paragraph) : escape(paragraph)}</h4>`;
      if (paragraph.startsWith("|")) {
        const rows = paragraph.split("\n").map(row => row.split("|").slice(1,-1).map(cell => cell.trim()));
        return `<table><thead><tr>${rows[0].map(cell=>`<th scope="col">${escape(cell)}</th>`).join("")}</tr></thead><tbody>${rows.slice(2).map(row=>`<tr>${row.map(cell=>`<td>${escape(cell)}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
      }
      if (/^\d+\. /.test(paragraph)) return `<ol>${paragraph.split("\n").map(line=>`<li>${escape(line.replace(/^\d+\. /,""))}</li>`).join("")}</ol>`;
      if (paragraph.startsWith("- ")) return `<ul>${paragraph.split("\n").map(line=>`<li>${escape(line.slice(2))}</li>`).join("")}</ul>`;
      return `<p${paragraph.startsWith("（教学示例") ? ' class="teaching-note"' : ""}>${annotated ? annotatedParagraph(paragraph) : escape(paragraph)}</p>`;
    }).join("");
  }
  function renderDocument() {
    const text = state.view === "final" ? data.final : data.original;
    $("#document").innerHTML = renderPlain(text, state.view === "annotated");
    $("#document").setAttribute("aria-labelledby", `doc-tab-${state.view}`);
    $("#document-caption").textContent = state.view === "final" ? "无批注成稿 · 保留事实和使用条件" : state.view === "original" ? "完整原稿 · 有意保留问题以便对照" : "点击标记，查看这一处为什么改";
    selectTab($$(".doc-tabs [role=tab]"), $(`#doc-tab-${state.view}`));
    renderAnnotation();
    $$("#revision-index button").forEach((button,index) => button.classList.toggle("active", index === state.revision && state.view === "annotated"));
  }
  function renderAnnotation() {
    const revision = data.revisions[state.revision];
    $("#revision-position").textContent = state.view === "annotated" ? `${String(revision.id).padStart(2,"0")} / ${data.revisions.length}` : "阅读模式";
    $(".revision-navigation").hidden = state.view !== "annotated";
    if (state.view !== "annotated") {
      $("#annotation-detail").innerHTML = `<h3>${state.view === "final" ? "修改后的完整稿件" : "先读一遍原稿"}</h3><div class="plain-view-note"><p>${state.view === "final" ? "操作、数字与功能范围都能回到事实底稿核对。成稿比原稿稍长，增加的是必要步骤、条件与限制。" : "这篇稿子故意混合了空泛评价、含糊步骤、事实错误和未确认的功能承诺。先读全文，再打开批注看每处改变。"}</p><p>例子中的产品和数据均为虚构，不能用于评价真实产品性能。</p><button type="button" data-return-annotations>返回逐处批注 ↗</button></div>`;
      return;
    }
    const facts = revision.facts.map(id => data.facts.find(fact=>fact.id===id));
    $("#annotation-detail").innerHTML = `<span class="annotation-type">${escape(revision.type)}修改</span><h3>${escape(revision.title)}</h3><p class="change-label">原稿</p><p class="change-old">${escape(revision.quote)}</p><p class="change-label">修改后 / 编辑动作</p><p class="change-new">${escape(revision.replacement)}</p><p class="change-why">${escape(revision.why)}</p><div class="annotation-rules">${revision.rules.map(id=>`<button type="button" data-open-rule="${id}" title="查看规则 ${id}">${id} ↗</button>`).join("")}</div><div class="fact-reference">${facts.length ? "事实依据" : "依据：表达与结构判断，没有补充产品事实"}${facts.map(fact=>`<p><strong>${fact.id}</strong> ${escape(fact.text)}</p>`).join("")}</div>`;
    $("#previous-revision").disabled = state.revision === 0;
    $("#next-revision").disabled = state.revision === data.revisions.length - 1;
  }
  function chooseRevision(index, scroll = true) {
    state.revision = Math.max(0, Math.min(index, data.revisions.length-1));
    if (state.view !== "annotated") {
      state.view = "annotated";
      renderDocument();
    } else {
      $$(".edit-mark").forEach(mark => {
        const active = Number(mark.dataset.revision) === state.revision;
        mark.classList.toggle("active", active);
        mark.setAttribute("aria-pressed", String(active));
      });
      renderAnnotation();
      $$("#revision-index button").forEach((button,i)=>button.classList.toggle("active", i===state.revision));
    }
    if (scroll) {
      const mark = $(`.edit-mark[data-revision="${state.revision}"]`);
      if (mark) mark.scrollIntoView({block:"nearest",behavior:reducedMotion()?"auto":"smooth"});
    }
  }
  function setupWorkshop() {
    $("#fact-grid").innerHTML = data.facts.map(fact=>`<div class="fact-item" id="fact-${fact.id}"><strong><span>${fact.id}</span>${escape(fact.title)}</strong><p>${escape(fact.text)}</p></div>`).join("");
    $("#revision-index").innerHTML = data.revisions.map((revision,index)=>`<button type="button" data-revision="${index}" class="${index===0?"active":""}" aria-label="修改 ${revision.id}：${escape(revision.title)}" title="${escape(revision.title)}">${String(revision.id).padStart(2,"0")}</button>`).join("");
    $(".doc-tabs").addEventListener("click",event=>{
      const button = event.target.closest("[data-view]");
      if (!button) return;
      state.view = button.dataset.view;
      renderDocument();
      $("#document").scrollTop=0;
    });
    keyboardTabs($(".doc-tabs"));
    $("#workshop").addEventListener("click",event=>{
      const revision = event.target.closest("[data-revision]");
      if (revision) {
        chooseRevision(Number(revision.dataset.revision));
        if (revision.classList.contains("edit-mark") && innerWidth <= 800) $("#annotation-column").scrollIntoView({block:"nearest",behavior:reducedMotion()?"auto":"smooth"});
      }
      const rule=event.target.closest("[data-open-rule]");
      if (rule) openRule(rule.dataset.openRule);
      if (event.target.closest("[data-return-annotations]")) { state.view="annotated"; renderDocument(); }
    });
    $("#previous-revision").addEventListener("click",()=>chooseRevision(state.revision-1));
    $("#next-revision").addEventListener("click",()=>chooseRevision(state.revision+1));
    $("#copy-document").addEventListener("click",()=>copy(state.view==="final"?data.final:data.original));
    $("#download-final").addEventListener("click",()=>download(data.final+"\n","oil-tone-教学示例-最终成稿.md"));
    renderDocument();
  }

  function renderSource() {
    const source = data.sources[state.source];
    const selected = $(`[data-source="${state.source}"]`);
    selectTab($$(".source-tabs [role=tab]"), selected);
    $("#source-code").setAttribute("aria-labelledby", selected.id);
    $("#source-code").innerHTML = source.trimEnd().split("\n").map((line,index)=>`<span class="code-line" id="source-line-${index+1}"><span class="code-number" aria-hidden="true">${index+1}</span><span class="code-content">${escape(line)||" "}</span></span>`).join("");
    $("#source-code").scrollTop=0;
    $("#download-source").href=`./assets/source/${state.source}`;
    const path=state.source==="SKILL.md"?"SKILL.md":state.source==="tone_lint.py"?"scripts/tone_lint.py":"agents/openai.yaml";
    $("#upstream-file-link").href=commitRoot+path;
  }
  function setupEvidence() {
    $("#original-warning-count").textContent = data.lint.original.warning_count;
    $("#final-warning-count").textContent = data.lint.final.warning_count;
    $("#warning-list").innerHTML = data.lint.original.warnings.map(warning=>`<div class="warning-item"><code>WARN L${warning.line}</code><div><p>${escape(warning.text)}</p><span>↳ ${escape(warning.advice)}</span></div></div>`).join("");
    $(".source-tabs").addEventListener("click",event=>{
      const button=event.target.closest("[data-source]");
      if (!button) return;
      state.source=button.dataset.source;
      renderSource();
    });
    keyboardTabs($(".source-tabs"));
    $("#copy-source").addEventListener("click",()=>copy(data.sources[state.source]));
    renderSource();
  }
  renderStages();
  renderFilters();
  $("#writing-prompt").value = data.writingPrompt;
  $("#prompt-meta").textContent = `23 条规则 · 任务模板 · 交付要求 · ${data.writingPrompt.length.toLocaleString()} 字符`;
  $("#copy-writing-prompt").addEventListener("click",()=>copy(data.writingPrompt,"已复制完整提示词，填写方括号后即可发送给 AI"));
  $("#download-writing-prompt").addEventListener("click", event => {
    event.preventDefault();
    download(data.writingPrompt, "oil-tone-完整写作提示词.txt", "text/plain;charset=utf-8");
  });
  setupWorkshop();
  setupEvidence();
  document.addEventListener("keydown",event=>{
    if (event.key === "/" && !/INPUT|TEXTAREA/.test(event.target.tagName) && !event.ctrlKey && !event.metaKey && !event.altKey) {
      event.preventDefault();
      $("#rule-search").focus();
    }
  });
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries=>{
      entries.forEach(entry=>{
        if (entry.isIntersecting) $$(".site-header nav a").forEach(link=>link.classList.toggle("active",link.hash===`#${entry.target.id}`));
      });
    },{rootMargin:"-15% 0px -65% 0px"});
    ["understanding","mechanism","rules","prompt","workshop","evidence"].forEach(id=>observer.observe(document.getElementById(id)));
  }
})();
