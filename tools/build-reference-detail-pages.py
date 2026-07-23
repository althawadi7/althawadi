#!/usr/bin/env python3
"""Build individual SEO detail pages for each reference card."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from footer_snippet import footer_contact_col, footer_nav_cols  # noqa: E402
from site_chrome import header_html, hreflang_tags_for, normalize_path  # noqa: E402
INDEX = ROOT / "references" / "index.html"
OUT_DIR = ROOT / "references" / "item"
MANIFEST = ROOT / "data" / "references-manifest.json"
CARDS_DATA = ROOT / "data" / "references-cards.json"
IG_DATA = ROOT / "data" / "instagram-history.json"
BOOK_NAWAKHIDA = ROOT / "data" / "book-nawakhida-bahrain.json"
BASE = ""
ITEM_BASE = f"{BASE}/references/item"


def abs_url(path: str) -> str:
    """Root-absolute site URL. Note: path.startswith('') is always True, so never use BASE that way."""
    if not path:
        return path
    if path.startswith(("http://", "https://")):
        return path
    if path.startswith("../"):
        path = path[3:]
    if path.startswith("/"):
        return path
    prefix = (BASE or "").rstrip("/")
    return f"{prefix}/{path}" if prefix else f"/{path}"


def strip_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def first_match(block: str, pattern: str) -> str:
    m = re.search(pattern, block, flags=re.I | re.S)
    return m.group(1).strip() if m else ""


def caption_to_fulltext(caption: str) -> str:
    clean = (caption or "").strip().replace('"\n', "\n").strip('"')
    parts = [p.strip() for p in re.split(r"\n\n+", clean) if p.strip()]
    blocks = []
    for para in parts:
        lines = [html.escape(l.strip()) for l in para.split("\n") if l.strip()]
        inner = "<br />".join(lines)
        blocks.append(f'<p class="ref-ig-caption-p">{inner}</p>')
    return "\n                ".join(blocks)


def title_from_caption(caption: str) -> str:
    line = (caption or "").strip().split("\n")[0].strip()
    line = re.sub(r'^[\s"]+|[\s"]+$', "", line)
    if len(line) > 100:
        return line[:97].rstrip() + "…"
    return line or "منشور من @althawadi_majlis"


def excerpt_from_caption(caption: str, max_len: int = 160) -> str:
    clean = re.sub(r"\s+", " ", (caption or "").strip().replace('"\n', "\n").strip('"'))
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 1].rstrip() + "…"


def card_from_ig_post(post: dict, index: int) -> dict:
    code = post["shortcode"]
    caption = post.get("caption") or ""
    card = {
        "slug": f"ig-{code}",
        "index": index,
        "is_source": False,
        "title": title_from_caption(caption),
        "excerpt": excerpt_from_caption(caption),
        "author": "",
        "num": f"{index:02d}",
        "search": f"{code} {caption}",
        "fulltext": caption_to_fulltext(caption),
        "external_url": post.get("url") or f"https://www.instagram.com/p/{code}/?hl=ar",
        "media": {"kind": "none"},
    }
    enrich_media_from_json(card, {code: post})
    return card


def sync_ig_posts_into_cards(cards: list[dict], ig_posts: dict[str, dict]) -> list[dict]:
    """Prepend any Instagram posts from JSON that are missing on the page."""
    if not IG_DATA.exists():
        return cards
    data = json.loads(IG_DATA.read_text(encoding="utf-8"))
    ordered = data.get("posts") or []
    existing = {c["slug"] for c in cards}
    missing = []
    for post in ordered:
        code = post.get("shortcode")
        if not code:
            continue
        slug = f"ig-{code}"
        if slug in existing:
            continue
        missing.append(post)
        ig_posts[code] = post

    if not missing:
        # Still renumber IG cards to match JSON order preference for new ones at top
        return renumber_ig_cards(cards)

    # Insert missing after last source card (or at start if none)
    insert_at = 0
    for i, c in enumerate(cards):
        if c.get("is_source"):
            insert_at = i + 1
    new_cards = [card_from_ig_post(p, 0) for p in missing]
    cards = cards[:insert_at] + new_cards + cards[insert_at:]
    return renumber_ig_cards(cards)


def renumber_ig_cards(cards: list[dict]) -> list[dict]:
    n = 0
    for i, c in enumerate(cards, 1):
        c["index"] = i
        if not c.get("is_source") and str(c.get("slug", "")).startswith("ig-"):
            n += 1
            c["num"] = f"{n:02d}"
    return cards


def book_entry_fulltext(book: str, author: str, entry: dict) -> str:
    name = html.escape(entry.get("name") or "")
    dates = html.escape(entry.get("dates") or "")
    pages = html.escape(entry.get("pages") or "")
    text = (entry.get("text") or "").strip()
    photo_note = (entry.get("photo_note") or "").strip()
    book_e = html.escape(book)
    author_e = html.escape(author)
    cite = (
        '<aside class="ref-book-cite" aria-label="بيانات المصدر">'
        f'<p><strong class="text-foreground">المصدر:</strong> {book_e}</p>'
        f'<p><strong class="text-foreground">تأليف:</strong> {author_e}</p>'
        f'<p><strong class="text-foreground">الصفحات:</strong> {pages}</p>'
        "</aside>"
    )
    body_parts = []
    if photo_note:
        body_parts.append(
            f'<p class="mt-4 text-sm text-muted-foreground">{html.escape(photo_note)}</p>'
        )
    if text:
        paras = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        if len(paras) == 1 and len(paras[0]) > 350:
            chunk = paras[0]
            mid = chunk.find("، ويشير")
            if mid < 0:
                mid = chunk.find(". وقد ")
            if mid > 80:
                paras = [chunk[: mid + 1].strip(), chunk[mid + 1 :].lstrip(" ،.")]
        for para in paras:
            body_parts.append(
                f'<p class="ref-ig-caption-p mt-6">{html.escape(para)}</p>'
            )
    dates_line = (
        f'<p class="mt-4 text-sm text-muted-foreground">التواريخ في الكتاب: {dates}</p>'
        if dates
        else ""
    )
    return (
        f"{cite}\n"
        f'<h2 class="ref-article-h2 mt-8">{name}</h2>\n'
        f"{dates_line}\n"
        f"{''.join(body_parts)}"
    )


def card_from_book_entry(book: str, author: str, entry: dict, index: int) -> dict:
    slug = entry["slug"]
    name = entry.get("name") or slug
    pages = entry.get("pages") or ""
    text = entry.get("text") or ""
    imgs_raw = entry.get("images") or []
    if not imgs_raw and entry.get("image"):
        imgs_raw = [entry["image"]]
    imgs = [abs_url(u) for u in imgs_raw if u]
    excerpt = excerpt_from_caption(
        f"من {book} — تأليف {author} — ص {pages}. {text}",
        160,
    )
    media = {"kind": "none"}
    if len(imgs) > 1:
        media = {
            "kind": "gallery",
            "src": imgs[0],
            "thumb": imgs[0],
            "images": imgs,
            "alt": name,
        }
    elif imgs:
        media = {
            "kind": "image",
            "src": imgs[0],
            "thumb": imgs[0],
            "images": imgs,
            "alt": name,
        }
    return {
        "slug": slug,
        "index": index,
        "is_source": True,
        "title": name,
        "excerpt": excerpt,
        "author": f"{author} — {book}",
        "num": "",
        "search": f"{name} {book} {author} صفحات {pages} {text}",
        "fulltext": book_entry_fulltext(book, author, entry),
        "external_url": "",
        "media": media,
    }


def sync_book_nawakhida_into_cards(cards: list[dict]) -> list[dict]:
    """Insert/update character entries from كتاب نواخذة البحرين."""
    if not BOOK_NAWAKHIDA.exists():
        return cards
    data = json.loads(BOOK_NAWAKHIDA.read_text(encoding="utf-8"))
    book = data.get("book") or "كتاب نواخذة البحرين"
    author = data.get("author") or "بشار بن يوسف الحادي"
    entries = data.get("entries") or []
    if not entries:
        return cards

    book_slugs = {e.get("slug") for e in entries if e.get("slug")}
    book_titles = {e.get("name") for e in entries if e.get("name")}

    # Drop orphaned ref-* ghosts that duplicated book characters (broken slug parse)
    cleaned = []
    for c in cards:
        slug = c.get("slug") or ""
        title = c.get("title") or ""
        if (
            slug.startswith("ref-")
            and slug not in {f"ref-{i:02d}" for i in range(1, 20)}
            and title in book_titles
        ):
            continue
        if slug.startswith("book-nawakhida-") and slug not in book_slugs:
            # keep unknown book pages unless clearly orphans; skip none
            pass
        cleaned.append(c)
    cards = cleaned

    by_slug = {c["slug"]: i for i, c in enumerate(cards)}
    insert_at = 0
    for i, c in enumerate(cards):
        if c.get("is_source"):
            insert_at = i + 1

    for entry in entries:
        slug = entry.get("slug")
        if not slug:
            continue
        card = card_from_book_entry(book, author, entry, 0)
        if slug in by_slug:
            idx = by_slug[slug]
            card["index"] = cards[idx]["index"]
            cards[idx] = card
        else:
            cards.insert(insert_at, card)
            insert_at += 1
            by_slug = {c["slug"]: i for i, c in enumerate(cards)}

    for i, c in enumerate(cards, 1):
        c["index"] = i
    return cards


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
    if post.get("url"):
        card["external_url"] = post["url"]
    imgs = [abs_url(u) for u in (post.get("local_images") or [])]
    vids = [abs_url(u) for u in (post.get("local_videos") or [])]
    media = card["media"]
    if post.get("type") == "video" and vids:
        media["kind"] = "video"
        media["src"] = vids[0]
        media["poster"] = imgs[0] if imgs else media.get("poster") or media.get("thumb")
        media["thumb"] = media["poster"] or media["src"]
        if len(vids) > 1:
            media["videos"] = [
                {
                    "src": v,
                    "poster": imgs[i] if i < len(imgs) else (imgs[0] if imgs else ""),
                }
                for i, v in enumerate(vids)
            ]
        if post.get("hide_post_label"):
            card["num"] = ""
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
        if not detail_href:
            detail_href = first_match(block, r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*ref-ig-read-more')
        if not detail_href:
            detail_href = first_match(block, r'class="ref-ig-card-title-link"[^>]*href="([^"]+)"')
        if not detail_href:
            detail_href = first_match(block, r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*ref-ig-card-title-link')
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
        videos = media.get("videos") or []
        if len(videos) > 1:
            parts = []
            for i, v in enumerate(videos, 1):
                poster = html.escape(v.get("poster") or "")
                src = html.escape(v.get("src") or "")
                parts.append(
                    f'<figure class="ref-detail-media ref-detail-media--video">'
                    f'<video class="ref-detail-video" controls playsinline preload="metadata" '
                    f'{"poster=\"" + poster + "\"" if poster else ""} src="{src}"></video>'
                    f'<figcaption class="ref-media-caption text-sm text-muted-foreground mt-2">'
                    f"فيديو {i}</figcaption>"
                    f"</figure>"
                )
            return f'<div class="ref-detail-gallery ref-detail-gallery--videos">{"".join(parts)}</div>'
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
        caption = (media.get("caption") or "").strip()
        cap_html = (
            f"<figcaption>{html.escape(caption)}</figcaption>" if caption else ""
        )
        fig_class = "ref-detail-media archive-doc" if caption else "ref-detail-media"
        if len(imgs) == 1:
            src = html.escape(imgs[0])
            alt = html.escape(media.get("alt") or title)
            return (
                f'<figure class="{fig_class}">'
                f'<img src="{src}" alt="{alt}" loading="lazy" />'
                f"{cap_html}"
                f"</figure>"
            )
        parts = []
        for idx, u in enumerate(imgs, 1):
            parts.append(
                f'<figure class="ref-detail-media ref-detail-media--slide">'
                f'<img src="{html.escape(u)}" alt="{html.escape(title)} — {idx}" loading="lazy" />'
                f"</figure>"
            )
        gallery = f'<div class="ref-detail-gallery">{"".join(parts)}</div>'
        if caption:
            return gallery + f'<p class="ref-media-caption text-sm text-muted-foreground mt-3">{html.escape(caption)}</p>'
        return gallery
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
    id_attr = f' id="{html.escape(card["slug"])}"'
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
  <title>{t} — مراجع الذوادي</title>
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
        <a href="{BASE}/references/" class="text-sm text-muted-foreground hover:text-accent">← مراجع ومصادر</a>
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
    cards = sync_book_nawakhida_into_cards(cards)
    cards = sync_ig_posts_into_cards(cards, ig_posts)

    # Keep British tribal table scan on ref-06 (not scraped from Instagram)
    for card in cards:
        if card.get("slug") == "ref-06":
            card["media"] = {
                "kind": "image",
                "src": f"{BASE}/assets/E5UyU7aXEAIYjw9.jpg",
                "thumb": f"{BASE}/assets/E5UyU7aXEAIYjw9.jpg",
                "images": [f"{BASE}/assets/E5UyU7aXEAIYjw9.jpg"],
                "alt": "صفحة 608 — Settled Tribes of the Centre — Beni Khālid — جدول AL Thawawdah (Dawāudah في النص الأصلي) تحت بطن 'Amā'ir",
                "caption": (
                    "صورة الأصل: صفحة 608 — «13. Beni Khālid» — جدول BENI KHĀLID — "
                    "IOR/L/PS/20/E84/1 (Settled Tribes of the Centre, 1916). "
                    "يظهر الذواودة — AL Thawawdah (وردت في النص البريطاني Dawāudah) تحت بطن العماير ('Amā'ir)."
                ),
            }
            break

    # Fill missing IG fulltext from JSON captions; always refresh media paths from JSON
    for card in cards:
        slug = card.get("slug") or ""
        if not slug.startswith("ig-"):
            continue
        code = slug[3:]
        post = ig_posts.get(code)
        if not post:
            continue
        if post.get("caption"):
            if not card.get("fulltext"):
                card["fulltext"] = caption_to_fulltext(post["caption"])
            if not card.get("title"):
                card["title"] = title_from_caption(post["caption"])
            if not card.get("excerpt"):
                card["excerpt"] = excerpt_from_caption(post["caption"])
            if not card.get("external_url"):
                card["external_url"] = post.get("url") or ""
        enrich_media_from_json(card, ig_posts)

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
