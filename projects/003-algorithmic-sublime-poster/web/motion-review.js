(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const panel = $("motion-compare");
  if (!panel) return;
  const players = Array.from(panel.querySelectorAll("[data-compare-film]"));
  const master = players[0];
  const main = $("emotion-film-video");
  const records = new Map();
  const fields = {impression: "motion-review-impression", focus: "motion-review-focus", atSeconds: "motion-review-time", problem: "motion-review-problem", target: "motion-review-target"};
  const focusLabels = {action: "人物行动与关系", camera: "镜头与空间", timing: "事件出现与停留时间", sound: "声音与节奏", signal: "计算隐喻与特效"};
  let current = null;
  let sourceEdition = null;
  let comparisonTime = 0;
  let sourcesLoading = false;
  let pendingMetadata = new Set();
  let playRequest = 0;
  let repair = "";
  let pendingAnchor = ["#motion-compare", "#motion-review"].includes(location.hash) ? location.hash.slice(1) : null;
  const clock = (time) => "00:" + String(Math.floor(Math.max(0, time))).padStart(2, "0");
  function openSection(id) {
    const section = $(id);
    section.open = true;
    history.replaceState(null, "", "#" + id);
    section.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start"});
  }
  $("motion-compare-open").addEventListener("click", () => openSection("motion-compare"));
  $("motion-review-open").addEventListener("click", () => openSection("motion-review"));

  function pauseComparison() {
    playRequest++;
    players.forEach((video) => { video.pause(); video.playbackRate = 1; });
    if (sourceEdition) $("motion-compare-status").textContent = master.ended || master.currentTime >= 11.98 ? "三片已到结尾，可以回到开头重播。" : "三片已暂停，可以比较当前定格。";
    renderClock();
  }
  function renderClock() {
    const time = Number.isFinite(master.currentTime) && sourceEdition && !sourcesLoading ? master.currentTime : comparisonTime;
    $("motion-compare-clock").textContent = clock(time) + " / 00:12";
    $("motion-compare-scrub").value = String(time);
    $("motion-compare-scrub").setAttribute("aria-valuetext", time.toFixed(1) + "秒，共12秒");
    $("motion-compare-play").textContent = master.paused ? (time >= 11.98 ? "重新同步播放" : "同步播放三片") : "暂停三片 / 比较定格";
  }
  function audio() {
    const id = $("motion-compare-audio").value;
    players.forEach((video) => { video.muted = id !== video.dataset.compareFilm; });
  }
  function ensureSources() {
    if (!current || !panel.open || sourceEdition === current.edition) return;
    pauseComparison();
    sourceEdition = current.edition;
    sourcesLoading = true;
    pendingMetadata = new Set(players);
    players.forEach((video) => {
      const id = video.dataset.compareFilm;
      video.preload = "metadata";
      video.src = current.base + id + ".mp4";
      video.poster = current.base + id + "-poster.jpg";
      video.load();
    });
    audio();
    $("motion-compare-play").disabled = false;
    $("motion-compare-status").textContent = "当前为" + current.label + "。三片将定位到同一时刻。";
  }
  panel.addEventListener("toggle", () => { if (panel.open) ensureSources(); else pauseComparison(); });
  players.forEach((video) => {
    video.addEventListener("loadedmetadata", () => {
      video.currentTime = Math.min(comparisonTime, 11.95);
      pendingMetadata.delete(video);
      sourcesLoading = pendingMetadata.size > 0;
      renderClock();
    });
    video.addEventListener("error", () => {
      pauseComparison();
      $("motion-compare-status").textContent = "有影片未能载入，请使用上方单片播放或下载原片。";
    });
  });
  master.addEventListener("timeupdate", () => {
    if (sourcesLoading) return;
    comparisonTime = master.currentTime;
    if (!master.paused && !master.seeking) {
      players.slice(1).forEach((video) => {
        if (video.readyState < 2 || video.seeking) return;
        const delta = video.currentTime - master.currentTime;
        if (Math.abs(delta) > .12) video.currentTime = master.currentTime;
        video.playbackRate = Math.abs(delta) > .04 ? (delta > 0 ? .98 : 1.02) : 1;
      });
    }
    renderClock();
  });
  master.addEventListener("ended", pauseComparison);
  ["play", "pause", "seeked"].forEach((event) => master.addEventListener(event, renderClock));
  window.addEventListener("poster:motion-play", pauseComparison);
  $("motion-video")?.addEventListener("play", () => { pauseComparison(); main.pause(); });
  $("motion-compare-play").addEventListener("click", async () => {
    ensureSources();
    if (!sourceEdition) return;
    if (!master.paused) return pauseComparison();
    if (master.ended || comparisonTime >= 11.98) {
      comparisonTime = 0;
      players.forEach((video) => { video.currentTime = 0; });
    }
    window.dispatchEvent(new Event("poster:comparison-play"));
    const request = ++playRequest;
    $("motion-compare-status").textContent = "正在开始同步播放……";
    const results = await Promise.allSettled(players.map((video) => video.play()));
    if (request !== playRequest) return;
    if (results.some((result) => result.status === "rejected")) {
      pauseComparison();
      $("motion-compare-status").textContent = "同步播放未能开始，请重新点击，或使用上方单片播放器。";
    } else {
      $("motion-compare-status").textContent = "三片正在近似同步播放；声音只来自所选的一片。";
    }
    renderClock();
  });
  function seek(time) {
    pauseComparison();
    comparisonTime = time;
    ensureSources();
    players.forEach((video) => { if (video.readyState >= 1) video.currentTime = time; });
    renderClock();
  }
  $("motion-compare-restart").addEventListener("click", () => seek(0));
  $("motion-compare-scrub").addEventListener("input", (event) => seek(Number(event.target.value)));
  $("motion-compare-audio").addEventListener("change", audio);

  function key() { return current ? current.edition + ":" + current.active : ""; }
  function film() { return current?.study.films.find((entry) => entry.id === current.active); }
  function renderReview() {
    if (!current) return;
    const record = records.get(key());
    Object.entries(fields).forEach(([field, id]) => {
      $(id).value = String(record?.[field] ?? (field === "focus" ? "action" : field === "atSeconds" ? 0 : ""));
    });
    $("motion-review-context").textContent = current.label + " / " + film().title + " · 切换单片或版本可分别记录。";
    buildRepair();
  }
  function buildRepair() {
    const record = records.get(key());
    repair = "";
    if (record?.problem.trim() && record?.target.trim()) {
      const entry = film();
      repair = ["【针对性返修草案 / 尚未执行】", "素材：" + current.label + " / " + entry.title,
        "艺术意图：" + entry.goal, "情绪走向：" + entry.arc,
        "定位：约" + record.atSeconds.toFixed(1) + "秒，重点只改「" + focusLabels[record.focus] + "」。",
        "个人实际感受：" + (record.impression || "未填写"), "这一刻的偏差：" + record.problem.trim(),
        "希望的具体变化：" + record.target.trim(),
        "保持：12秒画幅、场景、人物辨识、基础色调、稀疏计算关系，以及未涉及的导演要求。",
        "修改时先处理上述问题，不用增加特效密度代替情绪。保留前后画面，按同一时刻比较。",
        "审片检查：" + entry.check,
        "这是已知目标的个人复盘，不能作为独立情绪评价。网页只整理返修要求，没有调用模型或生成新视频。"].join("\n");
    }
    $("motion-review-prompt").textContent = repair || "写清偏差与期望变化后，这里生成针对当前版本的返修指令。";
    $("motion-review-copy").disabled = !repair;
    $("motion-review-txt").disabled = !repair;
    $("motion-review-count").textContent = records.size + "份记录";
  }
  function saveReview() {
    if (!current) return;
    const value = Object.fromEntries(Object.entries(fields).map(([field, id]) => [field, $(id).value]));
    const seconds = Number(value.atSeconds);
    if (!Number.isFinite(seconds) || seconds < 0 || seconds > 12) {
      repair = "";
      $("motion-review-copy").disabled = true;
      $("motion-review-txt").disabled = true;
      $("motion-review-prompt").textContent = "先将偏差时刻设为0到12秒，再生成返修草案。";
      $("motion-review-status").textContent = "请填写0到12之间的秒数。";
      return;
    }
    const record = {edition: current.edition, filmId: current.active, ...value, atSeconds: seconds,
      intentVisible: true, soundEnabledAtEdit: !main.muted, noteType: "personal-review", generated: false};
    if (record.impression || record.problem.trim() || record.target.trim()) records.set(key(), record);
    else records.delete(key());
    buildRepair();
    $("motion-review-status").textContent = "当前页已更新这份个人复盘，未上传。";
  }
  Object.values(fields).forEach((id) => $(id).addEventListener("input", saveReview));
  $("motion-review-capture").addEventListener("click", () => {
    $("motion-review-time").value = (Number.isFinite(main.currentTime) ? main.currentTime : 0).toFixed(1);
    saveReview();
  });
  function download(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a"); link.href = url; link.download = filename;
    document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  }
  $("motion-review-copy").addEventListener("click", async () => {
    if (!repair) return;
    try { await navigator.clipboard.writeText(repair); $("motion-review-status").textContent = "已复制针对当前版本的返修草案。"; }
    catch { $("motion-review-status").textContent = "无法自动复制，可以下载TXT或手动选择文本。"; }
  });
  $("motion-review-txt").addEventListener("click", () => {
    if (repair) download(new Blob([repair + "\n"], {type: "text/plain;charset=utf-8"}), "motion-repair-" + current.edition + "-" + current.active + ".txt");
  });
  $("motion-review-export").addEventListener("click", () => {
    const entries = Array.from(records.values());
    const data = {version: 1, kind: "personal-motion-review", independentBlindStudy: false,
      modelCalled: false, generatedAt: new Date().toISOString(), records: entries,
      currentRepairDraft: repair || null, limitation: "已知作者目标的个人记录；没有情绪成功率或模型评测意义。"};
    download(new Blob([JSON.stringify(data, null, 2) + "\n"], {type: "application/json;charset=utf-8"}), "my-motion-reviews.json");
    $("motion-review-status").textContent = "已准备下载" + entries.length + "份个人复盘与当前返修草案。";
  });
  window.addEventListener("poster:motion-state", (event) => {
    const next = event.detail;
    const changed = !current || current.edition !== next.edition || current.active !== next.active;
    if (current && current.edition !== next.edition) {
      comparisonTime = Number.isFinite(master.currentTime) ? master.currentTime : comparisonTime;
      pauseComparison();
    }
    current = next;
    $("motion-compare-version").textContent = current.label + " / 同一时刻，三种导演方案";
    ensureSources();
    if (changed) renderReview();
    if (pendingAnchor) {
      const id = pendingAnchor;
      pendingAnchor = null;
      requestAnimationFrame(() => openSection(id));
    }
  });
  window.dispatchEvent(new Event("poster:motion-request"));
})();
