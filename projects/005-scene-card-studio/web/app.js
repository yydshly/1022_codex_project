"use strict";
(() => {
  const data = window.SCENE_CARD;
  if (!data) return;
  const $ = (selector) => document.querySelector(selector);
  const promptText = $("#prompt-text");
  const promptTabs = [...document.querySelectorAll("[data-prompt]")];
  let selectedPrompt = "quick";

  function showPrompt(id) {
    const entry = data.prompts.find((item) => item.id === id);
    if (!entry) return;
    selectedPrompt = id;
    promptText.value = entry.text;
    $("#prompt-count").textContent = `${[...entry.text].length.toLocaleString("zh-CN")} 字符`;
    $("#download-prompt").href = entry.url;
    $("#prompt-panel").setAttribute("aria-labelledby", `tab-${id}`);
    $("#copy-status").textContent = entry.note;
    promptTabs.forEach((tab) => {
      const active = tab.dataset.prompt === id;
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
  }
  promptTabs.forEach((tab, index) => {
    tab.addEventListener("click", () => showPrompt(tab.dataset.prompt));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % promptTabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + promptTabs.length) % promptTabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = promptTabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      showPrompt(promptTabs[next].dataset.prompt);
      promptTabs[next].focus();
    });
  });

  async function copy(text, status, fallback) {
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(text);
      status.textContent = "已复制，可以粘贴到你的模型对话。";
    } catch {
      if (fallback) {
        fallback.hidden = false;
        fallback.focus();
        fallback.select();
        try {
          if (document.execCommand("copy")) {
            status.textContent = "已复制，可以粘贴到你的模型对话。";
            return;
          }
        } catch { /* Selection remains available for manual copying. */ }
        status.textContent = "内容已选中，请按 Ctrl/Cmd+C 复制，或下载文件。";
      }
    }
  }
  $("#copy-prompt").addEventListener("click", () => copy(promptText.value, $("#copy-status"), promptText));

  const caseTabs = [...document.querySelectorAll("[data-case]")];
  function fillCaseList(selector, items) {
    $(selector).replaceChildren(...items.map((item) => {
      const row = document.createElement("li");
      row.textContent = item;
      return row;
    }));
  }
  function showCase(id) {
    const entry = data.cases.find((item) => item.id === id);
    if (!entry) return;
    $("#case-title").textContent = entry.title;
    $("#case-combination").textContent = entry.combination;
    $("#case-input-summary").textContent = entry.input_summary;
    $("#case-brief").textContent = entry.brief;
    $("#case-brief-provenance").textContent = entry.brief_provenance;
    for (const kind of ["before", "after"]) {
      const image = $(`#case-${kind}-image`);
      const button = $(`#case-${kind}-button`);
      image.src = `./${entry[kind].path}`;
      image.alt = entry[kind].alt;
      image.width = entry[kind].width;
      image.height = entry[kind].height;
      button.dataset.image = image.getAttribute("src");
      button.dataset.caption = `${entry.tab} · ${kind === "before" ? "上游AI输入示例" : "上游生成成片"}`;
    }
    fillCaseList("#case-preserve", entry.preserve);
    fillCaseList("#case-transform", entry.transform);
    fillCaseList("#case-remove", entry.remove);
    fillCaseList("#case-observations", entry.observations);
    $("#case-prompt-text").value = entry.compiled_prompt;
    $("#case-prompt-provenance").textContent = entry.prompt_provenance;
    $("#case-prompt-download").href = `./${entry.prompt_path}`;
    $("#case-story-link").href = `./${entry.evidence["story.json"].path}`;
    $("#case-manifest-link").href = `./${entry.evidence["prompt-manifest.json"].path}`;
    $("#case-copy-status").textContent = "原文可复制或下载。";
    $("#case-panel").setAttribute("aria-labelledby", `case-tab-${id}`);
    caseTabs.forEach((tab) => {
      const active = tab.dataset.case === id;
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
  }
  caseTabs.forEach((tab, index) => {
    tab.addEventListener("click", () => showCase(tab.dataset.case));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % caseTabs.length;
      if (event.key === "ArrowLeft") next = (index - 1 + caseTabs.length) % caseTabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = caseTabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      showCase(caseTabs[next].dataset.case);
      caseTabs[next].focus();
    });
  });
  document.querySelectorAll("[data-view-case]").forEach((link) => {
    link.addEventListener("click", () => showCase(link.dataset.viewCase));
  });
  $("#copy-case-prompt").addEventListener("click", () => {
    copy($("#case-prompt-text").value, $("#case-copy-status"), $("#case-prompt-text"));
  });

  const systemSelect = $("#system-select");
  const profileSelect = $("#profile-select");
  const profileById = new Map(data.profiles.map((profile) => [profile.id, profile]));
  function option(value, text) {
    const result = document.createElement("option");
    result.value = value;
    result.textContent = text;
    return result;
  }
  data.systems.forEach((system) => systemSelect.append(option(system.id, system.name)));
  systemSelect.value = "memory-atlas";
  function renderRules(reset = false) {
    const system = data.systems.find((item) => item.id === systemSelect.value);
    if (reset) {
      const previous = profileSelect.value;
      profileSelect.replaceChildren(...system.profiles.map((id) => option(id, profileById.get(id).name)));
      profileSelect.value = system.profiles.includes(previous) ? previous : "source-led";
    }
    const profile = profileById.get(profileSelect.value);
    $("#system-rule").textContent = system.summary;
    $("#profile-rule").textContent = profile.summary;
    $("#compatibility-note").textContent = `已按上游兼容关系筛选 ${system.profiles.length} 种表达；多图融合需明确选定。`;
    $("#rule-status").textContent = "复制后追加到你的需求即可。";
    $("#rule-copy-text").hidden = true;
  }
  systemSelect.addEventListener("change", () => renderRules(true));
  profileSelect.addEventListener("change", () => renderRules());
  $("#copy-rule").addEventListener("click", () => {
    const system = data.systems.find((item) => item.id === systemSelect.value);
    const profile = profileById.get(profileSelect.value);
    const text = `请选择 ${system.name}（${system.id}）＋${profile.name}（${profile.id}）。\n叙事规则：${system.summary}\n表达与检查：${profile.summary}\n请结合实际照片填写必须保留、允许变化、明确删除三类清单；默认单图独立成片、多图逐张，融合需明确授权。`;
    $("#rule-copy-text").value = text;
    copy(text, $("#rule-status"), $("#rule-copy-text"));
  });

  const dialog = $("#image-dialog");
  let imageOpener;
  document.querySelectorAll("[data-image]").forEach((button) => {
    button.addEventListener("click", () => {
      imageOpener = button;
      $("#image-title").textContent = button.dataset.caption;
      $("#lightbox-image").src = button.dataset.image;
      $("#lightbox-image").alt = button.querySelector("img").alt;
      dialog.showModal();
    });
  });
  $("#close-image").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener("close", () => imageOpener?.focus());

  showPrompt(selectedPrompt);
  showCase("threaded-landscape");
  renderRules(true);
})();
