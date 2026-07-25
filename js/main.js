(function () {
  'use strict';

  var LEGACY_PREFIX = '/althawadi/';
  var PAGES = ['about', 'tree', 'ancestors', 'gallery', 'news', 'references', 'contact', 'site-map'];

  function isEnglish() {
    return (
      (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0 ||
      /^\/en(\/|$)/i.test(window.location.pathname)
    );
  }

  function siteHome() {
    return isEnglish() ? '/en/' : '/';
  }

  function fileSiteRoot() {
    var url = window.location.href.split('#')[0].split('?')[0];
    var idx = url.toLowerCase().indexOf(LEGACY_PREFIX);
    if (idx !== -1) {
      return url.substring(0, idx + LEGACY_PREFIX.length);
    }
    var slash = url.lastIndexOf('/');
    return slash === -1 ? url + '/' : url.substring(0, slash + 1);
  }

  function toFileHref(absPath) {
    var root = fileSiteRoot();
    if (!root) {
      return absPath;
    }
    if (absPath.charAt(0) === '/') {
      return root + absPath.slice(1);
    }
    return absPath;
  }

  function normalizeSiteLinks() {
    if (window.location.protocol !== 'file:') {
      return;
    }
    document.querySelectorAll('[href^="/"], [src^="/"]').forEach(function (el) {
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
      var reEn = new RegExp('^/en/' + p + '\\.html$', 'i');
      var reAr = new RegExp('^/' + p + '\\.html$', 'i');
      if (reEn.test(path)) {
        window.history.replaceState(null, '', '/en/' + p + '/' + tail);
        return;
      }
      if (reAr.test(path)) {
        window.history.replaceState(null, '', '/' + p + '/' + tail);
        return;
      }
    }
  }

  function isHomePath(pathname) {
    var p = pathname.replace(/\\/g, '/');
    if (/\/index\.html$/i.test(p)) {
      p = p.replace(/\/index\.html$/i, '/');
    }
    return (
      p === '/' ||
      p === '/en/' ||
      /\/althawadi\/?$/i.test(p) ||
      /\/althawadi\/en\/?$/i.test(p)
    );
  }

  normalizeSiteLinks();
  cleanUrlBar();
  window.addEventListener('pageshow', cleanUrlBar);

  var SITE_HOME = siteHome();

  function siteHomeHref() {
    if (window.location.protocol === 'file:') {
      var url = window.location.href.split('#')[0].split('?')[0];
      var idx = url.toLowerCase().indexOf(LEGACY_PREFIX);
      if (idx !== -1) {
        var base = url.substring(0, idx + LEGACY_PREFIX.length);
        return isEnglish() ? base + 'en/index.html' : base + 'index.html';
      }
    }
    return SITE_HOME;
  }

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

  function pageFromPath(pathStr) {
    var segs = pathStr.replace(/\\/g, '/').split('/').filter(Boolean);
    if (segs.length && segs[segs.length - 1] === 'index.html') {
      segs.pop();
    }
    if (segs[0] === 'en') {
      segs.shift();
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
    if (
      href === './' ||
      href === '../' ||
      href === '.' ||
      href === '..' ||
      href === '/' ||
      href === '/en/'
    ) {
      linkPage = 'home';
    } else {
      linkPage = pageFromPath(href);
    }
    if (linkPage === page) {
      link.classList.add('is-active');
    }
  });

  var yearEl = document.getElementById('footer-year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      alert(
        isEnglish()
          ? 'Thank you for reaching out. We will reply soon, God willing.'
          : 'شكرًا لتواصلكم. سيتمّ الرّد عليكم قريبًا إن شاء الله.'
      );
      form.reset();
    });
  }

  var THEME_KEY = 'althawadi-theme';

  function currentTheme() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  }

  function updateThemeToggle(btn) {
    if (!btn) return;
    var dark = currentTheme() === 'dark';
    var en = isEnglish();
    btn.setAttribute('aria-pressed', dark ? 'true' : 'false');
    btn.setAttribute(
      'aria-label',
      dark
        ? en
          ? 'Enable light mode'
          : 'تفعيل الوضع الفاتح'
        : en
          ? 'Enable dark mode'
          : 'تفعيل الوضع الليلي'
    );
    btn.setAttribute(
      'title',
      dark ? (en ? 'Light mode' : 'الوضع الفاتح') : en ? 'Dark mode' : 'الوضع الليلي'
    );
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
      var menuBtn2 = document.getElementById('menu-toggle');
      if (menuBtn2) {
        actions.insertBefore(btn, menuBtn2);
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

  /* One reference video at a time */
  (function initRefDetailVideos() {
    var videos = document.querySelectorAll('.ref-detail-page .ref-detail-video');
    if (!videos.length) return;
    videos.forEach(function (video) {
      video.addEventListener('play', function () {
        videos.forEach(function (other) {
          if (other !== video && !other.paused) other.pause();
        });
      });
    });
  })();

  /* Image carousel + fullscreen lightbox on detail pages */
  (function initRefMediaCarousel() {
    var carousels = document.querySelectorAll('[data-ref-carousel]');
    var zoomables = document.querySelectorAll('[data-ref-zoom], [data-ref-carousel]');
    if (!carousels.length && !document.querySelector('[data-ref-expand]')) return;

    var isEn = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0;
    var labelClose = isEn ? 'Close' : 'إغلاق';
    var labelPrev = isEn ? 'Previous image' : 'الصورة السابقة';
    var labelNext = isEn ? 'Next image' : 'الصورة التالية';

    function ensureLightbox() {
      var box = document.getElementById('ref-detail-lightbox');
      if (box) return box;
      box = document.createElement('div');
      box.id = 'ref-detail-lightbox';
      box.className = 'ref-detail-lightbox';
      box.hidden = true;
      box.setAttribute('role', 'dialog');
      box.setAttribute('aria-modal', 'true');
      box.innerHTML =
        '<button type="button" class="ref-detail-lightbox__backdrop" data-lb-close aria-label="' + labelClose + '"></button>' +
        '<div class="ref-detail-lightbox__panel">' +
        '<div class="ref-detail-lightbox__toolbar">' +
        '<p class="ref-detail-lightbox__counter"><span data-lb-current>1</span> / <span data-lb-total>1</span></p>' +
        '<button type="button" class="ref-detail-lightbox__close" data-lb-close aria-label="' + labelClose + '">×</button>' +
        '</div>' +
        '<div class="ref-detail-lightbox__stage">' +
        '<button type="button" class="ref-detail-lightbox__nav ref-detail-lightbox__nav--prev" data-lb-prev aria-label="' + labelPrev + '">' +
        '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.75"><path d="m15 18-6-6 6-6"/></svg>' +
        '</button>' +
        '<div class="ref-detail-lightbox__media"><img data-lb-img alt="" /></div>' +
        '<button type="button" class="ref-detail-lightbox__nav ref-detail-lightbox__nav--next" data-lb-next aria-label="' + labelNext + '">' +
        '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.75"><path d="m9 18 6-6-6-6"/></svg>' +
        '</button>' +
        '</div></div>';
      document.body.appendChild(box);
      return box;
    }

    var lightbox = ensureLightbox();
    var lbImg = lightbox.querySelector('[data-lb-img]');
    var lbCurrent = lightbox.querySelector('[data-lb-current]');
    var lbTotal = lightbox.querySelector('[data-lb-total]');
    var lbPrev = lightbox.querySelector('[data-lb-prev]');
    var lbNext = lightbox.querySelector('[data-lb-next]');
    var lbState = { items: [], index: 0 };

    function showLightbox(items, index) {
      lbState.items = items || [];
      lbState.index = index || 0;
      if (!lbState.items.length) return;
      renderLightbox();
      lightbox.hidden = false;
      document.body.classList.add('ref-detail-lightbox-open');
    }

    function hideLightbox() {
      lightbox.hidden = true;
      document.body.classList.remove('ref-detail-lightbox-open');
      lbImg.removeAttribute('src');
      lbState.items = [];
    }

    function renderLightbox() {
      var item = lbState.items[lbState.index];
      if (!item) return;
      lbImg.src = item.src;
      lbImg.alt = item.alt || '';
      lbCurrent.textContent = String(lbState.index + 1);
      lbTotal.textContent = String(lbState.items.length);
      var multi = lbState.items.length > 1;
      lbPrev.hidden = !multi;
      lbNext.hidden = !multi;
    }

    function stepLightbox(delta) {
      if (lbState.items.length < 2) return;
      lbState.index = (lbState.index + delta + lbState.items.length) % lbState.items.length;
      renderLightbox();
    }

    lightbox.addEventListener('click', function (e) {
      var t = e.target;
      if (t.closest('[data-lb-close]')) hideLightbox();
      else if (t.closest('[data-lb-prev]')) stepLightbox(-1);
      else if (t.closest('[data-lb-next]')) stepLightbox(1);
    });

    document.addEventListener('keydown', function (e) {
      if (lightbox.hidden) return;
      if (e.key === 'Escape') hideLightbox();
      else if (e.key === 'ArrowLeft') stepLightbox(document.documentElement.dir === 'rtl' ? 1 : -1);
      else if (e.key === 'ArrowRight') stepLightbox(document.documentElement.dir === 'rtl' ? -1 : 1);
    });

    function collectItems(root) {
      return Array.prototype.map.call(root.querySelectorAll('img[data-fullsrc], .ref-detail-image-frame img'), function (img) {
        return {
          src: img.getAttribute('data-fullsrc') || img.currentSrc || img.src,
          alt: img.getAttribute('alt') || ''
        };
      });
    }

    function initCarousel(root) {
      var slides = Array.prototype.slice.call(root.querySelectorAll('.ref-media-carousel__slide'));
      var dots = Array.prototype.slice.call(root.querySelectorAll('.ref-media-carousel__dot'));
      var currentEl = root.querySelector('[data-ref-current]');
      var index = 0;

      function goTo(next) {
        if (!slides.length) return;
        index = (next + slides.length) % slides.length;
        slides.forEach(function (slide, i) {
          var on = i === index;
          slide.classList.toggle('is-active', on);
          if (on) slide.removeAttribute('hidden');
          else slide.setAttribute('hidden', '');
        });
        dots.forEach(function (dot, i) {
          var on = i === index;
          dot.classList.toggle('is-active', on);
          dot.setAttribute('aria-current', on ? 'true' : 'false');
        });
        if (currentEl) currentEl.textContent = String(index + 1);
      }

      var prevBtn = root.querySelector('[data-ref-prev]');
      var nextBtn = root.querySelector('[data-ref-next]');
      if (prevBtn) prevBtn.addEventListener('click', function () { goTo(index - 1); });
      if (nextBtn) nextBtn.addEventListener('click', function () { goTo(index + 1); });
      dots.forEach(function (dot) {
        dot.addEventListener('click', function () {
          var n = parseInt(dot.getAttribute('data-goto') || '0', 10);
          goTo(n);
        });
      });

      var expand = root.querySelector('[data-ref-expand]');
      if (expand) {
        expand.addEventListener('click', function () {
          showLightbox(collectItems(root), index);
        });
      }

      /* swipe */
      var startX = null;
      var viewport = root.querySelector('.ref-media-carousel__viewport');
      if (viewport) {
        viewport.addEventListener('touchstart', function (e) {
          if (!e.changedTouches || !e.changedTouches.length) return;
          startX = e.changedTouches[0].clientX;
        }, { passive: true });
        viewport.addEventListener('touchend', function (e) {
          if (startX == null || !e.changedTouches || !e.changedTouches.length) return;
          var dx = e.changedTouches[0].clientX - startX;
          startX = null;
          if (Math.abs(dx) < 40) return;
          var rtl = document.documentElement.dir === 'rtl';
          if (dx > 0) goTo(index + (rtl ? 1 : -1));
          else goTo(index + (rtl ? -1 : 1));
        }, { passive: true });
      }

      goTo(0);
    }

    carousels.forEach(initCarousel);

    document.querySelectorAll('[data-ref-zoom] [data-ref-expand]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var root = btn.closest('[data-ref-zoom]');
        if (!root) return;
        showLightbox(collectItems(root), 0);
      });
    });
  })();
})();
