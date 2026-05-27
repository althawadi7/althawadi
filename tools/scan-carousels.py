#!/usr/bin/env python3
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "instagram-history.json").read_text(encoding="utf-8"))
HEADERS = {"User-Agent": "Mozilla/5.0", "X-IG-App-ID": "936619743392459"}

for p in DATA["posts"]:
    code = p["shortcode"]
    try:
        page = urllib.request.urlopen(
            urllib.request.Request(f"https://www.instagram.com/p/{code}/?hl=ar", headers=HEADERS),
            timeout=45,
        ).read().decode("utf-8", "ignore")
    except Exception as e:
        print(code, "ERR", e)
        continue
    m = re.search(r'"carousel_children":(true|false)', page)
    children = m.group(1) if m else "?"
    # count og:image or distinct heic/jpg in meta
    og_images = len(re.findall(r'property="og:image"', page))
    local = len(list((ROOT / "assets" / "instagram" / "history").glob(f"{code}*.jpg")))
    if children == "true" or local > 1:
        print(f"{code}: carousel_children={children} local_jpg={local}")
    time.sleep(0.3)
