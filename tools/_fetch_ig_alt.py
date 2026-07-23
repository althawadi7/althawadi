#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from pathlib import Path

CODE = "DZwndVCtV4L"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "instagram" / "history"
OUT.mkdir(parents=True, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
CTX = ssl.create_default_context()


def get(url: str, binary: bool = False):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "*/*",
            "Accept-Language": "ar,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def try_get(url: str, binary: bool = False):
    try:
        print("GET", url[:140])
        data = get(url, binary=binary)
        print("  ok", len(data) if isinstance(data, (bytes, str)) else data)
        return data
    except Exception as e:
        print("  fail", type(e).__name__, e)
        return None


candidates = [
    f"https://www.ddinstagram.com/p/{CODE}/",
    f"https://www.ddinstagram.com/reels/{CODE}/",
    f"https://ddinstagram.com/p/{CODE}/",
    f"https://insta-stories-viewer.com/p/{CODE}/",
    f"https://api.instagram.com/oembed/?url=https://www.instagram.com/p/{CODE}/",
    f"https://www.instagram.com/api/v1/media/{CODE}/info/",
]

for url in candidates:
    html = try_get(url)
    if not html:
        continue
    path = ROOT / "tools" / f"_tmp_{re.sub(r'[^a-z0-9]+', '_', url)[:40]}.txt"
    if isinstance(html, str):
        path.write_text(html[:100000], encoding="utf-8")
        print("  wrote", path.name)
        # oembed json?
        if html.strip().startswith("{"):
            try:
                print(json.dumps(json.loads(html), ensure_ascii=False, indent=2)[:2000])
            except Exception:
                pass
        ar = re.findall(r"[\u0600-\u06FF].{10,200}", html)
        print("  arabic", len(ar))
        for a in ar[:8]:
            print("   ", a[:250])
        for key in ("og:title", "og:description", "og:image", "og:video"):
            m = re.search(rf'<meta[^>]+property=["\']{key}["\'][^>]+content=["\']([^"\']+)', html, re.I)
            if not m:
                m = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{key}', html, re.I)
            if m:
                print(f"  {key}:", m.group(1)[:250])
