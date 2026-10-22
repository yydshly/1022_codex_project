(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const section = $("intent-template");
  if (!section) return;
  const tabs = Array.from(section.querySelectorAll('[role="tab"]'));
  const editor = $("intent-draft");
  let library = null;
  let libraryText = "";
  let mode = "image";
  const drafts = new Map();
  const asset = (file) => "./assets/" + file;
  const make = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  function settleEntry() {
    const target = location.hash === "#intent-template" ? section : location.hash === "#intent-editor" && library ? $("intent-editor") : null;
    if (target) requestAnimationFrame(() => target.scrollIntoView({behavior: "instant", block: "start"}));
  }
  function sync() {
    if (!library) return;
    const draft = drafts.get(mode);
    editor.value = draft.text;
    $("intent-panel").setAttribute("aria-labelledby", "intent-tab-" + mode);
    tabs.forEach((tab) => {
      const selected = tab.dataset.intentMode === mode;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    const origin = draft.caseId ? library.cases.find((item) => item.id === draft.caseId).title + " / 事后整理的复用方案" : "空白" + library.templates[mode].title;
    $("intent-draft-state").textContent = origin + (draft.modified ? " · 已编辑" : "") + " · 当前文本尚未生成新作品";
  }
  function select(next, focus = false) {
    if (!library) return;
    mode = next; sync();
    if (focus) $("intent-tab-" + mode).focus();
  }
  function loadCase(item, next) {
    drafts.set(next, {text: item.briefs[next], caseId: item.id, modified: false});
    select(next);
    $("intent-status").textContent = "已载入「" + item.title + "」的复用方案。可改写后交给AI；这不是该作品的准确历史指令。";
    history.replaceState(null, "", "#intent-editor");
    $("intent-editor").scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
    editor.focus({preventScroll: true});
  }
  function renderCases() {
    for (const item of library.cases) {
      const card = make("article", undefined, "intent-case");
      const artwork = make("div", undefined, "intent-case-art");
      const image = make("img"); image.src = asset(item.image); image.alt = item.image_alt;
      image.width = item.medium === "video" ? 1902 : 1122; image.height = item.medium === "video" ? 1092 : 1402; image.loading = "lazy";
      artwork.append(image);
      const body = make("div", undefined, "intent-case-body");
      body.append(make("span", item.family, "intent-case-family"), make("h5", item.title));
      for (const [label, value] of [["意图", item.intent], ["落地", item.translation]]) {
        const paragraph = make("p"); paragraph.append(make("b", label + " / "), document.createTextNode(value)); body.append(paragraph);
      }
      body.append(make("p", item.observation, "intent-case-observed"));
      const promptLink = make("a", "查看首轮实际生成指令 ↗"); promptLink.href = asset(item.actual_prompt); promptLink.target = "_blank"; promptLink.rel = "noopener"; body.append(promptLink);
      if (item.repair_prompt) {
        const link = make("a", "查看已执行的实际返修指令 ↗"); link.href = asset(item.repair_prompt); link.target = "_blank"; link.rel = "noopener"; body.append(link);
      }
      const resultLink = make("a", item.medium === "video" ? "播放实际AI原片 ↓" : "查看实际作品与对照 ↓"); resultLink.href = "#" + item.result_anchor; body.append(resultLink);
      const controls = make("div", undefined, "intent-case-buttons");
      for (const next of Object.keys(item.briefs)) {
        const button = make("button", next === "repair" ? "载入尺度返修方案" : "载入" + (next === "video" ? "视频" : "图片") + "复用方案");
        button.type = "button"; button.setAttribute("aria-label", item.title + "：" + button.textContent);
        button.addEventListener("click", () => loadCase(item, next)); controls.append(button);
      }
      body.append(controls); card.append(artwork, body); $("intent-cases").append(card);
    }
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => select(tab.dataset.intentMode));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = tabs.length - 1;
      else return;
      event.preventDefault(); select(tabs[next].dataset.intentMode, true);
    });
  });
  editor.addEventListener("input", () => {
    if (!library) return;
    const draft = drafts.get(mode); draft.text = editor.value; draft.modified = true;
    const origin = draft.caseId ? library.cases.find((item) => item.id === draft.caseId).title + " / 复用方案" : library.templates[mode].title;
    $("intent-draft-state").textContent = origin + " · 已编辑 · 当前文本尚未生成新作品";
  });
  $("intent-reset").addEventListener("click", () => {
    if (!library) return;
    drafts.set(mode, {text: library.templates[mode].text, caseId: null, modified: false}); sync();
    $("intent-status").textContent = "当前类型已恢复空白模板。其他类型草稿仍保留。";
  });
  function download(content, mime, name) {
    const url = URL.createObjectURL(new Blob([content], {type: mime}));
    const link = make("a"); link.href = url; link.download = name; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  $("intent-copy").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(editor.value); $("intent-status").textContent = "已复制当前完整指令，可与标明角色的素材一并交给AI。"; }
    catch { $("intent-status").textContent = "可以选择文本手动复制，或下载当前TXT。"; }
  });
  $("intent-library-download").addEventListener("click", (event) => {
    if (!libraryText) return;
    event.preventDefault();
    download(libraryText, "application/json;charset=utf-8", "art-intent-library.json");
  });
  $("intent-txt").addEventListener("click", () => download(editor.value, "text/plain;charset=utf-8", "art-intent-" + mode + ".txt"));
  $("intent-json").addEventListener("click", () => {
    if (!library) return;
    const draft = drafts.get(mode);
    const sourceCase = draft.caseId ? library.cases.find((item) => item.id === draft.caseId) : null;
    const exported = {version: 1, kind: "art-intent-prompt-draft", template_type: mode, medium: mode === "repair" ? null : mode, generated: false, modified: draft.modified,
      principle: library.principle, prompt: editor.value, source_case: sourceCase ? {id: sourceCase.id, title: sourceCase.title,
        exact_historical_prompt: "assets/" + (mode === "repair" ? sourceCase.repair_prompt : sourceCase.actual_prompt), record: "assets/" + sourceCase.record,
        preview_asset: "assets/" + sourceCase.image, input_role: sourceCase.input_role,
        adapted_from_existing_case: true} : null, actual_new_output: null};
    download(JSON.stringify(exported, null, 2) + "\n", "application/json;charset=utf-8", "art-intent-" + mode + "-draft.json");
  });
  async function init() {
    try {
      const response = await fetch(asset("intent/templates.json")); if (!response.ok) throw new Error("Guide unavailable");
      libraryText = await response.text(); library = JSON.parse(libraryText);
      for (const [id, template] of Object.entries(library.templates)) drafts.set(id, {text: template.text, caseId: null, modified: false});
      renderCases(); sync();
      $("intent-loading").hidden = true; $("intent-tools").hidden = false;
      document.dispatchEvent(new Event("poster:intent-template-ready")); settleEntry();
    } catch {
      $("intent-loading").textContent = "模板未能载入，可通过上方链接下载完整创作总纲或模板与案例库。";
    }
  }
  window.addEventListener("load", settleEntry, {once: true});
  init();
})();
