export const PAPERS = [
  {
    id: "nature-2021-li-air",
    pdf: "paper/s41586-021-03410-9 (1).pdf",
    doi: "https://doi.org/10.1038/s41586-021-03410-9",
    journal: "Nature",
    year: "2021",
    titleKey: "paper1Title",
    authorsKey: "paper1Authors",
    summaryKey: "paper1Summary",
  },
  {
    id: "jacs-2023-guest-wrench",
    pdf: "paper/enabling-high-performance-all-solid-state-batteries-via-guest-wrench-in-zeolite-strategy.pdf",
    doi: "https://doi.org/10.1021/jacs.3c07858",
    journal: "JACS",
    year: "2023",
    titleKey: "paper2Title",
    authorsKey: "paper2Authors",
    summaryKey: "paper2Summary",
  },
];

function pdfHref(path) {
  const parts = path.split("/");
  return parts.map((part, i) => (i === 0 ? part : encodeURIComponent(part))).join("/");
}

export function initPaperReader(t) {
  const modal = document.getElementById("pdf-modal");
  const frame = document.getElementById("pdf-frame");
  const titleEl = document.getElementById("pdf-modal-title");
  const metaEl = document.getElementById("pdf-modal-meta");
  const downloadEl = document.getElementById("pdf-download");
  const doiEl = document.getElementById("pdf-doi-link");
  const closeBtn = document.getElementById("pdf-close");
  const grid = document.getElementById("paper-grid");

  if (!modal || !grid) return;

  function closePdfModal() {
    modal.classList.remove("open");
    frame.removeAttribute("src");
    document.body.style.overflow = "";
  }

  function openPdfModal(paper) {
    const url = pdfHref(paper.pdf);
    titleEl.textContent = t(paper.titleKey);
    metaEl.textContent = `${t(paper.authorsKey)} · ${paper.journal} (${paper.year})`;
    frame.src = url;
    downloadEl.href = url;
    downloadEl.setAttribute("download", paper.pdf.split("/").pop());
    doiEl.href = paper.doi;
    modal.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function renderPaperCards() {
    grid.innerHTML = "";
    PAPERS.forEach((paper) => {
      const card = document.createElement("article");
      card.className = "paper-card";
      card.innerHTML = `
      <div class="paper-meta">${paper.journal} · ${paper.year}</div>
      <h3 class="paper-title" data-i18n="${paper.titleKey}"></h3>
      <p class="paper-authors" data-i18n="${paper.authorsKey}"></p>
      <p class="paper-summary" data-i18n="${paper.summaryKey}"></p>
      <div class="paper-actions">
        <button type="button" class="btn btn-primary btn-sm paper-preview-btn" data-i18n="paperPreview">Preview PDF</button>
        <a class="btn btn-outline btn-sm" href="${paper.doi}" target="_blank" rel="noopener" data-i18n="paperDoi">DOI</a>
      </div>
    `;
      card.querySelector(".paper-preview-btn").addEventListener("click", () => openPdfModal(paper));
      grid.appendChild(card);
    });
    grid.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    });
  }

  renderPaperCards();

  closeBtn.addEventListener("click", closePdfModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closePdfModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("open")) closePdfModal();
  });

  document.addEventListener("langchange", () => {
    renderPaperCards();
  });
}
