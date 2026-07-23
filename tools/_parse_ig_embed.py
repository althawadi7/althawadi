#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import urllib.request
import ssl
from pathlib import Path

CODE = "DZwndVCtV4L"
ROOT = Path(__file__).resolve().parents[1]
html_path = ROOT / "tools" / "_tmp_ig_embed.html"
html = html_path.read_text(encoding="utf-8")

# Arabic chunks
ar = re.findall(r"[\u0600-\u06FF][\u0600-\u06FF\s\dA-Za-z#@.,،؛:!؟\-\"']{15,}", html)
print("arabic chunks", len(ar))
seen = set()
for a in ar:
    a = re.sub(r"\s+", " ", a).strip()
    if a in seen or len(a) < 20:
        continue
    seen.add(a)
    print("---", a[:400])

# Find media urls in escaped JSON
urls = re.findall(r"https:\\/\\/[^\"\\]+", html)
urls = [u.replace("\\/", "/") for u in urls]
img_urls = [u for u in urls if any(x in u for x in (".jpg", ".jpeg", ".webp", "scontent", "cdninstagram"))]
vid_urls = [u for u in urls if ".mp4" in u or "video" in u.lower()]
print("\nimg sample", len(img_urls))
for u in img_urls[:20]:
    print(u[:180])
print("\nvid sample", len(vid_urls))
for u in vid_urls[:20]:
    print(u[:180])

# Try parse JSON blobs for caption text
for m in re.finditer(r'<script type="application/json"[^>]*>(\{.*?\})</script>', html, re.S):
    blob = m.group(1)
    if "Caption" in blob or "caption" in blob or "\u0628" in blob:
        # extract "text":"..." near caption
        for tm in re.finditer(r'"text"\s*:\s*"((?:\\.|[^"\\])*)"', blob):
            t = tm.group(1)
            try:
                t = json.loads(f'"{t}"')
            except Exception:
                t = t.encode("utf-8").decode("unicode_escape", errors="replace")
            if any("\u0600" <= c <= "\u06FF" for c in t) and len(t) > 30:
                print("\nTEXT:", t[:800])
