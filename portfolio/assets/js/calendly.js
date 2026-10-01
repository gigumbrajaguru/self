// Calendly popup for every [data-calendly] link; the widget loads on first click (no floating badge)
const CALENDLY_URL = 'https://calendly.com/gigumbrajaguru/15min';
let calendlyReady;

function loadCalendly() {
  calendlyReady ??= new Promise((resolve, reject) => {
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://assets.calendly.com/assets/external/widget.css';
    const script = document.createElement('script');
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.onload = resolve;
    script.onerror = reject;
    document.head.append(css, script);
  });
  return calendlyReady;
}

document.addEventListener('click', async (e) => {
  const link = e.target.closest('[data-calendly]');
  if (!link) return;
  e.preventDefault();
  // A modal <dialog> stays above everything else, so close it before the popup opens
  link.closest('dialog')?.close();
  try {
    await loadCalendly();
    Calendly.initPopupWidget({ url: CALENDLY_URL });
  } catch {
    // Widget blocked or offline: go to the Calendly page instead
    calendlyReady = null;
    location.assign(link.href);
  }
});
