#!/usr/bin/env python3
"""Deep scan for carousel videos in Instagram posts."""

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-IG-App-ID": "936619743392459",
}


def scan(code):
    url = f"https://www.instagram.com/p/{urllib.parse.quote(code)}/?hl=ar"
    html = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=45).read().decode("utf-8", "ignore")
    vids = re.findall(r'"video_url":"([^"]+)"', html)
    vids = [v.encode("utf-8").decode("unicode_escape") for v in vids]
    carousel = len(re.findall(r'"carousel_media"', html))
    mt2 = len(re.findall(r'"media_type":2', html))
    return len(vids), carousel, mt2


data = json.loads((ROOT / "data" / "instagram-history.json").read_text(encoding="utf-8"))
for p in data["posts"]:
    n, c, m = scan(p["shortcode"])
    if n or m:
        print(p["shortcode"], "videos", n, "carousel", c, "media_type2", m)
