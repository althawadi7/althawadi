#!/usr/bin/env python3
"""Inject family news cards into news/index.html from data/family-news.json."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "family-news.json"
NEWS = ROOT / "news" / "index.html"
BASE = "/althawadi"
ITEM_BASE = f"{BASE}/news/item"


def trim_caption(text: str, limit: int = 260) -> str:
    t = " ".join((text or "").split())
    if len(t) <= limit:
        return t
    return t[: limit - 1].rstrip() + "…"


def card_html(post: dict) -> str:
    code = post["shortcode"]
    detail_url = html.escape(f"{ITEM_BASE}/{code}/")
    title = html.escape(trim_caption(post.get("caption") or post.get("text") or code, 80))
    body = html.escape(trim_caption(post.get("text") or post.get("caption") or "", 240))
    kind = post.get("type", "image")
    imgs = post.get("local_images") or []
    cover = html.escape(imgs[0] if imgs else "")
    badge = ""
    if kind == "album" and len(imgs) > 1:
        badge = f'<span class="family-news-badge">{len(imgs)} صور</span>'
    elif kind == "video":
        badge = '<span class="family-news-badge">فيديو</span>'
    meta = f"Instagram / {code}"
    return f"""          <article class="family-news-card">
            <a class="family-news-thumb" href="{detail_url}" aria-label="عرض التفاصيل">
              <img src="{BASE}/{cover}" alt="{title}" loading="lazy" />
              {badge}
            </a>
            <div class="family-news-body">
              <p class="family-news-meta font-latin">{meta}</p>
              <h3 class="family-news-title"><a href="{detail_url}" class="family-news-card-title-link">{title}</a></h3>
              <p class="family-news-text">{body}</p>
              <a class="family-news-link" href="{detail_url}">اقرأ التفاصيل ←</a>
            </div>
          </article>"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    posts = data.get("posts", [])
    cards = "\n".join(card_html(p) for p in posts)
    block = f'<div class="family-news-grid">\n{cards}\n        </div>'

    text = NEWS.read_text(encoding="utf-8")
    text = re.sub(
        r"<!-- FAMILY_NEWS_START -->[\s\S]*?<!-- FAMILY_NEWS_END -->",
        f"<!-- FAMILY_NEWS_START -->\n        {block}\n        <!-- FAMILY_NEWS_END -->",
        text,
        count=1,
    )
    NEWS.write_text(text, encoding="utf-8")
    print(f"Injected {len(posts)} family news cards.")


if __name__ == "__main__":
    main()
