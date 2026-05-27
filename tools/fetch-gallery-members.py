#!/usr/bin/env python3
"""Fetch selected gallery Instagram posts into data/gallery-members.json."""

import json
import re
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from html import unescape
from datetime import date
from pathlib import Path

from gallery_members_sort import sort_posts

ROOT = Path(__file__).resolve().parents[1]
INSTAGRAM_CACHE = ROOT / "data" / "instagram.json"
OUT = ROOT / "data" / "gallery-members.json"
ASSETS = ROOT / "assets" / "instagram" / "gallery-members"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-IG-App-ID": "936619743392459",
    "Accept-Language": "ar,en;q=0.9",
}

SHORTCODES = [
    "fs4qCrRSc_",
    "fs4-stxSde",
    "fs5mUixSew",
    "fs5_AgRSfd",
    "fs6WIdxSQF",
    "fs7qpSRSTG",
    "fvNPQrxSaT",
    "sL7l4YRSQV",
    "BXv2X-zlm6P",
    "BXxPNZzlQCU",
    "BXz7xNuFDVN",
    "BX0hBg2FrGB",
    "BX2_hEplZRL",
    "BX8LUx-FG0Q",
    "BX-5C7cl-KB",
    "BYTg8kYFZsg",
    "BYdFuMclVJ3",
    "BYiuaQKFyNs",
    "BYs9FbIFibw",
    "BZBGSBQlSKi",
    "BZMgF-ulJQm",
    "BZeRh_gFZ6q",
    "BaBsXM1F8Ld",
    "BaqsyNbFnDZ",
    "BfzFmntAijf",
    "Bf1cLTfA9No",
    "Bf2B3EKg_5X",
    "Bf340zCANo7",
    "BgDvBebBoTx",
    "BgqlCzbA9BW",
    "DYmffBbM3N-",
    "DYmf5qAs4Ge",
    "DYouivNATcR",
    "DYoulRSA5dW",
    "DYrBDESgx9D",
    "DYrBY4Xg4Ik",
    "DYtiyl5MAUi",
    "DYtjGY6soQ4",
    "DYyusCGATDb",
    "DYyu6LKgX-9",
    "DY1fYN3A6r6",
    "DY1grV3gsR7",
]


def instagram_seed() -> dict[str, dict]:
    if not INSTAGRAM_CACHE.exists():
        return {}
    data = json.loads(INSTAGRAM_CACHE.read_text(encoding="utf-8"))
    return {p["shortcode"]: p for p in data.get("recent_posts", []) if p.get("shortcode")}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
        data = urllib.request.urlopen(req, timeout=90).read()
        if len(data) < 5000:
            return False
        dest.write_bytes(data)
        return True
    except (urllib.error.URLError, OSError):
        return False


def clean_text(text: str) -> str:
    return " ".join(unescape(text or "").split())


def clean_caption_text(text: str) -> str:
    t = clean_text(text)
    t = re.sub(r"^\d+\s+likes?,\s+\d+\s+comments?\s+-\s+", "", t, flags=re.I)
    t = re.sub(r"^althawadi_majlis\s+.*?:\s*", "", t, flags=re.I)
    t = re.sub(r"^[\d\s‏‎]+likes?.*?\"([^\"]+)\".*$", r"\1", t, flags=re.I)
    t = t.strip().strip('"').strip()
    return t


def largest_candidate_url(candidates: list[dict]) -> str | None:
    if not candidates:
        return None
    best = max(candidates, key=lambda c: (c.get("width") or 0) * (c.get("height") or 0))
    return best.get("url")


def all_images(item: dict) -> list[str]:
    urls: list[str] = []
    if item.get("carousel_media"):
        for slide in item["carousel_media"]:
            if slide.get("image_versions2", {}).get("candidates"):
                url = largest_candidate_url(slide["image_versions2"]["candidates"])
                if url:
                    urls.append(url)
            elif slide.get("video_versions"):
                thumb = slide.get("thumbnail_url")
                if thumb:
                    urls.append(thumb)
    elif item.get("image_versions2", {}).get("candidates"):
        url = largest_candidate_url(item["image_versions2"]["candidates"])
        if url:
            urls.append(url)
    elif item.get("video_versions"):
        thumb = item.get("thumbnail_url")
        if thumb:
            urls.append(thumb)
    return [u for u in urls if u]


def media_type_label(item: dict) -> str:
    mt = item.get("media_type")
    if mt == 8 or item.get("carousel_media"):
        return "album"
    if mt == 2 or item.get("video_versions"):
        return "video"
    return "image"


def fetch_post(shortcode: str) -> dict | None:
    url = f"https://www.instagram.com/api/v1/media/shortcode/{urllib.parse.quote(shortcode)}/info/"
    try:
        data = fetch_json(url)
        item = data.get("items", [None])[0]
        if item:
            return item
    except Exception as exc:
        print(f"  api info fail {shortcode}: {exc}")

    page_url = f"https://www.instagram.com/p/{shortcode}/?hl=ar"
    try:
        req = urllib.request.Request(page_url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=45).read().decode("utf-8", errors="ignore")
        caption = ""
        m = re.search(r'property="og:description"\s+content="([^"]+)"', html)
        if m:
            caption = urllib.parse.unquote(m.group(1))
        image = ""
        m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
        if m:
            image = m.group(1)
        if caption or image:
            return {
                "caption": {"text": caption},
                "_og_image": image,
                "media_type": 1,
            }
    except Exception:
        pass
    return None


def media_large_url(shortcode: str) -> str:
    return f"https://www.instagram.com/p/{urllib.parse.quote(shortcode)}/media/?size=l"


def copy_cached_image(code: str) -> list[str]:
    dest = ASSETS / f"{code}.jpg"
    if dest.exists():
        return [f"assets/instagram/gallery-members/{code}.jpg"]
    src = ROOT / "assets" / "instagram" / f"{code}.jpg"
    if src.exists():
        shutil.copy2(src, dest)
        return [f"assets/instagram/gallery-members/{code}.jpg"]
    return []


def load_existing() -> dict[str, dict]:
    if not OUT.exists():
        return {}
    data = json.loads(OUT.read_text(encoding="utf-8"))
    return {p["shortcode"]: p for p in data.get("posts", []) if p.get("shortcode")}


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    seed = instagram_seed()
    existing = load_existing()

    posts_by_code: dict[str, dict] = {}
    failed: list[str] = []

    for i, code in enumerate(SHORTCODES, 1):
        print(f"[{i}/{len(SHORTCODES)}] {code}")
        prior = existing.get(code)
        if prior and prior.get("local_images"):
            posts_by_code[code] = prior
            print("  reuse cached entry")
            continue

        item = fetch_post(code)
        if not item and code in seed:
            item = {
                "caption": {"text": seed[code].get("caption", "")},
                "media_type": 1,
                "taken_at": seed[code].get("timestamp"),
            }
            if seed[code].get("display_url"):
                item["_og_image"] = seed[code]["display_url"]

        if not item:
            failed.append(code)
            time.sleep(2)
            continue

        image_urls = all_images(item)
        local_images: list[str] = []

        for idx, url in enumerate(image_urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            if download(url, dest):
                local_images.append(f"assets/instagram/gallery-members/{code}{suffix}.jpg")
        if not local_images:
            dest = ASSETS / f"{code}.jpg"
            if download(media_large_url(code), dest):
                local_images.append(f"assets/instagram/gallery-members/{code}.jpg")

        if not local_images and item.get("_og_image"):
            dest = ASSETS / f"{code}.jpg"
            if download(item["_og_image"], dest):
                local_images.append(f"assets/instagram/gallery-members/{code}.jpg")

        if not local_images:
            local_images = copy_cached_image(code)

        caption_obj = item.get("caption") or {}
        raw_caption = caption_obj.get("text") if isinstance(caption_obj, dict) else str(caption_obj or "")
        caption = clean_caption_text(raw_caption)
        if not caption and code in seed:
            caption = clean_caption_text(seed[code].get("caption", ""))

        posted_at = item.get("taken_at") or item.get("timestamp")
        if not posted_at and code in seed:
            posted_at = seed[code].get("timestamp")

        posts_by_code[code] = {
            "shortcode": code,
            "url": f"https://www.instagram.com/p/{code}/",
            "type": media_type_label(item),
            "caption": caption,
            "first_comment": "",
            "text": caption,
            "posted_at": posted_at or 0,
            "local_images": local_images,
            "local_videos": [],
            "cover": (local_images[0] if local_images else ""),
            "image_count": len(local_images),
        }
        time.sleep(0.8)

    posts = sort_posts([posts_by_code[c] for c in SHORTCODES if c in posts_by_code])

    out = {
        "source": "https://www.instagram.com/althawadi_majlis/?hl=ar",
        "fetched_at": date.today().isoformat(),
        "posts": posts,
        "failed": failed,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(posts)} posts to {OUT}")
    if failed:
        print("Failed:", ", ".join(failed))


if __name__ == "__main__":
    main()
