(function () {
  'use strict';

  var SITE_HOME = '/althawadi/';

  function siteHomeHref() {
    if (window.location.protocol === 'file:') {
      var url = window.location.href.split('#')[0].split('?')[0];
      var marker = '/altahwadi/';
      var idx = url.toLowerCase().indexOf(marker);
      if (idx !== -1) {
        return url.substring(0, idx + marker.length) + 'index.html';
      }
    }
    return SITE_HOME;
  }

  /* Logo + الرئيسية → /althawadi/ (not …/index.html) on GitHub Pages */
  document.querySelectorAll('[data-home]').forEach(function (link) {
    link.setAttribute('href', siteHomeHref());
  });

  if (window.location.protocol.startsWith('http') && /\/index\.html$/i.test(window.location.pathname)) {
    var clean = window.location.pathname.replace(/index\.html$/i, '');
    if (!clean.endsWith('/')) {
      clean += '/';
    }
    window.history.replaceState(null, '', clean + window.location.search + window.location.hash);
  }

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

  /* Active nav link — works on file:// and https:// */
  function pageFromPath(pathStr) {
    var segs = pathStr.replace(/\\/g, '/').split('/').filter(Boolean);
    if (segs.length && segs[segs.length - 1] === 'index.html') {
      segs.pop();
    }
    var last = segs.length ? segs[segs.length - 1] : 'home';
    if (last === 'altahwadi' || /^[a-z]:$/i.test(last)) {
      return 'home';
    }
    return last;
  }

  var page = pageFromPath(window.location.pathname);

  document.querySelectorAll('.nav-link').forEach(function (link) {
    var href = link.getAttribute('href') || '';
    if (!href || href.indexOf('http') === 0) return;
    var linkPage = 'home';
    if (href === './' || href === '../' || href === '.' || href === '..') {
      linkPage = 'home';
    } else {
      linkPage = pageFromPath(href);
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
