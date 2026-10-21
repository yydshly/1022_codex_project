"use strict";
(() => {
  const media = window.PANEL_MEDIA;
  if (!media) {
    document.getElementById("gallery-count").textContent = "请先运行素材打包命令，再刷新页面。";
    return;
  }
  const $ = (id) => document.getElementById(id);
  const escape = (text) => String(text).replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
  const source = {...media.source, id: "source", note: "真实实拍输入，摄影 Chris Karidis。原站下载版本，未额外裁切或调色。"};
  const promptEntries = window.PANEL_PROMPTS || [];
  const promptByPath = new Map(promptEntries.map((item) => [item.path, item]));
  const all = [...media.upstream_samples, source, ...media.demo_outputs, ...media.rejected_outputs, ...(media.study_guides || [])];
  const byId = new Map(all.map((item) => [item.id, item]));
  const dimensions = (item) => `${item.width} × ${item.height} px`;
  const modeLabel = (mode) => mode === "left-right" ? "左右对照" : "上下对照";
  let viewerIds = [];
  let viewerIndex = 0;
  let filteredSamples = media.upstream_samples;

  function configurePromptLink(link, item) {
    if (promptByPath.has(item.prompt)) {
      link.href = "#prompts";
      link.dataset.prompt = item.prompt;
      link.removeAttribute("target");
      link.removeAttribute("rel");
    } else {
      link.href = item.source || item.prompt;
      delete link.dataset.prompt;
      link.target = "_blank";
      link.rel = "noreferrer";
    }
  }

  function renderPrompt() {
    const item = promptByPath.get($("prompt-select").value);
    if (!item) return;
    const hasAddition = Boolean(item.addition);
    $("prompt-additions").disabled = !hasAddition;
    if (!hasAddition) $("prompt-additions").checked = false;
    const additionOnly = $("prompt-additions").checked;
    const text = additionOnly ? item.addition : item.text;
    $("prompt-content").value = text;
    $("prompt-kind").textContent = item.kind === "成功输出" ? "已保留输出" : item.kind;
    $("prompt-origin").textContent = `${item.path} · 原文件原文`;
    $("prompt-note").textContent = item.note;
    $("prompt-view").textContent = `${additionOnly ? "当前显示：追加指令" : "当前显示：完整原文"} · ${Array.from(text).length} 字符`;
    $("prompt-download").href = item.path;
    $("prompt-download").download = item.path.split("/").pop();
    $("prompt-copy-status").textContent = "";
  }
  function selectPrompt(path) {
    if (!promptByPath.has(path)) return;
    $("prompt-select").value = path;
    $("prompt-additions").checked = false;
    renderPrompt();
  }
  $("prompt-select").innerHTML = promptEntries.map((item) => `<option value="${escape(item.path)}">${escape(item.title)}</option>`).join("");
  $("prompt-select").addEventListener("change", () => selectPrompt($("prompt-select").value));
  $("prompt-additions").addEventListener("change", renderPrompt);
  $("prompt-expand").addEventListener("click", () => {
    const expanded = $("prompt-expand").getAttribute("aria-expanded") !== "true";
    $("prompt-expand").setAttribute("aria-expanded", String(expanded));
    $("prompt-expand").textContent = expanded ? "收起阅读区" : "展开阅读区";
    document.querySelector(".prompt-panel").classList.toggle("expanded", expanded);
  });
  $("prompt-copy").addEventListener("click", async () => {
    const text = $("prompt-content").value;
    try {
      if (!navigator.clipboard?.writeText) throw new Error("clipboard unavailable");
      await navigator.clipboard.writeText(text);
      $("prompt-copy-status").textContent = `已复制当前内容（${Array.from(text).length} 字符）`;
    } catch {
      $("prompt-content").focus();
      $("prompt-content").select();
      $("prompt-copy-status").textContent = "已选中当前内容，请按 Ctrl+C 或使用设备的复制操作。";
    }
  });
  document.addEventListener("click", (event) => {
    const link = event.target.closest("[data-prompt]");
    if (!link || !promptByPath.has(link.dataset.prompt)) return;
    selectPrompt(link.dataset.prompt);
    if ($("viewer").open) $("viewer").close();
  });

  function renderGallery(filter = "all") {
    filteredSamples = media.upstream_samples.filter((item) => filter === "all" || item.mode === filter);
    $("gallery-grid").innerHTML = filteredSamples.map((item) => `<figure class="gallery-card"><button class="image-button" data-zoom="${item.id}" aria-label="放大官方样张：${escape(item.title)}"><img src="${item.path}" width="${item.width}" height="${item.height}" alt="官方${escape(item.title)}：${escape(item.note)}" loading="lazy" decoding="async"></button><figcaption><div class="card-topline"><span>UPSTREAM / ${item.id.slice(-2)}</span><span>${item.category} · ${modeLabel(item.mode)}</span></div><h3>${escape(item.title)}</h3><p>${escape(item.note)}</p><div class="card-meta"><span>${dimensions(item)} · 官方原图</span><a href="${item.source}" target="_blank" rel="noreferrer">来源 ↗</a></div></figcaption></figure>`).join("");
    $("gallery-count").textContent = `展示 ${filteredSamples.length} / 8 张`;
  }
  document.querySelectorAll("[data-filter]").forEach((button) => button.addEventListener("click", () => {
    document.querySelectorAll("[data-filter]").forEach((entry) => { entry.classList.toggle("active", entry === button); entry.setAttribute("aria-pressed", String(entry === button)); });
    renderGallery(button.dataset.filter);
  }));

  const verdicts = {
    source: "真实原照；2400 × 1596 下载版本。",
    "left-right": "中文准确；分界偏 1 像素；未命中请求像素。",
    "top-bottom": "中线等分、自动英文完成；未命中请求像素。",
    "design-only": "第二次请求去除摄影区；极简留白仅部分满足。"
  };
  function selectDemo(id) {
    const item = byId.get(id);
    const bitmap = $("demo-image");
    bitmap.src = item.path;
    bitmap.alt = `${item.title}：${item.note}`;
    bitmap.width = item.width;
    bitmap.height = item.height;
    $("demo-zoom").dataset.zoom = id;
    $("demo-label").textContent = id === "source" ? "REAL PHOTOGRAPH / INPUT" : "GENERATED IN THIS STUDY / OUTPUT";
    $("demo-title").textContent = item.title;
    $("demo-note").textContent = item.note;
    $("demo-size").textContent = `${dimensions(item)}${item.requested_pixels ? `（请求 ${item.requested_pixels}）` : ""}`;
    $("demo-verdict").textContent = verdicts[id];
    $("demo-download").href = item.path;
    $("demo-download").textContent = id === "source" ? "下载输入照片 JPEG ↓" : "下载原尺寸 PNG ↓";
    configurePromptLink($("demo-prompt"), item);
    $("demo-prompt").textContent = id === "source" ? "查看摄影作品来源 ↗" : "在本页查看完整请求 ↗";
    document.querySelectorAll("[data-demo]").forEach((button) => { const active = button.dataset.demo === id; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
  }
  document.querySelectorAll("[data-demo]").forEach((button) => button.addEventListener("click", () => selectDemo(button.dataset.demo)));

  const deviceLabels = {"wallpaper-phone":"手机 · 定调图", "wallpaper-ipad":"平板 · 独立构图", "wallpaper-desktop":"电脑 · 横向重构", "wallpaper-watch":"手表 · 方形重构"};
  $("wallpaper-grid").innerHTML = media.demo_outputs.filter((item) => item.id.startsWith("wallpaper-")).map((item) => `<figure class="wallpaper-card"><button class="image-button" data-zoom="${item.id}" aria-label="放大${escape(item.title)}"><img src="${item.path}" alt="${escape(item.title)}：巴黎铁塔的全幅无文字像素艺术" width="${item.width}" height="${item.height}" loading="lazy" decoding="async"></button><figcaption><h4>${deviceLabels[item.id]}</h4><p>${dimensions(item)}<br>请求 ${item.requested_pixels}<br>${item.attempts === 2 ? "重试一次后保留" : "首次输出"}</p><div class="wallpaper-actions"><a href="${item.path}" download>下载原尺寸 PNG ↓</a><a href="#prompts" data-prompt="${item.prompt}">对应完整请求 ↗</a></div></figcaption></figure>`).join("");
  $("rejected-grid").innerHTML = media.rejected_outputs.map((item) => `<figure><button class="image-button" data-zoom="${item.id}" aria-label="放大${escape(item.title)}"><img src="${item.path}" alt="${escape(item.title)}：${escape(item.reason)}" width="${item.width}" height="${item.height}" loading="lazy" decoding="async"></button><figcaption><h4>${escape(item.title)}</h4><p>${escape(item.reason)}。${dimensions(item)}。</p><a href="#prompts" data-prompt="${item.prompt}">在本页查看首轮请求 ↗</a></figcaption></figure>`).join("");

  const scenes = {
    travel: {fit:"优先适合 · 本次实测", title:"个人旅行纪念海报", why:"地标轮廓鲜明，几处关键空间关系就能建立身份感。海报允许改变色彩和构图，可以把旅行照片重写成一种记忆。", input:"主体清楚的地标、街景或自然景观，一张照片只强调一段记忆。", check:"轮廓是否仍可辨，地标与环境关系是否保留；实际尺寸和文字是否满足用途。", link:"看本次巴黎真实演示 ↗", target:"#demo"},
    plants: {fit:"优先适合 · 上游样张", title:"花束、植物与一份礼物", why:"花朵颜色、枝条方向与包装轮廓都有明确的视觉特征，适合减少细节之后保留情绪。源库有蒲公英、花枝与花束案例。", input:"花束整体、单株植物或一枝花，避免大量小花争夺视觉中心。", check:"是否仍有一个视觉核心，叶片与背景是否确实简化，颜色有没有失去原来的关系。", link:"看全部官方植物效果 ↗", target:"#gallery"},
    life: {fit:"适合 · 接受视觉变化", title:"生活瞬间与私人壁纸", why:"灯光、杯子与动作可以成为简单的记忆锚点。壁纸可利用不同画幅重新安排主体，让同一瞬间适配多台设备。", input:"动作明确、光感鲜明、主体关系简单的生活照片。", check:"各设备独立构图；文字、图标与表盘是否遮挡。当前只展示生成图，没有真机验证。", link:"查看本次四端壁纸 ↗", target:"#wallpaper-grid"},
    portrait: {fit:"条件适合 · 本次未测人脸", title:"人物纪念与重要动作", why:"姿态关系可以提炼，但面部、服饰和身份信息可能随简化而改变。若某个人必须被准确认出，验收要求会更高。", input:"姿态与轮廓清楚的单人或简单关系照片，明确必须保留的细节。", check:"面部、手部、人数、姿态与重要服饰；不能用地标测试推断人脸一致性。", link:"查看骑手的官方样张 ↗", target:"#gallery"},
    product: {fit:"条件较弱 · 精确信息易变", title:"商品与品牌文字", why:"风格重构会删去材质和结构，图中文字也可能变化。精确商品图、品牌规范和复杂长文的要求与强抽象不完全一致。", input:"以氛围为目的的静物照片；若要准确商品描述，应使用适合的保真流程。", check:"型号、标识、结构、颜色和每一个字。上游为非商业许可，不能从场景推荐推断商用授权。", link:"阅读本次准确中文结果 ↗", target:"#demo"},
    evidence: {fit:"不适合当前目标", title:"证据、图纸与精确数据", why:"这些内容依赖细节与事实保持，而此风格主动删减、合并、重排视觉元素。生成作品不应承担原始证据的角色。", input:"需要证据或准确数据时，应保留原始资料。", check:"不要把生成的摄影参考区当作原片，也不要从画面重构推断真实结构。", link:"理解模型与辅助代码的边界 ↗", target:"#mechanism"}
  };
  function selectScene(key) {
    const item = scenes[key];
    $("scene-fit").textContent = item.fit;
    $("scene-title").textContent = item.title;
    $("scene-why").textContent = item.why;
    $("scene-input").textContent = item.input;
    $("scene-check").textContent = item.check;
    $("scene-link").textContent = item.link;
    $("scene-link").href = item.target;
    document.querySelectorAll("[data-scene]").forEach((button) => { const active = button.dataset.scene === key; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
  }
  document.querySelectorAll("[data-scene]").forEach((button) => button.addEventListener("click", () => selectScene(button.dataset.scene)));

  function updateViewer() {
    const item = byId.get(viewerIds[viewerIndex]);
    $("viewer-image").src = item.path;
    $("viewer-image").alt = `${item.title}：${item.note || item.reason || ""}`;
    $("viewer-title").textContent = item.title;
    const kind = item.provenance === "upstream" ? "官方样张" : item.provenance === "rejected-generation" ? "本次未通过检查" : item.provenance === "real-photograph" ? "真实摄影输入" : item.provenance === "generated-explainer" ? "研究理解图" : "本次生成结果";
    $("viewer-label").textContent = `${kind} / ${viewerIndex + 1} OF ${viewerIds.length}`;
    $("viewer-note").textContent = item.note || item.reason || "";
    $("viewer-size").textContent = dimensions(item);
    $("viewer-download").href = item.path;
    configurePromptLink($("viewer-source"), item);
    $("viewer-prev").disabled = viewerIds.length < 2;
    $("viewer-next").disabled = viewerIds.length < 2;
  }
  function openViewer(id) {
    const item = byId.get(id);
    if (!item) return;
    viewerIds = item.provenance === "upstream" ? filteredSamples.map((entry) => entry.id) : item.provenance === "rejected-generation" ? media.rejected_outputs.map((entry) => entry.id) : item.provenance === "generated-explainer" ? media.study_guides.map((entry) => entry.id) : ["source", ...media.demo_outputs.map((entry) => entry.id)];
    viewerIndex = Math.max(0, viewerIds.indexOf(id));
    updateViewer();
    $("viewer").showModal();
    document.body.style.overflow = "hidden";
  }
  function changeViewer(delta) { viewerIndex = (viewerIndex + delta + viewerIds.length) % viewerIds.length; updateViewer(); }
  document.addEventListener("click", (event) => { const button = event.target.closest("[data-zoom]"); if (button) openViewer(button.dataset.zoom); });
  $("viewer-close").addEventListener("click", () => $("viewer").close());
  $("viewer").addEventListener("close", () => { document.body.style.overflow = ""; });
  $("viewer-prev").addEventListener("click", () => changeViewer(-1));
  $("viewer-next").addEventListener("click", () => changeViewer(1));
  $("viewer").addEventListener("keydown", (event) => { if (event.key === "ArrowLeft" || event.key === "ArrowRight") { event.preventDefault(); changeViewer(event.key === "ArrowLeft" ? -1 : 1); } });
  $("viewer").addEventListener("click", (event) => { if (event.target === $("viewer")) { const box = $("viewer").getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) $("viewer").close(); } });
  renderGallery();
  selectDemo("left-right");
  selectScene("travel");
  selectPrompt("prompts/original.zh-CN.md");
})();
