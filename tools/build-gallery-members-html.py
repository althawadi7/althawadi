#!/usr/bin/env python3
"""Inject gallery member cards into gallery/index.html."""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gallery_members_sort import clean_display_name, sort_posts  # noqa: E402
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
    cleaned = " ".join(raw.split()).strip(' .-"')
    display = clean_display_name(cleaned)
    return display or cleaned


def caption_title(post: dict) -> str:
    base = normalized_text(post)
    return trim_text(base, 70)


def caption_body(post: dict) -> str:
    return trim_text(normalized_text(post), 120)


def card_html(post: dict) -> str:
    title = html.escape(caption_title(post))
    body = html.escape(caption_body(post))
    imgs = post.get("local_images") or []
    cover = html.escape(imgs[0] if imgs else "")
    image_count = len(imgs)

    badge = ""
    if post.get("type") == "album" and image_count > 1:
        badge = f"<span>{image_count} صور</span>"
    elif post.get("type") == "video":
        badge = "<span>فيديو</span>"

    body_html = ""
    if body and body != title:
        body_html = f'<p class="gallery-member-text">{body}</p>'

    badge_html = (
        f'<span class="gallery-member-badge font-latin">{badge}</span>' if badge else ""
    )

    return f"""          <figure class="gallery-member-card">
            <div class="gallery-member-thumb">
              <img src="{BASE}/{cover}" alt="{title}" loading="lazy" />
            </div>
            <figcaption class="gallery-member-caption">
              <div class="gallery-member-title">{title}</div>
              {body_html}
              {badge_html}
            </figcaption>
          </figure>"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    posts = sort_posts(data.get("posts", []))
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
