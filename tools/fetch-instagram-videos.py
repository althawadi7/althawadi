#!/usr/bin/env python3
"""Detect and download Instagram videos for history posts."""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
ASSETS = ROOT / "assets" / "instagram" / "history"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-IG-App-ID": "936619743392459",
    "Accept-Language": "ar,en;q=0.9",
}


def fetch_page(code: str) -> str:
    url = f"https://www.instagram.com/p/{urllib.parse.quote(code)}/?hl=ar"
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "ignore")


def extract_videos(html: str) -> list[str]:
    urls = re.findall(r'"video_url":"([^"]+)"', html)
    cleaned = []
    seen = set()
    for u in urls:
        u = u.encode("utf-8").decode("unicode_escape")
        if u not in seen:
            seen.add(u)
            cleaned.append(u)
    og = re.search(r'property="og:video(?::url)?" content="([^"]+)"', html)
    if og:
        u = og.group(1).replace("&amp;", "&")
        if u not in seen:
            cleaned.insert(0, u)
    return cleaned


def is_video_post(html: str) -> bool:
    if re.search(r'property="og:type" content="video', html):
        return True
    if '"video_url"' in html:
        return True
    if re.search(r'"media_type":\s*2', html):
        return True
    return False


def download(url: str, dest: Path) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
    dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return True


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    video_posts = []

    for post in data["posts"]:
        code = post["shortcode"]
        try:
            html = fetch_page(code)
            vids = extract_videos(html)
            has = is_video_post(html)
            print(f"{code}: video={has} urls={len(vids)}")
            if vids:
                local_videos = []
                for i, url in enumerate(vids):
                    suffix = f"_{i}" if i else ""
                    dest = ASSETS / f"{code}{suffix}.mp4"
                    if not dest.exists():
                        try:
                            download(url, dest)
                            print(f"  saved {dest.name}")
                        except Exception as exc:
                            print(f"  fail {dest.name}: {exc}")
                            continue
                    local_videos.append(f"assets/instagram/history/{code}{suffix}.mp4")
                post["local_videos"] = local_videos
                post["type"] = "video" if len(vids) == 1 and not post.get("local_images") else "album"
                if len(vids) == 1 and post.get("local_images"):
                    post["type"] = "video"
                video_posts.append(code)
            time.sleep(0.8)
        except Exception as exc:
            print(f"{code}: ERR {exc}")

    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nVideo posts: {video_posts}")


if __name__ == "__main__":
    main()
