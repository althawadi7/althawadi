(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  var resizeTimer;
  var SVG_NS = 'http://www.w3.org/2000/svg';
  var CORNER_R = 10;

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

  function addPath(svg, d) {
    var path = document.createElementNS(SVG_NS, 'path');
    path.setAttribute('d', d);
    svg.appendChild(path);
  }

  /** One continuous trunk + horizontal bar (no gaps). */
  function trunkAndBar(parentX, parentY, barY, leftX, rightX) {
    var minX = Math.min(leftX, rightX, parentX);
    var maxX = Math.max(leftX, rightX, parentX);
    var d = 'M ' + parentX + ' ' + parentY;
    d += ' L ' + parentX + ' ' + barY;
    if (Math.abs(minX - parentX) > 0.5) {
      d += ' L ' + minX + ' ' + barY;
    }
    if (Math.abs(maxX - minX) > 0.5) {
      d += ' L ' + maxX + ' ' + barY;
    }
    return d;
  }

  /** Curved drop from bar down into child card top. */
  function curvedDrop(x, barY, childY) {
    var drop = childY - barY;
    var r = Math.min(CORNER_R, Math.max(4, drop * 0.35));
    if (drop <= r * 2) {
      return 'M ' + x + ' ' + barY + ' L ' + x + ' ' + childY;
    }
    return (
      'M ' + x + ' ' + barY +
      ' C ' + x + ' ' + (barY + r) +
      ' ' + x + ' ' + (barY + r) +
      ' ' + x + ' ' + (barY + r * 1.6) +
      ' L ' + x + ' ' + childY
    );
  }

  /** Curved link parent → single child. */
  function parentToChild(parentX, parentY, childX, childY) {
    if (Math.abs(parentX - childX) < 1) {
      return 'M ' + parentX + ' ' + parentY + ' L ' + childX + ' ' + childY;
    }
    var midY = parentY + (childY - parentY) * 0.45;
    return (
      'M ' + parentX + ' ' + parentY +
      ' C ' + parentX + ' ' + midY +
      ' ' + childX + ' ' + midY +
      ' ' + childX + ' ' + childY
    );
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
        addPath(
          svg,
          parentToChild(parentX, parentY, childPoints[0].x, childPoints[0].y)
        );
        return;
      }

      var ulPad = parseFloat(getComputedStyle(ul).paddingTop) || 28;
      var barY = parentY + ulPad * 0.5;
      var leftX = childPoints[0].x;
      var rightX = childPoints[childPoints.length - 1].x;

      addPath(svg, trunkAndBar(parentX, parentY, barY, leftX, rightX));

      childPoints.forEach(function (pt) {
        addPath(svg, curvedDrop(pt.x, barY, pt.y));
      });
    });

    canvas.appendChild(svg);
    canvas.classList.add('family-tree-canvas--wired');
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

  window.__familyTreeLayout = layoutAll;
})();
