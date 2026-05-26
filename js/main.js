(function () {
  'use strict';

  /* Mobile menu */
  var menuBtn = document.getElementById('menu-toggle');
  var mobileNav = document.getElementById('mobile-nav');
  var menuIcon = document.getElementById('menu-icon');
  var closeIcon = document.getElementById('close-icon');

  if (menuBtn && mobileNav) {
    menuBtn.addEventListener('click', function () {
      var open = mobileNav.classList.toggle('is-open');
      menuIcon.style.display = open ? 'none' : '';
      closeIcon.style.display = open ? '' : 'none';
    });

    mobileNav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileNav.classList.remove('is-open');
        menuIcon.style.display = '';
        closeIcon.style.display = 'none';
      });
    });
  }

  /* Active nav link (clean URLs: /althawadi/, /althawadi/about/, …) */
  var parts = window.location.pathname.replace(/\/$/, '').split('/').filter(Boolean);
  var page = 'home';
  if (parts.length >= 2 && parts[0] === 'althawadi') {
    page = parts[1] || 'home';
  } else if (parts.length === 1 && parts[0] !== 'althawadi') {
    page = parts[0];
  }

  document.querySelectorAll('.nav-link').forEach(function (link) {
    var href = (link.getAttribute('href') || '').replace(/\/$/, '');
    if (!href) return;
    var linkPage = href.split('/').filter(Boolean).pop() || 'home';
    if (href === '.' || href === '..' || href === './' || href.endsWith('/althawadi')) {
      linkPage = 'home';
    }
    if (linkPage === page) {
      link.classList.add('is-active');
    }
  });

  /* Footer year */
  var yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* Contact form */
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      alert('شكرًا لتواصلكم. سيتمّ الرّد عليكم قريبًا إن شاء الله.');
      form.reset();
    });
  }
})();
