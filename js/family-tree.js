(function () {
  'use strict';

  var pans = document.querySelectorAll('.family-tree-pan');
  if (!pans.length) return;

  var MEMBER_SELECTOR =
    '.tree li > .family-tree-node, .tree li > a.family-tree-node, .tree li > a.family-tree-node--link';

  function countTreeMembers() {
    var tree = document.querySelector('.tree');
    if (!tree) return 0;
    return tree.querySelectorAll(MEMBER_SELECTOR).length;
  }

  function updateMemberCount() {
    var wrap = document.getElementById('family-tree-member-count');
    if (!wrap) return;

    var total = countTreeMembers();
    var numEl = wrap.querySelector('.family-tree-member-count-num');
    if (numEl) {
      numEl.textContent = total.toLocaleString('ar');
    }
    wrap.setAttribute('aria-label', 'إجمالي الأفراد في الشجرة: ' + total);
  }

  window.__familyTreeCountMembers = countTreeMembers;
  window.__familyTreeUpdateMemberCount = updateMemberCount;

  function centerPan(pan) {
    var maxX = pan.scrollWidth - pan.clientWidth;
    var maxY = pan.scrollHeight - pan.clientHeight;
    pan.scrollLeft = maxX > 0 ? maxX / 2 : 0;
    pan.scrollTop = maxY > 0 ? 0 : 0;
  }

  function layoutAll() {
    pans.forEach(function (pan) {
      var canvas = pan.querySelector('.family-tree-canvas');
      centerPan(pan);
      if (canvas) {
        pan.style.minHeight = Math.max(canvas.scrollHeight + 56, 520) + 'px';
      }
    });
  }

  function onResize() {
    clearTimeout(layoutAll._timer);
    layoutAll._timer = setTimeout(layoutAll, 200);
  }

  function runInitial() {
    updateMemberCount();
    layoutAll();
    requestAnimationFrame(function () {
      updateMemberCount();
      layoutAll();
    });
  }

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(runInitial);
  } else {
    runInitial();
  }

  window.addEventListener('load', runInitial);
  window.addEventListener('resize', onResize);

  var themeObserver = new MutationObserver(onResize);
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });

  window.__familyTreeLayout = layoutAll;
})();
