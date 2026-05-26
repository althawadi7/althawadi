#!/usr/bin/env python3
"""Fetch specific Instagram posts by shortcode (caption + images)."""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "instagram-history.json"
ASSETS = ROOT / "assets" / "instagram" / "history"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-IG-App-ID": "936619743392459",
    "Accept-Language": "ar,en;q=0.9",
}

SHORTCODES = [
    "DYg1frRABy6",
    "DX3tjkvgFU7",
    "DKSPaQot4pT",
    "DIV70GZtgNN",
    "DBetmvkRmOo",
    "DBpq9l-i3kl",
    "C-ixCuuNdhp",
    "C-l6FMOisnj",
    "DAGHk3hNNAT",
    "C8nBlnbtJjg",
    "C8j_GlAtkLn",
    "C0m1kvntnLN",
    "CzTTSp0RjVS",
    "C0JF28UN0oA",
    "Cxu0HuTM4Zw",
    "CxuzbJnA6DP",
    "Cr8BolYAMd7",
    "CsOQ-H3MzAM",
    "CpQWCsktNpj",
    "Cr6kSQtrX_o",
    "CPvj182hg4T",
    "Bv_l0deFcq2",
    "Bv_mbFnF1tj",
    "CHSyFQiAST7",
    "Buw0SAGFvfs",
    "BuyonGkFexZ",
    "Bu3kpdMF9lW",
    "BuwySjBFvQc",
    "BuwzdiilqMd",
    "Buw0J_glD9C",
    "Br-gRJCBb7n",
    "Bsask1OBW5C",
    "BuwyET5ghvm",
]


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
        dest.write_bytes(urllib.request.urlopen(req, timeout=45).read())
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"  download fail {dest.name}: {exc}")
        return False


def media_large_url(shortcode: str) -> str:
    return f"https://www.instagram.com/p/{urllib.parse.quote(shortcode)}/media/?size=l"


def download_full_image(shortcode: str, dest: Path) -> bool:
    """Instagram public endpoint — full JPEG (not cropped thumbnail)."""
    return download(media_large_url(shortcode), dest)


def largest_candidate_url(candidates: list[dict]) -> str | None:
    if not candidates:
        return None
    best = max(candidates, key=lambda c: (c.get("width") or 0) * (c.get("height") or 0))
    return best.get("url")


def best_image(item: dict) -> str | None:
    if item.get("image_versions2", {}).get("candidates"):
        return largest_candidate_url(item["image_versions2"]["candidates"])
    if item.get("carousel_media"):
        first = item["carousel_media"][0]
        if first.get("image_versions2", {}).get("candidates"):
            return largest_candidate_url(first["image_versions2"]["candidates"])
    return item.get("display_url") or item.get("thumbnail_url")


def all_images(item: dict) -> list[str]:
    urls: list[str] = []
    if item.get("carousel_media"):
        for slide in item["carousel_media"]:
            if slide.get("image_versions2", {}).get("candidates"):
                url = largest_candidate_url(slide["image_versions2"]["candidates"])
                if url:
                    urls.append(url)
            elif slide.get("video_versions"):
                urls.append(slide["video_versions"][0].get("url") or slide.get("thumbnail_url", ""))
    elif item.get("image_versions2", {}).get("candidates"):
        url = largest_candidate_url(item["image_versions2"]["candidates"])
        if url:
            urls.append(url)
    elif item.get("video_versions"):
        thumb = item.get("display_url") or item.get("thumbnail_url")
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
    # Primary: public media info endpoint
    url = f"https://www.instagram.com/api/v1/media/shortcode/{urllib.parse.quote(shortcode)}/info/"
    try:
        data = fetch_json(url)
        item = data.get("items", [None])[0]
        if item:
            return item
    except Exception as exc:
        print(f"  api info fail {shortcode}: {exc}")

    # Fallback: scrape og tags from page
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
                "code": shortcode,
                "caption": {"text": caption},
                "taken_at": 0,
                "media_type": 1,
                "_fallback": True,
                "_og_image": image,
            }
    except Exception as exc:
        print(f"  page scrape fail {shortcode}: {exc}")
    return None


def normalize_post(item: dict, shortcode: str) -> dict:
    caption_obj = item.get("caption") or {}
    caption = caption_obj.get("text") if isinstance(caption_obj, dict) else str(caption_obj or "")
    images = all_images(item)
    if not images and item.get("_og_image"):
        images = [item["_og_image"]]
    if not images:
        one = best_image(item)
        if one:
            images = [one]

    return {
        "shortcode": shortcode,
        "url": f"https://www.instagram.com/p/{shortcode}/?hl=ar",
        "type": media_type_label(item),
        "timestamp": item.get("taken_at") or item.get("taken_at_timestamp") or 0,
        "caption": caption.strip(),
        "images": images,
    }


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    posts = []
    failed = []

    for i, code in enumerate(SHORTCODES, 1):
        print(f"[{i}/{len(SHORTCODES)}] {code}")
        item = fetch_post(code)
        if not item:
            failed.append(code)
            time.sleep(0.8)
            continue

        post = normalize_post(item, code)
        local_images = []
        dest = ASSETS / f"{code}.jpg"
        if download_full_image(code, dest):
            local_images.append(f"assets/instagram/history/{code}.jpg")
        else:
            for idx, img_url in enumerate(post["images"]):
                suffix = f"_{idx}" if idx else ""
                dest = ASSETS / f"{code}{suffix}.jpg"
                if download(img_url, dest):
                    local_images.append(f"assets/instagram/history/{code}{suffix}.jpg")
        post["local_images"] = local_images or post["images"]
        post["cover"] = local_images[0] if local_images else (post["images"][0] if post["images"] else None)
        posts.append(post)
        time.sleep(0.6)

    out = {
        "source": "https://www.instagram.com/althawadi_majlis/?hl=ar",
        "description": "منشورات تاريخية مختارة من حساب مجلس الذواودة",
        "fetched_at": date.today().isoformat(),
        "posts": posts,
        "failed": failed,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(posts)} posts to {OUT}")
    if failed:
        print("Failed:", ", ".join(failed))


if __name__ == "__main__":
    main()
