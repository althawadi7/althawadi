(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan, .family-tree-pan--branch');
  if (!pans.length) return;

  var resizeTimer;

  function centerPan(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    var max = pan.scrollWidth - pan.clientWidth;
    pan.scrollLeft = max > 0 ? max / 2 : 0;
  }

  function layoutBranch(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    canvas.style.transform = '';
    canvas.style.width = '';
    pan.style.minHeight = '';

    var contentWidth = canvas.scrollWidth;
    var panWidth = pan.clientWidth;
    var available = Math.max(panWidth - 32, 200);

    if (contentWidth > available) {
      var scale = available / contentWidth;
      scale = Math.max(0.35, Math.min(1, scale));
      canvas.style.transform = 'scale(' + scale + ')';
      canvas.style.transformOrigin = 'top center';
    }

    requestAnimationFrame(function () {
      pan.style.minHeight = Math.ceil(canvas.getBoundingClientRect().height + 16) + 'px';
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
