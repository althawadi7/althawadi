#!/usr/bin/env python3
"""Download all carousel/sidecar images for instagram-history posts."""

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
SLEEP = 5.0


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


def slide_urls(post) -> list[str]:
    if post.typename == "GraphSidecar":
        urls = []
        for node in post.get_sidecar_nodes():
            url = node.display_url or node.video_url
            if url:
                urls.append(url)
        return urls
    if post.typename == "GraphImage" and post.url:
        return [post.url]
    if post.typename == "GraphVideo" and post.url:
        return [post.url]
    return []


def media_type(post) -> str:
    if post.typename == "GraphSidecar":
        return "album"
    if post.typename == "GraphVideo":
        return "video"
    return "image"


def fetch_post(loader: instaloader.Instaloader, code: str):
    for attempt in range(3):
        try:
            return instaloader.Post.from_shortcode(loader.context, code)
        except instaloader.exceptions.ConnectionException as exc:
            wait = SLEEP * (attempt + 2)
            print(f"  retry {attempt + 1} after {wait:.0f}s ({exc})")
            time.sleep(wait)
    return None


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False,
    )
    loader.context.max_connection_attempts = 2

    albums = 0
    new_files = 0

    for i, entry in enumerate(data["posts"], 1):
        code = entry["shortcode"]
        print(f"[{i}/{len(data['posts'])}] {code}")
        post = fetch_post(loader, code)
        if not post:
            print("  skip (fetch failed)")
            time.sleep(SLEEP)
            continue

        urls = slide_urls(post)
        if not urls:
            print("  skip (no urls)")
            time.sleep(SLEEP)
            continue

        kind = media_type(post)
        if kind != "album":
            existing = sorted(ASSETS.glob(f"{code}.jpg"))
            if existing:
                entry["local_images"] = [f"assets/instagram/history/{existing[0].name}"]
                entry["cover"] = entry["local_images"][0]
                entry["image_count"] = 1
            time.sleep(1.0)
            continue

        albums += 1
        print(f"  album with {len(urls)} slides")

        local = []
        for idx, url in enumerate(urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            if not dest.exists() or kind == "album":
                if download(url, dest):
                    if kind == "album":
                        new_files += 1
                else:
                    print(f"    missing slide {idx + 1}")
                    continue
            local.append(f"assets/instagram/history/{code}{suffix}.jpg")

        if local:
            entry["type"] = kind
            entry["local_images"] = local
            entry["cover"] = local[0]
            entry["image_count"] = len(local)

        time.sleep(SLEEP)

    data["fetched_at"] = date.today().isoformat()
    data["carousel_refetch"] = date.today().isoformat()
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone: {albums} albums, wrote {new_files} slide files")


if __name__ == "__main__":
    main()
