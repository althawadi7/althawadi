#!/usr/bin/env python3
"""Remove an Instagram post card by shortcode from HTML files."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = sys.argv[1] if len(sys.argv) > 1 else "DIb5jY-tkVi"

pattern = re.compile(
    rf'\s*<li class="ref-ig-card" id="ig-{re.escape(CODE)}"[\s\S]*?</li>\n',
    re.MULTILINE,
)

for rel in ("references.html", "partials/ref-instagram-posts.html"):
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    new, n = pattern.subn("\n", text, count=1)
    if n:
        path.write_text(new, encoding="utf-8")
        print(f"Removed ig-{CODE} from {rel}")
    else:
        print(f"Not found in {rel}")
