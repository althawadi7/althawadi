#!/usr/bin/env python3
"""Build individual detail pages for family news posts."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "family-news.json"
OUT_DIR = ROOT / "news" / "item"
BASE = "/althawadi"
ITEM_BASE = f"{BASE}/news/item"


def abs_url(path: str) -> str:
    if not path:
        return path
    if path.startswith("http") or path.startswith(BASE):
        return path
    return f"{BASE}/{path.lstrip('/')}"


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
            f'<figure class="ref-detail-media ref-detail-media--video">'
            f'<video class="ref-detail-video" controls playsinline preload="metadata"'
            f'{poster_attr} src="{src}"></video>'
            f"</figure>"
        )

    if len(imgs) > 1:
        parts = []
        for idx, u in enumerate(imgs, 1):
            parts.append(
                f'<figure class="ref-detail-media ref-detail-media--slide">'
                f'<img src="{html.escape(u)}" alt="{html.escape(title)} — {idx}" loading="lazy" />'
                f"</figure>"
            )
        return f'<div class="ref-detail-gallery">{"".join(parts)}</div>'

    if imgs:
        return (
            f'<figure class="ref-detail-media">'
            f'<img src="{html.escape(imgs[0])}" alt="{html.escape(title)}" loading="lazy" />'
            f"</figure>"
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
    canonical = f"{ITEM_BASE}/{slug}/"
    og_img_tag = ""
    if og_image:
        og_img_tag = f'  <meta property="og:image" content="{html.escape(og_image)}" />\n'
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{t} — أخبار عائلة الذوادي</title>
  <meta name="description" content="{d}" />
  <meta property="og:title" content="{t}" />
  <meta property="og:description" content="{d}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{canonical}" />
{og_img_tag}  <link rel="canonical" href="{canonical}" />
  <link rel="stylesheet" href="{BASE}/css/styles.css" />
  <script src="{BASE}/js/url-clean.js"></script>
  <script src="{BASE}/js/main.js" defer></script>
</head>
<body>
  <div class="min-h-screen flex flex-col">
    <header class="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur">
      <div class="site-header-inner mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-4">
        <a href="{BASE}/" data-home class="flex items-center gap-3 group">
          <span class="site-logo-text leading-tight">
            <span class="block font-display text-lg text-foreground">الذوادي</span>
            <span class="block text-[11px] uppercase tracking-[0.25em] text-muted-foreground font-latin">AL Thawadi</span>
          </span>
        </a>
        <nav class="hidden lg:flex items-center gap-7 text-sm">
          <a href="{BASE}/" data-home class="nav-link text-foreground/70 hover:text-foreground transition-colors">الرئيسية</a>
          <a href="{BASE}/about/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">عن العائلة</a>
          <a href="{BASE}/tree/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">شجرة العائلة</a>
          <a href="{BASE}/ancestors/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">الأجداد</a>
          <a href="{BASE}/gallery/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">الصور</a>
          <a href="{BASE}/news/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">أخبار العائلة</a>
          <a href="{BASE}/references/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">مراجع</a>
          <a href="{BASE}/contact/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">تواصل</a>
        </nav>
        <div class="flex items-center gap-3">
          <a href="https://www.instagram.com/althawadi_majlis/?hl=ar" target="_blank" rel="noreferrer" class="hidden sm:inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs text-foreground/80 hover:bg-card transition-colors">
            <span class="font-latin tracking-wide">@althawadi_majlis</span>
          </a>
          <button id="menu-toggle" type="button" class="lg:hidden p-2 rounded-md hover:bg-card" aria-label="القائمة">
            <svg id="menu-icon" class="icon h-5 w-5" viewBox="0 0 24 24" aria-hidden="true"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
            <svg id="close-icon" class="icon h-5 w-5" viewBox="0 0 24 24" aria-hidden="true" style="display:none"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
      </div>
      <div id="mobile-nav" class="lg:hidden border-t border-border bg-background">
        <nav class="flex flex-col px-6 py-4 gap-3 text-sm">
          <a href="{BASE}/" data-home class="nav-link py-1 text-foreground/80">الرئيسية</a>
          <a href="{BASE}/about/" class="nav-link py-1 text-foreground/80">عن العائلة</a>
          <a href="{BASE}/tree/" class="nav-link py-1 text-foreground/80">شجرة العائلة</a>
          <a href="{BASE}/ancestors/" class="nav-link py-1 text-foreground/80">الأجداد</a>
          <a href="{BASE}/gallery/" class="nav-link py-1 text-foreground/80">الصور</a>
          <a href="{BASE}/news/" class="nav-link py-1 text-foreground/80">أخبار العائلة</a>
          <a href="{BASE}/references/" class="nav-link py-1 text-foreground/80">مراجع</a>
          <a href="{BASE}/contact/" class="nav-link py-1 text-foreground/80">تواصل</a>
        </nav>
      </div>
    </header>

    <main class="flex-1 ref-detail-page">
      <nav class="ref-detail-breadcrumb mx-auto max-w-3xl px-4 sm:px-6 pt-8" aria-label="مسار التصفح">
        <a href="{BASE}/news/" class="text-sm text-muted-foreground hover:text-accent">← أخبار العائلة</a>
      </nav>
      <article class="mx-auto max-w-3xl px-4 sm:px-6 py-10 pb-20">
        {body}
      </article>
    </main>

    <footer class="mt-24 border-t border-border bg-card/40">
      <div class="mx-auto max-w-7xl px-6 py-14 grid gap-10 md:grid-cols-3">
        <div>
          <a href="{BASE}/" data-home class="font-display text-2xl text-foreground hover:text-accent">الذواودة</a>
          <p class="mt-3 text-sm text-muted-foreground leading-7 max-w-sm">بيت من الذكريات، وصفحة من التاريخ. نوثّق هنا نسب عائلتنا، وسير أجدادنا، وصورًا تحكي مسيرتنا جيلًا بعد جيل.</p>
        </div>
        <div>
          <h4 class="text-xs uppercase tracking-[0.3em] text-muted-foreground font-latin">روابط</h4>
          <ul class="mt-4 space-y-2 text-sm" style="list-style:none;padding:0;">
            <li><a href="{BASE}/news/" class="hover:text-accent">أخبار العائلة</a></li>
            <li><a href="{BASE}/contact/" class="hover:text-accent">تواصل</a></li>
          </ul>
        </div>
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
