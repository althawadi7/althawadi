#!/usr/bin/env python3
"""Reorganize site footer navigation into grouped columns."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from footer_snippet import footer_contact_col, footer_nav_cols  # noqa: E402

NAV_COLS = footer_nav_cols()
CONTACT_COL = footer_contact_col()

OLD_LINKS = re.compile(
    r"\s*<div>\s*"
    r'<h4 class="text-xs uppercase tracking-\[0\.3em\] text-muted-foreground font-latin">روابط</h4>\s*'
    r"<ul[^>]*>.*?</ul>\s*"
    r"</div>",
    re.DOTALL,
)

OLD_CONTACT = re.compile(
    r'\s*<div(?: class="footer-contact-col")?>\s*'
    r'<h4 class="(?:text-xs uppercase tracking-\[0\.3em\] text-muted-foreground font-latin|footer-nav-heading font-latin)">تواصل</h4>.*?'
    r'</div>\s*'
    r'(?=</div>\s*<div class="border-t border-border)',
    re.DOTALL,
)


def update_footer(text: str) -> str:
    if "footer-nav-col" in text and "footer-grid" in text:
        return text

    text = text.replace(
        "mx-auto max-w-7xl px-6 py-14 grid gap-10 md:grid-cols-3",
        "mx-auto max-w-7xl px-6 py-14 footer-grid",
    )

    text = re.sub(
        r'(class="mt-24 border-t border-border bg-card/40">\s*<div class="mx-auto max-w-7xl px-6 py-14 footer-grid">\s*)<div>',
        r'\1<div class="footer-brand">',
        text,
        count=1,
    )

    text = OLD_LINKS.sub("", text)
    text = OLD_CONTACT.sub("", text)

    if "footer-nav-col" not in text:
        text = re.sub(
            r'(\s*)(</div>\s*<div class="border-t border-border/60">)',
            "\n" + NAV_COLS + "\n" + CONTACT_COL + r"\1\2",
            text,
            count=1,
        )

    return text


def main() -> None:
    updated = 0
    for path in ROOT.rglob("*.html"):
        if "partials" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if 'class="mt-24 border-t border-border bg-card/40"' not in text:
            continue
        new_text = update_footer(text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1
    print(f"Updated footer in {updated} files.")


if __name__ == "__main__":
    main()
