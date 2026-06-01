(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  var resizeTimer;

  function centerPan(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    var maxX = pan.scrollWidth - pan.clientWidth;
    pan.scrollLeft = maxX > 0 ? maxX / 2 : 0;
  }

  function layoutBranch(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    canvas.style.transform = '';
    canvas.style.width = '';
    pan.style.minHeight = '';

    requestAnimationFrame(function () {
      var h = Math.ceil(canvas.getBoundingClientRect().height + 24);
      pan.style.minHeight = Math.min(Math.max(h, 320), window.innerHeight * 0.85) + 'px';
      centerPan(pan);
    });
  }

  function layoutAll() {
    pans.forEach(layoutBranch);
  }

  function onResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(layoutAll, 120);
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(layoutAll);
  }

  window.addEventListener('load', layoutAll);
  window.addEventListener('resize', onResize);

  if (typeof ResizeObserver !== 'undefined') {
    pans.forEach(function (pan) {
      new ResizeObserver(onResize).observe(pan);
    });
  }

  layoutAll();
})();
