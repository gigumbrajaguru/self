// Navbar: add 'scrolled' class when page is scrolled
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 20);
});

// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const navLinks = document.querySelector('.nav-links');
navToggle.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});

// Close mobile nav when a link is clicked
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => navLinks.classList.remove('open'));
});

// Contact form — submits to FormSubmit (AJAX)
const form = document.getElementById('contactForm');
const formStatus = document.getElementById('form-status');
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.textContent = 'Sending…';
  const data = Object.fromEntries(new FormData(form));
  try {
    const res = await fetch('https://formsubmit.co/ajax/gigumbrajaguru@gmail.com', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const json = await res.json();
    if (res.ok && json.success === 'true') {
      formStatus.textContent = 'Thanks! Your message has been sent.';
      formStatus.style.color = 'var(--clr-accent, #7c6af7)';
      form.reset();
    } else {
      formStatus.textContent = 'Oops! Something went wrong. Please try again.';
      formStatus.style.color = '#e55';
    }
  } catch {
    formStatus.textContent = 'Network error. Please check your connection.';
    formStatus.style.color = '#e55';
  }
  formStatus.style.display = 'block';
  btn.disabled = false;
  btn.textContent = 'Send Message';
});
