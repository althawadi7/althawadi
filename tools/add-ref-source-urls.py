#!/usr/bin/env python3
"""Ensure every ref-source card ends with an original-source URL block."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "references" / "index.html"

# title substring -> (url, label) ; url None = print-only
URL_BY_TITLE = {
    "من أخبار وتاريخ بني خالد": None,
    "بنو خالد عبر القرون": None,
    "القبائل والبيوتات المؤرخة في دولة البحرين": None,
    "الجمهرة في أنساب الأسر": None,
    "دليل الخليج": (
        "https://www.qdl.qa/ar/archive/81055/voyage_Persian_Gulf/voyage_Persian_Gulf-Arabic/lorimer-gulf-arabic-bahrain-ar",
        "qdl.qa — دليل الخليج (مادة البحرين)",
    ),
    "تقرير استخباري بريطاني — تقسيم بني خالد": (
        "https://www.qdl.qa/en/archive/81055/voyage_Persian_Gulf/voyage_Persian_Gulf-English",
        "qdl.qa — أرشيف دليل الخليج / IOR/L/PS/20/E84/1",
    ),
    "معجم قبائل الخليج في المخطوطات البريطانية": None,
    "سجلات المقيمية البريطانية في الخليج": (
        "https://www.qdl.qa/",
        "qdl.qa — Qatar Digital Library",
    ),
    "عريضة نواخذة الغوص": (
        "https://www.startimes.com/?t=21673424",
        "startimes.com — عريضة نواخذة الغوص ودانة عبدالله الذوادي",
    ),
    "مراسلات بلدية المحرق": (
        "https://www.startimes.com/?t=21673424",
        "startimes.com — مراسلات بلدية المحرق",
    ),
    "نواخذة البحرين — بشار الحادي": (
        "https://bashaaralhadi.blogspot.com/2014/11/blog-post_5.html",
        "bashaaralhadi.blogspot.com — نواخذة البحرين",
    ),
    "أسماء سفن البحرين الشراعية": (
        "https://bashaaralhadi.blogspot.com/2010/04/blog-post_7829.html",
        "bashaaralhadi.blogspot.com — أسماء سفن البحرين الشراعية",
    ),
    "أعيان البحرين في القرن الرابع عشر الهجري": (
        "https://bashaaralhadi.blogspot.com/2010/09/3.html",
        "bashaaralhadi.blogspot.com — أعيان البحرين الجزء 3",
    ),
    "التحفة النبهانية": None,
    "تاريخ القبائل العربية في جزر البحرين": None,
    "جريدة البحرين — دانة عبد الله الذوادي": (
        "https://www.startimes.com/?t=21673424",
        "startimes.com — دانة عبدالله الذوادي / جريدة البحرين",
    ),
    "دانة عيسو ودانة الذوادي": (
        "https://www.alayam.com/Article/alayam-article/414597/Index.html",
        "alayam.com — Article 414597",
    ),
    "صحيفة الأيام — محاكم وأحكام": (
        "https://www.alayam.com/Article/courts-article/411751/Index.html",
        "alayam.com — courts-article 411751",
    ),
    "حساب مجلس الذوادي على إنستغرام": (
        "https://www.instagram.com/althawadi_majlis/?hl=ar",
        "instagram.com/althawadi_majlis",
    ),
}

PRINT_NOTE = (
    '<p class="ref-source-url mt-4 text-xs text-muted-foreground leading-6">'
    "<strong class=\"text-foreground\">المرجع الأصلي:</strong> كتاب مطبوع — لا يتوفر رابط إلكتروني موثّق."
    "</p>"
)

LINK_TEMPLATE = (
    '<p class="ref-source-url mt-4 text-sm leading-6">'
    '<strong class="text-foreground">المرجع الأصلي:</strong> '
    '<a href="{url}" target="_blank" rel="noreferrer" '
    'class="text-accent hover:underline font-latin break-all">{label}</a>'
    "</p>"
)


def url_block(title: str) -> str | None:
    for key, val in URL_BY_TITLE.items():
        if key in title:
            if val is None:
                return PRINT_NOTE
            url, label = val
            return LINK_TEMPLATE.format(url=url, label=label)
    return None


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    # Fix typo keys
    text = text.replace("البahrain", "البحرين")

    parts = re.split(r'(<li class="ref-ig-card ref-ig-card--source"[^>]*>)', text)
    out = [parts[0]]
    changed = 0

    for i in range(1, len(parts), 2):
        opener = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        chunk = opener + body

        if "ref-source-url" in chunk or 'class="ref-source-url"' in chunk:
            out.append(chunk)
            continue

        m = re.search(
            r'<h3 class="ref-ig-card-title[^"]*">([^<]+)</h3>',
            chunk,
        )
        if not m:
            out.append(chunk)
            continue

        title = m.group(1)
        block = url_block(title)
        if not block:
            out.append(chunk)
            continue

        # Remove old bare URL lines in fulltext (non ref-source-url)
        chunk = re.sub(
            r'\n\s*<a href="https?://[^"]+"[^>]*class="mt-3 inline-block text-xs text-accent[^"]*"[^>]*>[^<]+</a>',
            "",
            chunk,
        )
        chunk = re.sub(
            r'\n\s*<p class="ref-ig-caption-p font-latin">https?://[^<]+</p>',
            "",
            chunk,
        )
        chunk = re.sub(
            r'\n\s*<p class="ref-ig-caption-p font-latin">alayam\.com[^<]*</p>',
            "",
            chunk,
        )

        # Insert before closing ref-source-fulltext or ref-ig-fulltext
        inserted = False
        for wrapper in ("ref-source-fulltext", "ref-ig-fulltext"):
            pat = rf'(</div>\s*</details>\s*</div>\s*</li>\s*)(?=\s*<li class="ref-ig-card)'
            # find inner wrapper close
            inner = rf'(<div class="ref-ig-fulltext {wrapper}">.*?)(</div>\s*</details>)'
            m2 = re.search(inner, chunk, re.DOTALL)
            if m2 and block not in m2.group(1):
                chunk = chunk[: m2.start(2)] + "\n" + block + "\n" + chunk[m2.start(2) :]
                inserted = True
                changed += 1
                break
            inner2 = rf'(<div class="ref-ig-fulltext">.*?)(</div>\s*</details>)'
            m3 = re.search(inner2, chunk, re.DOTALL)
            if m3 and block not in m3.group(1):
                chunk = chunk[: m3.start(2)] + "\n" + block + "\n" + chunk[m3.start(2) :]
                inserted = True
                changed += 1
                break
        if not inserted:
            pass
        out.append(chunk)

    result = "".join(out)
    PATH.write_text(result, encoding="utf-8")
    print(f"Updated {changed} reference cards with original URL blocks.")


if __name__ == "__main__":
    main()
