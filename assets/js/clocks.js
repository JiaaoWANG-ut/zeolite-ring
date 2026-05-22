const CLOCKS = [
  { id: "beijing", tz: "Asia/Shanghai", labelKey: "clockBeijing" },
  { id: "austin", tz: "America/Chicago", labelKey: "clockAustin" },
  { id: "sf", tz: "America/Los_Angeles", labelKey: "clockSF" },
];

function clockLocale(lang) {
  return lang === "zh" ? "zh-CN" : "en-US";
}

function formatTime(date, tz, locale) {
  return new Intl.DateTimeFormat(locale, {
    timeZone: tz,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(date);
}

function formatDate(date, tz, locale) {
  return new Intl.DateTimeFormat(locale, {
    timeZone: tz,
    month: "short",
    day: "numeric",
    weekday: "short",
  }).format(date);
}

export function initClocks(t, getLang) {
  const root = document.getElementById("footer-clocks");
  if (!root) return;

  root.innerHTML = CLOCKS.map(
    (c) => `
    <div class="clock-item" data-clock="${c.id}">
      <span class="clock-label" data-i18n="${c.labelKey}"></span>
      <span class="clock-time" id="clock-time-${c.id}">--:--:--</span>
      <span class="clock-date" id="clock-date-${c.id}"></span>
    </div>`
  ).join("");

  function applyLabels() {
    root.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (key) el.textContent = t(key);
    });
  }

  function tick() {
    const now = new Date();
    const locale = clockLocale(getLang());
    CLOCKS.forEach((c) => {
      const timeEl = document.getElementById(`clock-time-${c.id}`);
      const dateEl = document.getElementById(`clock-date-${c.id}`);
      if (timeEl) timeEl.textContent = formatTime(now, c.tz, locale);
      if (dateEl) dateEl.textContent = formatDate(now, c.tz, locale);
    });
  }

  applyLabels();
  tick();
  setInterval(tick, 1000);
  document.addEventListener("langchange", () => {
    applyLabels();
    tick();
  });
}
