(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const video = $("emotion-film-video");
  if (!video) return;
  const root = "./assets/motion-emotions/";
  const editions = {v1: {base: root, label: "首版 V1"}, v2: {base: root + "v2/", label: "优化版 V2"}};
  let edition = "v2";
  let base = editions[edition].base;
  let allStudies = {};
  let allPrompts = {};
  const choices = Array.from(document.querySelectorAll("[data-emotion-film]"));
  const phases = Array.from(document.querySelectorAll("[data-film-phase]"));
  const status = $("emotion-film-status");
  let study = null;
  let active = "solitude";
  let prompts = {};
  let pendingSeek = null;
  let loadingVersion = 0;

  function announce() {
    if (study) window.dispatchEvent(new CustomEvent("poster:motion-state", {detail: {edition, label: editions[edition].label, base, study, active}}));
  }
  window.addEventListener("poster:motion-request", announce);
  window.addEventListener("poster:comparison-play", () => { video.pause(); $("motion-video")?.pause(); });

  function go() {
    const target = $("ai-film") || $("motion-emotions");
    history.replaceState(null, "", "#" + target.id);
    target.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
  }
  ["validation-to-motion", "motion-to-dynamic"].forEach((id) => $(id)?.addEventListener("click", go));
  const clock = (t) => "00:" + String(Math.floor(Math.max(t, 0))).padStart(2, "0");
  function sync() {
    const time = Number.isFinite(video.currentTime) ? video.currentTime : 0;
    $("emotion-film-play").textContent = video.paused ? (video.ended ? "重新播放" : "播放动态影片") : "暂停 / 看定格";
    $("emotion-film-sound").textContent = video.muted ? "声音：关闭" : "声音：开启";
    $("emotion-film-sound").setAttribute("aria-pressed", String(!video.muted));
    $("emotion-film-clock").textContent = clock(time) + " / 00:12";
    $("emotion-film-scrub").value = String(time);
    $("emotion-film-scrub").setAttribute("aria-valuetext", time.toFixed(1) + "秒，共12秒");
    const film = study?.films.find((item) => item.id === active);
    if (!film) return;
    const index = Math.min(2, Math.floor(time / 4));
    const stage = film.stages[index];
    $("emotion-film-stage-name").textContent = `${stage.start}–${stage.end}秒 / ${stage.name}`;
    $("emotion-film-stage-detail").textContent = stage.detail;
    phases.forEach((button, i) => button.setAttribute("aria-pressed", String(index === i)));
  }
  function seek(time) {
    video.pause();
    if (video.readyState < 1) {
      pendingSeek = time;
    } else {
      video.currentTime = Math.min(time, Math.max(video.duration - .01, 0));
    }
    sync();
  }
  function select(id, keepTime = false) {
    const film = study?.films.find((item) => item.id === id);
    if (!film) return;
    const time = keepTime && Number.isFinite(video.currentTime) ? Math.min(video.currentTime, 11.95) : null;
    video.pause();
    active = id;
    pendingSeek = time;
    video.poster = base + id + "-poster.jpg";
    video.src = base + id + ".mp4";
    video.setAttribute("aria-label", film.title + "，12秒动态影片，含原创合成声音");
    video.load();
    choices.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.emotionFilm === id)));
    choices.forEach((button) => { button.querySelector("img").src = base + button.dataset.emotionFilm + "-poster.jpg"; });
    $("emotion-film-name").textContent = film.title;
    $("emotion-film-arc").textContent = film.arc;
    $("emotion-film-code").textContent = film.label;
    ["goal", "action", "camera", "weather", "sound", "signal", "check", "avoid"].forEach((field) => {
      $("emotion-film-" + (field === "sound" ? "sound-plan" : field)).textContent = film[field];
    });
    phases.forEach((button, i) => {
      const stage = film.stages[i];
      button.querySelector("span").textContent = `${stage.start}–${stage.end}S`;
      button.querySelector("b").textContent = stage.name;
    });
    $("emotion-film-prompt").textContent = prompts[id] || "指令载入中……";
    status.textContent = "已选择「" + editions[edition].label + " / " + film.title + "」。" + (keepTime ? "已保留对照时刻并暂停。" : "点击播放，再打开声音比较听觉的作用。");
    $("emotion-film-error").hidden = true;
    sync();
    announce();
  }
  document.querySelectorAll("[data-film-edition]").forEach((button) => button.addEventListener("click", () => {
    const value = button.dataset.filmEdition;
    if (!allStudies[value] || edition === value) return;
    edition = value;
    base = editions[value].base;
    study = allStudies[value];
    prompts = allPrompts[value];
    document.querySelectorAll("[data-film-edition]").forEach((item) => item.setAttribute("aria-pressed", String(item.dataset.filmEdition === value)));
    choices.forEach((item) => { item.querySelector("img").src = base + item.dataset.emotionFilm + "-poster.jpg"; });
    $("emotion-film-edition-note").textContent = value === "v2" ? "V2：放大人物、对齐步态、平滑停步，补充接地和随行走变化的脚步声。" : "V1：保留首轮实际成片。切换版本会保留同一时刻，方便看修改改变了什么。";
    select(active, true);
  }));
  choices.forEach((button) => button.addEventListener("click", () => select(button.dataset.emotionFilm)));
  phases.forEach((button) => button.addEventListener("click", () => seek(Number(button.dataset.filmPhase) * 4)));
  $("emotion-film-scrub").addEventListener("input", (event) => seek(Number(event.target.value)));
  $("emotion-film-play").addEventListener("click", async () => {
    if (!video.paused) return video.pause();
    if (video.ended) video.currentTime = 0;
    // Keep the previous concept film from playing its sound at the same time.
    $("motion-video")?.pause();
    try {
      await video.play();
      $("emotion-film-error").hidden = true;
    } catch {
      $("emotion-film-error").textContent = "播放未能开始，请使用影片的原生播放按钮，或下载MP4查看。";
      $("emotion-film-error").hidden = false;
    }
  });
  $("emotion-film-restart").addEventListener("click", () => seek(0));
  $("emotion-film-sound").addEventListener("click", () => { video.muted = !video.muted; });
  video.addEventListener("loadedmetadata", () => {
    if (pendingSeek !== null) {
      video.currentTime = pendingSeek;
      pendingSeek = null;
    }
    sync();
  });
  ["timeupdate", "play", "pause", "ended", "seeked", "volumechange"].forEach((event) => video.addEventListener(event, sync));
  video.addEventListener("play", () => { $("motion-video")?.pause(); window.dispatchEvent(new Event("poster:motion-play")); });
  video.addEventListener("error", () => {
    $("emotion-film-error").textContent = "影片暂时未能载入，请刷新或下载MP4。导演方案仍可阅读。";
    $("emotion-film-error").hidden = false;
  });
  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  $("emotion-film-download").addEventListener("click", async () => {
    const button = $("emotion-film-download");
    const id = active;
    const selectedEdition = edition;
    const selectedBase = base;
    button.disabled = true;
    try {
      const response = await fetch(selectedBase + id + ".mp4");
      if (!response.ok) throw new Error("Unavailable film");
      download(await response.blob(), "rain-shelter-" + selectedEdition + "-" + id + ".mp4");
      status.textContent = "已准备下载「" + id + "」12秒有声MP4。";
    } catch {
      status.textContent = "下载暂时失败，请刷新重试，或使用原生视频控件保存。";
    } finally { button.disabled = false; }
  });
  $("emotion-film-copy").addEventListener("click", async () => {
    if (!prompts[active]) return;
    try {
      await navigator.clipboard.writeText(prompts[active]);
      status.textContent = "已复制对应的视频导演指令；这是后续模型输入草案，本片没有执行视频模型。";
    } catch {
      status.textContent = "无法自动复制，可选择指令文本，或下载TXT。";
    }
  });
  $("emotion-film-txt").addEventListener("click", () => {
    if (!prompts[active]) return;
    download(new Blob([prompts[active]], {type: "text/plain;charset=utf-8"}), edition + "-" + active + "-video-direction.txt");
    status.textContent = "已准备下载对应导演指令。";
  });
  $("emotion-film-json").addEventListener("click", () => {
    if (!study) return;
    download(new Blob([JSON.stringify(study, null, 2) + "\n"], {type: "application/json;charset=utf-8"}), "rain-shelter-" + edition + "-motion-study.json");
    status.textContent = "已准备下载三段影片的完整情绪与分镜方案。";
  });
  async function load() {
    const version = ++loadingVersion;
    try {
      const loaded = await Promise.all(Object.entries(editions).map(async ([id, info]) => {
        const response = await fetch(info.base + "study.json");
        if (!response.ok) throw new Error("Unavailable study");
        const data = await response.json();
        const entries = await Promise.all(data.films.map(async (film) => {
          const result = await fetch(info.base + film.id + "-video-direction.txt");
          if (!result.ok) throw new Error("Unavailable prompt");
          return [film.id, await result.text()];
        }));
        return [id, data, Object.fromEntries(entries)];
      }));
      if (version !== loadingVersion) return;
      allStudies = Object.fromEntries(loaded.map(([id, data]) => [id, data]));
      allPrompts = Object.fromEntries(loaded.map(([id, , text]) => [id, text]));
      study = allStudies[edition];
      prompts = allPrompts[edition];
      document.querySelectorAll("[data-film-edition]").forEach((button) => { button.disabled = false; });
      choices.forEach((button) => { button.disabled = false; });
      ["emotion-film-copy", "emotion-film-txt", "emotion-film-json"].forEach((id) => { $(id).disabled = false; });
      select(active);
    } catch {
      status.textContent = "导演方案暂时无法载入。默认影片仍可使用原生控件播放。";
    }
  }
  sync();
  load();
})();
