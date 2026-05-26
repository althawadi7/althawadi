(function () {
  'use strict';

  var root = document.getElementById('instagram-history-archive');
  if (!root) return;

  function escapeHtml(text) {
    return String(text || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatDate(ts) {
    if (!ts) return '';
    try {
      return new Intl.DateTimeFormat('ar-BH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }).format(new Date(ts * 1000));
    } catch (e) {
      return '';
    }
  }

  function cleanCaption(text) {
    return String(text || '')
      .replace(/^[\s"]+/, '')
      .replace(/[\s"]+$/, '')
      .replace(/"\n/g, '\n')
      .trim();
  }

  function captionToHtml(caption) {
    var clean = cleanCaption(caption);
    if (!clean) return '';

    var paragraphs = clean.split(/\n\n+/);
    return paragraphs
      .map(function (para) {
        var lines = para.split('\n').filter(function (l) { return l.trim(); });
        if (!lines.length) return '';
        var inner = lines
          .map(function (line) {
            return linkifyHashtags(escapeHtml(line.trim()));
          })
          .join('<br />');
        return '<p class="ig-archive-caption-p">' + inner + '</p>';
      })
      .join('');
  }

  function linkifyHashtags(html) {
    return html.replace(/#([\u0600-\u06FF\w]+)/g, function (_, tag) {
      return (
        '<a href="https://www.instagram.com/explore/tags/' +
        encodeURIComponent(tag) +
        '/" class="ig-archive-tag" target="_blank" rel="noreferrer">#' +
        tag +
        '</a>'
      );
    });
  }

  function typeLabel(type) {
    if (type === 'album') return 'ألبوم';
    if (type === 'video') return 'فيديو';
    return 'صورة';
  }

  function renderPost(post, index) {
    var imgs = post.local_images && post.local_images.length
      ? post.local_images
      : post.cover
        ? [post.cover]
        : [];
    var cover = imgs[0] || '';
    var dateStr = formatDate(post.timestamp);
    var id = 'ig-' + post.shortcode;

    var mediaHtml = '';
    if (imgs.length > 1) {
      mediaHtml =
        '<div class="ig-archive-gallery">' +
        imgs
          .map(function (src, i) {
            return (
              '<figure class="ig-archive-figure">' +
              '<img src="' +
              escapeHtml(src) +
              '" alt="صورة ' +
              (i + 1) +
              ' من المنشور" loading="lazy" />' +
              '</figure>'
            );
          })
          .join('') +
        '</div>';
    } else if (cover) {
      mediaHtml =
        '<figure class="ig-archive-figure ig-archive-figure--solo">' +
        '<a href="' +
        escapeHtml(post.url) +
        '" target="_blank" rel="noreferrer">' +
        '<img src="' +
        escapeHtml(cover) +
        '" alt="منشور ' +
        escapeHtml(String(index + 1)) +
        ' من أرشيف مجلس الذواودة" loading="lazy" />' +
        '</a>' +
        '</figure>';
    }

    return (
      '<article class="ig-archive-item" id="' +
      escapeHtml(id) +
      '">' +
      '<header class="ig-archive-item-head">' +
      '<span class="ig-archive-num">' +
      String(index + 1).padStart(2, '0') +
      '</span>' +
      '<div class="ig-archive-item-meta">' +
      (dateStr ? '<time datetime="' + escapeHtml(String(post.timestamp)) + '">' + escapeHtml(dateStr) + '</time>' : '') +
      '<span class="ig-archive-type">' +
      escapeHtml(typeLabel(post.type)) +
      '</span>' +
      '</div>' +
      '<a href="' +
      escapeHtml(post.url) +
      '" target="_blank" rel="noreferrer" class="ig-archive-ig-link font-latin">Instagram ↗</a>' +
      '</header>' +
      '<div class="ig-archive-item-body">' +
      mediaHtml +
      '<div class="ig-archive-text">' +
      captionToHtml(post.caption) +
      '<a href="' +
      escapeHtml(post.url) +
      '" target="_blank" rel="noreferrer" class="ig-archive-source">المصدر: @althawadi_majlis</a>' +
      '</div>' +
      '</div>' +
      '</article>'
    );
  }

  function renderArchive(data) {
    var posts = (data && data.posts) || [];
    if (!posts.length) {
      root.innerHTML =
        '<p class="text-sm text-muted-foreground text-center py-8">لا توجد منشورات في الأرشيف.</p>';
      return;
    }
    root.innerHTML =
      '<div class="ig-archive-list">' +
      posts.map(renderPost).join('') +
      '</div>' +
      (data.fetched_at
        ? '<p class="ig-archive-updated">آخر تحديث للأرشيف: ' +
          escapeHtml(data.fetched_at) +
          ' — ' +
          posts.length +
          ' منشوراً</p>'
        : '');
  }

  if (window.INSTAGRAM_HISTORY_DATA) {
    renderArchive(window.INSTAGRAM_HISTORY_DATA);
    return;
  }

  root.innerHTML =
    '<p class="text-sm text-muted-foreground text-center py-10">جاري تحميل الأرشيف…</p>';

  fetch('data/instagram-history.json')
    .then(function (res) {
      if (!res.ok) throw new Error('fetch failed');
      return res.json();
    })
    .then(renderArchive)
    .catch(function () {
      root.innerHTML =
        '<div class="notice-box text-center">' +
        '<p class="text-sm text-muted-foreground leading-8" style="margin:0;">تعذّر تحميل الأرشيف. افتحوا ' +
        '<a href="archive.html" class="text-accent hover:underline">archive.html</a> أو راجعوا ' +
        '<a href="https://www.instagram.com/althawadi_majlis/?hl=ar" class="text-accent hover:underline" target="_blank" rel="noreferrer">@althawadi_majlis</a>.' +
        '</p></div>';
    });
})();
