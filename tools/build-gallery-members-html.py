#!/usr/bin/env python3
"""Inject gallery member cards into gallery/index.html."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "gallery-members.json"
GALLERY = ROOT / "gallery" / "index.html"
BASE = "/althawadi"


def trim_text(text: str, limit: int = 140) -> str:
    t = " ".join((text or "").split())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def normalized_text(post: dict) -> str:
    raw = post.get("first_comment") or post.get("caption") or post.get("text") or post["shortcode"]
    raw = html.unescape(raw)
    raw = re.sub(r"[\u200e\u200f\u202a-\u202e]", "", raw)
    m = re.search(r':\s*"([^"]+)"', raw)
    if m:
        raw = m.group(1)
    raw = re.sub(r"#\w+", "", raw)
    return " ".join(raw.split()).strip(' .-"')


def caption_title(post: dict) -> str:
    base = normalized_text(post)
    return trim_text(base, 70)


def caption_body(post: dict) -> str:
    return trim_text(normalized_text(post), 120)


def card_html(post: dict) -> str:
    code = post["shortcode"]
    title = html.escape(caption_title(post))
    body = html.escape(caption_body(post))
    url = html.escape(post["url"])
    imgs = post.get("local_images") or []
    cover = html.escape(imgs[0] if imgs else "")
    image_count = len(imgs)

    badge = ""
    if post.get("type") == "album" and image_count > 1:
        badge = f"<span>{image_count} صور</span>"
    elif post.get("type") == "video":
        badge = "<span>فيديو</span>"

    badge_html = (
        f'<div class="mt-2 text-xs text-muted-foreground font-latin">{badge}</div>' if badge else ""
    )

    return f"""          <figure class="mb-6 break-inside-avoid group overflow-hidden rounded-sm border border-border bg-card">
            <a href="{url}" target="_blank" rel="noreferrer" class="block overflow-hidden">
              <img src="{BASE}/{cover}" alt="{title}" loading="lazy" class="w-full h-auto object-cover group-hover:scale-[1.03] transition-transform duration-700" />
            </a>
            <figcaption class="p-4 border-t border-border">
              <div class="font-display text-lg text-foreground">{title}</div>
              <p class="text-xs text-muted-foreground mt-1">{body}</p>
              <div class="mt-2 text-xs"><a class="text-accent hover:underline font-latin" href="{url}" target="_blank" rel="noreferrer">Instagram / {code} ↗</a></div>
              {badge_html}
            </figcaption>
          </figure>"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    posts = data.get("posts", [])
    cards = "\n".join(card_html(p) for p in posts if (p.get("local_images") or p.get("local_videos")))
    if not cards:
        cards = '<p class="text-sm text-muted-foreground">لا توجد صور متاحة حاليًا.</p>'

    text = GALLERY.read_text(encoding="utf-8")
    text = re.sub(
        r"<!-- GALLERY_MEMBERS_START -->[\s\S]*?<!-- GALLERY_MEMBERS_END -->",
        f"<!-- GALLERY_MEMBERS_START -->\n{cards}\n        <!-- GALLERY_MEMBERS_END -->",
        text,
        count=1,
    )
    GALLERY.write_text(text, encoding="utf-8")
    print(f"Injected {len(posts)} gallery member posts.")


if __name__ == "__main__":
    main()
