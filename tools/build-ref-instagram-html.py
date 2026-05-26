#!/usr/bin/env python3
"""Generate static Instagram archive HTML for references.html."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
OUT = ROOT / "partials" / "ref-instagram-posts.html"


def title_from_caption(caption: str) -> str:
    line = caption.strip().split("\n")[0].strip()
    line = re.sub(r'^[\s"]+|[\s"]+$', "", line)
    if len(line) > 120:
        return line[:117].rstrip() + "…"
    return line or "منشور من @althawadi_majlis"


def caption_html(caption: str) -> str:
    clean = caption.strip().replace('"\n', "\n").strip('"')
    parts = [p.strip() for p in re.split(r"\n\n+", clean) if p.strip()]
    blocks = []
    for para in parts:
        lines = [html.escape(l.strip()) for l in para.split("\n") if l.strip()]
        inner = "<br />".join(lines)
        blocks.append(f'<p class="ref-ig-caption-p">{inner}</p>')
    return "\n              ".join(blocks)


def media_html(post: dict) -> str:
    imgs = post.get("local_images") or ([post["cover"]] if post.get("cover") else [])
    if not imgs:
        return ""
    if len(imgs) == 1:
        src = html.escape(imgs[0])
        return (
            f'<figure class="ref-ig-media">'
            f'<img src="{src}" alt="" loading="lazy" />'
            f"</figure>"
        )
    items = "".join(
        f'<figure class="ref-ig-media ref-ig-media--thumb">'
        f'<img src="{html.escape(src)}" alt="" loading="lazy" />'
        f"</figure>"
        for src in imgs
    )
    return f'<div class="ref-ig-gallery">{items}</div>'


def render_post(post: dict, index: int) -> str:
    code = post["shortcode"]
    url = html.escape(post["url"])
    title = html.escape(title_from_caption(post.get("caption", "")))
    cap = caption_html(post.get("caption", ""))
    media = media_html(post)
    num = f"{index:02d}"

    return f"""          <li class="ref-ig-post" id="ig-{code}">
            <div class="ref-ig-post-head">
              <span class="ref-ig-num">{num}</span>
              <h3 class="font-display text-xl text-foreground">{title}</h3>
              <a href="{url}" target="_blank" rel="noreferrer" class="ref-ig-link font-latin">Instagram ↗</a>
            </div>
            <div class="ref-ig-post-body">
              {media}
              <div class="ref-ig-text">
              {cap}
              </div>
            </div>
          </li>"""


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    posts = data["posts"]
    items = "\n".join(render_post(p, i) for i, p in enumerate(posts, 1))

    block = f"""        <h2 class="ref-section-title" id="instagram-archive">٥ — أرشيف منشورات @althawadi_majlis</h2>
        <p class="text-sm text-muted-foreground mb-6 leading-7">
          {len(posts)} منشوراً محفوظاً محلياً من حساب مجلس الذواودة — صور ونصوص كاملة كما نُشرت على
          <a href="https://www.instagram.com/althawadi_majlis/?hl=ar" class="text-accent hover:underline font-latin" target="_blank" rel="noreferrer">Instagram</a>.
        </p>
        <ul class="ref-ig-list space-y-8" style="list-style:none;padding:0;margin:0;">
{items}
        </ul>

"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(block, encoding="utf-8")
    print(f"Wrote {len(posts)} posts to {OUT}")


if __name__ == "__main__":
    main()
