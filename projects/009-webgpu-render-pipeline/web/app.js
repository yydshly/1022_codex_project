"use strict";
(() => {
  const data = window.RESEARCH;
  if (!data) return;
  const $ = (selector) => document.querySelector(selector);
  const escape = (value) => String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
  const categoryMap = new Map(data.categories.map((item) => [item.id, item]));
  const sceneMap = new Map(data.scenes.map((item) => [item.id, item]));
  const state = { category: "all", scope: "all", query: "" };
  let toastTimer;
  let detailHash = "#capabilities";
  const badgeClass = (status) => ["可选", "历史路径"].includes(status) ? " optional" : ["实验室", "集成待补", "独立资料"].includes(status) ? " limited" : "";
  const showToast = (message) => {
    const toast = $("#toast");
    toast.textContent = message;
    toast.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 2400);
  };
  async function copy(text, label = "已复制") {
    try {
      await navigator.clipboard.writeText(text);
      showToast(label);
    } catch {
      const field = document.createElement("textarea");
      field.value = text;
      field.style.cssText = "position:fixed;opacity:0";
      (document.querySelector("dialog[open]") || document.body).append(field);
      field.select();
      const success = document.execCommand("copy");
      field.remove();
      showToast(success ? label : "复制未成功，请选择路由或参数文本后复制");
    }
  }
  function renderCategories() {
    $("#category-filters").innerHTML = [{ id: "all", name: "全部", count: data.capabilities.length }, ...data.categories].map((item) => `<button class="chip" type="button" data-category="${item.id}" aria-pressed="${state.category === item.id}">${escape(item.name)}<span>${item.count}</span></button>`).join("");
  }
  function renderCapabilities() {
    const terms = state.query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    const visible = data.capabilities.filter((item) => {
      const haystack = [item.title, item.effect, item.mechanism, item.boundary, item.parameters, item.source.path, categoryMap.get(item.category).name].join(" ").toLocaleLowerCase();
      return (state.category === "all" || item.category === state.category) && (state.scope === "all" || item.availability === state.scope) && terms.every((term) => haystack.includes(term));
    });
    $("#result-count").textContent = `显示 ${visible.length} / ${data.capabilities.length} 项能力条目`;
    const groups = data.categories.map((group, index) => {
      const items = visible.filter((item) => item.category === group.id);
      if (!items.length) return "";
      return `<section class="capability-group" aria-labelledby="group-${group.id}"><div class="group-heading"><span class="group-index">${String(index + 1).padStart(2, "0")} / ${items.length}</span><h3 id="group-${group.id}">${escape(group.name)}</h3><p>${escape(group.description)}</p></div><div class="capability-grid">${items.map((item) => `<button class="capability-card" data-capability="${item.id}" type="button" aria-label="查看${escape(item.title)}的原理与范围"><div class="card-top"><span class="card-id">${item.id}</span><span class="status-badge${badgeClass(item.availability)}">${escape(item.availability)}</span></div><h4>${escape(item.title)}</h4><p>${escape(item.effect)}</p><div class="card-bottom"><span>源码依据 / 效果 / 边界</span><span aria-hidden="true">↗</span></div></button>`).join("")}</div></section>`;
    }).join("");
    $("#capability-results").innerHTML = groups || '<div class="empty-state"><strong>没有匹配的条目</strong><p>可以尝试“光照”“水”“反射”，或重置分类与接入范围。</p></div>';
  }
  function openCapability(id, updateHash = true) {
    const item = data.capabilities.find((record) => record.id === id);
    if (!item) return;
    const scenes = item.scenes.includes("all") ? "主应用各场景，具体默认值由配置决定" : item.scenes.map((scene) => sceneMap.get(scene)?.title || scene).join("、");
    $("#detail-content").innerHTML = `<span class="dialog-id">${escape(categoryMap.get(item.category).name)} / ${item.id}</span><h2 id="dialog-title">${escape(item.title)}</h2><p>${escape(item.effect)}</p><div class="detail-block"><h3>如何实现</h3><p>${escape(item.mechanism)}。</p></div><div class="detail-block detail-scope"><h3>${escape(item.availability)} / 适用范围</h3><p>${escape(item.boundary)}。</p></div><div class="detail-block"><h3>从哪个场景观察</h3><p>${escape(scenes)}。</p></div>${item.parameters ? `<div class="detail-block"><h3>上游参数示例</h3><div class="detail-params"><code>?${escape(item.parameters)}</code><button class="small-copy" type="button" data-copy-params="${escape(item.parameters)}">复制</button></div><p style="font-size:10px;margin-top:7px">接到正确上游场景路径后使用；当前研究页不执行此参数。</p></div>` : ""}<div class="detail-block"><h3>固定源码依据 / ca576b6</h3><a class="detail-source" href="${item.source.url}" target="_blank" rel="noreferrer">${escape(item.source.path)}:${item.source.line} ↗</a></div><p class="detail-verification">本条已核对源码存在与接入条件；真实演示验证了 Cornell Box、村庄、海滩与森林的指定配置，不表示本条在所有场景、设备或质量设置下均已验收。</p>`;
    const dialog = $("#detail-dialog");
    if (!dialog.open) {
      detailHash = location.hash.startsWith("#capability=") ? "#capabilities" : location.hash || "#capabilities";
      dialog.showModal();
    }
    if (updateHash) history.replaceState(null, "", `#capability=${encodeURIComponent(id)}`);
    dialog.scrollTop = 0;
  }
  function renderPipeline(active = 0) {
    $("#pipeline-steps").innerHTML = data.pipeline.map((item, index) => `<button type="button" class="step-button" data-step="${index}" aria-pressed="${active === index}"><span>${item.step}</span>${escape(item.title)}<span aria-hidden="true">↗</span></button>`).join("");
    const item = data.pipeline[active];
    $("#pipeline-detail").innerHTML = `<span class="step-number">${item.step}</span><h3>${escape(item.title)}</h3><p>${escape(item.text)}</p><span class="step-scope">${active < 2 ? "准备阶段 / 结果可保存复用" : "逐帧阶段 / 依场景配置执行"}</span>`;
  }
  function renderScenes() {
    $("#scene-grid").innerHTML = data.scenes.map((scene) => `<article class="scene-card" id="scene-${scene.id}"><span class="scene-type">${escape(scene.kind)}</span><h3>${escape(scene.title)}</h3><p class="scene-focus">${escape(scene.focus)}</p><p class="scene-note">${escape(scene.note)}</p><details><summary>观察路线与相机 <span aria-hidden="true">＋</span></summary><p>${escape(scene.checks)}</p>${scene.cameras.length ? `<div class="camera-list">${scene.cameras.map((cam) => `<code>${escape(cam)}</code>`).join("")}</div>` : '<p>默认相机或实验室内置控制。</p>'}</details><div class="route-wrap"><button class="scene-route" type="button" data-route="${escape(scene.route)}" aria-label="复制${escape(scene.title)}的上游路由">${escape(scene.route)} <span aria-hidden="true">⧉</span></button><a class="scene-source" href="${scene.url}" target="_blank" rel="noreferrer">阅读对应源码 ↗</a></div></article>`).join("");
  }
  function renderParameters() {
    const term = $("#parameter-search").value.trim().toLowerCase();
    const items = data.parameters.filter((item) => item.name.toLowerCase().includes(term));
    $("#parameter-count").textContent = `显示 ${items.length} / ${data.parameters.length} 个参数名；点击前往首次出现的源码位置。`;
    $("#parameter-results").innerHTML = items.map((item) => { const first = item.occurrences[0]; return `<a class="parameter-row" href="${first.url}" target="_blank" rel="noreferrer"><code>${escape(item.name)}</code><span>${escape(first.path.split("/").slice(-2).join("/"))}:${first.line}</span></a>`; }).join("") || '<p class="parameter-empty">没有找到该参数名。</p>';
  }
  $("#status-filter").innerHTML += [...new Set(data.capabilities.map((item) => item.availability))].map((scope) => `<option value="${escape(scope)}">${escape(scope)}</option>`).join("");
  $("#category-filters").addEventListener("click", (event) => { const button = event.target.closest("[data-category]"); if (!button) return; state.category = button.dataset.category; renderCategories(); renderCapabilities(); });
  $(".overview-map").addEventListener("click", (event) => {
    const category = event.target.closest("[data-overview-category]")?.dataset.overviewCategory;
    if (category && categoryMap.has(category)) {
      state.category = category; state.scope = "all"; state.query = "";
      $("#capability-search").value = ""; $("#status-filter").value = "all";
      renderCategories(); renderCapabilities();
    }
    const scene = event.target.closest("[data-overview-scene]")?.dataset.overviewScene;
    if (scene) {
      const picker = $("#live-scene");
      picker.value = scene;
      picker.dispatchEvent(new Event("change", { bubbles: true }));
    }
  });
  $("#capability-search").addEventListener("input", (event) => { state.query = event.target.value; renderCapabilities(); });
  $("#status-filter").addEventListener("change", (event) => { state.scope = event.target.value; renderCapabilities(); });
  $("#reset-filters").addEventListener("click", () => { Object.assign(state, { category: "all", scope: "all", query: "" }); $("#capability-search").value = ""; $("#status-filter").value = "all"; renderCategories(); renderCapabilities(); });
  $("#capability-results").addEventListener("click", (event) => { const button = event.target.closest("[data-capability]"); if (button) openCapability(button.dataset.capability); });
  $("#detail-content").addEventListener("click", (event) => { const button = event.target.closest("[data-copy-params]"); if (button) copy(`?${button.dataset.copyParams}`, "上游参数已复制"); });
  $("#pipeline-steps").addEventListener("click", (event) => { const button = event.target.closest("[data-step]"); if (button) { const index = Number(button.dataset.step); renderPipeline(index); document.querySelector(`[data-step="${index}"]`)?.focus({ preventScroll: true }); } });
  $("#scene-grid").addEventListener("click", (event) => { const button = event.target.closest("[data-route]"); if (button) copy(button.dataset.route, "上游路由已复制，需在补齐环境后使用"); });
  $("#parameter-search").addEventListener("input", renderParameters);
  $("#boundary-grid").innerHTML = data.limitations.map((item) => `<article class="boundary-item"><span>${escape(item.severity)}</span><h3>${escape(item.title)}</h3><p>${escape(item.text)}</p></article>`).join("");
  const images = {
    overview: { src: "assets/project-overview.svg", title: "一图总览 · 核心价值 / 原理 / 全部能力 / 实测 / 复用", alt: "10 类全部 89 项能力、光照计算流程、四场景真实效果和复用方向的完整总览", caption: "原创研究总览；可上下与左右滚动阅读。四张效果图为本机实测缩略图，能力接入状态与运行验收分别说明。" },
    light: { src: "assets/light-transport-explained.svg", title: "红墙与白球 · 教学示意", alt: "直接光、红墙反弹光、表面采样和光照缓存复用的图解", caption: "原创教学图解，非上游渲染结果。箭头表示能量关系；实际积分器从表面采样估计入射光，不是逐光子模拟。" },
    comparison: { src: "assets/rendering-vs-ai.svg", title: "三维渲染与 AI 图像处理 · 教学示意", alt: "三维场景按几何和光照规则成像，与图像模型按输入条件生成外观的流程对照", caption: "比较常见单图重绘，不代表所有 AI 方法；AI 可以接收空间结构条件。本图未调用 AI 或上游引擎。" },
    baseline: { src: "assets/upstream/lighting-baseline.png", title: "作者历史运行画面", alt: "上游村庄历史运行画面，非本次运行", caption: "从固定上游光照文档 live-image 原样提取。是作者提供的历史画面，不能代表当前设备实测。" },
    concept: { src: "assets/upstream/lighting-concept.png", title: "概念参考 · 非运行效果", alt: "上游村庄概念参考图，非引擎运行结果", caption: "从同一文档 concept-image 原样提取。用于说明美术目标；构图和已有画面不同，不作为严格 A/B。" },
    map: { src: "assets/capability-map.svg", title: "渲染原理图解 · 本次研究整理", alt: "准备期光照缓存与逐帧效果的组合图解", caption: "原创源码研究图示，10 类 89 项条目；不是上游效果截图或运行验收。" },
  };
  document.querySelectorAll("[data-image]").forEach((button) => button.addEventListener("click", () => {
    const item = images[button.dataset.image];
    $("#image-dialog-title").textContent = item.title;
    $("#expanded-image").src = item.src;
    $("#expanded-image").alt = item.alt;
    $("#image-dialog").classList.toggle("diagram-dialog", item.src.endsWith(".svg"));
    $("#image-dialog").classList.toggle("overview-dialog", button.dataset.image === "overview");
    $("#image-dialog-caption").textContent = item.caption + (item.src.endsWith(".svg") ? " 小屏可在图中左右滑动，键盘可聚焦图片区域后使用方向键。" : "");
    $("#image-dialog").showModal();
    $("#image-dialog .image-viewport").scrollTo(0, 0);
    if (button.dataset.image === "overview") $("#image-dialog .image-viewport").focus();
  }));
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => { const rect = dialog.getBoundingClientRect(); if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close(); });
    dialog.addEventListener("close", () => { if (dialog.id === "detail-dialog" && location.hash.startsWith("#capability=")) history.replaceState(null, "", detailHash); });
  });
  renderCategories(); renderCapabilities(); renderPipeline(); renderScenes(); renderParameters();
  if (location.hash.startsWith("#capability=")) openCapability(decodeURIComponent(location.hash.slice(12)), false);
})();
