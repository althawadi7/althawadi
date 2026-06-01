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
    return li.querySelector(
      ':scope > .family-tree-unit > .family-tree-node, :scope > .family-tree-unit > a.family-tree-node--link, :scope > .family-tree-unit--leaf > .family-tree-node, :scope > .family-tree-unit--leaf > a.family-tree-node--link'
    );
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

  function rowGap(ul) {
    var section = ul.closest('.family-tree-section');
    var raw = section
      ? getComputedStyle(section).getPropertyValue('--family-tree-h-gap').trim()
      : '0.35rem';
    if (raw.indexOf('rem') !== -1) return parseFloat(raw) * 16;
    return parseFloat(raw) || 6;
  }

  function rowPadTop(ul) {
    return parseFloat(getComputedStyle(ul).paddingTop) || 22;
  }

  function resetLayout(canvas) {
    canvas.querySelectorAll('.family-tree-parent').forEach(function (wrap) {
      wrap.style.transform = '';
      wrap.style.width = '';
    });
    canvas.querySelectorAll('.family-tree-unit').forEach(function (unit) {
      unit.style.width = '';
    });
    canvas.querySelectorAll('.family-tree-children').forEach(function (ul) {
      ul.style.position = '';
      ul.style.display = '';
      ul.style.width = '';
      ul.style.minWidth = '';
      ul.style.minHeight = '';
      ul.style.height = '';
      ul.style.marginLeft = '';
    });
    canvas.querySelectorAll('.family-tree-children > li').forEach(function (li) {
      li.style.position = '';
      li.style.left = '';
      li.style.top = '';
      li.style.width = '';
      li.style.height = '';
      li.style.transform = '';
    });
    canvas.querySelectorAll('.family-tree-lines').forEach(function (svg) {
      svg.remove();
    });
  }

  function measureNode(node) {
    if (!node) return 72;
    var clone = node.cloneNode(true);
    clone.style.cssText =
      'position:absolute;visibility:hidden;pointer-events:none;' +
      'width:auto;height:auto;display:inline-block;left:-99999px;top:0;';
    document.body.appendChild(clone);
    var w = clone.getBoundingClientRect().width;
    document.body.removeChild(clone);
    return Math.ceil(w) || 72;
  }

  /** Pack sibling columns tightly — width = subtree need, not flex stretch. */
  function compactRow(ul) {
    var items = Array.from(ul.querySelectorAll(':scope > li'));
    if (!items.length) {
      ul.style.width = '0px';
      ul.style.minHeight = '0px';
      return { width: 0, height: 0 };
    }

    ul.style.width = 'auto';
    ul.style.minWidth = '0';

    var gap = rowGap(ul);
    var padTop = rowPadTop(ul);
    var x = 0;
    var maxBottom = 0;

    items.forEach(function (li) {
      var unit = li.querySelector(':scope > .family-tree-unit');
      if (!unit) return;

      li.style.width = 'auto';
      unit.style.width = 'auto';

      var node = directNode(li);
      var nodeW = measureNode(node);
      var nodeH = node ? node.offsetHeight : 0;
      var nestedUl = unit.querySelector(':scope > .family-tree-children');
      var nestedSize = nestedUl ? compactRow(nestedUl) : { width: 0, height: 0 };
      var slotW = Math.max(nodeW, nestedSize.width);

      li.style.position = 'absolute';
      li.style.left = x + 'px';
      li.style.top = '0';
      li.style.width = slotW + 'px';
      unit.style.width = slotW + 'px';

      var parentWrapEl = unit.querySelector(':scope > .family-tree-parent');
      if (parentWrapEl) {
        parentWrapEl.style.width = 'auto';
        var shift = (slotW - nodeW) / 2;
        parentWrapEl.style.transform = shift > 0.5 ? 'translateX(' + round(shift) + 'px)' : '';
      }

      if (nestedUl && nestedSize.width > 0) {
        nestedUl.style.marginLeft = round((slotW - nestedSize.width) / 2) + 'px';
      }

      var bottom = nodeH + (nestedUl ? padTop + nestedSize.height : 0);
      maxBottom = Math.max(maxBottom, bottom);
      x += slotW + gap;
    });

    var totalW = Math.max(x - gap, 0);
    ul.style.position = 'relative';
    ul.style.display = 'block';
    ul.style.width = totalW + 'px';
    ul.style.minWidth = totalW + 'px';
    ul.style.minHeight = maxBottom + 'px';
    ul.style.height = maxBottom + 'px';

    return { width: totalW, height: maxBottom };
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

    var d = 'M ' + parentX + ' ' + parentY + ' L ' + parentX + ' ' + barY;
    d += ' M ' + minX + ' ' + barY + ' L ' + maxX + ' ' + barY;

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

    var rootUl = canvas.querySelector('.family-tree > li > .family-tree-unit > .family-tree-children');
    if (rootUl) compactRow(rootUl);

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
