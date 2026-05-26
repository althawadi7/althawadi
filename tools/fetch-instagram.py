#!/usr/bin/env python3
"""Fetch latest Instagram data for @althawadi_majlis and save to data/instagram.json."""

import json
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "instagram.json"
ASSETS = ROOT / "assets" / "instagram"
USERNAME = "althawadi_majlis"
API_URL = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={USERNAME}"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-IG-App-ID": "936619743392459",
}


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    dest.write_bytes(urllib.request.urlopen(req, timeout=30).read())


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ROOT / "data").mkdir(parents=True, exist_ok=True)

    req = urllib.request.Request(API_URL, headers=HEADERS)
    payload = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
    user = payload["data"]["user"]

    posts = []
    for edge in user["edge_owner_to_timeline_media"]["edges"][:12]:
        node = edge["node"]
        caption = ""
        if node.get("edge_media_to_caption", {}).get("edges"):
            caption = node["edge_media_to_caption"]["edges"][0]["node"]["text"]

        shortcode = node.get("shortcode")
        thumb = node.get("thumbnail_src") or node.get("display_url")
        local_image = None
        if shortcode and thumb:
            dest = ASSETS / f"{shortcode}.jpg"
            try:
                download(thumb, dest)
                local_image = f"assets/instagram/{shortcode}.jpg"
            except OSError as exc:
                print(f"warn: could not download {shortcode}: {exc}")

        posts.append(
            {
                "shortcode": shortcode,
                "url": f"https://www.instagram.com/p/{shortcode}/",
                "type": node.get("__typename"),
                "timestamp": node.get("taken_at_timestamp"),
                "caption": caption,
                "thumbnail": thumb,
                "display_url": node.get("display_url"),
                "local_image": local_image,
            }
        )

    profile_pic = user.get("profile_pic_url_hd") or user.get("profile_pic_url")
    local_profile = None
    if profile_pic:
        profile_dest = ASSETS / "profile.jpg"
        try:
            download(profile_pic, profile_dest)
            local_profile = "assets/instagram/profile.jpg"
        except OSError as exc:
            print(f"warn: could not download profile pic: {exc}")

    out = {
        "username": user.get("username"),
        "full_name": user.get("full_name"),
        "biography": user.get("biography"),
        "followers": user["edge_followed_by"]["count"],
        "following": user["edge_follow"]["count"],
        "posts_count": user["edge_owner_to_timeline_media"]["count"],
        "profile_pic": local_profile or profile_pic,
        "profile_url": f"https://www.instagram.com/{USERNAME}/?hl=ar",
        "fetched_at": date.today().isoformat(),
        "recent_posts": posts,
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(posts)} posts to {OUT}")


if __name__ == "__main__":
    main()
