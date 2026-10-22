(() => {
  "use strict";
  const lesson = window.EXPLAINER;
  const $ = (selector) => document.querySelector(selector);
  const escape = (value) => String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
  const sources = (items) => `<div class="lesson-sources"><span>固定源码 / ca576b6</span>${items.map((item) => `<a href="${escape(item.url)}" target="_blank" rel="noreferrer">${escape(item.title)} ↗</a>`).join("")}</div>`;
  $("#model-meanings").innerHTML = lesson.model_meanings.map((item) => `<article><h3>${escape(item.name)}</h3><p class="model-example">${escape(item.example)}</p><p>${escape(item.meaning)}</p></article>`).join("");
  $("#light-step-controls").innerHTML = lesson.red_wall.steps.map((item, index) => `<button type="button" class="light-step" data-light-step="${index}" aria-pressed="${index === 0}" aria-controls="light-explanation"><span>0${index + 1}</span><strong>${escape(item.title)}</strong><small>${escape(item.short)}</small></button>`).join("");
  function showLightStep(index) {
    const item = lesson.red_wall.steps[index];
    $("#light-explanation").innerHTML = `<div><span class="eyebrow">STEP 0${index + 1} / 04</span><h3>${escape(item.title)}</h3><p>${escape(item.text)}</p></div><div class="light-takeaway"><span>记住这一点</span><p>${escape(item.takeaway)}</p>${sources(item.sources)}</div>`;
    document.querySelectorAll("[data-light-step]").forEach((button) => button.setAttribute("aria-pressed", String(Number(button.dataset.lightStep) === index)));
  }
  $("#light-step-controls").addEventListener("click", (event) => {
    const button = event.target.closest("[data-light-step]");
    if (button) showLightStep(Number(button.dataset.lightStep));
  });
  $("#algorithm-grid").innerHTML = lesson.algorithms.map((item, index) => `<article class="algorithm-card"><span class="algorithm-number">${String(index + 1).padStart(2, "0")}</span><h4>${escape(item.name)}</h4><p class="algorithm-plain">${escape(item.plain)}</p><p class="algorithm-example">${escape(item.example)}</p><details><summary>方法、边界与源码 <span aria-hidden="true">＋</span></summary><h5>怎样做</h5><p>${escape(item.method)}</p><h5>适用边界</h5><p>${escape(item.boundary)}</p>${sources(item.sources)}</details></article>`).join("");
  const scenarioLabels = ["阴天改夕阳", "绕到背面看", "手里只有照片"];
  $("#scenario-controls").innerHTML = lesson.scenarios.map((item, index) => `<button type="button" class="scenario-button" data-scenario="${escape(item.id)}" aria-pressed="${index === 0}" aria-controls="scenario-content">${escape(scenarioLabels[index])}<span aria-hidden="true">↗</span></button>`).join("");
  function showScenario(id) {
    const item = lesson.scenarios.find((scenario) => scenario.id === id);
    $("#scenario-content").innerHTML = `<h3>${escape(item.title)}</h3><div class="scenario-columns"><div class="render-answer"><span>A / 三维渲染</span><p>${escape(item.render)}</p></div><div class="ai-answer"><span>B / AI 图像处理</span><p>${escape(item.ai)}</p></div></div><div class="scenario-decision"><span>如何选择</span><p>${escape(item.decision)}</p></div>`;
    document.querySelectorAll("[data-scenario]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.scenario === id)));
  }
  $("#scenario-controls").addEventListener("click", (event) => {
    const button = event.target.closest("[data-scenario]");
    if (button) showScenario(button.dataset.scenario);
  });
  $("#comparison-table").innerHTML = `<table class="comparison-table"><caption>本项目的三维渲染与常见 AI 单图重绘</caption><thead><tr><th scope="col">对比点</th><th scope="col">三维渲染</th><th scope="col">AI 图像重绘</th></tr></thead><tbody>${lesson.comparison.map((item) => `<tr><th scope="row">${escape(item.aspect)}</th><td>${escape(item.render)}</td><td>${escape(item.ai)}</td></tr>`).join("")}</tbody></table>`;
  $("#ai-nuance-text").textContent = lesson.ai_nuance;
  showLightStep(0);
  showScenario(lesson.scenarios[0].id);
})();
