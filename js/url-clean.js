(function () {
  'use strict';

  var THEME_KEY = 'althawadi-theme';
  var PAGES = ['about', 'tree', 'ancestors', 'gallery', 'news', 'references', 'contact', 'site-map'];

  try {
    if (localStorage.getItem(THEME_KEY) === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  } catch (e) {
    /* ignore */
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

  cleanUrlBar();
  window.addEventListener('pageshow', cleanUrlBar);
})();
