(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const section = $("skill-trial");
  if (!section) return;
  const root = "./assets/chair-data/";
  let studyText = "";
  const make = (tag, text, className) => {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  const status = (text) => { $("fusion-status").textContent = text; };
  function settleEntry() {
    if (location.hash === "#skill-trial") requestAnimationFrame(() => section.scrollIntoView({behavior: "instant", block: "start"}));
  }
  function revealPhoto() {
    if (location.hash === "#chair-photo-trial") $("chair-photo-trial").open = true;
  }
  function download(blob, name) {
    const url = URL.createObjectURL(blob), link = make("a"); link.href = url; link.download = name;
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  async function saveOriginal(row, button) {
    button.disabled = true;
    try {
      const response = await fetch(root + row.actual.file); if (!response.ok) throw new Error("Unavailable original");
      download(await response.blob(), "red-chair-data-" + row.id + ".png"); status("已准备下载" + row.title + "的原始PNG。");
    } catch { status("暂未能下载，可从原件与来源记录中的文件地址查看。"); }
    finally { button.disabled = false; }
  }
  function show(row) {
    $("fusion-dialog-title").textContent = row.code + " / " + row.title + " / 实体与数据融合原图";
    $("fusion-dialog-image").src = root + row.actual.file; $("fusion-dialog-image").alt = row.alt;
    $("fusion-dialog").showModal();
  }
  $("fusion-dialog-close").addEventListener("click", () => $("fusion-dialog").close());
  $("fusion-dialog").addEventListener("click", (event) => { if (event.target === $("fusion-dialog")) $("fusion-dialog").close(); });
  function card(row) {
    const article = make("article", undefined, "trial-card fusion-card"); article.dataset.fusionId = row.id;
    const open = make("button", undefined, "trial-image-button"); open.type = "button"; open.setAttribute("aria-label", "放大融合" + row.code + "：" + row.title);
    const image = make("img"); image.src = root + row.actual.file; image.alt = row.alt; image.width = row.actual.width; image.height = row.actual.height; image.loading = "lazy";
    open.append(image, make("span", "实际生成原图 / 放大 ↗")); open.addEventListener("click", () => show(row));
    const body = make("div", undefined, "trial-card-body");
    body.append(make("p", row.code + " / 同一风格 · " + row.emotion, "trial-direction"), make("h4", row.title), make("p", row.intent, "trial-intent"));
    const relation = make("p", undefined, "fusion-relation"); relation.append(make("b", "实体 × 数据 / "), document.createTextNode(row.data_relation)); body.append(relation, make("p", row.translation, "trial-translation"), make("span", row.status, "trial-result-label"));
    const findings = make("details"); findings.append(make("summary", "实际效果、风格与偏差"));
    for (const [label, text] of [["实际看见", row.observed], ["偏差与歧义", row.deviations], ["下一轮建议 / 未执行", row.next_revision]]) {
      const p = make("p"); p.append(make("b", label + "："), document.createTextNode(text)); findings.append(p);
    }
    const prompts = make("details"); prompts.append(make("summary", row.repair ? "首轮生成提示词 / 另有尺度返修" : "本轮融合图的实际提示词"));
    const pre = make("pre", row.prompt); pre.tabIndex = 0; pre.setAttribute("aria-label", "融合" + row.code + "实际生成提示词"); prompts.append(pre);
    const promptActions = make("div", undefined, "trial-prompt-actions");
    const copy = make("button", "复制实际指令"); copy.type = "button"; copy.setAttribute("aria-label", "复制融合" + row.code + "实际指令");
    copy.addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(row.prompt); status("已复制融合" + row.code + "实际提交的完整指令。"); }
      catch { status("可以选择指令文本，或下载实际指令TXT。"); }
    });
    const txt = make("button", "下载实际 TXT ↓"); txt.type = "button"; txt.setAttribute("aria-label", "下载融合" + row.code + "实际指令TXT");
    txt.addEventListener("click", () => download(new Blob([row.prompt], {type: "text/plain;charset=utf-8"}), "red-chair-data-" + row.id + "-actual-prompt.txt"));
    promptActions.append(copy, txt); prompts.append(promptActions);
    const photo = make("details", undefined, "fusion-photo"); photo.append(make("summary", "与前轮摄影分支对照"));
    const photoImage = make("img"); photoImage.src = root + row.photo_file; photoImage.alt = "前轮摄影分支 / " + row.emotion + "；用于比较，没有实体数据转化"; photoImage.width = 1122; photoImage.height = 1402; photoImage.loading = "lazy";
    photo.append(photoImage, make("p", "上图是前轮摄影分支；卡片首图是本轮融合海报。两轮独立重生成，变化包括空间、文字与数据关系，不能视作只增加数据的单变量对照。"));
    const previous = make("a", "查看前轮摄影的实际指令 ↗"); previous.href = "./assets/skill-trial/" + row.id + "-prompt.txt"; previous.target = "_blank"; previous.rel = "noopener"; photo.append(previous);
    const actions = make("div", undefined, "trial-card-actions"); const png = make("button", "下载融合原始 PNG ↓"); png.type = "button"; png.setAttribute("aria-label", "下载融合" + row.code + "原始PNG"); png.addEventListener("click", () => saveOriginal(row, png)); actions.append(png);
    body.append(findings, prompts);
    if (row.repair) {
      const repair = make("details", undefined, "fusion-photo"); repair.append(make("summary", "已执行的尺度返修 / 前后与实际指令"));
      const before = make("img"); before.src = root + row.repair.before.file; before.alt = "孤独融合首轮原图，椅子偏大；卡片首图为实际返修后"; before.width = row.repair.before.width; before.height = row.repair.before.height; before.loading = "lazy";
      repair.append(make("p", "返修前原图 / 卡片首图为实际返修后"), before, make("p", row.repair.observation));
      const rp = make("pre", row.repair.prompt); rp.tabIndex = 0; rp.setAttribute("aria-label", "孤独融合实际返修提示词"); repair.append(rp);
      const actions = make("div", undefined, "trial-prompt-actions");
      const copyRepair = make("button", "复制已执行返修指令"); copyRepair.type = "button";
      copyRepair.addEventListener("click", async () => { try { await navigator.clipboard.writeText(row.repair.prompt); status("已复制孤独方向实际执行的尺度返修指令。"); } catch { status("可以选择返修文本或下载TXT。"); } });
      const txtRepair = make("button", "下载已执行返修 TXT ↓"); txtRepair.type = "button";
      txtRepair.addEventListener("click", () => download(new Blob([row.repair.prompt], {type: "text/plain;charset=utf-8"}), "red-chair-data-solitude-repair.txt"));
      actions.append(copyRepair, txtRepair); repair.append(actions); body.append(repair);
    }
    body.append(photo, actions); article.append(open, body); return article;
  }
  $("fusion-export").addEventListener("click", () => {
    if (studyText) download(new Blob([studyText], {type: "application/json;charset=utf-8"}), "red-chair-data-trial.json");
  });
  async function init() {
    try {
      const response = await fetch(root + "study.json"); if (!response.ok) throw new Error("Study unavailable");
      studyText = await response.text(); const study = JSON.parse(studyText);
      if (!study.generated || study.status !== "completed" || study.cases.length !== 3) throw new Error("Incomplete trial");
      $("fusion-grid").append(...study.cases.map(card));
      study.findings.forEach((text) => $("fusion-findings").append(make("li", text)));
      study.fixed_rules.forEach((text) => $("fusion-rule-list").append(make("li", text)));
      study.limits.forEach((text) => $("fusion-limit-list").append(make("li", text)));
      const sizes = [...new Set(study.cases.map((r) => r.actual.width + "×" + r.actual.height))]; $("fusion-size").textContent = "实际" + sizes.join(" / ");
      $("fusion-loading").hidden = true; $("fusion-content").hidden = false; $("fusion-export").disabled = false;
      document.dispatchEvent(new Event("poster:chair-data-ready")); settleEntry();
    } catch { $("fusion-loading").textContent = "实际融合图暂时未能载入，可查看生成记录与原图文件。"; }
  }
  document.addEventListener("poster:intent-template-ready", settleEntry, {once: true});
  window.addEventListener("load", settleEntry, {once: true}); window.addEventListener("hashchange", revealPhoto);
  revealPhoto(); init();
})();
