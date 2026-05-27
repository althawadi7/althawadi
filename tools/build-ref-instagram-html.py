#!/usr/bin/env python3
"""Generate static Instagram archive HTML for references.html."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
OUT = ROOT / "partials" / "ref-instagram-posts.html"


def asset_path(rel: str) -> str:
    if rel.startswith("../") or rel.startswith("http"):
        return rel
    if rel.startswith("assets/"):
        return f"../{rel}"
    return rel


def thumb_html(post: dict) -> str:
    videos = post.get("local_videos") or []
    imgs = post.get("local_images") or ([post["cover"]] if post.get("cover") else [])
    imgs = [asset_path(p) for p in imgs if p]
    poster = imgs[0] if imgs else ""

    if videos:
        src = html.escape(asset_path(videos[0]))
        thumb = html.escape(poster or asset_path(videos[0].replace(".mp4", ".jpg")))
        return (
            f'<button type="button" class="ref-ig-thumb ref-ig-lightbox-trigger" '
            f'data-type="video" data-src="{src}" data-poster="{thumb}" '
            f'aria-label="تشغيل الفيديو">'
            f'<img src="{thumb}" alt="" loading="lazy" />'
            f'<span class="ref-ig-play" aria-hidden="true"></span>'
            f'<span class="ref-ig-type-badge">فيديو</span>'
            f"</button>"
        )

    if not imgs:
        return (
            '<div class="ref-ig-thumb ref-ig-thumb--empty">'
            '<span class="text-xs text-muted-foreground">بدون وسائط</span></div>'
        )

    src = html.escape(imgs[0])
    if len(imgs) > 1:
        images_json = html.escape(json.dumps(imgs, ensure_ascii=False), quote=True)
        label = f"عرض {len(imgs)} صور"
        return (
            f'<button type="button" class="ref-ig-thumb ref-ig-lightbox-trigger" '
            f'data-type="gallery" data-images="{images_json}" data-src="{src}" '
            f'aria-label="{html.escape(label)}">'
            f'<img src="{src}" alt="" loading="lazy" />'
            f'<span class="ref-ig-type-badge">{len(imgs)} صور</span>'
            f"</button>"
        )

    return (
        f'<button type="button" class="ref-ig-thumb ref-ig-lightbox-trigger" '
        f'data-type="image" data-src="{src}" aria-label="عرض الصورة بالحجم الكامل">'
        f'<img src="{src}" alt="" loading="lazy" />'
        f"</button>"
    )


def title_from_caption(caption: str) -> str:
    line = caption.strip().split("\n")[0].strip()
    line = re.sub(r'^[\s"]+|[\s"]+$', "", line)
    if len(line) > 100:
        return line[:97].rstrip() + "…"
    return line or "منشور من @althawadi_majlis"


def excerpt_from_caption(caption: str, max_len: int = 160) -> str:
    clean = re.sub(r"\s+", " ", caption.strip().replace('"\n', "\n").strip('"'))
    if len(clean) <= max_len:
        return clean
    return clean[: max_len - 1].rstrip() + "…"


def search_blob(post: dict) -> str:
    cap = post.get("caption", "")
    code = post.get("shortcode", "")
    return html.escape(f"{code} {cap}", quote=True)


def caption_html(caption: str) -> str:
    clean = caption.strip().replace('"\n', "\n").strip('"')
    parts = [p.strip() for p in re.split(r"\n\n+", clean) if p.strip()]
    blocks = []
    for para in parts:
        lines = [html.escape(l.strip()) for l in para.split("\n") if l.strip()]
        inner = "<br />".join(lines)
        blocks.append(f'<p class="ref-ig-caption-p">{inner}</p>')
    return "\n                ".join(blocks)


def render_post(post: dict, index: int) -> str:
    code = post["shortcode"]
    url = html.escape(post["url"])
    title = html.escape(title_from_caption(post.get("caption", "")))
    excerpt = html.escape(excerpt_from_caption(post.get("caption", "")))
    cap = caption_html(post.get("caption", ""))
    thumb = thumb_html(post)
    num = f"{index:02d}"
    search = search_blob(post)

    return f"""          <li class="ref-ig-card" id="ig-{code}" data-search="{search}">
            {thumb}
            <div class="ref-ig-card-body">
              <div class="ref-ig-card-meta">
                <span class="ref-ig-num">{num}</span>
                <a href="{url}" target="_blank" rel="noreferrer" class="ref-ig-link font-latin">Instagram ↗</a>
              </div>
              <h3 class="ref-ig-card-title font-display text-foreground">{title}</h3>
              <p class="ref-ig-excerpt">{excerpt}</p>
              <details class="ref-ig-details">
                <summary>عرض النص الكامل</summary>
                <div class="ref-ig-fulltext">
                {cap}
                </div>
              </details>
            </div>
          </li>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    posts = data["posts"]
    items = "\n".join(render_post(p, i) for i, p in enumerate(posts, 1))

    block = f"""        <div class="ref-archive-section" id="instagram-archive">
        <h2 class="ref-section-title">٥ — أرشيف منشورات @althawadi_majlis</h2>
        <p class="text-sm text-muted-foreground mb-4 leading-7">
          {len(posts)} منشوراً محفوظاً محلياً — انقر على الصورة أو الفيديو للعرض بالحجم الكامل.
        </p>
        <div class="ref-ig-toolbar">
          <label class="ref-ig-search-wrap">
            <span class="sr-only">بحث في المنشورات</span>
            <input type="search" id="ref-ig-search" class="ref-ig-search" placeholder="ابحث في المنشورات… (مثال: عبدالله، غوص، الحد)" autocomplete="off" />
          </label>
          <p id="ref-ig-count" class="ref-ig-count" aria-live="polite">{len(posts)} منشور</p>
        </div>
        <p id="ref-ig-empty" class="ref-ig-empty" hidden>لا توجد نتائج مطابقة للبحث.</p>
        <ul class="ref-ig-grid" id="ref-ig-grid">
{items}
        </ul>
        </div>

        <div id="ref-ig-lightbox" class="ref-ig-lightbox" hidden aria-hidden="true" role="dialog" aria-modal="true" aria-label="عرض الوسائط">
          <button type="button" class="ref-ig-lightbox-backdrop" aria-label="إغلاق"></button>
          <div class="ref-ig-lightbox-panel">
            <button type="button" class="ref-ig-lightbox-close" aria-label="إغلاق">&times;</button>
            <div class="ref-ig-lightbox-media" id="ref-ig-lightbox-media"></div>
          </div>
        </div>

"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(block, encoding="utf-8")
    print(f"Wrote {len(posts)} posts to {OUT}")


if __name__ == "__main__":
    main()
