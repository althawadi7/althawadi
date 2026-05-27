#!/usr/bin/env python3
"""Build individual SEO detail pages for each reference card."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "index.html"
OUT_DIR = ROOT / "references" / "item"
MANIFEST = ROOT / "data" / "references-manifest.json"
CARDS_DATA = ROOT / "data" / "references-cards.json"
IG_DATA = ROOT / "data" / "instagram-history.json"
BASE = "/althawadi"
ITEM_BASE = f"{BASE}/references/item"


def abs_url(path: str) -> str:
    if not path:
        return path
    if path.startswith("http") or path.startswith(BASE):
        return path
    if path.startswith("../"):
        return f"{BASE}/{path[3:]}"
    if path.startswith("assets/"):
        return f"{BASE}/{path}"
    return path


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def first_match(block: str, pattern: str) -> str:
    m = re.search(pattern, block, flags=re.I | re.S)
    return m.group(1).strip() if m else ""


def load_ig_posts() -> dict[str, dict]:
    if not IG_DATA.exists():
        return {}
    posts = json.loads(IG_DATA.read_text(encoding="utf-8")).get("posts", [])
    out = {}
    for p in posts:
        code = p.get("shortcode")
        if code:
            out[code] = p
    return out


def load_ig_images(ig_posts: dict[str, dict]) -> dict[str, list[str]]:
    out = {}
    for code, p in ig_posts.items():
        imgs = p.get("local_images") or []
        if imgs:
            out[code] = [abs_url(u) for u in imgs]
    return out


def load_fulltext_from_details() -> dict[str, str]:
    out = {}
    if not OUT_DIR.exists():
        return out
    for path in OUT_DIR.glob("*/index.html"):
        slug = path.parent.name
        text = path.read_text(encoding="utf-8")
        m = re.search(
            r'<div class="ref-detail-body[^"]*">([\s\S]*?)</div>\s*<footer',
            text,
            flags=re.I,
        )
        if m:
            out[slug] = m.group(1).strip()
    return out


def slug_from_href(href: str) -> str:
    m = re.search(r"/item/([^/]+)/?", href)
    return m.group(1) if m else ""


def enrich_media_from_json(card: dict, ig_posts: dict[str, dict]) -> None:
    slug = card["slug"]
    if not slug.startswith("ig-"):
        return
    code = slug[3:]
    post = ig_posts.get(code)
    if not post:
        return
    if post.get("url") and not card.get("external_url"):
        card["external_url"] = post["url"]
    imgs = [abs_url(u) for u in (post.get("local_images") or [])]
    vids = [abs_url(u) for u in (post.get("local_videos") or [])]
    media = card["media"]
    if post.get("type") == "video" and vids:
        media["kind"] = "video"
        media["src"] = vids[0]
        media["poster"] = imgs[0] if imgs else media.get("poster") or media.get("thumb")
        media["thumb"] = media["poster"] or media["src"]
        return
    if len(imgs) > 1:
        media["kind"] = "gallery"
        media["images"] = imgs
        media["thumb"] = imgs[0]
        media["src"] = imgs[0]
    elif imgs:
        media["kind"] = "image"
        media["images"] = imgs
        media["thumb"] = imgs[0]
        media["src"] = imgs[0]


def find_grid_end(text: str, grid_start: int) -> int:
    for marker in (
        "\n        </ul>\n\n        <div id=\"ref-ig-lightbox\"",
        "\n        </ul>\n        <div class=\"mt-16 border-t",
        "\n        </ul>\n\n        <div class=\"mt-16 border-t",
    ):
        pos = text.find(marker, grid_start)
        if pos >= 0:
            return pos
    raise ValueError("Could not locate end of ref-all-grid")


def parse_cards(
    text: str,
    ig_posts: dict[str, dict],
    saved_fulltext: dict[str, str],
) -> list[dict]:
    grid_start = text.index('<ul class="ref-ig-grid" id="ref-all-grid">')
    grid_end = find_grid_end(text, grid_start)
    grid = text[grid_start:grid_end]
    parts = re.split(r"(?=<li class=\"ref-ig-card)", grid)
    blocks = []
    for part in parts:
        if not part.strip().startswith("<li"):
            continue
        end = part.rfind("</li>")
        if end < 0:
            continue
        blocks.append(part[: end + len("</li>")])
    cards = []
    for i, block in enumerate(blocks, 1):
        card_id = first_match(block, r'\bid="([^"]+)"')
        detail_href = first_match(block, r'class="ref-ig-read-more"[^>]*href="([^"]+)"')
        slug = card_id or slug_from_href(detail_href) or f"ref-{i:02d}"
        is_source = "ref-ig-card--source" in block
        title = strip_tags(
            first_match(block, r"<h3[^>]*class=\"ref-ig-card-title[^\"]*\"[^>]*>([\s\S]*?)</h3>")
        )
        excerpt = strip_tags(first_match(block, r"<p class=\"ref-ig-excerpt\"[^>]*>([\s\S]*?)</p>"))
        author = strip_tags(first_match(block, r"<span class=\"ref-ig-sub\"[^>]*>([\s\S]*?)</span>"))
        num = strip_tags(first_match(block, r"<span class=\"ref-ig-num\"[^>]*>([\s\S]*?)</span>"))
        search = first_match(block, r'data-search="([^"]*)"')
        fulltext = first_match(
            block, r'<div class="ref-ig-fulltext[^"]*">([\s\S]*?)</div>\s*</details>'
        )
        if not fulltext:
            fulltext = saved_fulltext.get(slug, "")
        external = first_match(block, r'class="ref-ig-link font-latin"[^>]*href="([^"]+)"')
        if not external:
            external = first_match(block, r'href="([^"]+)"[^>]*class="ref-ig-link font-latin"')

        media = parse_media(block)
        card = {
            "slug": slug,
            "index": i,
            "is_source": is_source,
            "title": title,
            "excerpt": excerpt,
            "author": author,
            "num": num,
            "search": search,
            "fulltext": fulltext.strip(),
            "external_url": external,
            "media": media,
        }
        enrich_media_from_json(card, ig_posts)
        cards.append(card)
    return cards


def parse_media(block: str) -> dict:
    btn = re.search(
        r'<button[^>]*class="[^"]*ref-ig-lightbox-trigger[^"]*"([^>]*)>([\s\S]*?)</button>',
        block,
        flags=re.I,
    )
    if btn:
        attrs = btn.group(1)
        mtype = first_match(f"x {attrs}", r'data-type="([^"]+)"') or "image"
        src = abs_url(first_match(f"x {attrs}", r'data-src="([^"]+)"'))
        poster = abs_url(first_match(f"x {attrs}", r'data-poster="([^"]+)"'))
        images_raw = first_match(f"x {attrs}", r'data-images="([^"]+)"')
        images = []
        if images_raw:
            try:
                images = [abs_url(u) for u in json.loads(html.unescape(images_raw))]
            except json.JSONDecodeError:
                images = []
        img_m = re.search(r'<img[^>]+src="([^"]+)"', btn.group(2), flags=re.I)
        thumb = abs_url(img_m.group(1)) if img_m else (poster or src)
        alt = first_match(btn.group(2), r'alt="([^"]*)"')
        return {
            "kind": mtype,
            "src": src,
            "poster": poster,
            "images": images or ([src] if src else []),
            "thumb": thumb,
            "alt": alt,
        }

    link_thumb = re.search(
        r'<a[^>]*class="[^"]*ref-ig-thumb[^"]*"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>',
        block,
        flags=re.I,
    )
    if link_thumb:
        inner = link_thumb.group(2)
        is_video = "ref-ig-play" in inner or "فيديو" in inner
        img_m = re.search(r'<img[^>]+src="([^"]+)"', inner, flags=re.I)
        thumb = abs_url(img_m.group(1)) if img_m else ""
        if is_video and thumb:
            src = thumb.rsplit(".", 1)[0] + ".mp4" if "." in thumb else ""
            return {
                "kind": "video",
                "src": src,
                "poster": thumb,
                "thumb": thumb,
                "images": [],
            }
        if img_m:
            return {
                "kind": "image",
                "src": thumb,
                "thumb": thumb,
                "images": [thumb],
            }
        return {"kind": "none"}

    return {"kind": "none"}


def fix_paths_in_html(fragment: str) -> str:
    fragment = fragment.replace('href="../', f'href="{BASE}/')
    fragment = fragment.replace('src="../', f'src="{BASE}/')
    return fragment


def media_block(media: dict, title: str) -> str:
    kind = media.get("kind")
    if kind == "video":
        poster = html.escape(media.get("poster") or "")
        src = html.escape(media.get("src") or "")
        return (
            f'<figure class="ref-detail-media ref-detail-media--video">'
            f'<video class="ref-detail-video" controls playsinline preload="metadata" '
            f'{"poster=\"" + poster + "\"" if poster else ""} src="{src}"></video>'
            f"</figure>"
        )
    if kind in ("image", "gallery"):
        imgs = media.get("images") or ([media.get("src")] if media.get("src") else [])
        if len(imgs) == 1:
            src = html.escape(imgs[0])
            alt = html.escape(media.get("alt") or title)
            return (
                f'<figure class="ref-detail-media">'
                f'<img src="{src}" alt="{alt}" loading="lazy" />'
                f"</figure>"
            )
        parts = []
        for idx, u in enumerate(imgs, 1):
            parts.append(
                f'<figure class="ref-detail-media ref-detail-media--slide">'
                f'<img src="{html.escape(u)}" alt="{html.escape(title)} — {idx}" loading="lazy" />'
                f"</figure>"
            )
        return f'<div class="ref-detail-gallery">{"".join(parts)}</div>'
    return ""


def card_thumb_html(card: dict) -> str:
    url = f"{ITEM_BASE}/{card['slug']}/"
    media = card["media"]
    if media.get("kind") == "video":
        thumb = html.escape(media.get("thumb") or "")
        return (
            f'<a href="{url}" class="ref-ig-thumb ref-ig-thumb--card-link" aria-label="عرض التفاصيل والفيديو">'
            f'<img src="{thumb}" alt="" loading="lazy" />'
            f'<span class="ref-ig-play" aria-hidden="true"></span>'
            f'<span class="ref-ig-type-badge">فيديو</span></a>'
        )
    if media.get("kind") in ("image", "gallery"):
        thumb = html.escape(media.get("thumb") or media.get("src") or "")
        badge = ""
        imgs = media.get("images") or []
        if len(imgs) > 1:
            badge = f'<span class="ref-ig-type-badge">{len(imgs)} صور</span>'
        return (
            f'<a href="{url}" class="ref-ig-thumb ref-ig-thumb--card-link" aria-label="عرض التفاصيل">'
            f'<img src="{thumb}" alt="" loading="lazy" />{badge}</a>'
        )
    if media.get("kind") == "external":
        return (
            f'<a href="{url}" class="ref-ig-thumb ref-ig-thumb--empty ref-ig-thumb--link" aria-label="عرض التفاصيل">'
            f'<span class="ref-ig-thumb-label">رابط ↗</span></a>'
        )
    label = "مرجع"
    return (
        f'<a href="{url}" class="ref-ig-thumb ref-ig-thumb--empty ref-ig-thumb--card-link" aria-label="عرض التفاصيل">'
        f'<span class="ref-ig-thumb-label">{label}</span></a>'
    )


def card_html(card: dict) -> str:
    url = f"{ITEM_BASE}/{card['slug']}/"
    title = html.escape(card["title"])
    excerpt = html.escape(card["excerpt"])
    search = html.escape(card["search"], quote=True)
    thumb = card_thumb_html(card)
    classes = "ref-ig-card ref-ig-card--source" if card["is_source"] else "ref-ig-card"
    id_attr = f' id="{card["slug"]}"' if card["slug"].startswith("ig-") else ""
    meta_bits = []
    if card["is_source"]:
        meta_bits.append('<span class="ref-ig-badge">مرجع</span>')
        if card["author"]:
            meta_bits.append(f'<span class="ref-ig-sub">{html.escape(card["author"])}</span>')
    else:
        if card["num"]:
            meta_bits.append(f'<span class="ref-ig-num">{html.escape(card["num"])}</span>')
        if card["external_url"]:
            ext = html.escape(card["external_url"])
            meta_bits.append(
                f'<a href="{ext}" target="_blank" rel="noreferrer" class="ref-ig-link font-latin">Instagram ↗</a>'
            )
    meta = "\n                ".join(meta_bits)
    return f"""          <li class="{classes}"{id_attr} data-search="{search}">
            {thumb}
            <div class="ref-ig-card-body">
              <div class="ref-ig-card-meta">
                {meta}
              </div>
              <h3 class="ref-ig-card-title font-display text-foreground"><a href="{url}" class="ref-ig-card-title-link">{title}</a></h3>
              <p class="ref-ig-excerpt">{excerpt}</p>
              <p class="ref-ig-card-actions"><a href="{url}" class="ref-ig-read-more">اقرأ التفاصيل ←</a></p>
            </div>
          </li>"""


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
  <title>{t} — مراجع الذوادي</title>
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
          <a href="{BASE}/news/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">أخبار المجلس</a>
          <a href="{BASE}/references/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">مراجع</a>
          <a href="{BASE}/contact/" class="nav-link text-foreground/70 hover:text-foreground transition-colors">تواصل</a>
        </nav>
        <div class="flex items-center gap-3">
          <a href="https://www.instagram.com/althawadi_majlis/?hl=ar" target="_blank" rel="noreferrer" class="hidden sm:inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs text-foreground/80 hover:bg-card transition-colors">
            <span class="font-latin tracking-wide">@althawadi_majlis</span>
          </a>
          <button id="theme-toggle" type="button" class="theme-toggle" aria-label="تفعيل الوضع الليلي" aria-pressed="false" title="الوضع الليلي">
            <svg class="icon theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            <svg class="icon theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
          </button>
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
          <a href="{BASE}/news/" class="nav-link py-1 text-foreground/80">أخبار المجلس</a>
          <a href="{BASE}/references/" class="nav-link py-1 text-foreground/80">مراجع</a>
          <a href="{BASE}/contact/" class="nav-link py-1 text-foreground/80">تواصل</a>
        </nav>
      </div>
    </header>

    <main class="flex-1 ref-detail-page">
      <nav class="ref-detail-breadcrumb mx-auto max-w-3xl px-4 sm:px-6 pt-8" aria-label="مسار التصفح">
        <a href="{BASE}/references/" class="text-sm text-muted-foreground hover:text-accent">← مراجع ومصادر</a>
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
            <li><a href="{BASE}/references/" class="hover:text-accent">مراجع ومصادر</a></li>
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


def detail_body(card: dict) -> str:
    title = html.escape(card["title"])
    parts = [
        '<header class="ref-detail-header">',
        '<p class="ref-detail-kicker text-xs uppercase tracking-[0.3em] text-accent font-latin">Reference</p>',
    ]
    if card["is_source"]:
        parts.append('<span class="ref-ig-badge">مرجع</span>')
        if card["author"]:
            parts.append(f'<p class="ref-detail-author text-sm text-muted-foreground mt-2">{html.escape(card["author"])}</p>')
    elif card["num"]:
        parts.append(f'<p class="ref-detail-num text-sm text-muted-foreground mt-2">منشور {html.escape(card["num"])} — @althawadi_majlis</p>')
    parts.extend([f'<h1 class="ref-detail-title font-display text-3xl md:text-4xl text-foreground mt-4">{title}</h1>', "</header>"])

    media_html = media_block(card["media"], card["title"])
    if media_html:
        parts.append(media_html)

    if card["fulltext"]:
        parts.append(f'<div class="ref-detail-body prose-ref mt-8">{fix_paths_in_html(card["fulltext"])}</div>')

    links = []
    if card["external_url"]:
        ext = html.escape(card["external_url"])
        links.append(
            f'<a href="{ext}" target="_blank" rel="noreferrer" class="ref-detail-ext-link font-latin">Instagram ↗</a>'
        )
    links.append(f'<a href="{BASE}/references/" class="ref-detail-back">← كل المراجع</a>')
    parts.append(f'<footer class="ref-detail-footer mt-12 pt-8 border-t border-border flex flex-wrap gap-4">{"".join(links)}</footer>')
    return "\n        ".join(parts)


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    ig_posts = load_ig_posts()
    saved_fulltext = load_fulltext_from_details()
    cards = parse_cards(text, ig_posts, saved_fulltext)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for child in OUT_DIR.iterdir():
        if child.is_dir():
            for f in child.iterdir():
                f.unlink()
            child.rmdir()

    manifest = []
    for card in cards:
        slug = card["slug"]
        desc = card["excerpt"][:155] or card["title"][:155]
        og_image = card["media"].get("thumb") or card["media"].get("poster") or ""
        if og_image and card["media"].get("kind") == "gallery":
            imgs = card["media"].get("images") or []
            og_image = imgs[0] if imgs else og_image
        page = page_shell(card["title"], desc, slug, detail_body(card), og_image)
        dest = OUT_DIR / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        manifest.append({"slug": slug, "title": card["title"], "url": f"{ITEM_BASE}/{slug}/"})

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    CARDS_DATA.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")

    new_cards = "\n".join(card_html(c) for c in cards)
    grid_start = text.index('<ul class="ref-ig-grid" id="ref-all-grid">')
    grid_end = find_grid_end(text, grid_start)
    new_text = text[: grid_start + len('<ul class="ref-ig-grid" id="ref-all-grid">\n')] + new_cards + "\n        " + text[grid_end:]

    new_text = re.sub(
        r'\n\s*<div id="ref-ig-lightbox"[\s\S]*?</div>\s*\n\s*<div class="mt-16 border-t',
        '\n        <div class="mt-16 border-t',
        new_text,
        count=1,
    )
    new_text = re.sub(
        r'\n\s*<div id="ref-details-dialog"[\s\S]*?</div>\s*\n\s*<div class="mt-16 border-t',
        '\n        <div class="mt-16 border-t',
        new_text,
        count=1,
    )
    INDEX.write_text(new_text, encoding="utf-8")
    print(f"Built {len(cards)} detail pages under {OUT_DIR}")


if __name__ == "__main__":
    main()
