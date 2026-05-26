#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
lines_to_remove = [
    '          <a href="archive.html" class="nav-link text-foreground/70 hover:text-foreground transition-colors">أرشيف المنشورات</a>\n',
    '          <a href="archive.html" class="nav-link py-1 text-foreground/80">أرشيف المنشورات</a>\n',
]

for path in ROOT.glob("*.html"):
    text = path.read_text(encoding="utf-8")
    orig = text
    for line in lines_to_remove:
        text = text.replace(line, "")
    if text != orig:
        path.write_text(text, encoding="utf-8")
        print("cleaned", path.name)
