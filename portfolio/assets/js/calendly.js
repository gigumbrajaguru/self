// Calendly: popup for every [data-calendly] link (no floating badge)
const CALENDLY_URL = 'https://calendly.com/gigumbrajaguru/15min';

// Falls back to opening the Calendly page when the widget script is unavailable
document.addEventListener('click', (e) => {
  const link = e.target.closest('[data-calendly]');
  if (!link || !window.Calendly) return;
  e.preventDefault();
  Calendly.initPopupWidget({ url: CALENDLY_URL });
});
