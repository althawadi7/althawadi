(function () {
  'use strict';

  var PAGES = ['about', 'tree', 'ancestors', 'gallery', 'news', 'references', 'contact'];

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

  cleanUrlBar();
  window.addEventListener('pageshow', cleanUrlBar);
})();
