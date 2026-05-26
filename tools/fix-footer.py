#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BRAND = '<a href="/althawadi/" data-home class="font-display text-2xl text-foreground hover:text-accent">الذواودة</a>'

LINKS = """<ul class="mt-4 space-y-2 text-sm" style="list-style:none;padding:0;">
            <li><a href="/althawadi/" data-home class="hover:text-accent">الرئيسية</a></li>
            <li><a href="/althawadi/about/" class="hover:text-accent">عن العائلة</a></li>
            <li><a href="/althawadi/tree/" class="hover:text-accent">شجرة العائلة</a></li>
            <li><a href="/althawadi/ancestors/" class="hover:text-accent">الأجداد</a></li>
            <li><a href="/althawadi/gallery/" class="hover:text-accent">الصور</a></li>
            <li><a href="/althawadi/news/" class="hover:text-accent">أخبار المجلس</a></li>
            <li><a href="/althawadi/references/" class="hover:text-accent">مراجع ومصادر</a></li>
            <li><a href="/althawadi/contact/" class="hover:text-accent">تواصل</a></li>
          </ul>"""


def fix_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text

    text = text.replace(
        '<div class="font-display text-2xl text-foreground">الذواودة</div>',
        BRAND,
    )

    import re

    text = re.sub(
        r'<h4 class="text-xs uppercase tracking-\[0\.3em\] text-muted-foreground font-latin">روابط</h4>\s*<ul[^>]*>.*?</ul>',
        f'<h4 class="text-xs uppercase tracking-[0.3em] text-muted-foreground font-latin">روابط</h4>\n          {LINKS}',
        text,
        count=1,
        flags=re.DOTALL,
    )

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    for p in ROOT.rglob("*.html"):
        if p.name.endswith(".html") and p.parent == ROOT and p.stem in (
            "about",
            "tree",
            "ancestors",
            "gallery",
            "news",
            "references",
            "contact",
        ):
            continue  # skip redirect stubs at root
        if "partials" in p.parts:
            continue
        if fix_file(p):
            print(p.relative_to(ROOT))


if __name__ == "__main__":
    main()
