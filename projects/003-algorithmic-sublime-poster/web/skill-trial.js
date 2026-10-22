(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const section = $("chair-photo-content");
  if (!section) return;
  const root = "./assets/skill-trial/";
  let studyText = "";
  const make = (tag, text, className) => {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  const status = (text) => { $("trial-status").textContent = text; };
  function settleEntry() {
    if (location.hash === "#chair-photo-trial") requestAnimationFrame(() => section.scrollIntoView({behavior: "instant", block: "start"}));
  }
  function download(blob, name) {
    const url = URL.createObjectURL(blob), link = make("a"); link.href = url; link.download = name;
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  async function saveOriginal(row, button) {
    button.disabled = true;
    try {
      const response = await fetch(root + row.actual.file); if (!response.ok) throw new Error("Unavailable original");
      download(await response.blob(), "red-chair-" + row.id + ".png"); status("已准备下载" + row.title + "的原始PNG，未加滤镜或裁切。");
    } catch { status("原图暂时未能下载，可通过实际记录中的文件地址查看。"); }
    finally { button.disabled = false; }
  }
  function show(row) {
    $("trial-dialog-title").textContent = row.code + " / " + row.title + " / 实际生成原图";
    $("trial-dialog-image").src = root + row.actual.file;
    $("trial-dialog-image").alt = row.alt;
    $("trial-dialog").showModal();
  }
  $("trial-dialog-close").addEventListener("click", () => $("trial-dialog").close());
  $("trial-dialog").addEventListener("click", (event) => { if (event.target === $("trial-dialog")) $("trial-dialog").close(); });
  function card(row) {
    const article = make("article", undefined, "trial-card"); article.dataset.trialId = row.id;
    const open = make("button", undefined, "trial-image-button"); open.type = "button"; open.setAttribute("aria-label", "放大" + row.code + "：" + row.title + "实际原图");
    const image = make("img"); image.src = root + row.actual.file; image.alt = row.alt; image.width = row.actual.width; image.height = row.actual.height; image.loading = "lazy";
    open.append(image, make("span", "原图 / 点击放大 ↗")); open.addEventListener("click", () => show(row));
    const body = make("div", undefined, "trial-card-body"); body.append(make("p", row.code + " / " + row.art_direction, "trial-direction"), make("h4", row.title), make("p", row.intent, "trial-intent"), make("p", row.translation, "trial-translation"), make("span", row.status, "trial-result-label"));
    const findings = make("details"); findings.append(make("summary", "实际效果与偏差"));
    for (const [label, text] of [["实际看见", row.observed], ["偏差与歧义", row.deviations], ["下一轮建议 / 未执行", row.next_revision]]) {
      const paragraph = make("p"); paragraph.append(make("b", label + "："), document.createTextNode(text)); findings.append(paragraph);
    }
    const prompts = make("details"); prompts.append(make("summary", "本张实际提交的提示词"));
    const pre = make("pre", row.prompt); pre.tabIndex = 0; pre.setAttribute("aria-label", row.code + "实际生成提示词"); prompts.append(pre);
    const promptActions = make("div", undefined, "trial-prompt-actions");
    const copy = make("button", "复制实际指令"); copy.type = "button"; copy.setAttribute("aria-label", "复制" + row.code + "实际指令");
    copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(row.prompt); status("已复制" + row.code + "实际提交的完整指令。"); }
      catch { status("可以选择指令文本，或下载本张实际指令TXT。"); }
    });
    const txt = make("button", "下载实际 TXT ↓"); txt.type = "button"; txt.setAttribute("aria-label", "下载" + row.code + "实际指令TXT");
    txt.addEventListener("click", () => download(new Blob([row.prompt], {type: "text/plain;charset=utf-8"}), "red-chair-" + row.id + "-actual-prompt.txt"));
    promptActions.append(copy, txt); prompts.append(promptActions);
    const actions = make("div", undefined, "trial-card-actions"); const png = make("button", "下载原始 PNG ↓"); png.type = "button"; png.setAttribute("aria-label", "下载" + row.code + "原始PNG"); png.addEventListener("click", () => saveOriginal(row, png)); actions.append(png);
    body.append(findings, prompts, actions); article.append(open, body); return article;
  }
  $("trial-export").addEventListener("click", () => {
    if (studyText) download(new Blob([studyText], {type: "application/json;charset=utf-8"}), "red-chair-skill-trial.json");
  });
  async function init() {
    try {
      const response = await fetch(root + "study.json"); if (!response.ok) throw new Error("Study unavailable");
      studyText = await response.text(); const study = JSON.parse(studyText);
      if (!study.generated || study.status !== "completed" || study.cases.length !== 3) throw new Error("Incomplete trial");
      $("trial-grid").append(...study.cases.map(card));
      study.findings.forEach((text) => $("trial-findings").append(make("li", text)));
      study.limits.forEach((text) => $("trial-limit-list").append(make("li", text)));
      study.cases.forEach((row) => {
        const tr = make("tr"); tr.append(make("td", row.code + " / " + row.title.split(" / ")[0]), make("td", row.planned_scale), make("td", "约" + Math.round(row.approximate_height_fraction * 100) + "%")); $("trial-scale-body").append(tr);
      });
      $("trial-reference-image").src = root + study.reference.file;
      $("trial-reference-observed").textContent = study.reference.observation;
      $("trial-loading").hidden = true; $("trial-content").hidden = false; $("trial-export").disabled = false;
      document.dispatchEvent(new Event("poster:skill-trial-ready")); settleEntry();
    } catch { $("trial-loading").textContent = "实际对照暂时未能载入，可查看完整记录与原图文件。"; }
  }
  document.addEventListener("poster:intent-template-ready", settleEntry, {once: true});
  window.addEventListener("load", settleEntry, {once: true}); init();
})();
