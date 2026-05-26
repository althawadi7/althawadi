(function () {
  'use strict';

  var search = document.getElementById('ref-global-search');
  var countEl = document.getElementById('ref-global-count');
  var emptyEl = document.getElementById('ref-global-empty');
  var lightbox = document.getElementById('ref-ig-lightbox');
  var lightboxMedia = document.getElementById('ref-ig-lightbox-media');
  var detailsDialog = document.getElementById('ref-details-dialog');
  var detailsTitle = document.getElementById('ref-details-title');
  var detailsBody = document.getElementById('ref-details-body');
  var detailsTrigger = null;

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

  function openLightbox(type, src, poster) {
    if (!lightbox || !lightboxMedia) return;
    closeDetailsDialog();

    lightboxMedia.innerHTML = '';
    if (type === 'video') {
      var video = document.createElement('video');
      video.className = 'ref-ig-lightbox-full';
      video.controls = true;
      video.playsInline = true;
      video.autoplay = true;
      video.preload = 'auto';
      if (poster) video.poster = poster;
      video.src = src;
      lightboxMedia.appendChild(video);
    } else {
      var img = document.createElement('img');
      img.className = 'ref-ig-lightbox-full';
      img.src = src;
      img.alt = '';
      img.decoding = 'async';
      lightboxMedia.appendChild(img);
    }

    lightbox.hidden = false;
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.classList.add('ref-ig-lightbox-open');
    var closeBtn = lightbox.querySelector('.ref-ig-lightbox-close');
    if (closeBtn) closeBtn.focus();
  }

  function closeLightbox() {
    if (!lightbox || !lightboxMedia) return;
    var video = lightboxMedia.querySelector('video');
    if (video) {
      video.pause();
      video.removeAttribute('src');
      video.load();
    }
    lightboxMedia.innerHTML = '';
    lightbox.hidden = true;
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('ref-ig-lightbox-open');
  }

  function openDetailsDialog(card) {
    if (!detailsDialog || !detailsBody || !card) return;
    closeLightbox();

    var titleEl = card.querySelector('.ref-ig-card-title');
    var fulltext = card.querySelector('.ref-ig-fulltext');
    if (!fulltext) return;

    if (detailsTitle) {
      detailsTitle.textContent = titleEl ? titleEl.textContent.trim() : 'التفاصيل';
    }
    detailsBody.innerHTML = fulltext.innerHTML;

    detailsDialog.hidden = false;
    detailsDialog.setAttribute('aria-hidden', 'false');
    document.body.classList.add('ref-details-open');

    var closeBtn = detailsDialog.querySelector('.ref-details-close');
    if (closeBtn) closeBtn.focus();
  }

  function closeDetailsDialog() {
    if (!detailsDialog || !detailsBody) return;
    detailsDialog.hidden = true;
    detailsDialog.setAttribute('aria-hidden', 'true');
    detailsBody.innerHTML = '';
    document.body.classList.remove('ref-details-open');
    if (detailsTrigger && typeof detailsTrigger.focus === 'function') {
      detailsTrigger.focus();
    }
    detailsTrigger = null;
  }

  function isDialogOpen(el) {
    return el && !el.hidden;
  }

  document.addEventListener('click', function (e) {
    var mediaBtn = e.target.closest('.ref-ig-lightbox-trigger');
    if (mediaBtn) {
      e.preventDefault();
      openLightbox(
        mediaBtn.getAttribute('data-type') || 'image',
        mediaBtn.getAttribute('data-src') || '',
        mediaBtn.getAttribute('data-poster') || ''
      );
      return;
    }

    var summary = e.target.closest('.ref-ig-details summary');
    if (summary) {
      e.preventDefault();
      var card = summary.closest('.ref-ig-card');
      var details = summary.closest('details');
      if (details) details.open = false;
      detailsTrigger = summary;
      openDetailsDialog(card);
    }
  });

  if (lightbox) {
    var lbClose = lightbox.querySelector('.ref-ig-lightbox-close');
    var lbBackdrop = lightbox.querySelector('.ref-ig-lightbox-backdrop');
    if (lbClose) lbClose.addEventListener('click', closeLightbox);
    if (lbBackdrop) lbBackdrop.addEventListener('click', closeLightbox);
  }

  if (detailsDialog) {
    var detClose = detailsDialog.querySelector('.ref-details-close');
    var detBackdrop = detailsDialog.querySelector('.ref-details-backdrop');
    if (detClose) detClose.addEventListener('click', closeDetailsDialog);
    if (detBackdrop) detBackdrop.addEventListener('click', closeDetailsDialog);
  }

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (isDialogOpen(detailsDialog)) {
      closeDetailsDialog();
    } else if (isDialogOpen(lightbox)) {
      closeLightbox();
    }
  });

  if (search) search.addEventListener('input', filterAll);

  filterAll();
})();
