#!/usr/bin/env python3
"""Relative CSS/JS/links — works with file:// and GitHub Pages /althawadi/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("about", "tree", "ancestors", "gallery", "news", "references", "contact")
PREFIX = "/althawadi/"


def fix_root(html: str) -> str:
    html = html.replace(f"{PREFIX}css/", "css/")
    html = html.replace(f"{PREFIX}js/", "js/")
    html = html.replace(f"{PREFIX}assets/", "assets/")
    html = html.replace('href="/althawadi/"', 'href="./"')
    for p in PAGES:
        html = html.replace(f"{PREFIX}{p}/", f"{p}/")
    return html


def fix_sub(html: str) -> str:
    html = html.replace(f"{PREFIX}css/", "../css/")
    html = html.replace(f"{PREFIX}js/", "../js/")
    html = html.replace(f"{PREFIX}assets/", "../assets/")
    html = html.replace('href="/althawadi/"', 'href="../"')
    for p in PAGES:
        html = html.replace(f"{PREFIX}{p}/", f"../{p}/")
    return html


def main() -> None:
    for name in ("index.html", "404.html"):
        p = ROOT / name
        if p.exists():
            p.write_text(fix_root(p.read_text(encoding="utf-8")), encoding="utf-8")
            print("root", name)

    for page in PAGES:
        p = ROOT / page / "index.html"
        if p.exists():
            p.write_text(fix_sub(p.read_text(encoding="utf-8")), encoding="utf-8")
            print("sub", page)

    partial = ROOT / "partials" / "ref-instagram-posts.html"
    if partial.exists():
        partial.write_text(fix_sub(partial.read_text(encoding="utf-8")), encoding="utf-8")
        print("partial")


if __name__ == "__main__":
    main()
