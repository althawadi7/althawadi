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

  function parentNode(ul) {
    var unit = ul.parentElement;
    if (!unit || !unit.classList.contains('family-tree-unit')) return null;
    var wrap = unit.querySelector(':scope > .family-tree-parent');
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

  /** One continuous stem + horizontal bar, then drops to each child. */
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

    var d = 'M ' + parentX + ' ' + parentY;
    d += ' L ' + parentX + ' ' + barY;
    d += ' L ' + minX + ' ' + barY;
    d += ' L ' + maxX + ' ' + barY;

    childPoints.forEach(function (pt) {
      d += ' M ' + pt.x + ' ' + barY + ' L ' + pt.x + ' ' + pt.y;
    });

    return d;
  }

  function stemOffset() {
    var section = document.querySelector('.family-tree-section');
    var raw = section
      ? getComputedStyle(section).getPropertyValue('--family-tree-stem').trim()
      : '1.5rem';
    if (raw.indexOf('rem') !== -1) return parseFloat(raw) * 16;
    return parseFloat(raw) || 24;
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

    var minStem = stemOffset();

    canvas.querySelectorAll('.family-tree-children').forEach(function (ul) {
      var parentEl = parentNode(ul);
      if (!parentEl) return;

      var childPoints = [];
      ul.querySelectorAll(':scope > li').forEach(function (li) {
        var node = directNode(li);
        if (!node) return;
        var box = relBox(node, canvas);
        childPoints.push({ x: box.cx, y: box.top });
      });
      if (!childPoints.length) return;

      var parentBox = relBox(parentEl, canvas);
      var parentX = parentBox.cx;
      var parentY = parentBox.bottom;
      var childTop = childPoints.reduce(function (min, pt) {
        return Math.min(min, pt.y);
      }, childPoints[0].y);
      var gap = childTop - parentY;
      var barY = round(parentY + Math.max(gap * 0.5, minStem * 0.45));

      var path = document.createElementNS(SVG_NS, 'path');
      path.setAttribute('d', forkPath(parentX, parentY, barY, childPoints));
      svg.appendChild(path);
    });

    if (svg.childNodes.length) {
      canvas.insertBefore(svg, canvas.firstChild);
    }
  }

  function clearLines(canvas) {
    canvas.querySelectorAll('.family-tree-lines').forEach(function (svg) {
      svg.remove();
    });
    canvas.querySelectorAll('.family-tree-parent').forEach(function (wrap) {
      wrap.style.transform = '';
    });
  }

  function layoutCanvas(canvas) {
    clearLines(canvas);
    drawLines(canvas);
  }

  function centerPan(pan) {
    var maxX = pan.scrollWidth - pan.clientWidth;
    pan.scrollLeft = maxX > 0 ? maxX / 2 : 0;
    pan.scrollTop = 0;
  }

  function layoutBranch(pan) {
    var canvas = pan.querySelector('.family-tree-canvas');
    if (!canvas) return;

    layoutCanvas(canvas);

    var boxH = canvas.getBoundingClientRect().height;
    pan.style.minHeight =
      Math.min(Math.max(Math.ceil(boxH + 48), 480), window.innerHeight * 0.92) + 'px';
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
      requestAnimationFrame(layoutAll);
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
