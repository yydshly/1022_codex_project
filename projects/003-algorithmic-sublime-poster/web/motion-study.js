(() => {
  "use strict";
  const video = document.getElementById("motion-video");
  if (!video) return;
  const $ = (id) => document.getElementById(id);
  const buttons = Array.from(document.querySelectorAll("[data-motion-shot]"));
  const scrub = $("motion-scrub");
  const status = $("motion-status");
  let brief = null;
  let prompt = "";
  let activeShot = -1;
  let pendingSeek = null;

  function go(id) {
    const target = $(id);
    if (!target) return;
    history.replaceState(null, "", "#" + id);
    target.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start" });
  }
  $("emotion-to-works").addEventListener("click", () => go("creative-works"));
  $("creative-to-motion").addEventListener("click", () => go($("skill-film") ? "skill-film" : $("ai-film") ? "ai-film" : "motion-demo"));
  document.querySelector(".nav-motion").addEventListener("click", (event) => {
    event.preventDefault();
    go(event.currentTarget.getAttribute("href").slice(1));
  });
  function clock(value) {
    return "00:" + String(Math.floor(Math.max(0, value))).padStart(2, "0");
  }
  function sync() {
    const duration = Number.isFinite(video.duration) ? video.duration : 15;
    const time = Number.isFinite(video.currentTime) ? video.currentTime : 0;
    $("motion-time").textContent = clock(time) + " / " + clock(duration);
    scrub.value = String(time);
    scrub.setAttribute("aria-valuetext", time.toFixed(1) + "秒，共" + duration.toFixed(0) + "秒");
    $("motion-play").textContent = video.paused ? (video.ended ? "重新播放" : "播放概念片") : "暂停";
    $("motion-sound").textContent = video.muted ? "声音：关闭" : "声音：开启";
    $("motion-sound").setAttribute("aria-pressed", String(!video.muted));
    const x = 20 + Math.min(time / duration, 1) * 660;
    $("motion-arc-cursor").setAttribute("x1", String(x));
    $("motion-arc-cursor").setAttribute("x2", String(x));
    if (!brief) return;
    const index = Math.min(brief.shots.length - 1, brief.shots.findIndex((shot) => time < shot.end) < 0 ?
      brief.shots.length - 1 : brief.shots.findIndex((shot) => time < shot.end));
    if (index === activeShot) return;
    activeShot = index;
    const shot = brief.shots[index];
    $("motion-stage-time").textContent = String(shot.start).padStart(2, "0") + "–" + String(shot.end).padStart(2, "0") + "S / 当前阶段";
    $("motion-stage-title").textContent = shot.title;
    $("motion-stage-goal").textContent = shot.goal;
    $("motion-stage-camera").textContent = shot.camera;
    $("motion-stage-visual").textContent = shot.visual;
    $("motion-stage-sound").textContent = shot.sound;
    buttons.forEach((button, number) => button.setAttribute("aria-pressed", String(number === index)));
  }
  function seek(time) {
    video.pause();
    if (video.readyState < 1) {
      pendingSeek = time;
      video.load();
    } else {
      video.currentTime = Math.min(Math.max(time, 0), video.duration);
    }
    sync();
  }
  $("motion-play").addEventListener("click", async () => {
    if (!video.paused) {
      video.pause();
      return;
    }
    if (video.ended) video.currentTime = 0;
    try {
      await video.play();
      $("motion-error").hidden = true;
    } catch {
      $("motion-error").textContent = "暂时无法播放。可以使用影片下方的原生播放控件，或下载 MP4 在本地查看。";
      $("motion-error").hidden = false;
    }
  });
  $("motion-restart").addEventListener("click", () => seek(0));
  $("motion-sound").addEventListener("click", () => { video.muted = !video.muted; });
  scrub.addEventListener("input", () => seek(Number(scrub.value)));
  buttons.forEach((button) => button.addEventListener("click", () => {
    if (brief) seek(brief.shots[Number(button.dataset.motionShot)].seek);
  }));
  ["timeupdate", "seeked", "play", "pause", "ended", "volumechange"].forEach((event) => video.addEventListener(event, sync));
  video.addEventListener("loadedmetadata", () => {
    if (pendingSeek !== null) {
      video.currentTime = Math.min(pendingSeek, video.duration);
      pendingSeek = null;
    }
    sync();
  });
  video.addEventListener("error", () => {
    $("motion-error").textContent = "影片未能载入。请刷新后重试，或下载 MP4 查看。分镜与创作指令仍可单独阅读。";
    $("motion-error").hidden = false;
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
  function textFile(text, filename, type) {
    download(new Blob([text], { type: type || "text/plain;charset=utf-8" }), filename);
    status.textContent = "已准备下载：" + filename;
  }
  $("motion-copy").addEventListener("click", async () => {
    if (!prompt) return;
    try {
      await navigator.clipboard.writeText(prompt);
      status.textContent = "已复制：艺术总纲、三段分镜、固定规则与返修要求。";
    } catch {
      status.textContent = "浏览器未允许复制。可选中上方指令手动复制，或下载 TXT。";
    }
  });
  $("motion-txt").addEventListener("click", () => {
    if (prompt) textFile(prompt + "\n", "night-signal-motion-prompt.txt");
  });
  $("motion-json").addEventListener("click", () => {
    if (brief) textFile(JSON.stringify(brief, null, 2) + "\n", "night-signal-storyboard.json", "application/json;charset=utf-8");
  });
  $("motion-download").addEventListener("click", async () => {
    const button = $("motion-download");
    button.disabled = true;
    status.textContent = "正在准备影片下载……";
    try {
      const response = await fetch("./assets/motion/night-signal.mp4");
      if (!response.ok) throw new Error("Film unavailable");
      download(await response.blob(), "night-signal.mp4");
      status.textContent = "已准备下载：夜香 · 15秒 MP4，含原创合成声音。";
    } catch {
      status.textContent = "暂时无法下载。请确认网页连接后重试，也可使用原生视频控件保存影片。";
    } finally {
      button.disabled = false;
    }
  });
  async function load() {
    try {
      const response = await fetch("./assets/motion/night-signal-brief.json");
      if (!response.ok) throw new Error("Brief unavailable");
      brief = await response.json();
      const lines = [
        "作品：" + brief.title,
        "交付：15秒，16:9，24fps。用途与观众：" + brief.intent.audience,
        "",
        "【艺术意图】",
        "主情绪：" + brief.intent.primary + "；副情绪：" + brief.intent.secondary + "。",
        "情绪走向：" + brief.intent.start + " → " + brief.intent.turn + " → " + brief.intent.end,
        "避免：" + brief.intent.avoid.join("；") + "。",
        "主体：" + brief.subject,
        "",
        "【跨镜头固定规则】"
      ];
      brief.locked_style.forEach((rule, index) => lines.push((index + 1) + ". " + rule));
      brief.shots.forEach((shot) => {
        lines.push("", "【" + shot.start + "–" + shot.end + "秒 / " + shot.title + "】",
          "目标感受：" + shot.goal, "镜头：" + shot.camera, "光色与计算转化：" + shot.visual,
          "声音：" + shot.sound, "逐镜生成要求：" + shot.prompt, "检查：" + shot.check);
      });
      lines.push("", "【评审与返修】");
      brief.review.forEach((rule, index) => lines.push((index + 1) + ". " + rule));
      lines.push("", "【当前示例的制作记录】", brief.production.method, brief.production.limitations,
        "上面的逐镜要求也可用于后续视频模型或拍摄；本示例没有调用视频生成模型。");
      prompt = lines.join("\n");
      $("motion-prompt").textContent = prompt;
      ["motion-copy", "motion-txt", "motion-json"].forEach((id) => { $(id).disabled = false; });
      sync();
    } catch {
      $("motion-prompt").textContent = "分镜档案暂时无法载入，请刷新后重试。影片与三个阶段的实际画面仍可查看。";
      status.textContent = "分镜档案载入失败。";
    }
  }
  load();
  sync();
})();
