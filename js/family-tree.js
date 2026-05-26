(function () {
  'use strict';

  var pan = document.getElementById('family-tree-pan');
  var canvas = document.getElementById('family-tree-canvas');
  if (!pan || !canvas) return;

  var tree = canvas.querySelector('.family-tree');
  if (!tree) return;

  var resizeTimer;

  function centerPan() {
    var max = pan.scrollWidth - pan.clientWidth;
    if (max <= 0) {
      pan.scrollLeft = 0;
      return;
    }
    pan.scrollLeft = max / 2;
  }

  function layoutTree() {
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
      centerPan();
    });
  }

  function onResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(layoutTree, 120);
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(layoutTree);
  }

  window.addEventListener('load', layoutTree);
  window.addEventListener('resize', onResize);

  if (typeof ResizeObserver !== 'undefined') {
    new ResizeObserver(onResize).observe(pan);
  }

  layoutTree();
})();
