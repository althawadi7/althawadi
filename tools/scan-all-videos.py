#!/usr/bin/env python3
import re, urllib.request, json
from pathlib import Path

HEADERS = {"User-Agent": "Mozilla/5.0", "X-IG-App-ID": "936619743392459"}
codes = json.loads((Path(r"J:\altahwadi/data/instagram-history.json")).read_text())["posts"]
codes = [p["shortcode"] for p in codes]

for code in codes:
    try:
        html = urllib.request.urlopen(
            urllib.request.Request(f"https://www.instagram.com/p/{code}/?hl=ar", headers=HEADERS),
            timeout=30,
        ).read().decode("utf-8", "ignore")
        v = len(re.findall(r'"video_url"', html))
        c = len(re.findall(r'"carousel_media_count":(\d+)', html))
        if v:
            print(code, "video_urls", v, "carousel", c)
    except Exception as e:
        print(code, "err", e)
