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

  /* Active nav link */
  var path = window.location.pathname.replace(/\/$/, '') || '/';
  var page = path.split('/').pop() || 'index.html';
  if (page === '' || page === '/') page = 'index.html';

  document.querySelectorAll('.nav-link').forEach(function (link) {
    var href = link.getAttribute('href');
    if (!href) return;
    var linkPage = href.split('/').pop() || 'index.html';
    if (linkPage === page || (page === 'index.html' && (linkPage === 'index.html' || href === '/' || href === './'))) {
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
