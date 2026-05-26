#!/usr/bin/env python3
"""Merge references.html into one ref-ig-grid with a single top search bar."""

import re
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "references.html"


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def excerpt(text: str, max_len: int = 160) -> str:
    t = strip_tags(text)
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def li_blocks(html: str, class_hint: str) -> list[str]:
    pattern = rf"<li\b[^>]*\b{class_hint}\b[^>]*>[\s\S]*?</li>"
    return re.findall(pattern, html, flags=re.I)


def attr(block: str, name: str) -> str:
    m = re.search(rf'\b{name}="([^"]*)"', block)
    return m.group(1) if m else ""


def first_match(block: str, pattern: str) -> str:
    m = re.search(pattern, block, flags=re.I | re.S)
    return m.group(1).strip() if m else ""


def convert_source_li(block: str) -> str:
    lid = attr(block, "id")
    id_attr = f' id="{lid}"' if lid else ""

    # External link card
    if "ref-source-card--link" in block or 'class="ref-card ref-card--link' in block:
        href = first_match(block, r'<a[^>]+href="([^"]+)"')
        title = first_match(block, r"<h3[^>]*>([\s\S]*?)</h3>")
        body = first_match(block, r'<p class="mt-2 text-sm[^"]*"[^>]*>([\s\S]*?)</p>')
        url_label = first_match(block, r'<span class="mt-3 inline-block[^"]*"[^>]*>([\s\S]*?)</span>')
        search = escape(strip_tags(block), quote=True)
        return f"""          <li class="ref-ig-card ref-ig-card--source"{id_attr} data-search="{search}">
            <a href="{href}" target="_blank" rel="noreferrer" class="ref-ig-thumb ref-ig-thumb--empty ref-ig-thumb--link" aria-label="فتح الرابط">
              <span class="ref-ig-thumb-label">رابط ↗</span>
            </a>
            <div class="ref-ig-card-body">
              <div class="ref-ig-card-meta">
                <span class="ref-ig-badge">مرجع</span>
                <a href="{href}" target="_blank" rel="noreferrer" class="ref-ig-link font-latin">↗</a>
              </div>
              <h3 class="ref-ig-card-title font-display text-foreground">{title}</h3>
              <p class="ref-ig-excerpt">{excerpt(body)}</p>
              <details class="ref-ig-details">
                <summary>عرض التفاصيل</summary>
                <div class="ref-ig-fulltext">
                  <p class="ref-ig-caption-p">{body}</p>
                  <p class="ref-ig-caption-p font-latin">{url_label}</p>
                </div>
              </details>
            </div>
          </li>"""

    title = first_match(block, r"<h3[^>]*>([\s\S]*?)</h3>")
    author = first_match(
        block,
        r'<p class="text-sm text-muted-foreground mt-1[^"]*"[^>]*>([\s\S]*?)</p>',
    )
    if not author:
        author = first_match(
            block,
            r'<p class="text-sm text-muted-foreground mt-1 font-latin"[^>]*>([\s\S]*?)</p>',
        )

    # Thumb from lightbox button
    thumb = ""
    thumb_m = re.search(
        r'<button[^>]*class="[^"]*ref-ig-lightbox-trigger[^"]*"[^>]*>[\s\S]*?</button>',
        block,
        flags=re.I,
    )
    if thumb_m:
        thumb = "            " + thumb_m.group(0).replace("\n", "\n            ") + "\n"
    else:
        thumb = """            <div class="ref-ig-thumb ref-ig-thumb--empty" aria-hidden="true">
              <span class="ref-ig-thumb-label">مرجع</span>
            </div>
"""

    inner = re.sub(r"<h3[\s\S]*?</h3>", "", block, count=1, flags=re.I)
    inner = re.sub(
        r'<p class="text-sm text-muted-foreground mt-1[^"]*"[^>]*>[\s\S]*?</p>',
        "",
        inner,
        count=1,
        flags=re.I,
    )
    if thumb_m:
        inner = inner.replace(thumb_m.group(0), "", 1)

    inner = inner.strip()
    inner = re.sub(r"^\s*<li[^>]*>\s*", "", inner, flags=re.I)
    inner = re.sub(r"\s*</li>\s*$", "", inner, flags=re.I)

    search = escape(strip_tags(block), quote=True)
    summary_intro = first_match(
        inner,
        r'<p class="mt-3 text-sm text-muted-foreground leading-7"[^>]*>([\s\S]*?)</p>',
    )
    ex = excerpt(summary_intro or strip_tags(inner))

    return f"""          <li class="ref-ig-card ref-ig-card--source"{id_attr} data-search="{search}">
{thumb}            <div class="ref-ig-card-body">
              <div class="ref-ig-card-meta">
                <span class="ref-ig-badge">مرجع</span>
                <span class="ref-ig-sub">{author}</span>
              </div>
              <h3 class="ref-ig-card-title font-display text-foreground">{title}</h3>
              <p class="ref-ig-excerpt">{escape(ex)}</p>
              <details class="ref-ig-details">
                <summary>عرض التفاصيل</summary>
                <div class="ref-ig-fulltext ref-source-fulltext">
{inner}
                </div>
              </details>
            </div>
          </li>"""


def main() -> None:
    text = PATH.read_text(encoding="utf-8")

    start = text.index('<section class="mx-auto max-w-6xl px-6 pb-20 references-page"')
    end = text.index("    </main>", start)
    head, _, tail = text[:start], text[start:end], text[end:]

    # Drop duplicate notice if re-running
    head = re.sub(
        r"\s*<section class=\"mx-auto max-w-4xl px-6 py-12\">[\s\S]*?</section>\s*$",
        "\n",
        head,
        count=1,
    )

    ig_items = li_blocks(text, "ref-ig-card")
    source_items = li_blocks(text, "ref-source-card")

    converted = [convert_source_li(b) for b in source_items]
    ig_html = "\n".join("          " + re.sub(r"^\s+", "", b, count=1) for b in ig_items)

    body = f"""      <section class="mx-auto max-w-6xl px-6 pb-20 references-page" id="references-archive">
        <div class="ref-ig-toolbar ref-global-toolbar" id="ref-search-toolbar">
          <label class="ref-ig-search-wrap">
            <span class="sr-only">بحث في المراجع والمنشورات</span>
            <input type="search" id="ref-global-search" class="ref-ig-search" placeholder="ابحث في كل المراجع والمنشورات… (مثال: عبدالله، غوص، الخالدي)" autocomplete="off" />
          </label>
          <p id="ref-global-count" class="ref-ig-count" aria-live="polite"></p>
        </div>
        <p id="ref-global-empty" class="ref-ig-empty" hidden>لا توجد نتائج مطابقة للبحث.</p>

        <ul class="ref-ig-grid" id="ref-all-grid">
{chr(10).join(converted)}

{ig_html}
        </ul>

        <div id="ref-ig-lightbox" class="ref-ig-lightbox" hidden aria-hidden="true" role="dialog" aria-modal="true" aria-label="عرض الوسائط">
          <button type="button" class="ref-ig-lightbox-backdrop" aria-label="إغلاق"></button>
          <div class="ref-ig-lightbox-panel">
            <button type="button" class="ref-ig-lightbox-close" aria-label="إغلاق">&times;</button>
            <div class="ref-ig-lightbox-media" id="ref-ig-lightbox-media"></div>
          </div>
        </div>

        <div class="mt-16 border-t border-border pt-10 text-center">
          <p class="text-sm text-muted-foreground leading-8 max-w-xl mx-auto">
            هل تعرف مصدرًا أو وثيقةً تُثبت نسبًا أو حدثًا من تاريخ الذواودة في البحرين؟
            <a href="contact.html" class="text-accent hover:underline mr-1">تواصل معنا</a>
            لمراجعتها وإضافتها بعد التحقق.
          </p>
        </div>
      </section>
"""

    PATH.write_text(head + body + tail, encoding="utf-8")
    print(f"Done: {len(converted)} sources + {len(ig_items)} posts = {len(converted) + len(ig_items)} cards")


if __name__ == "__main__":
    main()
