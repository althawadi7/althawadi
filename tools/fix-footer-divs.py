#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = '        </div>\n      </div>\n      <div class="border-t"'

for p in ROOT.rglob("*.html"):
    text = p.read_text(encoding="utf-8")
    if "footer-contact-col" not in text:
        continue
    orig = text
    text = text.replace(
        '        </div></div>\r\n      <div class="border-t',
        NEW,
    )
    text = text.replace(
        '        </div></div>\n      <div class="border-t',
        NEW,
    )
    if text != orig:
        p.write_text(text, encoding="utf-8")
        print(p.relative_to(ROOT))
