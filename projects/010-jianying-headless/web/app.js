"use strict";
(() => {
  const data = window.RESEARCH;
  if (!data) return;
  const $ = (selector) => document.querySelector(selector);
  const escape = (value) => String(value).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const external = (url, label, className = "") => `<a class="${className}" href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(label)}</a>`;
  function selectTab(button, attribute) {
    const group = button.closest('[role="tablist"]');
    group.querySelectorAll('[role="tab"]').forEach((tab) => {
      const selected = tab === button;
      tab.setAttribute("aria-selected", String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    return button.dataset[attribute];
  }
  function renderMode(button) {
    const key = selectTab(button, "mode");
    const mode = data.modes[key];
    $(".architecture").dataset.mode = key;
    $("#mode-panel").setAttribute("aria-labelledby", button.id);
    mode.layers.forEach((layer, index) => {
      ["label", "title", "copy", "owner"].forEach((field) => { $(`#mode-${field}-${index}`).textContent = layer[field]; });
    });
    $("#mode-output").textContent = mode.output;
    $("#mode-dependency").textContent = mode.dependency;
    $("#mode-note").textContent = mode.note;
  }
  $("#step-tabs").innerHTML = data.steps.map((step, i) => `<button type="button" role="tab" id="step-${step.id}" aria-controls="step-panel" aria-selected="${i === 0}" tabindex="${i === 0 ? 0 : -1}" data-step="${i}"><span>0${i + 1}</span><strong>${escape(step.short)}</strong></button>`).join("");
  function renderStep(button) {
    const index = Number(selectTab(button, "step"));
    const step = data.steps[index];
    const panel = $("#step-panel");
    panel.setAttribute("aria-labelledby", button.id);
    panel.innerHTML = `<div class="step-description"><span class="step-kicker">STEP 0${index + 1} / ${escape(step.short)}</span><h3>${escape(step.title)}</h3><p>${escape(step.description)}</p></div><div class="step-artifacts"><div class="artifact"><span>INPUT</span><p>${escape(step.input)}</p></div><div class="artifact"><span>OUTPUT</span><p>${escape(step.output)}</p></div><div class="artifact"><span>关键点</span><p>${escape(step.key)}</p></div><div class="step-code"><span>源码中的对应位置</span>${escape(step.code)}</div>${external(step.source, `${step.sourceLabel} ↗`, "step-source")}</div>`;
  }
  $("#project-rows").innerHTML = data.projects.map((project) => `<tr><td><strong>${escape(project.name)}</strong><span class="project-layer">${escape(project.layer)}</span>${external(project.url,"固定源码 ↗","project-link")}</td><td>${escape(project.provides)}</td><td>${escape(project.depends)}</td><td>${escape(project.status)}<small>${escape(project.revision)}</small></td></tr>`).join("");
  $("#extension-list").innerHTML = data.extensions.map((item,i) => `<details class="extension" data-horizon="${item.horizon}" ${i === 0 ? "open" : ""}><summary><span class="extension-index">0${i + 1}</span><div><h3>${escape(item.title)}</h3><span class="extension-subtitle">${escape(item.subtitle)}</span></div><span class="horizon ${item.horizon}">${escape(item.horizonLabel)} · 提案</span><span class="extension-plus" aria-hidden="true">+</span></summary><div class="extension-content"><div><h4>用在什么场景</h4><p>${escape(item.scenario)}</p></div><div><h4>复用已有的什么</h4><p>${escape(item.reuse)}</p></div><div><h4>还需要新增什么</h4><p>${escape(item.work)}</p></div><div><h4>如何证明做成了</h4><p>${escape(item.acceptance)}</p></div></div></details>`).join("");
  document.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    document.querySelectorAll("[data-filter]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
    let count = 0;
    document.querySelectorAll(".extension").forEach((item) => { item.hidden = filter !== "all" && item.dataset.horizon !== filter; if (!item.hidden) count++; });
    $("#extension-count").textContent = `${count} 个扩展方向 · 均为待验证提案`;
  }));
  function renderRoute(button) {
    const route = data.routes[selectTab(button, "route")];
    const panel = $("#route-panel");
    panel.setAttribute("aria-labelledby", button.id);
    panel.innerHTML = `<div class="route-intro"><span class="mini-label">${escape(route.kicker)}</span><h3>${escape(route.title)}</h3><p>${escape(route.intro)}</p><p class="route-dependency">${escape(route.dependency)}</p></div><div class="route-work"><h4>主要需要完成的工作</h4><ul>${route.work.map((item) => `<li>${escape(item)}</li>`).join("")}</ul><p>${escape(route.limit)}</p></div>`;
  }
  $("#faq-list").innerHTML = data.questions.map((item) => `<details><summary>${escape(item.question)}</summary><p>${escape(item.answer)}</p></details>`).join("");
  $("#source-list").innerHTML = data.sources.map((source) => `<li id="source-${source.id}"><div>${external(source.url,`${source.title} ↗`)}<p>${escape(source.description)}</p></div><span class="source-revision">${escape(source.revision)}</span></li>`).join("");
  document.querySelectorAll('[role="tablist"]').forEach((group) => {
    group.addEventListener("click", (event) => {
      const button = event.target.closest('[role="tab"]');
      if (!button || !group.contains(button)) return;
      if (button.dataset.mode) renderMode(button);
      if (button.dataset.step !== undefined) renderStep(button);
      if (button.dataset.route) renderRoute(button);
    });
    group.addEventListener("keydown", (event) => {
      const tabs = Array.from(group.querySelectorAll('[role="tab"]'));
      const current = tabs.indexOf(document.activeElement);
      if (current < 0 || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      let next = event.key === "Home" ? 0 : event.key === "End" ? tabs.length - 1 : (current + (event.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
      tabs[next].focus(); tabs[next].click();
    });
  });
  function download(text, name, mime) {
    const url = URL.createObjectURL(new Blob([text], {type:mime}));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = name;
    document.body.append(anchor); anchor.click(); anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  $("#download-notes").addEventListener("click", () => download(data.export_markdown, "剪映引擎研究-原理与扩展.md", "text/markdown;charset=utf-8"));
  $("#download-data").addEventListener("click", () => { const {export_markdown, ...structured} = data; download(JSON.stringify(structured,null,2), "剪映引擎研究.json", "application/json;charset=utf-8"); });
  let scrollPending = false;
  function updateScroll() {
    const distance = document.documentElement.scrollHeight - window.innerHeight;
    $("#reading-progress").style.width = `${distance > 0 ? Math.min(100, window.scrollY / distance * 100) : 0}%`;
    const anchors = Array.from(document.querySelectorAll(".site-header nav a"));
    let active = anchors[0];
    anchors.forEach((anchor) => { const section = document.querySelector(anchor.getAttribute("href")); if(section && section.getBoundingClientRect().top < 180) active = anchor; });
    anchors.forEach((anchor) => { anchor.classList.toggle("active", anchor === active); if(anchor === active) anchor.setAttribute("aria-current","location"); else anchor.removeAttribute("aria-current"); });
    scrollPending = false;
  }
  window.addEventListener("scroll", () => { if(!scrollPending) { scrollPending = true; window.requestAnimationFrame(updateScroll); } }, {passive:true});
  window.addEventListener("resize", updateScroll);
  renderMode($("#mode-automated")); renderStep($("#step-plan")); renderRoute($("#route-reuse")); updateScroll();
})();
