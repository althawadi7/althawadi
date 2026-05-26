#!/usr/bin/env python3
"""Fetch selected Instagram history posts via user feed pagination."""

import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_ID = "619644424"
HEADERS = {
    "User-Agent": "Instagram 219.0.0.12.117 Android",
    "X-IG-App-ID": "936619743392459",
}
ORDER = [
    "DYg1frRABy6", "DX3tjkvgFU7", "DKSPaQot4pT", "DIb5jY-tkVi", "DIV70GZtgNN",
    "DBetmvkRmOo", "DBpq9l-i3kl", "C-ixCuuNdhp", "C-l6FMOisnj", "DAGHk3hNNAT",
    "C8nBlnbtJjg", "C8j_GlAtkLn", "C0m1kvntnLN", "CzTTSp0RjVS", "C0JF28UN0oA",
    "Cxu0HuTM4Zw", "CxuzbJnA6DP", "Cr8BolYAMd7", "CsOQ-H3MzAM", "CpQWCsktNpj",
    "Cr6kSQtrX_o", "CPvj182hg4T", "Bv_l0deFcq2", "Bv_mbFnF1tj", "CHSyFQiAST7",
    "Buw0SAGFvfs", "BuyonGkFexZ", "Bu3kpdMF9lW", "BuwySjBFvQc", "BuwzdiilqMd",
    "Buw0J_glD9C", "Br-gRJCBb7n", "Bsask1OBW5C", "BuwyET5ghvm",
]
TARGET_CODES = set(ORDER)
ASSETS = ROOT / "assets" / "instagram" / "history"
OUT = ROOT / "data" / "instagram-history.json"
CACHE = ROOT / "data" / "instagram-feed-cache.json"


def fetch_feed(max_id=None, retries=5):
    url = f"https://www.instagram.com/api/v1/feed/user/{USER_ID}/?count=50"
    if max_id:
        url += f"&max_id={max_id}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 429, 503) and attempt < retries - 1:
                wait = 3 * (attempt + 1)
                print(f"  retry {attempt + 1} after {wait}s ({exc.code})")
                time.sleep(wait)
                continue
            raise


def all_images(item):
    urls = []
    if item.get("carousel_media"):
        for slide in item["carousel_media"]:
            if slide.get("image_versions2", {}).get("candidates"):
                urls.append(slide["image_versions2"]["candidates"][0]["url"])
    elif item.get("image_versions2", {}).get("candidates"):
        urls.append(item["image_versions2"]["candidates"][0]["url"])
    elif item.get("thumbnail_url"):
        urls.append(item["thumbnail_url"])
    return urls


def media_type(item):
    if item.get("media_type") == 8 or item.get("carousel_media"):
        return "album"
    if item.get("media_type") == 2:
        return "video"
    return "image"


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
    dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())


def load_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def save_cache(found):
    CACHE.write_text(json.dumps(found, ensure_ascii=False), encoding="utf-8")


def collect_posts():
    found = load_cache()
    if len(found) >= len(TARGET_CODES):
        print(f"cache has {len(found)} posts")
        return found

    max_id = None
    pages = 0
    while pages < 30:
        pages += 1
        print(f"page {pages}...")
        data = fetch_feed(max_id)
        for item in data.get("items", []):
            code = item.get("code")
            if code in TARGET_CODES:
                found[code] = item
                print(f"  found {code} ({len(found)}/{len(TARGET_CODES)})")
        save_cache(found)
        if len(found) >= len(TARGET_CODES):
            break
        if not data.get("more_available"):
            break
        max_id = data.get("next_max_id")
        time.sleep(1.5)
    return found


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    found = collect_posts()
    posts = []
    missing = []

    for code in ORDER:
        item = found.get(code)
        if not item:
            missing.append(code)
            continue
        cap = (item.get("caption") or {}).get("text", "").strip()
        imgs = all_images(item)
        local = []
        for idx, url in enumerate(imgs):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            try:
                if not dest.exists():
                    download(url, dest)
                local.append(f"assets/instagram/history/{code}{suffix}.jpg")
            except Exception as e:
                print(f"  img fail {code}{suffix}: {e}")
        posts.append({
            "shortcode": code,
            "url": f"https://www.instagram.com/p/{code}/?hl=ar",
            "type": media_type(item),
            "timestamp": item.get("taken_at", 0),
            "caption": cap,
            "local_images": local,
            "cover": local[0] if local else None,
            "image_count": len(local),
        })
        print(f"saved post {code}")

    OUT.write_text(json.dumps({
        "source": "https://www.instagram.com/althawadi_majlis/?hl=ar",
        "description": "منشورات تاريخية مختارة من حساب مجلس الذواودة",
        "fetched_at": date.today().isoformat(),
        "posts": posts,
        "missing": missing,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone: {len(posts)}/{len(ORDER)} posts, missing: {missing}")


if __name__ == "__main__":
    main()
