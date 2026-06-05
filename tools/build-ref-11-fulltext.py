#!/usr/bin/env python3
"""Build full HTML body for ref-11 (نواخذة البحرين) with Thawadi highlights."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "ref-11-nakhudha-source.txt"
OUT_HTML = ROOT / "partials" / "ref-11-fulltext.html"
CARDS = ROOT / "data" / "references-cards.json"
DETAIL = ROOT / "references" / "item" / "ref-11" / "index.html"
SOURCE_URL = "https://bashaaralhadi.blogspot.com/2014/11/blog-post_5.html"

THAWADI_NAMES = (
    "عبدالله بن عيسى الذوادي",
    "عبد الله بن عيسى الذوادي",
    "محمد بن متعب الذوادي",
)


def highlight_thawadi(text: str) -> str:
    esc = html.escape(text)
    for name in THAWADI_NAMES:
        esc_name = html.escape(name)
        esc = esc.replace(
            esc_name,
            f'<mark class="ref-thawadi-mark">{esc_name}</mark>',
        )
    if "الذوادي" in text and "<mark" not in esc:
        esc = re.sub(
            r"(الذوادي)",
            r'<mark class="ref-thawadi-mark">\1</mark>',
            esc,
        )
    return esc


def parse_sections(raw: str) -> list[tuple[str, list[str]]]:
    """Return [(letter_heading, [nakhudha lines]), ...]."""
    raw = raw.strip()
    # Drop title block before first حرف
    start = raw.find("حرف الألف")
    if start > 0:
        raw = raw[start:]

    sections: list[tuple[str, list[str]]] = []
    current_heading = ""
    current_lines: list[str] = []

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\*\s+\*\s+\*$", line.replace(" ", "")):
            if current_heading:
                sections.append((current_heading, current_lines))
                current_lines = []
            continue
        if line.startswith("حرف "):
            if current_heading and current_lines:
                sections.append((current_heading, current_lines))
                current_lines = []
            current_heading = line
            continue
        if line.startswith("النوخذة"):
            current_lines.append(line)
            continue

    if current_heading and current_lines:
        sections.append((current_heading, current_lines))
    return sections


def build_html(sections: list[tuple[str, list[str]]]) -> str:
    parts = [
        '<aside class="ref-thawadi-related" aria-label="ما يخص عائلة الذوادي">',
        "<h2 class=\"ref-thawadi-related-title\">نواخذة من عائلة الذوادي في القائمة</h2>",
        '<ul class="ref-thawadi-related-list">',
        "<li><strong>عبد الله بن عيسى الذوادي</strong> — حرف العين</li>",
        "<li><strong>محمد بن متعب الذوادي</strong> — حرف الميم</li>",
        "</ul>",
        '<p class="ref-thawadi-related-note">العبارات المتعلقة بالذوادي '
        '<mark class="ref-thawadi-mark">مظلّلة</mark> في نص المقال.</p>',
        "</aside>",
        '<h2 class="ref-article-h2">نواخذة البحرين</h2>',
        "<p>بقلم بشار الحادي</p>",
        '<h3 class="ref-article-h3">أسماء نواخذة البحرين مرتبين على حروف المعجم<br>'
        "بين عامي (1920–1960)</h3>",
        "<p>هذه قائمة بأسماء النواخذة التي عثرنا عليها من خلال وثائق البلدية "
        "إضافة إلى مجموعة من المصادر والدفاتر الحكومية والخاصة، والتي استطعنا "
        "من خلالها إحصاء عدد كبير من نواخذة الغوص في البahrain ربما يتجاوز "
        "الأربعمائة اسم وهذه أسماؤهم مرتبة على حروف المعجم.</p>".replace(
            "البahrain", "البحرين"
        ),
    ]

    for heading, lines in sections:
        parts.append(f'<h3 class="ref-article-h3">{html.escape(heading)}</h3>')
        parts.append('<ol class="ref-ship-list">')
        for i, line in enumerate(lines, 1):
            is_thawadi = "الذوادي" in line
            cls = "ref-ship-item ref-ship-item--thawadi" if is_thawadi else "ref-ship-item"
            body = highlight_thawadi(line)
            parts.append(f'<li class="{cls}">{body}</li>')
        parts.append("</ol>")

    parts.append(
        f'<p class="ref-source-url mt-8"><strong class="text-foreground">المرجع الأصلي:</strong> '
        f'<a href="{SOURCE_URL}" target="_blank" rel="noreferrer" '
        f'class="text-accent hover:underline font-latin break-all">'
        f"bashaaralhadi.blogspot.com — نواخذة البحرين</a></p>"
    )
    return "\n".join(parts)


def inject_detail(fulltext: str) -> None:
    text = DETAIL.read_text(encoding="utf-8")
    text = re.sub(
        r'(<div class="ref-detail-body prose-ref mt-8">)[\s\S]*?(</div>\s*<footer)',
        rf"\1{fulltext}\n        \2",
        text,
        count=1,
    )
    DETAIL.write_text(text, encoding="utf-8")


def update_cards(fulltext: str) -> None:
    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    for card in cards:
        if card["slug"] == "ref-11":
            card["fulltext"] = fulltext
            card["excerpt"] = (
                "قائمة كاملة بأسماء نواخذة الغوص في البحرين (1920–1960) مرتبة على حروف المعجم؛ "
                "يذكر عبد الله بن عيسى الذوادي ومحمد بن متعب الذوادي."
            )
            break
    CARDS.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    sections = parse_sections(raw)
    total = sum(len(lines) for _, lines in sections)
    fulltext = build_html(sections)
    OUT_HTML.write_text(fulltext + "\n", encoding="utf-8")
    inject_detail(fulltext)
    update_cards(fulltext)
    print(f"Built ref-11: {len(sections)} letters, {total} nakhudhas")


if __name__ == "__main__":
    main()
