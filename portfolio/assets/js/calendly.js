// Calendly: floating badge + popup for every [data-calendly] link
const CALENDLY_URL = 'https://calendly.com/gigumbrajaguru/15min';

window.addEventListener('load', () => {
  if (!window.Calendly) return;
  Calendly.initBadgeWidget({ url: CALENDLY_URL, text: 'Schedule time with me', color: '#0069ff', textColor: '#ffffff', branding: true });
});

// Falls back to opening the Calendly page when the widget script is unavailable
document.addEventListener('click', (e) => {
  const link = e.target.closest('[data-calendly]');
  if (!link || !window.Calendly) return;
  e.preventDefault();
  Calendly.initPopupWidget({ url: CALENDLY_URL });
});
