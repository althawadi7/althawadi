(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  var resizeTimer;
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function round(n) {
    return Math.round(n * 10) / 10;
  }

  function directNode(li) {
    return li.querySelector(':scope > .family-tree-unit > .family-tree-node, :scope > .family-tree-unit > a.family-tree-node--link, :scope > .family-tree-unit--leaf > .family-tree-node, :scope > .family-tree-unit--leaf > a.family-tree-node--link, :scope > .family-tree-node, :scope > a.family-tree-node--link');
  }

  function parentWrap(ul) {
    var unit = ul.parentElement;
    if (!unit || !unit.classList.contains('family-tree-unit')) return null;
    return unit.querySelector(':scope > .family-tree-parent');
  }

  function parentNode(ul) {
    var wrap = parentWrap(ul);
    if (!wrap) return null;
    return wrap.querySelector('.family-tree-node, .family-tree-node--link');
  }

  function relBox(el, canvas) {
    var er = el.getBoundingClientRect();
    var cr = canvas.getBoundingClientRect();
    return {
      cx: round(er.left - cr.left + er.width / 2),
      top: round(er.top - cr.top),
      bottom: round(er.bottom - cr.top),
    };
  }

  function resetLayout(canvas) {
    canvas.querySelectorAll('.family-tree-parent').forEach(function (wrap) {
      wrap.style.transform = '';
    });
    canvas.querySelectorAll('.family-tree-node, .family-tree-node--link').forEach(function (node) {
      node.style.transform = '';
      node.style.position = '';
      node.style.left = '';
    });
    canvas.querySelectorAll('.family-tree-lines').forEach(function (svg) {
      svg.remove();
    });
  }

  function childCenters(canvas, ul) {
    var items = ul.querySelectorAll(':scope > li');
    var points = [];
    items.forEach(function (li) {
      var node = directNode(li);
      if (!node) return;
      var box = relBox(node, canvas);
      points.push({ x: box.cx, y: box.top });
    });
    return points;
  }

  function alignParents(canvas) {
    canvas.querySelectorAll('.family-tree-children').forEach(function (ul) {
      var wrap = parentWrap(ul);
      var parentEl = parentNode(ul);
      if (!wrap || !parentEl) return;

      var points = childCenters(canvas, ul);
      if (!points.length) return;

      var minX = points[0].x;
      var maxX = points[0].x;
      points.forEach(function (pt) {
        minX = Math.min(minX, pt.x);
        maxX = Math.max(maxX, pt.x);
      });

      var targetCx = (minX + maxX) / 2;
      var parentCx = relBox(parentEl, canvas).cx;
      var shift = targetCx - parentCx;

      if (Math.abs(shift) > 0.5) {
        wrap.style.transform = 'translateX(' + round(shift) + 'px)';
      } else {
        wrap.style.transform = '';
      }
    });
  }

  function forkPath(parentX, parentY, barY, childPoints) {
    if (childPoints.length === 1) {
      var c = childPoints[0];
      return 'M ' + parentX + ' ' + parentY + ' L ' + c.x + ' ' + c.y;
    }

    var xs = childPoints.map(function (pt) {
      return pt.x;
    });
    var minX = Math.min.apply(null, xs);
    var maxX = Math.max.apply(null, xs);
    var barMin = Math.min(minX, parentX);
    var barMax = Math.max(maxX, parentX);

    var d = 'M ' + parentX + ' ' + parentY + ' L ' + parentX + ' ' + barY;
    d += ' M ' + barMin + ' ' + barY + ' L ' + barMax + ' ' + barY;

    childPoints.forEach(function (pt) {
      d += ' M ' + pt.x + ' ' + barY + ' L ' + pt.x + ' ' + pt.y;
    });

    return d;
  }

  function drawLines(canvas) {
    canvas.querySelectorAll('.family-tree-lines').forEach(function (svg) {
      svg.remove();
    });

    var w = Math.max(canvas.scrollWidth, 1);
    var h = Math.max(canvas.scrollHeight, 1);

    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('class', 'family-tree-lines');
    svg.setAttribute('width', String(w));
    svg.setAttribute('height', String(h));
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    svg.style.width = w + 'px';
    svg.style.height = h + 'px';

    canvas.querySelectorAll('.family-tree-children').forEach(function (ul) {
      var parentEl = parentNode(ul);
      if (!parentEl) return;

      var childPoints = childCenters(canvas, ul);
      if (!childPoints.length) return;

      var parentBox = relBox(parentEl, canvas);
      var parentX = parentBox.cx;
      var parentY = parentBox.bottom;
      var childTop = childPoints.reduce(function (min, pt) {
        return Math.min(min, pt.y);
      }, childPoints[0].y);
      var barY = round(parentY + (childTop - parentY) * 0.5);

      var path = document.createElementNS(SVG_NS, 'path');
      path.setAttribute('d', forkPath(parentX, parentY, barY, childPoints));
      svg.appendChild(path);
    });

    if (svg.childNodes.length) {
      canvas.insertBefore(svg, canvas.firstChild);
    }
  }

  function layoutCanvas(canvas) {
    resetLayout(canvas);
    alignParents(canvas);
    drawLines(canvas);
    alignParents(canvas);
    drawLines(canvas);
  }

  function centerPan(pan) {
    var maxX = pan.scrollWidth - pan.clientWidth;
    pan.scrollLeft = maxX > 0 ? maxX / 2 : 0;
  }

  function layoutBranch(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    layoutCanvas(canvas);

    var boxH = canvas.getBoundingClientRect().height;
    pan.style.minHeight = Math.min(Math.max(Math.ceil(boxH + 24), 320), window.innerHeight * 0.88) + 'px';
    centerPan(pan);
  }

  function layoutAll() {
    pans.forEach(layoutBranch);
  }

  function onResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(layoutAll, 200);
  }

  function runInitialLayout() {
    layoutAll();
    requestAnimationFrame(function () {
      layoutAll();
    });
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(runInitialLayout);
  } else {
    runInitialLayout();
  }

  window.addEventListener('load', runInitialLayout);
  window.addEventListener('resize', onResize);

  var themeObserver = new MutationObserver(onResize);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });

  window.__familyTreeLayout = layoutAll;
})();
