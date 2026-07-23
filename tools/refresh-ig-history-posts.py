#!/usr/bin/env python3
"""Refresh specific Instagram history posts via Instaloader (caption + images)."""

import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import instaloader

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
ASSETS = ROOT / "assets" / "instagram" / "history"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
SLEEP = 3.0

SHORTCODES = [
    "DaanHrxsWB5",
    "DalEy-tgkDn",
    "Da0dbXTgWDr",
    "DaIyTwcg3d1",
    "DaNLL_xAuXx",
    "DaU754bAgdT",
]


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=90).read()
        if len(data) < 5000:
            return False
        dest.write_bytes(data)
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"    download fail: {exc}")
        return False


def media_urls(post) -> tuple[list[str], list[str]]:
    images: list[str] = []
    videos: list[str] = []
    if post.typename == "GraphSidecar":
        for node in post.get_sidecar_nodes():
            if node.is_video:
                if node.video_url:
                    videos.append(node.video_url)
                if node.display_url:
                    images.append(node.display_url)
            elif node.display_url:
                images.append(node.display_url)
    elif post.typename == "GraphVideo":
        if post.video_url:
            videos.append(post.video_url)
        if post.url:
            images.append(post.url)
    elif post.url:
        images.append(post.url)
    return images, videos


def media_type(post) -> str:
    if post.typename == "GraphSidecar":
        return "album"
    if post.typename == "GraphVideo":
        return "video"
    return "image"


def fetch_post(loader, code: str):
    for attempt in range(3):
        try:
            return instaloader.Post.from_shortcode(loader.context, code)
        except Exception as exc:
            wait = SLEEP * (attempt + 2)
            print(f"  retry {attempt + 1} after {wait:.0f}s ({exc})")
            time.sleep(wait)
    return None


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    by_code = {p["shortcode"]: p for p in data.get("posts", [])}

    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False,
    )
    loader.context.max_connection_attempts = 2

    updated = []
    failed = []
    for i, code in enumerate(SHORTCODES, 1):
        print(f"[{i}/{len(SHORTCODES)}] {code}")
        post = fetch_post(loader, code)
        if not post:
            failed.append(code)
            continue

        caption = (post.caption or "").strip()
        image_urls, video_urls = media_urls(post)
        local_images: list[str] = []
        local_videos: list[str] = []

        for idx, url in enumerate(image_urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            if download(url, dest):
                local_images.append(f"assets/instagram/history/{code}{suffix}.jpg")

        for idx, url in enumerate(video_urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.mp4"
            if download(url, dest):
                local_videos.append(f"assets/instagram/history/{code}{suffix}.mp4")

        entry = {
            "shortcode": code,
            "url": f"https://www.instagram.com/p/{code}/?hl=ar",
            "type": media_type(post),
            "timestamp": int(post.date_utc.timestamp()) if post.date_utc else 0,
            "caption": caption,
            "local_images": local_images,
            "cover": local_images[0] if local_images else None,
            "image_count": len(local_images),
        }
        if local_videos:
            entry["local_videos"] = local_videos
        by_code[code] = entry
        updated.append(code)
        print(f"  ok — {len(local_images)} img, {len(local_videos)} vid, caption {len(caption)} chars")
        time.sleep(SLEEP)

    # Keep requested new posts first, then the rest in previous order
    new_set = set(SHORTCODES)
    head = [by_code[c] for c in SHORTCODES if c in by_code]
    rest = [p for p in data.get("posts", []) if p.get("shortcode") not in new_set]
    # also include any updated that somehow weren't in SHORTCODES order already handled
    data["posts"] = head + rest
    data["fetched_at"] = date.today().isoformat()
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {len(updated)} posts; failed={failed}; total={len(data['posts'])}")


if __name__ == "__main__":
    main()
