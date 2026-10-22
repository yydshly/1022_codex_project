(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const section = $("ai-film");
  if (!section) return;
  const video = $("ai-film-video");
  let study = null;
  let prompt = "";
  let pendingSeek = null;
  const root = "./assets/ai-film/";
  const clock = (t) => "00:" + String(Math.floor(Math.max(t, 0))).padStart(2, "0");
  function sync() {
    const time = Number.isFinite(video.currentTime) ? video.currentTime : 0;
    const duration = Number.isFinite(video.duration) ? video.duration : (study?.actual.duration_seconds || 10);
    $("ai-film-clock").textContent = clock(time) + " / " + clock(duration);
    $("ai-film-play").textContent = video.paused ? (video.ended ? "重新播放原片" : "播放AI原片") : "暂停 / 查看这一帧";
    $("ai-film-sound").textContent = video.muted ? "声音：关闭" : "声音：开启";
    $("ai-film-sound").setAttribute("aria-pressed", String(!video.muted));
    $("ai-film-scrub").max = String(Math.max(duration - .01, 0));
    $("ai-film-scrub").value = String(time);
    $("ai-film-scrub").setAttribute("aria-valuetext", time.toFixed(1) + "秒，共" + duration.toFixed(1) + "秒");
  }
  function seek(time) {
    video.pause();
    if (video.readyState < 1) pendingSeek = time;
    else video.currentTime = Math.min(time, Math.max(video.duration - .01, 0));
    sync();
  }
  function go() {
    history.replaceState(null, "", "#ai-film");
    section.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
  }
  function settleEntry() {
    if (location.hash === "#ai-film") requestAnimationFrame(() => section.scrollIntoView({behavior: "instant", block: "start"}));
  }
  document.addEventListener("poster:emotion-library-ready", settleEntry, {once: true});
  document.addEventListener("poster:intent-template-ready", settleEntry, {once: true});
  document.addEventListener("poster:skill-trial-ready", settleEntry, {once: true});
  document.addEventListener("poster:chair-data-ready", settleEntry, {once: true});
  window.addEventListener("load", settleEntry, {once: true});
  function revealHistoric(id) {
    const target = $(id);
    if (!target) return;
    let parent = target;
    while (parent && parent !== document.body) {
      if (parent.tagName === "DETAILS") parent.open = true;
      parent = parent.parentElement;
    }
    target.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
  }
  document.querySelectorAll('.ai-film-history a[href^="#motion-"]').forEach((link) => link.addEventListener("click", (event) => {
    event.preventDefault();
    history.replaceState(null, "", link.getAttribute("href"));
    revealHistoric(location.hash.slice(1));
  }));
  if (location.hash.startsWith("#motion-")) revealHistoric(location.hash.slice(1));
  window.addEventListener("hashchange", () => { if (location.hash.startsWith("#motion-")) revealHistoric(location.hash.slice(1)); });
  document.querySelectorAll("[data-open-ai-film]").forEach((item) => item.addEventListener("click", (event) => { event.preventDefault(); go(); }));
  $("ai-film-play").addEventListener("click", async () => {
    if (!video.paused) return video.pause();
    if (video.ended) video.currentTime = 0;
    try { await video.play(); }
    catch { $("ai-film-status").textContent = "请使用影片原生播放按钮，或下载原片查看。"; }
  });
  video.addEventListener("play", () => {
    window.dispatchEvent(new Event("poster:motion-play"));
    ["motion-video", "emotion-film-video", "motion-compare-solitude", "motion-compare-unease", "motion-compare-hope"].forEach((id) => $(id)?.pause());
  });
  ["motion-video", "emotion-film-video", "motion-compare-solitude", "motion-compare-unease", "motion-compare-hope"].forEach((id) => {
    $(id)?.addEventListener("play", () => video.pause());
  });
  $("ai-film-sound").addEventListener("click", () => { video.muted = !video.muted; });
  $("ai-film-restart").addEventListener("click", () => seek(0));
  $("ai-film-scrub").addEventListener("input", (event) => seek(Number(event.target.value)));
  ["play", "pause", "ended", "seeked", "timeupdate", "volumechange"].forEach((event) => video.addEventListener(event, sync));
  video.addEventListener("loadedmetadata", () => {
    if (pendingSeek !== null) { video.currentTime = pendingSeek; pendingSeek = null; }
    sync();
  });
  video.addEventListener("error", () => { $("ai-film-error").hidden = false; });
  function download(blob, name) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a"); link.href = url; link.download = name;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  $("ai-film-copy").addEventListener("click", async () => {
    if (!prompt) return;
    try { await navigator.clipboard.writeText(prompt); $("ai-film-status").textContent = "已复制本片实际提交的视频生成指令。"; }
    catch { $("ai-film-status").textContent = "可以下载TXT或手动选择指令文本。"; }
  });
  $("ai-film-txt").addEventListener("click", () => {
    if (prompt) download(new Blob([prompt], {type: "text/plain;charset=utf-8"}), "shared-space-actual-prompt.txt");
  });
  $("ai-film-json").addEventListener("click", () => {
    if (study) download(new Blob([JSON.stringify(study, null, 2) + "\n"], {type: "application/json;charset=utf-8"}), "shared-space-actual-study.json");
  });
  $("ai-film-download").addEventListener("click", async () => {
    if (!study) return;
    const button = $("ai-film-download"); button.disabled = true;
    try {
      const response = await fetch(root + study.actual.file);
      if (!response.ok) throw new Error("Film unavailable");
      download(await response.blob(), "shared-space-ai-original.mp4");
      $("ai-film-status").textContent = "已准备下载未经动画合成或额外配音的模型原片。";
    } catch { $("ai-film-status").textContent = "原片下载暂时失败，请刷新或使用原生视频控件保存。"; }
    finally { button.disabled = false; }
  });
  async function load() {
    try {
      const [dataResponse, promptResponse] = await Promise.all([fetch(root + "study.json"), fetch(root + "shared-space-prompt.txt")]);
      if (!dataResponse.ok || !promptResponse.ok) throw new Error("Unavailable source");
      const data = await dataResponse.json();
      if (!data.generated || data.status !== "completed" || !data.actual?.file) throw new Error("No completed video");
      study = data;
      prompt = await promptResponse.text();
      $("ai-film-prompt").textContent = prompt;
      const stats = $("ai-film-stats");
      const values = [data.request.model, "实际 " + data.actual.width + "×" + data.actual.height,
        data.actual.duration_seconds.toFixed(2) + "秒", data.actual.has_audio ? "原片含音轨" : "原片无音轨", "视频模型实际生成"];
      values.forEach((text) => { const span = document.createElement("span"); span.textContent = text; stats.append(span); });
      $("ai-film-production").textContent = "生成于" + data.date + "，一次文字生成视频。请求：1080p / 16:9 / 10秒 / 有声；实际尺寸与时长见上方。生成前估算" + data.request.estimated_credits + "积分，服务返回实际" + (data.actual_cost_credits ?? "未提供") + "积分，原样记录差异。";
      data.frames.forEach((frame) => {
        const button = document.createElement("button"); button.type = "button"; button.className = "ai-film-frame";
        button.setAttribute("aria-label", "定位实际影片" + frame.seconds + "秒：" + frame.caption);
        const img = document.createElement("img"); img.src = root + frame.file; img.alt = frame.alt; img.width = data.actual.width; img.height = data.actual.height; img.loading = "lazy";
        const caption = document.createElement("span"); const small = document.createElement("small"); small.textContent = "ACTUAL FRAME / " + frame.seconds.toFixed(1) + "S";
        const label = document.createElement("span"); label.textContent = frame.caption;
        caption.append(small, label); button.append(img, caption); button.addEventListener("click", () => seek(frame.seconds)); $("ai-film-frames").append(button);
      });
      [["ai-film-observed", data.observations], ["ai-film-deviations", data.deviations]].forEach(([id, rows]) => rows.forEach((value) => {
        const li = document.createElement("li"); li.textContent = value; $(id).append(li);
      }));
      ["ai-film-copy", "ai-film-txt", "ai-film-json", "ai-film-download"].forEach((id) => { $(id).disabled = false; });
      sync(); settleEntry();
    } catch {
      $("ai-film-status").textContent = "成片记录暂时未能载入，请刷新。实际影片仍可通过原生控件播放。";
    }
  }
  sync(); load();
})();
