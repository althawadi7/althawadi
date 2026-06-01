(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  var resizeTimer;
  var layoutPending = false;
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
      top: er.top - cr.top,
      bottom: er.top - cr.top + er.height,
    };
  }

  function resetLayout(canvas) {
    canvas.querySelectorAll('.family-tree-node, .family-tree-node--link').forEach(function (node) {
      node.style.position = '';
      node.style.left = '';
    });
    canvas.querySelectorAll('.family-tree-lines').forEach(function (svg) {
      svg.remove();
    });
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

  function forkPath(parentX, parentY, barY, childPoints) {
    if (childPoints.length === 1) {
      var c = childPoints[0];
      return 'M ' + parentX + ' ' + parentY + ' L ' + c.x + ' ' + c.y;
    }

    var leftX = childPoints[0].x;
    var rightX = childPoints[childPoints.length - 1].x;
    var d = 'M ' + parentX + ' ' + parentY + ' L ' + parentX + ' ' + barY;
    d += ' M ' + leftX + ' ' + barY + ' L ' + rightX + ' ' + barY;

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

      var ulPad = parseFloat(getComputedStyle(ul).paddingTop) || 28;
      var barY = parentY + ulPad * 0.5;

      var path = document.createElementNS(SVG_NS, 'path');
      path.setAttribute('d', forkPath(parentX, parentY, barY, childPoints));
      svg.appendChild(path);
    });

    if (svg.childNodes.length) {
      canvas.insertBefore(svg, canvas.firstChild);
    }
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
      var nextMin = Math.min(Math.max(Math.ceil(boxH + 24), 320), window.innerHeight * 0.88);
      if (Math.abs(parseFloat(pan.style.minHeight) - nextMin) > 2) {
        pan.style.minHeight = nextMin + 'px';
      }
      centerPan(pan);
      layoutPending = false;
    });
  }

  function layoutAll() {
    if (layoutPending) return;
    layoutPending = true;
    pans.forEach(layoutBranch);
  }

  function onResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(layoutAll, 150);
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
      var canvas = pan.querySelector('.family-tree-canvas');
      if (canvas) {
        new ResizeObserver(onResize).observe(canvas);
      }
    });
  }

  layoutAll();

  window.__familyTreeLayout = layoutAll;
})();
