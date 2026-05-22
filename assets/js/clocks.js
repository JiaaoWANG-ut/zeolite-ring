const CLOCKS = [
  { id: "beijing", tz: "Asia/Shanghai", labelKey: "clockBeijing" },
  { id: "austin", tz: "America/Chicago", labelKey: "clockAustin" },
  { id: "sf", tz: "America/Los_Angeles", labelKey: "clockSF" },
];

function clockLocale(lang) {
  return lang === "zh" ? "zh-CN" : "en-US";
}

function formatTime(date, tz, locale) {
  try {
    return new Intl.DateTimeFormat(locale, {
      timeZone: tz,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    }).format(date);
  } catch {
    return date.toLocaleTimeString(locale, { hour12: false });
  }
}

function formatDate(date, tz, locale) {
  try {
    return new Intl.DateTimeFormat(locale, {
      timeZone: tz,
      month: "short",
      day: "numeric",
      weekday: "short",
    }).format(date);
  } catch {
    return date.toLocaleDateString(locale);
  }
}

export function initClocks(t, getLang) {
  const items = document.querySelectorAll("[data-clock]");
  if (!items.length) return;

  function applyLabels() {
    items.forEach((item) => {
      const config = CLOCKS.find((c) => c.id === item.dataset.clock);
      if (!config) return;
      const label = item.querySelector("[data-role='label']");
      if (label) label.textContent = t(config.labelKey);
    });
  }

  function tick() {
    const now = new Date();
    const locale = clockLocale(getLang());
    items.forEach((item) => {
      const config = CLOCKS.find((c) => c.id === item.dataset.clock);
      if (!config) return;
      const timeEl = item.querySelector("[data-role='time']");
      const dateEl = item.querySelector("[data-role='date']");
      if (timeEl) timeEl.textContent = formatTime(now, config.tz, locale);
      if (dateEl) dateEl.textContent = formatDate(now, config.tz, locale);
    });
  }

  applyLabels();
  tick();
  window.setInterval(tick, 1000);
  document.addEventListener("langchange", () => {
    applyLabels();
    tick();
  });
}
