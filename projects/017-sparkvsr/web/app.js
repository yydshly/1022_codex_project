"use strict";
const modes = {
  none: {psnr: "26.62", clip: "0.4303", dover: "0.5494", explanation: "无参考：依靠原视频和模型自身先验重建。这组数据的像素保真较高，但观感分数低于参考模式。作者主要将其作为备用与对比设置。"},
  nbp: {psnr: "23.70", clip: "0.5501", dover: "0.6902", explanation: "NBP 参考：观感与视频质量评分提高，但像素保真 PSNR 下降。精细纹理包含生成重建。"},
  pisa: {psnr: "23.43", clip: "0.6252", dover: "0.6411", explanation: "PiSA-SR 参考：这组图像观感分数更高，视频质量分数与 NBP 模式不同；像素保真仍有取舍。不能据此推出所有素材都更好。"}
};
document.querySelectorAll("[data-mode]").forEach(button => {
  button.addEventListener("click", () => {
    const mode = modes[button.dataset.mode];
    if (!mode) return;
    document.querySelectorAll("[data-mode]").forEach(item => {
      const active = item === button;
      item.setAttribute("aria-pressed", String(active));
      item.classList.toggle("active", active);
    });
    document.getElementById("psnrValue").textContent = mode.psnr;
    document.getElementById("clipValue").textContent = mode.clip;
    document.getElementById("doverValue").textContent = mode.dover;
    document.getElementById("modeExplanation").textContent = mode.explanation;
  });
});
const poster = document.getElementById("posterDialog");
document.getElementById("openPoster").addEventListener("click", () => {
  poster.showModal();
  poster.scrollTop = 0;
});
poster.addEventListener("click", event => {
  if (event.target !== poster) return;
  const r = poster.getBoundingClientRect();
  if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) poster.close();
});
