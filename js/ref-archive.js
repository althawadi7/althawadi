(function () {
  'use strict';

  var grid = document.getElementById('ref-ig-grid');
  var searchInput = document.getElementById('ref-ig-search');
  var countEl = document.getElementById('ref-ig-count');
  var emptyEl = document.getElementById('ref-ig-empty');
  var lightbox = document.getElementById('ref-ig-lightbox');
  var lightboxMedia = document.getElementById('ref-ig-lightbox-media');

  if (!grid || !searchInput) return;

  var cards = Array.prototype.slice.call(grid.querySelectorAll('.ref-ig-card'));
  var total = cards.length;

  function normalize(text) {
    return String(text || '')
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .trim();
  }

  function filterPosts() {
    var q = normalize(searchInput.value);
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
        ? visible + ' من ' + total + ' منشور'
        : total + ' منشور';
    }
    if (emptyEl) {
      emptyEl.hidden = visible > 0;
    }
  }

  function openLightbox(type, src, poster) {
    if (!lightbox || !lightboxMedia) return;

    lightboxMedia.innerHTML = '';
    if (type === 'video') {
      var video = document.createElement('video');
      video.controls = true;
      video.playsInline = true;
      video.autoplay = true;
      video.preload = 'auto';
      if (poster) video.poster = poster;
      video.src = src;
      lightboxMedia.appendChild(video);
    } else {
      var img = document.createElement('img');
      img.src = src;
      img.alt = '';
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

  grid.addEventListener('click', function (e) {
    var btn = e.target.closest('.ref-ig-lightbox-trigger');
    if (!btn) return;
    e.preventDefault();
    openLightbox(
      btn.getAttribute('data-type') || 'image',
      btn.getAttribute('data-src') || '',
      btn.getAttribute('data-poster') || ''
    );
  });

  if (lightbox) {
    lightbox.querySelector('.ref-ig-lightbox-close').addEventListener('click', closeLightbox);
    lightbox.querySelector('.ref-ig-lightbox-backdrop').addEventListener('click', closeLightbox);
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && lightbox && !lightbox.hidden) {
      closeLightbox();
    }
  });

  searchInput.addEventListener('input', filterPosts);
  filterPosts();
})();
