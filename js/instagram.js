(function () {
  'use strict';

  var feedRoot = document.getElementById('instagram-feed');
  if (!feedRoot) return;

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

  function captionPreview(caption, max) {
    var clean = String(caption || '').replace(/\s+/g, ' ').trim();
    if (clean.length <= max) return clean;
    return clean.slice(0, max).trim() + '…';
  }

  function renderProfile(data) {
    var bioHtml = escapeHtml(data.biography || '').replace(/\n/g, '<br />');
    return (
      '<div class="ig-profile border border-border rounded-sm p-6 bg-card/60">' +
        '<div class="ig-profile-inner">' +
          '<img class="ig-profile-pic" src="' + escapeHtml(data.profile_pic) + '" alt="' + escapeHtml(data.full_name) + '" loading="lazy" width="96" height="96" />' +
          '<div class="ig-profile-meta">' +
            '<h2 class="font-display text-2xl text-foreground">' + escapeHtml(data.full_name) + '</h2>' +
            '<p class="mt-1 text-sm font-latin text-muted-foreground">@' + escapeHtml(data.username) + '</p>' +
            '<p class="mt-3 text-sm text-muted-foreground leading-8">' + bioHtml + '</p>' +
            '<dl class="ig-stats">' +
              '<div><dt>منشورات</dt><dd>' + (data.posts_count || 0) + '</dd></div>' +
              '<div><dt>متابعون</dt><dd>' + (data.followers || 0) + '</dd></div>' +
              '<div><dt>يتابع</dt><dd>' + (data.following || 0) + '</dd></div>' +
            '</dl>' +
            '<a href="' + escapeHtml(data.profile_url) + '" target="_blank" rel="noreferrer" class="mt-4 inline-flex items-center gap-2 rounded-sm bg-primary px-5 py-2.5 text-sm text-primary-foreground hover:bg-primary/90 transition-colors">' +
              '<span>تابعونا على Instagram</span>' +
            '</a>' +
          '</div>' +
        '</div>' +
      '</div>'
    );
  }

  function renderPosts(posts) {
    if (!posts || !posts.length) {
      return '<p class="text-sm text-muted-foreground text-center py-8">لا توجد منشورات حالياً.</p>';
    }

    return (
      '<div class="ig-grid">' +
        posts.map(function (post) {
          var img = post.local_image || post.thumbnail || post.display_url;
          var typeLabel = post.type === 'GraphVideo' ? 'فيديو' : post.type === 'GraphSidecar' ? 'ألبوم' : 'صورة';
          return (
            '<article class="ig-card">' +
              '<a href="' + escapeHtml(post.url) + '" target="_blank" rel="noreferrer" class="ig-card-link">' +
                '<div class="ig-card-media">' +
                  '<img src="' + escapeHtml(img) + '" alt="" loading="lazy" />' +
                  '<span class="ig-card-type">' + typeLabel + '</span>' +
                '</div>' +
                '<div class="ig-card-body">' +
                  '<time class="ig-card-date" datetime="' + escapeHtml(String(post.timestamp || '')) + '">' + formatDate(post.timestamp) + '</time>' +
                  '<p class="ig-card-caption">' + escapeHtml(captionPreview(post.caption, 220)) + '</p>' +
                  '<span class="ig-card-more">عرض على Instagram ←</span>' +
                '</div>' +
              '</a>' +
            '</article>'
          );
        }).join('') +
      '</div>'
    );
  }

  feedRoot.innerHTML = '<p class="text-sm text-muted-foreground text-center py-10">جاري تحميل منشورات المجلس…</p>';

  fetch('data/instagram.json')
    .then(function (res) {
      if (!res.ok) throw new Error('fetch failed');
      return res.json();
    })
    .then(function (data) {
      feedRoot.innerHTML =
        renderProfile(data) +
        '<div class="mt-12">' +
          '<h2 class="font-display text-2xl text-foreground mb-6">آخر المنشورات</h2>' +
          renderPosts(data.recent_posts) +
        '</div>' +
        (data.fetched_at
          ? '<p class="mt-8 text-center text-xs text-muted-foreground">آخر تحديث للبيانات: ' + escapeHtml(data.fetched_at) + '</p>'
          : '');
    })
    .catch(function () {
      feedRoot.innerHTML =
        '<div class="notice-box text-center">' +
          '<p class="text-sm text-muted-foreground leading-8" style="margin:0;">تعذّر تحميل المنشورات. تابعوا حسابنا مباشرة على ' +
          '<a href="https://www.instagram.com/althawadi_majlis/?hl=ar" class="text-accent hover:underline" target="_blank" rel="noreferrer">@althawadi_majlis</a>.' +
          '</p>' +
        '</div>';
    });
})();
