// "More Information" box for service / gig cards, with a request form sent through FormSubmit
const svcDialog = document.getElementById('svcDialog');
const requestForm = document.getElementById('svcRequestForm');
const requestStatus = document.getElementById('svcRequestStatus');
const dialogActions = document.getElementById('svcDialogActions');
const meetingLink = document.getElementById('svcDialogMeeting');
const dialogParts = {
  icon: document.getElementById('svcDialogIcon'),
  title: document.getElementById('svcDialogTitle'),
  desc: document.getElementById('svcDialogDesc'),
  body: document.getElementById('svcDialogBody'),
  price: document.getElementById('svcDialogPrice'),
};

function showRequestForm() {
  dialogActions.hidden = true;
  requestForm.hidden = false;
  requestForm.querySelector(requestForm.elements.service.value ? '[name="name"]' : '[name="service"]').focus();
}

// card = the selected .svc-card, or null for a general request
function openDialog(card) {
  requestForm.reset();
  requestStatus.textContent = '';
  if (card) {
    const copy = (selector) => card.querySelector(selector).cloneNode(true).childNodes;
    dialogParts.icon.replaceChildren(...copy('.svc-icon'));
    dialogParts.title.textContent = card.querySelector('.project-title').textContent;
    dialogParts.desc.replaceChildren(...copy('.project-desc'));
    dialogParts.body.replaceChildren(card.querySelector('.svc-details').content.cloneNode(true));
    // Gigs carry a starting price and offer a meeting; other services are quoted after analysis
    const price = card.dataset.price;
    dialogParts.price.textContent = price
      ? `Pricing: ${price}. The final price depends on your scope.`
      : 'Pricing: personalised. You\'ll get a quote after I analyse your requirements.';
    meetingLink.hidden = !card.hasAttribute('data-meeting');
  } else {
    dialogParts.title.textContent = 'Request a Service';
    dialogParts.desc.textContent = 'Tell me what you need and I\'ll get back to you with a quote.';
    dialogParts.body.replaceChildren();
  }
  dialogParts.icon.hidden = !card;
  dialogParts.price.hidden = !card;
  requestForm.elements.service.value = card ? dialogParts.title.textContent : '';
  dialogActions.hidden = !card;
  requestForm.hidden = !!card;
  svcDialog.showModal();
  if (!card) showRequestForm();
}

document.addEventListener('click', (e) => {
  const more = e.target.closest('[data-more]');
  if (more) return openDialog(more.closest('.svc-card'));
  if (e.target.closest('[data-request]')) {
    e.preventDefault();
    openDialog(null);
  }
});

svcDialog.addEventListener('click', (e) => {
  // Clicks on the backdrop land on the <dialog> element itself
  if (e.target === svcDialog || e.target.closest('[data-close]')) svcDialog.close();
  if (e.target.closest('[data-show-form]')) showRequestForm();
});

requestForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = requestForm.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Sending…';
  const data = Object.fromEntries(new FormData(requestForm));
  data._subject = `Service request: ${data.service}`;
  data._template = 'table';
  try {
    const res = await fetch('https://formsubmit.co/ajax/gigumbrajaguru@gmail.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (res.ok && json.success === 'true') {
      requestStatus.textContent = 'Thanks! Your request has been sent. I\'ll reply by email with the next steps.';
      requestStatus.style.color = 'var(--clr-accent)';
      requestForm.reset();
    } else {
      requestStatus.textContent = 'Oops! Something went wrong. Please try again or email me directly.';
      requestStatus.style.color = '#e55';
    }
  } catch {
    requestStatus.textContent = 'Network error. Please check your connection.';
    requestStatus.style.color = '#e55';
  }
  btn.disabled = false;
  btn.textContent = 'Send Request';
});
