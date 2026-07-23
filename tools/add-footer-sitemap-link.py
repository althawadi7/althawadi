#!/usr/bin/env python3
"""Add خريطة الموقع link to every page footer that has the content nav list."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SITEMAP_LI = '<li><a href="/site-map/" class="hover:text-accent">خريطة الموقع</a></li>'
# Insert after references link inside footer content column
AFTER_REFS = re.compile(
    r'(<li><a href="[^"]*/references/"[^>]*>مراجع ومصادر</a></li>)(?!\s*<li><a href="[^"]*/site-map/")',
    flags=re.M,
)


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "/site-map/" in text and "خريطة الموقع" in text:
        # Already has at least one sitemap link in footer area — still ensure pattern
        if 'href="/site-map/"' in text or 'href="/site-map/"' in text:
            if "خريطة الموقع" in text:
                return False
    new, n = AFTER_REFS.subn(rf"\1\n            {SITEMAP_LI}", text)
    if n:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if "partials" in path.parts or "node_modules" in path.parts:
            continue
        # Skip root redirect stubs
        if path.parent == ROOT and path.name != "index.html":
            continue
        if patch(path):
            changed += 1
            print(path.relative_to(ROOT))
    print(f"Updated {changed} files")


if __name__ == "__main__":
    main()
