/* ═══════════════════════════════════════════
   WELL-BUILT V2 – MAIN JS
═══════════════════════════════════════════ */

// ── NAVBAR SCROLL ─────────────────────────
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
}

// ── MOBILE MENU ───────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('navLinks');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const isOpen = navLinks.classList.contains('open');
    hamburger.setAttribute('aria-expanded', isOpen);
  });
  // Close on outside click
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
    }
  });
  // Close on link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => navLinks.classList.remove('open'));
  });
}

// ── SCROLL REVEAL ─────────────────────────
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('visible'), i * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealEls.forEach(el => observer.observe(el));
}

// ── AUTO REVEAL SECTIONS ──────────────────
document.querySelectorAll('.section-header, .service-card, .project-card, .why-card, .client-badge, .about-mini-card').forEach(el => {
  el.classList.add('reveal');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  observer.observe(el);
});

// ── COUNTER ANIMATION ─────────────────────
function animateCounter(el, target, duration = 2000) {
  let start = null;
  // Reset to 0 first
  el.textContent = '0';
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(eased * target);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// Observe both possible stat containers (hero-stats-row OR hero-stats)
const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const numEls = entry.target.querySelectorAll('.stat-num[data-target]');
      numEls.forEach(el => {
        const target = parseInt(el.dataset.target);
        if (!isNaN(target)) {
          animateCounter(el, target);
          el.removeAttribute('data-target'); // prevent re-trigger
        }
      });
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

// Support both old and new class names
['hero-stats-row', 'hero-stats'].forEach(cls => {
  const el = document.querySelector('.' + cls);
  if (el) statsObserver.observe(el);
});

// ── SMOOTH NAVBAR ACTIVE ──────────────────
document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', e => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── STAGGER CHILDREN ──────────────────────
document.querySelectorAll('.services-grid, .projects-grid, .why-grid, .clients-grid').forEach(grid => {
  Array.from(grid.children).forEach((child, i) => {
    child.style.transitionDelay = `${i * 60}ms`;
  });
});