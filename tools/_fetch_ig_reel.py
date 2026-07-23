#!/usr/bin/env python3
"""Fetch Instagram reel metadata + optional media for DZwndVCtV4L."""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from pathlib import Path

CODE = "DZwndVCtV4L"
OUT = Path(__file__).resolve().parents[1] / "assets" / "instagram" / "history"
OUT.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()


def fetch(url: str, binary: bool = False):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "ar,en;q=0.9",
            "Accept": "*/*",
        },
    )
    with urllib.request.urlopen(req, context=CTX, timeout=45) as resp:
        data = resp.read()
    return data if binary else data.decode("utf-8", "replace")


def try_urls(urls: list[str]) -> str | None:
    for url in urls:
        try:
            print("TRY", url[:120])
            html = fetch(url)
            print("  ok len", len(html))
            return html
        except Exception as e:
            print("  fail", type(e).__name__, e)
    return None


def main() -> None:
    html = try_urls(
        [
            f"https://r.jina.ai/http://www.instagram.com/p/{CODE}/",
            f"https://r.jina.ai/https://www.instagram.com/reels/{CODE}/",
            f"https://www.instagram.com/p/{CODE}/embed/captioned/",
            f"https://www.instagram.com/p/{CODE}/?hl=ar",
            f"https://www.instagram.com/reels/{CODE}/",
        ]
    )
    if not html:
        print("NO_HTML")
        return

    meta = {}
    for key, pat in [
        ("og_title", r'<meta property="og:title" content="([^"]+)"'),
        ("og_desc", r'<meta property="og:description" content="([^"]+)"'),
        ("og_image", r'<meta property="og:image" content="([^"]+)"'),
        ("og_video", r'<meta property="og:video" content="([^"]+)"'),
        ("og_video2", r'<meta property="og:video:secure_url" content="([^"]+)"'),
    ]:
        m = re.search(pat, html, re.I)
        if m:
            meta[key] = (
                m.group(1)
                .replace("&amp;", "&")
                .replace("&#x27;", "'")
                .replace("&quot;", '"')
            )

    # jina markdown-ish caption
    if "Title:" in html[:500] or "Markdown Content" in html[:800]:
        # keep raw for inspection
        (OUT.parent.parent.parent / "tools" / "_tmp_ig_reel.txt").write_text(
            html[:50000], encoding="utf-8"
        )
        print("Wrote tools/_tmp_ig_reel.txt")

    # caption patterns
    caps = []
    for pat in [
        r'"caption"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'"text"\s*:\s*"((?:\\.|[^"\\])*)"',
        r'class="Caption"[^>]*>([\s\S]*?)</div>',
    ]:
        for m in re.finditer(pat, html):
            raw = m.group(1)
            if "\\" in raw:
                try:
                    raw = bytes(raw, "utf-8").decode("unicode_escape")
                except Exception:
                    pass
            raw = re.sub(r"<[^>]+>", "", raw).strip()
            if len(raw) > 40:
                caps.append(raw)

    meta["captions_found"] = caps[:5]
    print(json.dumps({k: (v[:400] if isinstance(v, str) else v) for k, v in meta.items()}, ensure_ascii=False, indent=2))

    img = meta.get("og_image")
    if img:
        try:
            data = fetch(img, binary=True)
            dest = OUT / f"{CODE}.jpg"
            dest.write_bytes(data)
            print("saved cover", dest, len(data))
        except Exception as e:
            print("cover fail", e)

    vid = meta.get("og_video") or meta.get("og_video2")
    if vid and "instagram" in vid:
        try:
            data = fetch(vid, binary=True)
            dest = OUT / f"{CODE}_dl.mp4"
            dest.write_bytes(data)
            print("saved video", dest, len(data))
        except Exception as e:
            print("video fail", e)


if __name__ == "__main__":
    main()
