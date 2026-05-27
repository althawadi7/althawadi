#!/usr/bin/env python3
"""Fetch selected family Instagram posts into data/family-news.json."""

import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import instaloader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "family-news.json"
ASSETS = ROOT / "assets" / "instagram" / "family-news"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

SHORTCODES = [
    "DMK2zPSNJqp",
    "DLuETdPtdjX",
    "DIb5jY-tkVi",
    "DIdu5N8NvCl",
    "DBVblo1tDCK",
    "C01oFAgNqxk",
    "C0hJiFqN3Qj",
    "CybcWAYtRfJ",
    "Ce2oYLuP9AE",
]


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=90).read()
        if len(data) < 5000:
            return False
        dest.write_bytes(data)
        return True
    except (urllib.error.URLError, OSError):
        return False


def clean_text(text: str) -> str:
    return " ".join((text or "").split())


def first_comment_text(post) -> str:
    try:
        for c in post.get_comments():
            owner = (c.owner.username or "").lower()
            if owner == "althawadi_majlis":
                return clean_text(c.text or "")
        return ""
    except Exception:
        return ""


def post_media(post) -> tuple[list[str], list[str]]:
    images: list[str] = []
    videos: list[str] = []
    if post.typename == "GraphSidecar":
        for node in post.get_sidecar_nodes():
            if node.is_video:
                if node.video_url:
                    videos.append(node.video_url)
                if node.display_url:
                    images.append(node.display_url)
            else:
                if node.display_url:
                    images.append(node.display_url)
    elif post.typename == "GraphVideo":
        if post.video_url:
            videos.append(post.video_url)
        if post.url:
            images.append(post.url)
    else:
        if post.url:
            images.append(post.url)
    return images, videos


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    loader = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        compress_json=False,
    )
    loader.context.max_connection_attempts = 2

    posts = []
    failed = []
    for i, code in enumerate(SHORTCODES, 1):
        print(f"[{i}/{len(SHORTCODES)}] {code}")
        try:
            post = instaloader.Post.from_shortcode(loader.context, code)
        except Exception as exc:
            print(f"  fail: {exc}")
            failed.append(code)
            time.sleep(2)
            continue

        image_urls, video_urls = post_media(post)
        local_images: list[str] = []
        local_videos: list[str] = []

        for idx, url in enumerate(image_urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            if download(url, dest):
                local_images.append(f"assets/instagram/family-news/{code}{suffix}.jpg")

        for idx, url in enumerate(video_urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.mp4"
            if download(url, dest):
                local_videos.append(f"assets/instagram/family-news/{code}{suffix}.mp4")

        caption = clean_text(post.caption or "")
        comment_text = first_comment_text(post)
        combined_text = caption
        if comment_text and comment_text not in combined_text:
            combined_text = f"{combined_text}\n\n{comment_text}".strip()

        kind = "image"
        if post.typename == "GraphSidecar":
            kind = "album"
        elif post.typename == "GraphVideo":
            kind = "video"

        posts.append(
            {
                "shortcode": code,
                "url": f"https://www.instagram.com/p/{code}/",
                "type": kind,
                "caption": caption,
                "first_comment": comment_text,
                "text": combined_text,
                "local_images": local_images,
                "local_videos": local_videos,
                "cover": (local_images[0] if local_images else ""),
                "image_count": len(local_images),
            }
        )
        time.sleep(2)

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
