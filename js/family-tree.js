(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  var resizeTimer;
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function directNode(li) {
    return li.querySelector(':scope > .family-tree-node, :scope > a.family-tree-node--link');
  }

  function parentNode(ul) {
    var li = ul.parentElement;
    if (!li) return null;
    return li.querySelector(':scope > .family-tree-node, :scope > a.family-tree-node--link');
  }

  function relBox(el, container) {
    var er = el.getBoundingClientRect();
    var cr = container.getBoundingClientRect();
    return {
      cx: er.left - cr.left + er.width / 2,
      cy: er.top - cr.top + er.height / 2,
      top: er.top - cr.top,
      bottom: er.top - cr.top + er.height,
    };
  }

  function resetLayout(canvas) {
    canvas.classList.remove('family-tree-canvas--wired');
    canvas.querySelectorAll('.family-tree-node, .family-tree-node--link').forEach(function (node) {
      node.style.position = '';
      node.style.left = '';
    });
    var svg = canvas.querySelector('.family-tree-lines');
    if (svg) svg.remove();
  }

  function alignParents(canvas) {
    canvas.querySelectorAll('.family-tree-children').forEach(function (ul) {
      var parentEl = parentNode(ul);
      if (!parentEl) return;

      var items = ul.querySelectorAll(':scope > li');
      if (!items.length) return;

      var firstNode = directNode(items[0]);
      var lastNode = directNode(items[items.length - 1]);
      if (!firstNode || !lastNode) return;

      var firstCx = relBox(firstNode, canvas).cx;
      var lastCx = relBox(lastNode, canvas).cx;
      var targetCx = (firstCx + lastCx) / 2;
      var parentCx = relBox(parentEl, canvas).cx;
      var shift = targetCx - parentCx;

      if (Math.abs(shift) > 0.5) {
        parentEl.style.position = 'relative';
        parentEl.style.left = shift + 'px';
      }
    });
  }

  function drawLines(canvas) {
    var w = canvas.scrollWidth;
    var h = canvas.scrollHeight;

    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'family-tree-lines');
    svg.setAttribute('width', String(w));
    svg.setAttribute('height', String(h));
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);

    canvas.querySelectorAll('.family-tree-children').forEach(function (ul) {
      var parentEl = parentNode(ul);
      if (!parentEl) return;

      var items = ul.querySelectorAll(':scope > li');
      if (!items.length) return;

      var parentBox = relBox(parentEl, canvas);
      var parentX = parentBox.cx;
      var parentY = parentBox.bottom;

      var childPoints = [];
      items.forEach(function (li) {
        var node = directNode(li);
        if (!node) return;
        var box = relBox(node, canvas);
        childPoints.push({ x: box.cx, y: box.top });
      });

      if (!childPoints.length) return;

      if (childPoints.length === 1) {
        addPath(svg, [
          [parentX, parentY],
          [childPoints[0].x, childPoints[0].y],
        ]);
        return;
      }

      var ulPad = parseFloat(getComputedStyle(ul).paddingTop) || 28;
      var barY = parentY + ulPad * 0.5;
      var leftX = childPoints[0].x;
      var rightX = childPoints[childPoints.length - 1].x;

      addPath(svg, [
        [parentX, parentY],
        [parentX, barY],
      ]);

      addPath(svg, [
        [leftX, barY],
        [rightX, barY],
      ]);

      childPoints.forEach(function (pt) {
        addPath(svg, [
          [pt.x, barY],
          [pt.x, pt.y],
        ]);
      });
    });

    canvas.appendChild(svg);
    canvas.classList.add('family-tree-canvas--wired');
  }

  function addPath(svg, points) {
    if (points.length < 2) return;
    var d = 'M ' + points[0][0] + ' ' + points[0][1];
    for (var i = 1; i < points.length; i++) {
      d += ' L ' + points[i][0] + ' ' + points[i][1];
    }
    var path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', d);
    svg.appendChild(path);
  }

  function centerPan(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    var maxX = pan.scrollWidth - pan.clientWidth;
    pan.scrollLeft = maxX > 0 ? maxX / 2 : 0;
  }

  function layoutBranch(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    resetLayout(canvas);

    requestAnimationFrame(function () {
      alignParents(canvas);
      drawLines(canvas);

      var boxH = canvas.getBoundingClientRect().height;
      pan.style.minHeight = Math.min(Math.max(Math.ceil(boxH + 24), 320), window.innerHeight * 0.88) + 'px';
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

  var themeObserver = new MutationObserver(onResize);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });

  if (typeof ResizeObserver !== 'undefined') {
    pans.forEach(function (pan) {
      new ResizeObserver(onResize).observe(pan);
    });
  }

  layoutAll();
})();
