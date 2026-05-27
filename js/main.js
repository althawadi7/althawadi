(function () {
  'use strict';

  var SITE_HOME = '/althawadi/';
  var PAGES = ['about', 'tree', 'ancestors', 'gallery', 'news', 'references', 'contact'];

  function fileSiteRoot() {
    var url = window.location.href.split('#')[0].split('?')[0];
    var marker = '/althawadi/';
    var idx = url.toLowerCase().indexOf(marker);
    if (idx === -1) {
      return null;
    }
    return url.substring(0, idx + marker.length);
  }

  function toFileHref(absPath) {
    var root = fileSiteRoot();
    if (!root || absPath.indexOf(SITE_HOME) !== 0) {
      return absPath;
    }
    return root + absPath.slice(SITE_HOME.length);
  }

  function normalizeSiteLinks() {
    if (window.location.protocol !== 'file:') {
      return;
    }
    document.querySelectorAll('[href^="/althawadi/"], [src^="/althawadi/"]').forEach(function (el) {
      var attr = el.hasAttribute('href') ? 'href' : 'src';
      el.setAttribute(attr, toFileHref(el.getAttribute(attr)));
    });
    var root = fileSiteRoot();
    if (!root) {
      return;
    }
    document.querySelectorAll('link[href^="../css/"], script[src^="../js/"]').forEach(function (el) {
      var attr = el.hasAttribute('href') ? 'href' : 'src';
      el.setAttribute(attr, root + el.getAttribute(attr).replace(/^\.\.\//, ''));
    });
    document.querySelectorAll('link[href^="css/"], script[src^="js/"]').forEach(function (el) {
      var attr = el.hasAttribute('href') ? 'href' : 'src';
      el.setAttribute(attr, root + el.getAttribute(attr));
    });
  }

  function cleanUrlBar() {
    if (!window.location.protocol.startsWith('http')) {
      return;
    }
    var path = window.location.pathname;
    var tail = window.location.search + window.location.hash;

    if (/\/index\.html$/i.test(path)) {
      path = path.replace(/\/index\.html$/i, '/');
      window.history.replaceState(null, '', path + tail);
      return;
    }

    for (var i = 0; i < PAGES.length; i++) {
      var p = PAGES[i];
      var re = new RegExp('/' + p + '\\.html$', 'i');
      if (re.test(path)) {
        window.history.replaceState(null, '', path.replace(re, '/' + p + '/') + tail);
        return;
      }
    }
  }

  function isHomePath(pathname) {
    var p = pathname.replace(/\\/g, '/');
    if (/\/index\.html$/i.test(p)) {
      p = p.replace(/\/index\.html$/i, '/');
    }
    return /\/althawadi\/?$/i.test(p);
  }

  normalizeSiteLinks();
  cleanUrlBar();
  window.addEventListener('pageshow', cleanUrlBar);

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
    link.addEventListener('click', function (e) {
      if (window.location.protocol === 'file:') {
        return;
      }
      e.preventDefault();
      if (isHomePath(window.location.pathname)) {
        cleanUrlBar();
        window.scrollTo(0, 0);
        return;
      }
      window.location.assign(SITE_HOME);
    });
  });

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

  /* Dark mode toggle */
  var THEME_KEY = 'althawadi-theme';

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function updateThemeToggle(btn) {
    if (!btn) return;
    var dark = currentTheme() === 'dark';
    btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
    btn.setAttribute('aria-label', dark ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الليلي');
    btn.setAttribute('title', dark ? 'الوضع الفاتح' : 'الوضع الليلي');
  }

  function applyTheme(theme, animate) {
    var root = document.documentElement;
    if (animate) {
      root.classList.add('theme-animate');
      window.setTimeout(function () {
        root.classList.remove('theme-animate');
      }, 260);
    }
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.removeAttribute('data-theme');
    }
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      /* ignore */
    }
    updateThemeToggle(document.getElementById('theme-toggle'));
  }

  function initThemeToggle() {
    var btn = document.getElementById('theme-toggle');
    if (!btn) {
      var actions = document.querySelector('.site-header-inner .flex.items-center.gap-3');
      if (!actions) return;
      btn = document.createElement('button');
      btn.id = 'theme-toggle';
      btn.type = 'button';
      btn.className = 'theme-toggle';
      btn.innerHTML =
        '<svg class="icon theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>' +
        '<svg class="icon theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
      var menuBtn = document.getElementById('menu-toggle');
      if (menuBtn) {
        actions.insertBefore(btn, menuBtn);
      } else {
        actions.appendChild(btn);
      }
    }
    updateThemeToggle(btn);
    btn.addEventListener('click', function () {
      applyTheme(currentTheme() === 'dark' ? 'light' : 'dark', true);
    });
  }

  initThemeToggle();
})();
