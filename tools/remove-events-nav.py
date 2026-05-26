#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
nav_desktop = '          <a href="events.html" class="nav-link text-foreground/70 hover:text-foreground transition-colors">المناسبات</a>\n'
nav_mobile = '          <a href="events.html" class="nav-link py-1 text-foreground/80">المناسبات</a>\n'

for path in ROOT.glob("*.html"):
    if path.name == "events.html":
        continue
    text = path.read_text(encoding="utf-8")
    new = text.replace(nav_desktop, "").replace(nav_mobile, "")
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("nav:", path.name)
