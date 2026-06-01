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

  function stemOffset() {
    var section = document.querySelector('.family-tree-section');
    var raw = section
      ? getComputedStyle(section).getPropertyValue('--family-tree-stem').trim()
      : '1.5rem';
    if (raw.indexOf('rem') !== -1) return parseFloat(raw) * 16;
    return parseFloat(raw) || 24;
  }

  function addSegment(svg, x1, y1, x2, y2) {
    if (Math.abs(x1 - x2) < 0.25 && Math.abs(y1 - y2) < 0.25) return;
    var line = document.createElementNS(SVG_NS, 'line');
    line.setAttribute('x1', String(round(x1)));
    line.setAttribute('y1', String(round(y1)));
    line.setAttribute('x2', String(round(x2)));
    line.setAttribute('y2', String(round(y2)));
    svg.appendChild(line);
  }

  function barYFor(parentY, childTop) {
    var gap = childTop - parentY;
    var minStem = stemOffset();
    if (gap < 12) gap = minStem;

    /* Bar must sit clearly BETWEEN parent bottom and child tops */
    var y = parentY + Math.max(gap * 0.42, minStem * 0.55);
    y = Math.min(y, childTop - 10);
    y = Math.max(y, parentY + 8);
    return round(y);
  }

  function drawFork(svg, parentX, parentY, childPoints) {
    if (childPoints.length === 1) {
      var c = childPoints[0];
      addSegment(svg, parentX, parentY, c.x, c.y);
      return;
    }

    var xs = childPoints.map(function (pt) {
      return pt.x;
    });
    var minX = Math.min.apply(null, xs);
    var maxX = Math.max.apply(null, xs);
    var childTop = childPoints.reduce(function (min, pt) {
      return Math.min(min, pt.y);
    }, childPoints[0].y);
    var barY = barYFor(parentY, childTop);

    /* 1) Father down to junction */
    addSegment(svg, parentX, parentY, parentX, barY);

    /* 2) Horizontal across all sons */
    addSegment(svg, minX, barY, maxX, barY);

    /* 3) Down into top of each card */
    childPoints.forEach(function (pt) {
      addSegment(svg, pt.x, barY, pt.x, pt.y);
    });
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

      var childPoints = [];
      ul.querySelectorAll(':scope > li').forEach(function (li) {
        var node = directNode(li);
        if (!node) return;
        var box = relBox(node, canvas);
        childPoints.push({ x: box.cx, y: box.top + 1 });
      });
      if (!childPoints.length) return;

      var parentBox = relBox(parentEl, canvas);
      drawFork(svg, parentBox.cx, parentBox.bottom, childPoints);
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
