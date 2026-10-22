"use strict";

// Finished model-generated artwork is deliberately separate from the Canvas studies.
(() => {
  const tabs = [...document.querySelectorAll("[data-art-tab]")];
  if (!tabs.length) return;
  const panels = [...document.querySelectorAll("[data-art-panel]")];
  const dialog = document.querySelector("#art-dialog");
  const dialogImage = document.querySelector("#art-dialog-image");
  const names = {bloom: "风有形", whale: "向蓝而生"};

  function select(tab, focus = false) {
    for (const item of tabs) {
      const active = item === tab;
      item.setAttribute("aria-selected", String(active));
      item.tabIndex = active ? 0 : -1;
    }
    for (const panel of panels) panel.hidden = panel.dataset.artPanel !== tab.dataset.artTab;
    if (focus) tab.focus();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => select(tab));
    tab.addEventListener("keydown", event => {
      let next;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = tabs.length - 1;
      else return;
      event.preventDefault();
      select(tabs[next], true);
    });
  });

  document.querySelectorAll("[data-art-open]").forEach(button => {
    button.addEventListener("click", () => {
      const id = button.dataset.artOpen;
      const image = document.querySelector(`[data-art-panel="${id}"] img`);
      dialogImage.src = image.getAttribute("src");
      dialogImage.alt = image.alt;
      document.querySelector("#art-dialog-title").textContent = `${names[id]} · 完整海报`;
      dialog.showModal();
      dialog.scrollTop = 0;
    });
  });
  document.querySelector("#art-dialog-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });

  // Preserve direct links shared before the finished-art gallery was added.
  function revealAlgorithmLink() {
    const targetId = location.hash.slice(1);
    if (!targetId.startsWith("extension-") && targetId !== "algorithm-details") return;
    const target = document.getElementById(targetId);
    if (!target || !document.querySelector("#algorithm-details").contains(target)) return;
    document.querySelector("#algorithm-details").open = true;
    if (target.closest("#extension-atlas")) document.querySelector("#extension-atlas").open = true;
    requestAnimationFrame(() => target.scrollIntoView({behavior: "instant", block: "start"}));
  }
  window.addEventListener("hashchange", revealAlgorithmLink);
  revealAlgorithmLink();
})();
