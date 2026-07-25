#!/usr/bin/env python3
"""Build individual detail pages for family news posts."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from footer_snippet import footer_contact_col, footer_nav_cols  # noqa: E402
from site_chrome import header_html, hreflang_tags_for, normalize_path  # noqa: E402
DATA = ROOT / "data" / "family-news.json"
OUT_DIR = ROOT / "news" / "item"
BASE = ""
ITEM_BASE = f"{BASE}/news/item"


def abs_url(path: str) -> str:
    if not path:
        return path
    if path.startswith(("http://", "https://", "/")):
        return path
    prefix = (BASE or "").rstrip("/")
    return f"{prefix}/{path}" if prefix else f"/{path}"


def trim_text(text: str, limit: int) -> str:
    t = " ".join((text or "").split())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def post_title(post: dict) -> str:
    return trim_text(post.get("caption") or post.get("text") or post["shortcode"], 100)


def post_description(post: dict) -> str:
    return trim_text(post.get("text") or post.get("caption") or "", 155)


def caption_html(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    parts = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if para:
            parts.append(f'<p class="ref-ig-caption-p">{html.escape(para)}</p>')
    return "\n                ".join(parts)


def media_block(post: dict, title: str) -> str:
    kind = post.get("type", "image")
    imgs = [abs_url(u) for u in (post.get("local_images") or [])]
    vids = [abs_url(u) for u in (post.get("local_videos") or [])]

    if kind == "video" and vids:
        poster = html.escape(imgs[0] if imgs else "")
        src = html.escape(vids[0])
        poster_attr = f' poster="{poster}"' if poster else ""
        return (
            f'<section class="ref-detail-media-section" aria-label="فيديو">'
            f'<figure class="ref-detail-media ref-detail-media--video">'
            f'<div class="ref-detail-video-frame">'
            f'<video class="ref-detail-video" controls playsinline preload="metadata"'
            f'{poster_attr} src="{src}"></video>'
            f"</div></figure></section>"
        )

    if len(imgs) > 1:
        parts = []
        for idx, u in enumerate(imgs, 1):
            parts.append(
                f'<figure class="ref-detail-media ref-detail-media--slide">'
                f'<div class="ref-detail-image-frame">'
                f'<img src="{html.escape(u)}" alt="{html.escape(title)} — {idx}" loading="lazy" />'
                f"</div>"
                f'<figcaption class="ref-media-caption">'
                f'<span class="ref-media-caption__index">{idx:02d}</span>'
                f'<span class="ref-media-caption__label">صورة {idx}</span>'
                f"</figcaption>"
                f"</figure>"
            )
        return (
            f'<section class="ref-detail-media-section" aria-label="معرض صور">'
            f'<div class="ref-detail-gallery ref-detail-gallery--images">'
            f'{"".join(parts)}</div></section>'
        )

    if imgs:
        return (
            f'<section class="ref-detail-media-section" aria-label="صورة">'
            f'<figure class="ref-detail-media ref-detail-media--image">'
            f'<div class="ref-detail-image-frame">'
            f'<img src="{html.escape(imgs[0])}" alt="{html.escape(title)}" loading="lazy" />'
            f"</div></figure></section>"
        )

    return ""


def detail_body(post: dict, index: int) -> str:
    title = html.escape(post_title(post))
    code = html.escape(post["shortcode"])
    text = post.get("text") or post.get("caption") or ""
    ig_url = html.escape(post["url"])

    parts = [
        '<header class="ref-detail-header">',
        '<p class="ref-detail-kicker text-xs uppercase tracking-[0.3em] text-accent font-latin">Family News</p>',
        f'<p class="ref-detail-num text-sm text-muted-foreground mt-2">منشور {index:02d} — @althawadi_majlis</p>',
        f'<h1 class="ref-detail-title font-display text-3xl md:text-4xl text-foreground mt-4">{title}</h1>',
        "</header>",
    ]

    media_html = media_block(post, post_title(post))
    if media_html:
        parts.append(media_html)

    body = caption_html(text)
    if body:
        parts.append(f'<div class="ref-detail-body prose-ref mt-8">{body}</div>')

    parts.append(
        f'<footer class="ref-detail-footer mt-12 pt-8 border-t border-border flex flex-wrap gap-4">'
        f'<a href="{ig_url}" target="_blank" rel="noreferrer" class="ref-detail-ext-link font-latin">Instagram ↗</a>'
        f'<a href="{BASE}/news/" class="ref-detail-back">← كل الأخبار</a>'
        f"</footer>"
    )
    return "\n        ".join(parts)


def page_shell(title: str, description: str, slug: str, body: str, og_image: str = "") -> str:
    t = html.escape(title)
    d = html.escape(description)
    canonical_path = normalize_path(f"{ITEM_BASE}/{slug}/")
    canonical = f"https://althawadi.org{canonical_path}"
    og_img_tag = ""
    if og_image:
        og_img_tag = f'  <meta property="og:image" content="{html.escape(og_image)}" />\n'
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="index, follow" />
  <title>{t} — أخبار عائلة الذوادي</title>
  <meta name="description" content="{d}" />
  <meta property="og:title" content="{t}" />
  <meta property="og:description" content="{d}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:site_name" content="AL Thawadi" />
{og_img_tag}  <link rel="canonical" href="{canonical}" />
{hreflang_tags_for("ar", canonical_path)}
  <link rel="stylesheet" href="{BASE}/css/styles.css" />
  <script src="{BASE}/js/url-clean.js"></script>
  <script src="{BASE}/js/main.js" defer></script>
</head>
<body>
  <div class="min-h-screen flex flex-col">
{header_html("ar", canonical_path)}

    <main class="flex-1 ref-detail-page">
      <nav class="ref-detail-breadcrumb mx-auto max-w-3xl px-4 sm:px-6 pt-8" aria-label="مسار التصفح">
        <a href="{BASE}/news/" class="text-sm text-muted-foreground hover:text-accent">← أخبار المجلس</a>
      </nav>
      <article class="mx-auto max-w-3xl px-4 sm:px-6 py-10 pb-20">
        {body}
      </article>
    </main>

    <footer class="mt-24 border-t border-border bg-card/40">
      <div class="mx-auto max-w-7xl px-6 py-14 footer-grid">
        <div class="footer-brand">
          <a href="{BASE}/" data-home class="font-display text-2xl text-foreground hover:text-accent">الذواودة</a>
          <p class="mt-3 text-sm text-muted-foreground leading-7 max-w-sm">بيت من الذكريات، وصفحة من التاريخ. نوثّق هنا نسب عائلتنا، وسير أجدادنا، وصورًا تحكي مسيرتنا جيلًا بعد جيل.</p>
        </div>
{footer_nav_cols(BASE)}
{footer_contact_col()}
      </div>
      <div class="border-t border-border/60">
        <div class="footer-bar mx-auto max-w-7xl px-4 sm:px-6 py-5 text-xs text-muted-foreground flex flex-wrap justify-between gap-3">
          <span>© <span id="footer-year"></span> الذواودة — جميع الحقوق محفوظة</span>
          <span class="font-latin tracking-[0.2em] uppercase">AL Thawadi Family</span>
        </div>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    posts = data.get("posts", [])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for child in OUT_DIR.iterdir():
        if child.is_dir():
            for f in child.iterdir():
                f.unlink()
            child.rmdir()

    for index, post in enumerate(posts, 1):
        slug = post["shortcode"]
        title = post_title(post)
        desc = post_description(post)
        imgs = post.get("local_images") or []
        og_image = abs_url(imgs[0]) if imgs else ""
        page = page_shell(title, desc, slug, detail_body(post, index), og_image)
        dest = OUT_DIR / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")

    print(f"Built {len(posts)} family news detail pages under {OUT_DIR}")


if __name__ == "__main__":
    main()
