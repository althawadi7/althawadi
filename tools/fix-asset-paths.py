#!/usr/bin/env python3
"""Use absolute / paths for CSS, JS, images — fixes styling on subpages."""
from pathlib import Path

from site_paths import page

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "/"
PAGES = ("about", "tree", "ancestors", "gallery", "news", "references", "contact")


def fix_content(html: str) -> str:
    import re

    html = re.sub(r'\s*<base href="[^"]*"\s*/>\s*\n', "\n", html)
    html = html.replace('href="css/', f'href="{PREFIX}css/')
    html = html.replace("href='css/", f"href='{PREFIX}css/")
    html = html.replace('src="js/', f'src="{PREFIX}js/')
    html = html.replace("src='js/", f"src='{PREFIX}js/")
    html = html.replace('src="assets/', f'src="{PREFIX}assets/')
    html = html.replace("src='assets/", f"src='{PREFIX}assets/")
    html = html.replace('href="assets/', f'href="{PREFIX}assets/')
    html = html.replace('poster="assets/', f'poster="{PREFIX}assets/')
    # internal nav (relative clean URLs)
    html = html.replace('href="./"', f'href="{PREFIX}"')
    for p in PAGES:
        html = html.replace(f'href="{p}/"', f'href="{page(p)}"')
        html = html.replace(f"href='{p}/", f"href='{page(p)}")
    return html


def main() -> None:
    files = [ROOT / "index.html", ROOT / "404.html"]
    files += [ROOT / p / "index.html" for p in PAGES]
    files.append(ROOT / "partials" / "ref-instagram-posts.html")

    for path in files:
        if not path.exists():
            continue
        text = fix_content(path.read_text(encoding="utf-8"))
        path.write_text(text, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
