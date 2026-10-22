(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  if (!$("emotion-validation")) return;
  const asset = (file) => "./assets/validation/" + file;
  const tabs = Array.from(document.querySelectorAll("[data-validation-group]"));
  let data, manifest, protocol;
  let groupId = "subject";
  let revealed = false;
  let everRevealed = false;
  let workMap = new Map();
  const prompts = new Map();
  const responses = new Map();
  const make = (tag, text, className) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    if (className) element.className = className;
    return element;
  };
  function go() {
    history.replaceState(null, "", "#emotion-validation");
    $("emotion-validation").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start" });
  }
  ["emotion-to-validation", "motion-to-validation"].forEach((id) => $(id).addEventListener("click", go));
  document.querySelector(".nav-validation").addEventListener("click", (event) => { event.preventDefault(); go(); });
  $("validation-to-images").addEventListener("click", () => {
    $("validation-panel").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start" });
  });
  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = make("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  function jsonFile(value, filename) {
    download(new Blob([JSON.stringify(value, null, 2) + "\n"], { type: "application/json;charset=utf-8" }), filename);
  }
  function openImage(file, title) {
    $("art-dialog-image").src = asset(file);
    $("art-dialog-image").alt = title;
    $("art-dialog-title").textContent = title;
    $("art-dialog").showModal();
    $("art-dialog").scrollTop = 0;
  }
  function ratio(work) {
    const meta = manifest.outputs.find((item) => item.id === work.id);
    return (work.bbox[3] - work.bbox[1]) / meta.height;
  }
  function record(id, key, value) {
    const previous = responses.get(id) || { impression: "", note: "", firstInputAfterReveal: everRevealed };
    responses.set(id, { ...previous, [key]: value, latestInputAfterReveal: everRevealed });
    const count = Array.from(responses.values()).filter((r) => r.impression || r.note.trim()).length;
    $("validation-status").textContent = "已在当前页面记录 " + count + " 张作品的感受；需要保留时请下载观图记录。";
  }
  function labelFor(index) {
    const letter = { subject: "A", transfer: "B", repair: "C" }[groupId];
    return letter + String(index + 1).padStart(2, "0");
  }
  function card(work, index) {
    const label = labelFor(index);
    const result = make("article", undefined, "validation-card");
    result.dataset.validationWork = work.id;
    const heading = make("div", undefined, "validation-card-heading");
    heading.append(make("strong", label), make("span", groupId === "repair" ? (index === 0 ? "首轮原图" : "一轮实际返修") : work.subject));
    const imageButton = make("button", undefined, "validation-image");
    imageButton.type = "button";
    imageButton.dataset.validationOpen = work.id;
    imageButton.setAttribute("aria-label", "放大" + label + (revealed ? "：" + work.target : "：目标标签隐藏"));
    const image = make("img");
    image.src = asset(work.image);
    image.alt = label + "完整生成海报" + (revealed ? "，目标：" + work.target : "，目标标签暂未显示");
    image.width = 1122;
    image.height = 1402;
    image.loading = "lazy";
    imageButton.append(image);
    if (groupId === "repair" && $("validation-show-boxes").checked && work.bbox) {
      const meta = manifest.outputs.find((item) => item.id === work.id);
      const [x1, y1, x2, y2] = work.bbox;
      const box = make("span", undefined, "validation-bbox");
      box.setAttribute("aria-hidden", "true");
      box.style.left = x1 / meta.width * 100 + "%";
      box.style.top = y1 / meta.height * 100 + "%";
      box.style.width = (x2 - x1) / meta.width * 100 + "%";
      box.style.height = (y2 - y1) / meta.height * 100 + "%";
      box.append(make("span", "约" + Math.round(ratio(work) * 100) + "% · 人工粗框"));
      imageButton.append(box);
    }
    imageButton.addEventListener("click", () => openImage(work.image, label + (revealed ? " · " + work.target : " · 完整原图 / 目标隐藏")));
    const caption = make("p", revealed ? work.target : "先看画面，记录第一感受。", "validation-image-caption");
    caption.append(make("small", revealed ? (work.input ? "使用图片输入 · " + work.input_role : "由文字生成") : "目标与作者观察暂未显示"));
    const viewer = make("div", undefined, "validation-viewer");
    const feelingLabel = make("label", label + " / 第一感受");
    const select = make("select");
    select.id = "validation-feeling-" + work.id;
    feelingLabel.htmlFor = select.id;
    const empty = make("option", "选择你的实际感受");
    empty.value = "";
    select.append(empty);
    data.response_options.forEach((text) => { const option = make("option", text); option.value = text; select.append(option); });
    select.value = responses.get(work.id)?.impression || "";
    select.addEventListener("change", () => record(work.id, "impression", select.value));
    feelingLabel.append(select);
    const noteLabel = make("label", "依据 / 哪个画面线索");
    const note = make("input");
    note.type = "text";
    note.id = "validation-note-" + work.id;
    note.maxLength = 200;
    note.placeholder = "光线、距离、主体关系……";
    note.value = responses.get(work.id)?.note || "";
    noteLabel.htmlFor = note.id;
    note.addEventListener("input", () => record(work.id, "note", note.value));
    noteLabel.append(note);
    viewer.append(feelingLabel, noteLabel);
    result.append(heading, imageButton, caption, viewer);
    if (revealed) {
      const observation = make("div", undefined, "validation-observation");
      for (const [title, text, className] of [
        ["实际要求", work.goal, ""], ["作者观察 / 已看到什么", work.observed, ""],
        ["偏差与歧义 / 仍未解决", work.drift, "validation-drift"], ["主体与风格保留", work.identity, ""]
      ]) observation.append(make("h6", title), make("p", text, className));
      const details = make("details", undefined, "validation-prompt");
      details.append(make("summary", "查看本张完整实际指令"));
      const pre = make("pre", prompts.get(work.id));
      pre.tabIndex = 0;
      pre.setAttribute("aria-label", label + "完整实际生成指令");
      details.append(pre);
      const actions = make("div", undefined, "validation-file-actions");
      const copy = make("button", "复制指令");
      copy.type = "button";
      copy.dataset.validationCopy = work.id;
      copy.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(prompts.get(work.id));
          $("validation-status").textContent = "已复制" + label + "的完整实际指令。";
        } catch {
          $("validation-status").textContent = "浏览器未允许复制，可选中指令或下载TXT。";
        }
      });
      const txt = make("button", "下载TXT");
      txt.type = "button";
      txt.dataset.validationTxt = work.id;
      txt.addEventListener("click", () => download(new Blob([prompts.get(work.id)], { type: "text/plain;charset=utf-8" }), work.prompt));
      actions.append(copy, txt);
      details.append(actions);
      observation.append(details);
      result.append(observation);
    }
    const fileActions = make("div", undefined, "validation-viewer");
    const fileButton = make("button", "下载原始PNG ↓");
    fileButton.type = "button";
    fileButton.dataset.validationDownload = work.id;
    const row = make("div", undefined, "validation-file-actions");
    row.style.marginTop = "0";
    row.append(fileButton);
    fileActions.append(row);
    fileButton.addEventListener("click", async () => {
      fileButton.disabled = true;
      try {
        const response = await fetch(asset(work.image));
        if (!response.ok) throw new Error("Image unavailable");
        download(await response.blob(), work.image);
        $("validation-status").textContent = "已准备下载" + label + "原始PNG，未经后期修改。";
      } catch { $("validation-status").textContent = "原图暂时无法下载，请确认连接后重试。"; }
      finally { fileButton.disabled = false; }
    });
    result.append(fileActions);
    return result;
  }
  function render() {
    if (!data) return;
    const group = data.groups.find((item) => item.id === groupId);
    tabs.forEach((tab) => {
      const active = tab.dataset.validationGroup === groupId;
      tab.setAttribute("aria-selected", String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    $("validation-panel").setAttribute("aria-labelledby", "validation-tab-" + groupId);
    $("validation-question").textContent = group.question;
    $("validation-fixed").textContent = group.fixed;
    $("validation-changed").textContent = group.changed;
    $("validation-group-finding").textContent = group.status + "：" + group.finding;
    $("validation-group-finding").hidden = !revealed;
    $("validation-findings").hidden = !revealed;
    $("validation-measurements").hidden = groupId !== "repair";
    $("validation-grid").dataset.group = groupId;
    $("validation-grid").replaceChildren(...group.items.map((id, index) => card(workMap.get(id), index)));
    $("validation-reveal").textContent = revealed ? "隐藏目标与作者观察" : "揭示目标与作者观察";
    $("validation-reveal").setAttribute("aria-pressed", String(revealed));
    $("validation-view-hint").textContent = revealed ?
      "已显示目标、实际指令与作者观察。现在填写的记录会标注为看过目标；再次隐藏不会重置这个标记。" :
      "目标标签与作者观察暂时隐藏。可以先记录自己的第一感受，再揭示对照；这只是查看方式，不是独立盲评实验。";
  }
  tabs.forEach((tab, index) => {
    const select = () => { groupId = tab.dataset.validationGroup; render(); };
    tab.addEventListener("click", select);
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = tabs.length - 1;
      else return;
      event.preventDefault();
      groupId = tabs[next].dataset.validationGroup;
      render();
      tabs[next].focus();
    });
  });
  $("validation-reveal").addEventListener("click", () => {
    revealed = !revealed;
    if (revealed) everRevealed = true;
    render();
  });
  $("validation-show-boxes").addEventListener("change", render);
  $("validation-reference-open").addEventListener("click", () => openImage(data.reference.image, "共同输入 · 中性主体识别图"));
  $("validation-evidence-download").addEventListener("click", () => {
    if (!data) return;
    jsonFile({ version: 1, kind: "emotion-guidance-evidence-bundle", protocol, manifest, study: data,
      prompts: Object.fromEntries(prompts), imageFilesIncluded: false,
      note: "Original PNGs are separately downloadable. Author observations are exploratory, not independent blind ratings or causal evidence." },
    "emotion-guidance-evidence.json");
    $("validation-status").textContent = "已准备下载：完整实际指令、来源、对照计划、返修与观察；原始PNG可逐张下载。";
  });
  $("validation-responses-download").addEventListener("click", () => {
    const records = Array.from(responses.entries()).filter(([, r]) => r.impression || r.note.trim())
      .map(([id, response]) => ({ id, ...response }));
    jsonFile({ version: 1, kind: "local-viewer-notes", generatedAt: new Date().toISOString(),
      independentBlindStudy: false, targetsRevealedInPage: everRevealed,
      limitation: "Prior conversation and downloaded filenames can reveal goals; this viewing mode is not a controlled blind experiment.",
      studySource: "assets/validation/study.json", responses: records }, "my-emotion-viewing-notes.json");
    $("validation-status").textContent = "已准备下载 " + records.length + " 张作品的个人观图记录；未上传，也未计算情绪准确率。";
  });
  async function readJson(file) {
    const response = await fetch(asset(file));
    if (!response.ok) throw new Error(file + " unavailable");
    return response.json();
  }
  async function init() {
    try {
      [data, manifest, protocol] = await Promise.all(["study.json", "manifest.json", "protocol.json"].map(readJson));
      workMap = new Map(data.works.map((work) => [work.id, work]));
      await Promise.all([data.reference, ...data.works].map(async (work) => {
        const response = await fetch(asset(work.prompt));
        if (!response.ok) throw new Error("Prompt unavailable");
        prompts.set(work.id, await response.text());
      }));
      $("validation-summary").textContent = data.summary;
      $("validation-findings-list").replaceChildren(...data.findings.map((finding) => make("li", finding)));
      $("validation-next-evidence").textContent = data.next_evidence;
      $("validation-caveat").textContent = data.caveat;
      $("validation-reference-caption").textContent = data.reference.caption;
      $("validation-before-ratio").textContent = "约" + Math.round(ratio(workMap.get(data.repair.before)) * 100) + "%";
      $("validation-after-ratio").textContent = "约" + Math.round(ratio(workMap.get(data.repair.after)) * 100) + "%";
      render();
      $("validation-content").hidden = false;
      $("validation-loading").hidden = true;
      $("validation-evidence-download").disabled = false;
    } catch {
      $("validation-loading").textContent = "生成记录暂时无法载入。请刷新后重试；原始研究数据与图片仍可从下方直接链接打开。";
      $("validation-loading").append(make("a", " 打开研究数据"));
      $("validation-loading").lastElementChild.href = asset("study.json");
    }
  }
  init();
})();
