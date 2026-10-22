/* Original research-page UI. Animation sequencing uses upstream MIT EpisodePlayer. */
"use strict";
const UPSTREAM = "https://github.com/Hchen1218/heytea-style/blob/d5125372adcc945c2314cfb649c50407379a18ab/";
const embedded = window.__HEYTEA_RESEARCH_OFFLINE__;
const asset = (path) => embedded?.images[path] || `assets/upstream/${path}`;
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const capabilities = {
  poster: {
    kicker: "真实食物，手绘表达", title: "给日常的一餐，<br>一个有趣的开场。",
    description: "保留食物的摄影质感，在留白中加入不规则的手写标题。小人围绕产品做一个明确动作，让实物成为画面的故事中心。",
    input: "poster/source-food.jpg", inputAlt: "餐桌上的原始食物照片", inputCaption: "一张餐桌照片，提供真实主体、色彩和质感。",
    facts: [["保留", "主体外观、表面质感与自然阴影"], ["变化", "背景、构图、手写字与小人动作"], ["交付", "两种独立构图的静态海报"]],
    variants: [
      { name: "带字版", image: "poster/typography-poster.png", alt: "泰香开饭带字海报：真实饭菜、歪扭标题与撒料小人", label: "带字海报 / OUTPUT", caption: "大留白和歪扭标题先吸引目光，真实食物与小人动作支持标题。" },
      { name: "无字版", image: "poster/doodle-poster.png", alt: "无字海报：小人站在梯子上，对真实食物做出倾倒动作", label: "无字海报 / OUTPUT", caption: "换一个主体、重新安排构图，让梯子、小人与食物完成一个动作故事。" },
    ], source: "references/style-guide.md",
  },
  monster: {
    kicker: "从食物特征，到一个新角色", title: "把风味，<br>变成一只小怪兽。",
    description: "从饮料中提取粉绿配色、黄色果粒、分层与材质关系，再设计独立的身体轮廓、五官和两手两腿。角色保留来源线索，身体形态可以重新想象。",
    input: "desktop-pet/source-drink.png", inputAlt: "粉色饮料、绿色上层与底部黄色果粒构成的原始饮品照片", inputCaption: "颜色、果粒、材质与分层，共同提供角色设计线索。",
    facts: [["保留", "来源配色、风味标记与材料关系"], ["变化", "从杯子形态到独立怪兽的身体结构"], ["交付", "先确认静态身份稿，再选择海报或桌宠"]],
    variants: [
      { name: "风味小怪兽", image: "pet-v3/preview.png", alt: "上游粉绿风味小怪兽身份稿，以蜡笔色块、果粒标记和黑线四肢组成", label: "风味小怪兽 / OUTPUT", caption: "身体、五官、四肢和材料关系确认后，作为后续海报与动作的共同身份。" },
      { name: "写实卡通角色", image: "desktop-pet/canonical-pet.png", alt: "保留饮料杯外轮廓和分层的写实卡通角色", label: "写实卡通 / ANOTHER MODE", caption: "另一条角色路线：保留杯子轮廓和饮料分层，将原物本身手绘角色化。" },
    ], source: "references/desktop-pet-character-modes.md",
  },
  fusion: {
    kicker: "让角色与产品发生一件事", title: "小怪兽，<br>回到它的灵感旁边。",
    description: "真实饮品继续提供摄影质感，确认后的角色只改变姿势。一个接触点、一条动作轨迹，让角色与产品之间有明确联系。",
    input: "desktop-pet/source-drink.png", inputAlt: "作为小怪兽灵感来源的粉绿饮品照片", inputCaption: "原始产品与已确认的角色稿，共同作为融合海报的输入。",
    facts: [["锁定", "角色身体、脸、两手两腿与材料特征"], ["动作", "本例用“投”，把黄色风味色块抛回饮品"], ["交付", "产品摄影与手绘角色互动的静态海报"]],
    variants: [{ name: "产品互动样张", image: "monster-poster/pink-green-monster-product-interaction.png", alt: "小怪兽将黄色风味色块投回真实粉绿饮品，标题为再来一口", label: "产品互动图 / OUTPUT", caption: "小怪兽把黄色风味色块投向饮品；轨迹、姿势和视线共同说明动作。" }],
    source: "references/monster-poster-workflow.md",
  },
  pet: {
    kicker: "让确认的形象，拥有行为", title: "把一个小角色，<br>留在日常的桌面上。",
    description: "原物角色化和风味小怪兽共用桌面运行器。生成动作帧、编排行为阶段，再按点击、拖拽、闲置与光标接近等事件播放。",
    input: "desktop-pet/canonical-pet.png", inputAlt: "已确认的粉绿饮料杯卡通桌宠身份稿", inputCaption: "确认后的角色身份，约束后续所有动作的外观。",
    facts: [["两条路线", "写实卡通 v2；风味小怪兽 v3"], ["动作", "v2 固定 12 动作；v3 定义 6–10 个多阶段行为"], ["交付", "透明角色包 ZIP，导入独立 Electron 运行器"]],
    variants: [
      { name: "动作预览", image: "desktop-pet/motion-preview.gif", alt: "上游写实卡通桌宠动作预览 GIF", label: "动作预览 / MOTION", caption: "上游 v2 角色动作预览；下方可交互查看 v3 小怪兽的行为阶段。" },
      { name: "动作审核表", image: "desktop-pet/contact-sheet.png", alt: "上游写实卡通桌宠十二动作审核表", label: "审核图 / REVIEW", caption: "用动作审核表查看身份与动作是否一致；运行素材还需逐帧检查透明边缘。" },
    ], source: "references/desktop-pet-pack.md",
  },
};

let selectedCapability = "poster";
let selectedVariant = 0;
function renderCapability(id, variant = 0) {
  const capability = capabilities[id];
  const output = capability.variants[variant];
  const restoreVariantFocus = document.activeElement?.dataset.variant;
  selectedCapability = id;
  selectedVariant = variant;
  $$("[data-capability]").forEach((button) => {
    const active = button.dataset.capability === id;
    button.setAttribute("aria-selected", String(active)); button.tabIndex = active ? 0 : -1;
  });
  $("#capability-panel").setAttribute("aria-labelledby", `tab-${id}`);
  $("#input-image").src = asset(capability.input);
  $("#input-image").alt = capability.inputAlt;
  $("#input-caption").textContent = capability.inputCaption;
  $("#output-image").src = asset(output.image); $("#output-image").alt = output.alt;
  $("#output-label").textContent = output.label; $("#output-caption").textContent = output.caption;
  $("#capability-kicker").textContent = capability.kicker;
  $("#capability-title").innerHTML = capability.title;
  $("#capability-description").textContent = capability.description;
  $("#result-facts").innerHTML = capability.facts.map(([key, value]) => `<div><dt>${key}</dt><dd>${value}</dd></div>`).join("");
  $("#effect-source").href = UPSTREAM + capability.source;
  $("#variant-switch").innerHTML = capability.variants.map((item, index) => `<button data-variant="${index}" class="${index === variant ? "active" : ""}" aria-pressed="${index === variant}">${item.name}</button>`).join("");
  if (restoreVariantFocus !== undefined) $("#variant-switch").querySelector(`[data-variant="${variant}"]`)?.focus({ preventScroll: true });
}
$$("[data-capability]").forEach((button, index, buttons) => {
  button.addEventListener("click", () => renderCapability(button.dataset.capability));
  button.addEventListener("keydown", (event) => {
    let next;
    if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
    if (event.key === "ArrowLeft") next = (index - 1 + buttons.length) % buttons.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = buttons.length - 1;
    if (next === undefined) return;
    event.preventDefault(); buttons[next].focus(); renderCapability(buttons[next].dataset.capability);
  });
});
$("#variant-switch").addEventListener("click", (event) => {
  const button = event.target.closest("[data-variant]");
  if (button) renderCapability(selectedCapability, Number(button.dataset.variant));
});
const dialog = $("#image-dialog");
$("#zoom-image").addEventListener("click", () => {
  $("#dialog-image").src = $("#output-image").src;
  $("#dialog-image").alt = $("#output-image").alt;
  $("#dialog-caption").textContent = $("#output-caption").textContent;
  dialog.showModal();
});
$("#close-dialog").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", (event) => {
  if (event.target !== dialog) return;
  const bounds = dialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
});

const pipelines = {
  poster: [
    ["识别照片与表达目标", "先决定这张海报要表达什么", "检查照片主体是否可用，确认带字还是无字。带字版让标题优先，无字版让动作成为主线；两版各自设计构图。", "主体、创作分支、一个明确动作与构图方向", "SKILL.md"],
    ["先做无标题底图", "给实物和标题各自留出位置", "图像模型结合原图与风格规则，保留实物的摄影质感，重整背景、位置和小人动作。带字版先预留标题区域。", "无字底图：实物 + 留白 + 克制的小人动作", "references/style-guide.md"],
    ["准备字形参考", "把“手写感”落实到字的结构", "从字形、笔画和标题节奏参考中组织构字参考图，控制歪扭程度、错落与粗细。脚本制作参考排版，图像模型据此生成或绘制标题。", "给模型使用的标题构字参考图", "scripts/build_title_reference_sheet.py"],
    ["生成独立标题层", "单独检查每一个字", "只处理指定的中文标题，审核字义、笔画与手绘节奏。文字出错时返修这一层，避免连带重做已经确认的实物底图。", "经过检查的黑色标题图层", "references/lettering-guide.md"],
    ["合成与最终审核", "脚本负责放好，人工负责看对", "Pillow 按灰度阈值提取黑色笔画，结合原图透明度建立标题蒙版，再缩放、定位并合成。最后检查标题、主体与动作故事是否成立。", "静态海报图片 + 视觉审核结论", "scripts/composite_title_layer.py"],
  ],
  monster: [
    ["提取来源关系", "让照片提供设计依据", "记录颜色、配料、材质，以及包含、沉积和覆盖关系。至少一个非颜色线索参与新身体的外形结构，避免只把通用角色换个颜色。", "来源关系图、身体构造、五官和材料分层约束", "references/desktop-pet-character-modes.md"],
    ["先画黑线母稿", "先确定角色能不能被认出来", "先确定轮廓、友好清楚的五官与两手两腿，再检查不规则线条和结构。上游要求看原尺寸、300% 局部和 120–140 px 小尺寸。", "通过结构与小尺寸可读性检查的黑线身份稿", "references/desktop-pet-workflow.md"],
    ["锁住线条再上色", "颜色表达来源，线条保持身份", "沿用已确认黑线，用蜡笔等干性材料的色块表现原图中的分层和材料关系。局部失败只做定向修正，通过的部分继续保留。", "带颜色、材质与来源标记的角色身份稿", "references/mixed-media-style-guide.md"],
    ["确认身份后分支", "一份身份，延续到不同产物", "人工确认角色后，这份 canonical identity 成为产品互动图与桌宠动作的共同参照。再按用途选择海报、桌宠或两者；角色设计阶段无需运行器。", "确认后的角色身份 + 下一步用途选择", "SKILL.md", "人工确认"],
  ],
  desktop: [
    ["确认角色与检查环境", "先有身份，再准备运行条件", "先确认角色形象，再只读检查桌宠环境。只有继续制作可运行桌宠才需要运行器。安装或升级有独立的计划与确认步骤。", "已确认身份、可用运行器与兼容的角色包版本", "references/desktop-pet-environment.md", "人工确认"],
    ["设计动作与行为阶段", "把一次回应拆成有边界的动作", "写实卡通 v2 使用十二个固定动作；风味小怪兽 v3 定义六至十个行为。v3 的行走、睡眠、拖拽等可拆成进入、循环和退出阶段。", "保持角色身份的动画帧 + 分阶段行为设计", "references/desktop-pet-workflow.md"],
    ["确认动作并处理透明帧", "逐帧看清，再交给运行器", "人工审核动作后，把已生成的帧条拆分、去底或保留 alpha、缩放与对齐。背景残留、邻帧串入和脚底漂移都需要检查。", "真实透明 PNG/WebP 帧条 + 动作审核结果", "scripts/prepare_generated_animation_strips.py", "人工确认"],
    ["描述、校验与打包", "让图像成为可读取的角色数据", "pet.json 描述画布、锚点、帧数、时间与完成事件。工具检查路径、尺寸、透明边角、可达行为等约束，并输出审核图与 ZIP。", "经过格式校验的角色包与审核图", "scripts/validate_desktop_pet_pack.py"],
    ["事件驱动桌面运行", "动画什么时候换，由事件决定", "Electron 创建透明桌面窗口，Canvas 切片播放帧条。阶段播放器收到播放完成、行走完成、落地、松手或唤醒等事件后前进；触发控制器负责优先级与冷却。", "可在桌面运行的角色、交互和行为切换", "assets/desktop-pet-runtime/src/core/episode-player.js"],
  ],
};
function renderPipeline(path, step = 0, moveFocus = false) {
  const steps = pipelines[path];
  $$("button[data-pipeline]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.pipeline === path)));
  $("#pipeline-steps").innerHTML = steps.map(([label], index) => `<li><button data-step="${index}" ${index === step ? 'aria-current="step"' : ""}><span>${String(index + 1).padStart(2, "0")}</span>${label}</button></li>`).join("");
  const [, title, description, output, source, gate] = steps[step];
  $("#step-content").innerHTML = `<span class="step-number">STEP ${String(step + 1).padStart(2, "0")} / ${String(steps.length).padStart(2, "0")}</span>${gate ? `<span class="step-gate">${gate}</span>` : ""}<h3>${title}</h3><p>${description}</p><div class="step-deliverable"><span>这一阶段得到什么</span>${output}</div><a href="${UPSTREAM + source}" target="_blank" rel="noreferrer">源码依据：${source} ↗</a>`;
  $("#pipeline-steps").dataset.path = path;
  if (moveFocus) $("#pipeline-steps").querySelector(`[data-step="${step}"]`).focus({ preventScroll: true });
}
$$("button[data-pipeline]").forEach((button) => button.addEventListener("click", () => renderPipeline(button.dataset.pipeline)));
$("#pipeline-steps").addEventListener("click", (event) => {
  const button = event.target.closest("[data-step]");
  if (button) renderPipeline($("#pipeline-steps").dataset.path, Number(button.dataset.step), true);
});

const scenarios = {
  content: ["围绕自有商品照片，延伸上新海报、产品互动图和社交内容，可继续接入批量任务。", "构图与动作语法、标题分层、风格规则和局部返修流程。", "需要品牌规范与批量管理；核对商品细节、中文及使用权，用可用率、返修次数和耗时实测。"],
  character: ["先确认原创角色，再发展系列互动图、角色姿态、贴纸和表情素材。", "来源特征映射、两阶段身份设计、canonical identity 与动作约束。", "需要多姿态一致性检查、输出规格与跨媒介适配；贴纸和表情导出属于后续开发。"],
  companion: ["将角色用于活动页、展陈终端或桌面轻陪伴，回应用户操作及活动事件。", "透明帧、分阶段行为、完成事件、交互优先级和共享运行器。", "活动页与终端需新增事件接入和宿主适配；原生桌宠还要验证多屏、物理、资源占用及系统兼容。"],
  workflow: ["把自有审美规则与不同图像模型接入可换风格的创作工具，管理生成、审核和返修。", "Skill 路由、阶段输入输出、通过项锁定、资产校验与打包工具链。", "需要模型接入、任务队列、审核界面和版本记录；用固定素材比较质量与修改成本。"],
};
function renderScenario(id) {
  $("#scenario-result").innerHTML = scenarios[id].map((text, index) => `<div><span>${["可以做什么", "值得复用什么", "落地时还要验证什么"][index]}</span><p>${text}</p></div>`).join("");
}
$("#scenario").addEventListener("change", (event) => renderScenario(event.target.value));

// The pinned upstream EpisodePlayer owns phase completion. This adapter only loads,
// displays and grounds frames; desktop physical completion is sent manually in this lab.
const behaviorLabels = {
  "awake-story": "日常发呆", "explore-walk": "走两步", "sleep-cycle": "睡个觉",
  "affection-click": "点一下", "cursor-encounter": "遇见光标", held: "拎起来",
  "drop-recover": "落地恢复", "fruit-hiccup": "果粒打嗝",
};
const eventLabels = {
  "motion-finished": "行走到达 →", "wake-requested": "叫醒它 →",
  "pointer-released": "放开它 →", "floor-impact": "已经落地 →",
};
const canvas = $("#pet-canvas");
const context = canvas.getContext("2d", { alpha: true });
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
let manifest, episode, images = new Map(), groundOffsets = new Map();
let behaviorId = "awake-story", phaseIndex = 0, frameIndex = 0, frameTimer;
let petReady = false, paused = reducedMotion.matches, finished = false, queuedWake = false;
function currentPhase() { return manifest?.behaviors[behaviorId].phases[phaseIndex]; }
function loadImage(path) {
  return new Promise((resolve, reject) => {
    const image = new Image(); image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`动画素材读取失败：${path}`)); image.src = asset(`pet-v3/${path}`);
  });
}
function getGroundOffsets(image, frames) {
  const probe = document.createElement("canvas");
  probe.width = manifest.canvas.width; probe.height = manifest.canvas.height;
  const probeContext = probe.getContext("2d", { willReadFrequently: true });
  const offsets = [];
  for (let frame = 0; frame < frames; frame++) {
    probeContext.clearRect(0, 0, probe.width, probe.height);
    probeContext.drawImage(image, frame * probe.width, 0, probe.width, probe.height, 0, 0, probe.width, probe.height);
    const pixels = probeContext.getImageData(0, 0, probe.width, probe.height).data;
    let bottom = 0;
    for (let y = probe.height - 1; y >= 0 && !bottom; y--)
      for (let x = 0; x < probe.width; x++)
        if (pixels[(y * probe.width + x) * 4 + 3] > 24) { bottom = y + 1; break; }
    offsets.push(bottom ? manifest.anchor.y - bottom : 0);
  }
  return offsets;
}
function drawFrame() {
  const phase = currentPhase(); if (!phase || !petReady) return;
  context.clearRect(0, 0, canvas.width, canvas.height);
  const offset = phase.grounding === "floor" ? groundOffsets.get(phase.file)[frameIndex] : 0;
  context.drawImage(images.get(phase.file), frameIndex * canvas.width, 0, canvas.width, canvas.height, 0, offset, canvas.width, canvas.height);
  canvas.dataset.behavior = behaviorId; canvas.dataset.phase = phase.id;
  canvas.dataset.frame = String(frameIndex); canvas.dataset.paused = String(paused);
  const state = finished ? "行为结束，保持末帧" : paused ? "已暂停" : phase.playback === "loop" ? `循环，等待 ${phase.completeOn}` : "播放中";
  $("#phase-detail").textContent = `${phase.id} · 第 ${frameIndex + 1}/${phase.frames} 帧 · ${state}`;
}
function renderPetPanel() {
  const phases = manifest.behaviors[behaviorId].phases;
  $("#behavior-name").textContent = `${behaviorLabels[behaviorId]} / ${behaviorId}`;
  $("#phase-list").innerHTML = phases.map((phase, index) => `<li class="${index === phaseIndex ? "current" : ""}" ${index === phaseIndex ? 'aria-current="step"' : ""}>${phase.id}</li>`).join("");
  const event = currentPhase().completeOn;
  $("#phase-event").hidden = !eventLabels[event] || finished;
  $("#phase-event").textContent = eventLabels[event] || "发送完成事件 →";
  $$("[data-behavior]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.behavior === behaviorId)));
  $("#pause-pet").setAttribute("aria-pressed", String(paused));
  $("#pause-pet").textContent = paused ? "继续动画 ▶" : "暂停动画 Ⅱ";
}
function scheduleFrame() {
  clearTimeout(frameTimer);
  if (!petReady || paused || finished || document.hidden) return;
  const phase = currentPhase();
  frameTimer = setTimeout(advanceFrame, phase.durationsMs?.[frameIndex] ?? 1000 / phase.fps);
}
function applyEpisodeResult(result) {
  if (result.status === "completed") {
    finished = true;
    if (behaviorId === "held") { startBehavior("drop-recover"); return; }
    if (behaviorId === "sleep-cycle" && queuedWake) { queuedWake = false; startBehavior("affection-click"); return; }
  } else if (result.status === "advanced") {
    phaseIndex = episode.episode.phaseIndex; frameIndex = 0;
    if (queuedWake && currentPhase().completeOn === "wake-requested") {
      applyEpisodeResult(episode.signal("wake-requested")); return;
    }
  }
  drawFrame(); renderPetPanel(); scheduleFrame();
}
function advanceFrame() {
  const phase = currentPhase();
  if (frameIndex + 1 < phase.frames) { frameIndex++; drawFrame(); scheduleFrame(); return; }
  if (phase.playback === "loop") { frameIndex = 0; drawFrame(); scheduleFrame(); return; }
  if (phase.completeOn === "animation-finished") applyEpisodeResult(episode.signal("animation-finished"));
}
function startBehavior(id) {
  if (!petReady) return;
  clearTimeout(frameTimer); queuedWake = false; behaviorId = id; phaseIndex = 0; frameIndex = 0; finished = false;
  episode.start(id); drawFrame(); renderPetPanel(); scheduleFrame();
}
function requestAffection() {
  if (!petReady) return;
  if (behaviorId === "sleep-cycle" && !finished) {
    queuedWake = true;
    if (currentPhase().completeOn === "wake-requested") applyEpisodeResult(episode.signal("wake-requested"));
    else $("#phase-detail").textContent += " · 已请求唤醒";
    return;
  }
  startBehavior("affection-click");
}
$$("[data-behavior]").forEach((button) => button.addEventListener("click", () => startBehavior(button.dataset.behavior)));
canvas.addEventListener("click", requestAffection);
canvas.addEventListener("keydown", (event) => { if (["Enter", " "].includes(event.key)) { event.preventDefault(); requestAffection(); } });
$("#phase-event").addEventListener("click", () => {
  if (!petReady || finished) return;
  if (currentPhase().completeOn === "wake-requested") queuedWake = true;
  applyEpisodeResult(episode.signal(currentPhase().completeOn));
});
$("#pause-pet").addEventListener("click", () => {
  paused = !paused; clearTimeout(frameTimer);
  if (petReady) { renderPetPanel(); drawFrame(); scheduleFrame(); }
});
document.addEventListener("visibilitychange", () => { clearTimeout(frameTimer); if (!document.hidden) scheduleFrame(); });
reducedMotion.addEventListener("change", (event) => {
  if (event.matches) { paused = true; clearTimeout(frameTimer); if (petReady) { renderPetPanel(); drawFrame(); } }
});
async function initializePet() {
  try {
    if (embedded?.manifest) manifest = embedded.manifest;
    else {
      const response = await fetch(asset("pet-v3/pet.json"));
      if (!response.ok) throw new Error("角色数据读取失败");
      manifest = await response.json();
    }
    if (!window.EpisodePlayer) throw new Error("上游阶段播放器未加载");
    episode = new window.EpisodePlayer(manifest);
    canvas.width = manifest.canvas.width; canvas.height = manifest.canvas.height;
    const phases = Object.values(manifest.behaviors).flatMap((behavior) => behavior.phases);
    await Promise.all(phases.map(async (phase) => {
      const image = await loadImage(phase.file); images.set(phase.file, image);
      groundOffsets.set(phase.file, getGroundOffsets(image, phase.frames));
    }));
    petReady = true; startBehavior("awake-story");
  } catch (error) {
    $("#pet-error").hidden = false; $("#pet-error").textContent = `${error.message}。可从下方链接查看原始动作预览。`;
    $("#behavior-name").textContent = "动画未能加载";
    $$("[data-behavior]").forEach((button) => { button.disabled = true; });
    $("#pause-pet").disabled = true;
  }
}
renderCapability("poster"); renderPipeline("poster"); renderScenario("content"); initializePet();
