(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const section = $("skill-film");
  if (!section) return;
  const root = "./assets/skill-film/";
  const video = $("skill-film-video");
  let brief = null;
  let study = null;
  let studyText = "";
  let prompt = "";
  let pendingSeek = null;
  const make = (tag, text, className) => {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  const status = (text) => { $("skill-film-status").textContent = text; };
  const clock = (time) => {
    const seconds = Math.floor(Math.max(0, Number.isFinite(time) ? time : 0));
    return String(Math.floor(seconds / 60)).padStart(2, "0") + ":" + String(seconds % 60).padStart(2, "0");
  };
  function settleEntry() {
    const target = location.hash === "#skill-film" ? section : location.hash === "#ai-film" ? $("ai-film") : null;
    if (target) requestAnimationFrame(() => target.scrollIntoView({behavior: "instant", block: "start"}));
  }
  function download(blob, name) {
    const url = URL.createObjectURL(blob), link = make("a"); link.href = url; link.download = name;
    document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  function sync() {
    const duration = Number.isFinite(video.duration) ? video.duration : study?.actual.duration_seconds || 0;
    const time = Number.isFinite(video.currentTime) ? video.currentTime : 0;
    $("skill-film-clock").textContent = clock(time) + " / " + clock(duration);
    $("skill-film-play").textContent = video.paused ? (video.ended ? "重新播放原片" : "播放本次AI原片") : "暂停 / 查看这一帧";
    $("skill-film-sound").textContent = video.muted ? "声音：关闭" : "声音：开启";
    $("skill-film-sound").setAttribute("aria-pressed", String(!video.muted));
    $("skill-film-scrub").max = String(Math.max(duration - .01, 0));
    $("skill-film-scrub").value = String(time);
    $("skill-film-scrub").setAttribute("aria-valuetext", time.toFixed(1) + "秒，共" + duration.toFixed(1) + "秒");
  }
  function seek(seconds) {
    if (!study) return;
    video.pause();
    if (video.readyState < 1) pendingSeek = seconds;
    else video.currentTime = Math.min(Math.max(seconds, 0), Math.max(video.duration - .01, 0));
    sync();
  }
  function clearCompleted() {
    study = null; studyText = ""; pendingSeek = null;
    video.pause(); video.removeAttribute("src"); video.removeAttribute("poster"); video.load();
    $("skill-film-completed").hidden = true; $("skill-film-pending").hidden = false; $("skill-film-error").hidden = true;
    $("skill-film-director").open = true;
    ["skill-film-download", "skill-film-json"].forEach((id) => { $(id).disabled = true; });
    ["skill-film-stats", "skill-film-frames", "skill-film-observed", "skill-film-deviations"].forEach((id) => $(id).replaceChildren());
  }
  function fillBrief(data) {
    $("skill-film-title").textContent = data.title + "。";
    $("skill-film-intent").textContent = data.intent.start + " → " + data.intent.event + " → " + data.intent.aftertaste + "。";
    $("skill-film-emotion").textContent = "起点：" + data.intent.start + "。结尾余味：" + data.intent.aftertaste + "。避免：" + data.intent.avoid + "。";
    $("skill-film-event").textContent = data.intent.event + "；" + data.intent.response + "。";
    $("skill-film-style").textContent = data.style.family + "：" + data.style.fixed_rules.join("；") + "。";
    $("skill-film-stages").replaceChildren(...data.planned_stages.map((stage) => {
      const li = make("li"); li.append(make("b", stage.start + "–" + stage.end + "秒 / " + stage.name), make("span", stage.observable)); return li;
    }));
    $("skill-film-inputs").replaceChildren(...data.inputs.map((input, index) => {
      const article = make("article"); const image = make("img"); image.src = root + input.file; image.alt = index === 0 ? "朱红色木椅身份参考，只约束椅型和红漆材质" : "窗边红椅的光色与材料氛围参考，不作为视频首帧"; image.width = 1122; image.height = 1402; image.loading = "lazy";
      const text = make("div"); text.append(make("h5", "参考 " + (index + 1) + " / " + (index === 0 ? "主体身份" : "光色与材料氛围")), make("p", input.role), make("p", "SHA-256 / " + input.sha256, "skill-film-hash"));
      const link = make("a", "查看参考原图 ↗"); link.href = root + input.file; link.target = "_blank"; link.rel = "noopener"; text.append(link); article.append(image, text); return article;
    }));
    $("skill-film-snapshot").replaceChildren(...data.skill_snapshot.map((file) => {
      const li = make("li"); li.append(make("b", file.file), make("code", file.sha256)); return li;
    }));
    $("skill-film-skill-name").textContent = data.skill;
    $("skill-film-prompt").textContent = prompt;
    ["skill-film-copy", "skill-film-txt", "skill-film-evidence"].forEach((id) => { $(id).disabled = false; });
  }
  function fillStudy(data, rawText) {
    study = data; studyText = rawText;
    const actual = data.actual;
    $("skill-film-pending").hidden = true; $("skill-film-completed").hidden = false;
    $("skill-film-director").open = false;
    video.src = root + actual.file; video.poster = root + data.frames[1].file; video.preload = "metadata";
    video.setAttribute("aria-label", data.title + "，本次视频模型实际生成的未经修改原片"); video.load();
    const values = [data.request.model, "图像参考生成 / " + (data.production.input_mode || "i2v"), "实际 " + actual.width + "×" + actual.height, actual.duration_seconds.toFixed(2) + "秒", actual.has_audio ? "原片含音轨" : "原片无音轨"];
    $("skill-film-stats").replaceChildren(...values.map((text) => make("span", text)));
    $("skill-film-production").textContent = "生成于" + data.date + "，一次视频模型调用，" + data.inputs.length + "张参考图。请求：" + data.request.resolution + "p / " + data.request.aspect_ratio + " / " + data.request.duration_seconds + "秒 / " + (data.request.sound ? "有声" : "无声") + "。估算" + data.request.estimated_credits + "积分，服务实际返回" + (data.actual_cost_credits ?? "未提供") + "积分。任务 " + data.task_id + "；实际媒体参数见上方。";
    $("skill-film-audio-review").textContent = data.audio_reviewed ? "已完成听觉审片，具体声音观察见下方记录。" : "本次尚未完成听觉审片；含音轨不等于已经验证声效内容与同步。";
    $("skill-film-review-method").textContent = typeof data.review_method === "string" ? data.review_method : JSON.stringify(data.review_method);
    $("skill-film-frames").replaceChildren(...data.frames.map((frame) => {
      const button = make("button", undefined, "ai-film-frame"); button.type = "button"; button.setAttribute("aria-label", "定位本次原片" + frame.seconds + "秒：" + frame.caption);
      const image = make("img"); image.src = root + frame.file; image.alt = frame.alt; image.width = actual.width; image.height = actual.height; image.loading = "lazy";
      const caption = make("span"); caption.append(make("small", "ACTUAL FRAME / " + frame.seconds.toFixed(1) + "S"), make("span", frame.caption));
      button.append(image, caption); button.addEventListener("click", () => seek(frame.seconds)); return button;
    }));
    $("skill-film-observed").replaceChildren(...data.observations.map((text) => make("li", text)));
    $("skill-film-deviations").replaceChildren(...data.deviations.map((text) => make("li", text)));
    $("skill-film-manifest").href = root + "manifest.json";
    $("skill-film-prompt-summary").textContent = "本片实际提交给视频模型的完整指令";
    ["skill-film-download", "skill-film-json"].forEach((id) => { $(id).disabled = false; });
    sync();
  }
  async function load() {
    $("skill-film-refresh").disabled = true;
    try {
      const [briefResponse, promptResponse] = await Promise.all([fetch(root + "brief.json"), fetch(root + "prompt.txt")]);
      if (!briefResponse.ok || !promptResponse.ok) throw new Error("Director records unavailable");
      const data = await briefResponse.json(); const exactPrompt = await promptResponse.text();
      if (!data.intent || !data.style || !Array.isArray(data.inputs) || !Array.isArray(data.skill_snapshot) || !Array.isArray(data.planned_stages)) throw new Error("Incomplete director records");
      brief = data; prompt = exactPrompt; clearCompleted(); fillBrief(data);
      $("skill-film-prompt-summary").textContent = "完整导演指令 / 生成记录中的准确文本";
      if (data.generated && data.status === "completed") {
        const response = await fetch(root + "study.json"); if (!response.ok) throw new Error("Completed study unavailable");
        const rawText = await response.text(); const completed = JSON.parse(rawText);
        if (!completed.generated || completed.status !== "completed" || !completed.actual || completed.actual.file !== "original.mp4" || !Number.isFinite(completed.actual.duration_seconds) || completed.actual.duration_seconds <= 0 || !Array.isArray(completed.frames) || completed.frames.length !== 3 || !Array.isArray(completed.observations) || !Array.isArray(completed.deviations)) throw new Error("No verified completed film");
        fillStudy(completed, rawText); status("实际原片、准确指令与审片记录已载入。网页播放原件，不额外制作动作或声音。");
      } else {
        $("skill-film-pending").textContent = data.status === "failed" ? "本次任务尚无已完成、已核验的原片。当前只展示导演方案与指令，未把方案当成影片。" : "本次原片尚未完成生成与核验。当前只展示Skill组织出的导演方案、参考角色和指令；完成记录载入后才显示实际播放器。";
        status("导演方案已载入；当前没有展示未经核验的成片。");
      }
      document.dispatchEvent(new Event("poster:skill-film-ready")); settleEntry();
    } catch {
      status("本次影片记录暂未能完整载入。已完成原片核验前仅显示方案，可重读生成记录。");
    } finally { $("skill-film-refresh").disabled = false; }
  }
  $("skill-film-refresh").addEventListener("click", load);
  $("skill-film-play").addEventListener("click", async () => {
    if (!study) return;
    if (!video.paused) return video.pause();
    if (video.ended) video.currentTime = 0;
    try { await video.play(); } catch { status("请使用原生视频控件播放，或下载原片查看。"); }
  });
  $("skill-film-sound").addEventListener("click", () => { video.muted = !video.muted; sync(); });
  $("skill-film-restart").addEventListener("click", () => seek(0));
  $("skill-film-scrub").addEventListener("input", (event) => seek(Number(event.target.value)));
  ["play", "pause", "ended", "seeked", "timeupdate", "volumechange"].forEach((event) => video.addEventListener(event, sync));
  video.addEventListener("loadedmetadata", () => { if (pendingSeek !== null) { const time = pendingSeek; pendingSeek = null; seek(time); } sync(); });
  video.addEventListener("error", () => { if (study) $("skill-film-error").hidden = false; });
  video.addEventListener("play", () => {
    document.querySelectorAll("video").forEach((other) => { if (other !== video) other.pause(); });
    window.dispatchEvent(new Event("poster:motion-play"));
  });
  document.querySelectorAll("video").forEach((other) => { if (other !== video) other.addEventListener("play", () => video.pause()); });
  $("skill-film-copy").addEventListener("click", async () => {
    if (!prompt) return;
    try { await navigator.clipboard.writeText(prompt); status("已复制本次记录中的准确完整指令。"); } catch { status("可以手动选择指令文本，或下载TXT。"); }
  });
  $("skill-film-txt").addEventListener("click", () => { if (prompt) download(new Blob([prompt], {type: "text/plain;charset=utf-8"}), "red-chair-film-actual-prompt.txt"); });
  $("skill-film-json").addEventListener("click", () => { if (studyText) download(new Blob([studyText], {type: "application/json;charset=utf-8"}), "red-chair-film-actual-study.json"); });
  $("skill-film-evidence").addEventListener("click", () => {
    if (!brief) return;
    const evidence = {id: brief.id, title: brief.title, skill: brief.skill, skill_snapshot: brief.skill_snapshot, inputs: brief.inputs, intent: brief.intent, style: brief.style, planned_stages: brief.planned_stages, prompt_file: brief.prompt_file, prompt_sha256: brief.prompt_sha256, generated: !!study, status: study ? "completed" : brief.status};
    download(new Blob([JSON.stringify(evidence, null, 2) + "\n"], {type: "application/json;charset=utf-8"}), "red-chair-film-skill-evidence.json");
  });
  $("skill-film-download").addEventListener("click", async () => {
    if (!study) return;
    const button = $("skill-film-download"); button.disabled = true;
    try {
      const response = await fetch(root + study.actual.file); if (!response.ok) throw new Error("Original unavailable");
      download(await response.blob(), "red-chair-film-original.mp4"); status("已准备下载未经改动的视频模型原片。");
    } catch { status("原片暂未能下载，可以刷新后重试，或使用原生视频控件保存。"); }
    finally { button.disabled = false; }
  });
  ["poster:emotion-library-ready", "poster:intent-template-ready", "poster:skill-trial-ready", "poster:chair-data-ready"].forEach((event) => document.addEventListener(event, settleEntry, {once: true}));
  window.addEventListener("load", settleEntry, {once: true}); window.addEventListener("hashchange", settleEntry);
  sync(); load();
})();
