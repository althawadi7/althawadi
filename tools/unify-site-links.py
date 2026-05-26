#!/usr/bin/env python3
"""All internal links → /althawadi/... for reliable GitHub Pages navigation."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "/althawadi/"
PAGES = ("about", "tree", "ancestors", "gallery", "news", "references", "contact")


def fix_html(html: str) -> str:
    for p in PAGES:
        # page/#anchor (any prefix)
        html = re.sub(
            rf'href="(?:\.\./)*(?:/althawadi/)?{p}/(#[^"]+)"',
            rf'href="{SITE}{p}/\1"',
            html,
        )
        html = re.sub(
            rf'href="(?:\.\./)*(?:/althawadi/)?{p}/"',
            f'href="{SITE}{p}/"',
            html,
        )
    html = html.replace('href="../css/', 'href="/althawadi/css/')
    html = html.replace('src="../js/', 'src="/althawadi/js/')
    html = html.replace('href="css/', 'href="/althawadi/css/')
    html = html.replace('src="js/', 'src="/althawadi/js/')
    return html


def main() -> None:
    for path in ROOT.rglob("*.html"):
        if path.parent.name == "partials" and path.name != "ref-instagram-posts.html":
            continue
        text = path.read_text(encoding="utf-8")
        new = fix_html(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
