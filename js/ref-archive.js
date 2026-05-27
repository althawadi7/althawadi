(function () {
  'use strict';

  var search = document.getElementById('ref-global-search');
  var countEl = document.getElementById('ref-global-count');
  var emptyEl = document.getElementById('ref-global-empty');

  var cards = Array.prototype.slice.call(
    document.querySelectorAll('#ref-all-grid > .ref-ig-card')
  );
  var total = cards.length;

  function normalize(text) {
    return String(text || '')
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .trim();
  }

  function filterAll() {
    var q = normalize(search ? search.value : '');
    var visible = 0;

    cards.forEach(function (card) {
      var hay = normalize(card.getAttribute('data-search') || card.textContent);
      var show = !q || hay.indexOf(q) !== -1;
      card.classList.toggle('is-hidden', !show);
      card.hidden = !show;
      if (show) visible += 1;
    });

    if (countEl) {
      countEl.textContent = q
        ? visible + ' من ' + total + ' نتيجة'
        : total + ' مرجع ومنشور';
    }
    if (emptyEl) emptyEl.hidden = visible > 0;
  }

  if (search) search.addEventListener('input', filterAll);

  filterAll();
})();
