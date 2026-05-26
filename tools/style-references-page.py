#!/usr/bin/env python3
"""Apply unified ref-grid card layout to references.html (sections 1–4, 6)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "references.html"
text = PATH.read_text(encoding="utf-8")

for marker in (
    '      <section class="mx-auto max-w-6xl px-6 pb-20 references-page">',
    '      <section class="mx-auto max-w-6xl px-6 pb-20">',
):
    if marker in text:
        start = text.index(marker)
        break
else:
    raise SystemExit("references main section not found")

end = text.index('        <div class="ref-archive-section" id="instagram-archive">')
head, mid, tail = text[:start], text[start:end], text[end:]

if "references-page" not in mid:
    mid = mid.replace(
        "      <section class=\"mx-auto max-w-6xl px-6 pb-20\">",
        "      <section class=\"mx-auto max-w-6xl px-6 pb-20 references-page\">",
        1,
    )

toolbar = """
        <div class="ref-ig-toolbar ref-page-toolbar">
          <label class="ref-ig-search-wrap">
            <span class="sr-only">بحث في المراجع</span>
            <input type="search" id="ref-page-search" class="ref-ig-search" placeholder="ابحث في كل المراجع والمصادر…" autocomplete="off" />
          </label>
          <p id="ref-page-count" class="ref-ig-count" aria-live="polite"></p>
        </div>
        <p id="ref-page-empty" class="ref-ig-empty" hidden>لا توجد نتائج مطابقة للبحث.</p>
"""

anchor = "          في سياق بني خالد والبحرين — للقراءة والتحقق الأكاديمي.\n        </p>"
if anchor in mid and "ref-page-search" not in mid:
    mid = mid.replace(anchor, anchor + toolbar, 1)

mid = re.sub(
    r'<ul class="space-y-6" style="list-style:none;padding:0;margin:0;">',
    '<ul class="ref-grid ref-source-grid">',
    mid,
)
mid = re.sub(
    r'<li class="border border-border rounded-sm p-6 bg-card/40"',
    '<li class="ref-card ref-source-card"',
    mid,
)
mid = re.sub(
    r'class="group block border border-border rounded-sm p-6 bg-card/40 hover:bg-card transition-colors"',
    'class="ref-card ref-card--link group block"',
    mid,
)
mid = re.sub(
    r'<li>\s*\n\s*<a href="(https://www\.alayam\.com[^"]+)"',
    r'<li class="ref-source-card ref-source-card--link">\n            <a href="\1"',
    mid,
)

if 'ref-doc-thumb' not in mid:
    mid = mid.replace(
        '<figure class="archive-doc">\n              <img src="assets/E5UyU7aXEAIYjw9.jpg"',
        '<figure class="archive-doc ref-card-media-wrap">\n              <button type="button" class="ref-ig-thumb ref-ig-lightbox-trigger ref-doc-thumb" data-type="image" data-src="assets/E5UyU7aXEAIYjw9.jpg" aria-label="عرض الوثيقة"><img src="assets/E5UyU7aXEAIYjw9.jpg"',
        1,
    )
    mid = mid.replace(
        'width="1200" height="900" />\n              <figcaption>',
        'width="1200" height="900" loading="lazy" /></button>\n              <figcaption>',
        1,
    )

tail = tail.replace(
    '<h2 class="ref-section-title">٦ — مجلس العائلة — تواصل رسمي</h2>\n        <ul class="space-y-6" style="list-style:none;padding:0;margin:0;">',
    '<h2 class="ref-section-title">٦ — مجلس العائلة — تواصل رسمي</h2>\n        <ul class="ref-grid ref-source-grid">',
    1,
)
tail = tail.replace(
    'class="group block border border-border rounded-sm p-6 bg-card/40 hover:bg-card transition-colors"',
    'class="ref-card ref-card--link group block"',
    1,
)
tail = tail.replace(
    '<li>\n            <a href="https://www.instagram.com/althawadi_majlis/',
    '<li class="ref-source-card ref-source-card--link">\n            <a href="https://www.instagram.com/althawadi_majlis/',
    1,
)

sections = [
    (
        '<h2 class="ref-section-title">١ — مصادر الأنساب',
        '</ul>\n\n        <h2 class="ref-section-title">٢ — المصادر التاريخية',
    ),
    (
        '<h2 class="ref-section-title">٢ — المصادر التاريخية',
        '</ul>\n\n        <h2 class="ref-section-title" id="abdullah-docs">٢-ب',
    ),
    (
        '<h2 class="ref-section-title" id="abdullah-docs">٢-ب',
        '</ul>\n\n        <h2 class="ref-section-title">٣ — كتب تاريخ',
    ),
    (
        '<h2 class="ref-section-title">٣ — كتب تاريخ',
        '</ul>\n\n        <h2 class="ref-section-title">٤ — صحافة',
    ),
    (
        '<h2 class="ref-section-title">٤ — صحافة',
        '</ul>\n\n        <div class="ref-archive-section"',
    ),
]
for start_marker, end_marker in sections:
    if start_marker in mid and f'<div class="ref-section-block">\n        {start_marker}' not in mid:
        mid = mid.replace(
            start_marker,
            f'<div class="ref-section-block">\n        {start_marker}',
            1,
        )
        mid = mid.replace(
            end_marker,
            f'</div>\n\n        {end_marker}',
            1,
        )

if '<div class="ref-section-block">\n        <h2 class="ref-section-title">٦ —' not in tail:
    tail = tail.replace(
        '<h2 class="ref-section-title">٦ — مجلس العائلة',
        '<div class="ref-section-block">\n        <h2 class="ref-section-title">٦ — مجلس العائلة',
        1,
    )
    tail = tail.replace(
        '</ul>\n\n        <div class="mt-16 border-t',
        '</ul>\n        </div>\n\n        <div class="mt-16 border-t',
        1,
    )

PATH.write_text(head + mid + tail, encoding="utf-8")
print("Done")
