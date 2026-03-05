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

// Contact form — swap the action URL for your Formspree endpoint
// e.g. action="https://formspree.io/f/yourcode"
const form = document.getElementById('contactForm');
form.addEventListener('submit', (e) => {
  e.preventDefault();
  // If you've added a Formspree action attribute, remove the e.preventDefault()
  // and it will submit normally. This alert is just a placeholder.
  alert('Thanks for your message! (Connect Formspree to send real emails.)');
  form.reset();
});
