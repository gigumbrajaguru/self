// "Show some support": the PayPal SDK loads only after a [data-support] button is clicked
const PAYPAL_SDK = 'https://www.paypal.com/sdk/js?client-id=BAAqESZztHDZsBnijdElHcsTKD7l6bd9zcuQmNUZGsMRS-scTh-HOYczec4HBoOxFnmfBVbPI8EMVjrV6c&components=hosted-buttons&disable-funding=venmo&currency=USD';
const HOSTED_BUTTON_ID = '8NFZ8MJP4FNAW';

const supportPanel = document.getElementById('supportPanel');
const supportStatus = document.getElementById('supportStatus');
let paypalRequested = false;

function showSupport() {
  supportPanel.hidden = false;
  supportPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
  if (paypalRequested) return;
  paypalRequested = true;

  const script = document.createElement('script');
  script.src = PAYPAL_SDK;
  script.onload = () => {
    paypal.HostedButtons({ hostedButtonId: HOSTED_BUTTON_ID })
      .render(`#paypal-container-${HOSTED_BUTTON_ID}`)
      .then(() => supportStatus.remove());
  };
  script.onerror = () => {
    paypalRequested = false;
    script.remove();
    supportStatus.textContent = 'PayPal could not load. Please check your connection or ad blocker and try again.';
  };
  document.head.appendChild(script);
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('[data-support]')) return;
  e.preventDefault();
  showSupport();
});

// Links such as "Show Some Support" on the portfolio arrive here as game/#support
if (location.hash === '#support') showSupport();
