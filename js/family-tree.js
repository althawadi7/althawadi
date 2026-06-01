(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  function centerPan(pan) {
    var maxX = pan.scrollWidth - pan.clientWidth;
    pan.scrollLeft = maxX > 0 ? maxX / 2 : 0;
    pan.scrollTop = 0;
  }

  function layoutAll() {
    pans.forEach(function (pan) {
      var canvas = pan.querySelector('.family-tree-canvas');
      centerPan(pan);
      if (canvas) {
        pan.style.minHeight = Math.max(canvas.scrollHeight + 56, 520) + 'px';
      }
    });
  }

  function onResize() {
    clearTimeout(layoutAll._timer);
    layoutAll._timer = setTimeout(layoutAll, 200);
  }

  function runInitial() {
    layoutAll();
    requestAnimationFrame(function () {
      layoutAll();
    });
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(runInitial);
  } else {
    runInitial();
  }

  window.addEventListener('load', runInitial);
  window.addEventListener('resize', onResize);

  var themeObserver = new MutationObserver(onResize);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });

  window.__familyTreeLayout = layoutAll;
})();
