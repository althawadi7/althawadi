#!/usr/bin/env python3
"""Fetch Instagram history posts via r.jina.ai (when Instagram API is blocked)."""

import html as html_lib
import json
import re
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
ASSETS = ROOT / "assets" / "instagram" / "history"
UA = {"User-Agent": "Mozilla/5.0 (compatible; AlThawadiBot/1.0)"}

SHORTCODES = [
    "DaanHrxsWB5",
    "DalEy-tgkDn",
    "Da0dbXTgWDr",
    "DaIyTwcg3d1",
    "DaNLL_xAuXx",
    "DaU754bAgdT",
]


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        data = urllib.request.urlopen(req, timeout=90).read()
        if len(data) < 5000:
            return False
        dest.write_bytes(data)
        return True
    except (urllib.error.URLError, OSError) as exc:
        print(f"    download fail: {exc}")
        return False


def caption_from_jina(text: str) -> str:
    m = re.search(r"Title:([\s\S]*?)\nURL Source:", text, flags=re.I)
    if not m:
        return ""
    block = m.group(1)
    i = block.find('"')
    j = block.rfind('"')
    if i < 0 or j <= i:
        return ""
    cap = html_lib.unescape(block[i + 1 : j])
    for ch in ("\u200e", "\u200f", "\u2066", "\u2067", "\u2068", "\u2069", "\ufeff"):
        cap = cap.replace(ch, "")
    return cap.strip().strip('"').strip()


def image_urls_from_jina(text: str) -> list[str]:
    urls = re.findall(r"!\[[^\]]*\]\((https://scontent[^)\s]+)\)", text)
    out = []
    seen_keys = set()
    for u in urls:
        if "s150x150" in u:
            continue
        if "t51.82787-15" not in u and "t51.2885-15" not in u:
            continue
        key_m = re.search(r"ig_cache_key=([^&]+)", u)
        key = key_m.group(1) if key_m else u.split("?")[0]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        out.append(u)
    return out


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    by_code = {p["shortcode"]: p for p in data.get("posts", [])}

    updated = []
    failed = []
    for i, code in enumerate(SHORTCODES, 1):
        print(f"[{i}/{len(SHORTCODES)}] {code}")
        try:
            text = fetch_text(f"https://r.jina.ai/http://www.instagram.com/p/{code}/")
        except Exception as exc:
            print(f"  jina fail: {exc}")
            failed.append(code)
            continue

        caption = caption_from_jina(text)
        urls = image_urls_from_jina(text)
        print(f"  caption={len(caption)} chars, media_urls={len(urls)}")
        if not caption:
            print("  WARN empty caption")
            (ROOT / "data" / f"_debug-jina-{code}.txt").write_text(text[:12000], encoding="utf-8")

        local_images: list[str] = []
        for idx, url in enumerate(urls):
            suffix = f"_{idx}" if idx else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            if download(url, dest):
                local_images.append(f"assets/instagram/history/{code}{suffix}.jpg")

        # Fallback: keep previously downloaded cover if CDN download failed
        if not local_images:
            prev = by_code.get(code, {})
            local_images = list(prev.get("local_images") or [])
            if not local_images and (ASSETS / f"{code}.jpg").exists():
                local_images = [f"assets/instagram/history/{code}.jpg"]

        entry = {
            "shortcode": code,
            "url": f"https://www.instagram.com/p/{code}/?hl=ar",
            "type": "album" if len(local_images) > 1 else "image",
            "timestamp": by_code.get(code, {}).get("timestamp", 0),
            "caption": caption,
            "local_images": local_images,
            "cover": local_images[0] if local_images else None,
            "image_count": len(local_images),
        }
        by_code[code] = entry
        updated.append(code)
        time.sleep(1.2)

    new_set = set(SHORTCODES)
    head = [by_code[c] for c in SHORTCODES if c in by_code]
    rest = [p for p in data.get("posts", []) if p.get("shortcode") not in new_set]
    data["posts"] = head + rest
    data["fetched_at"] = date.today().isoformat()
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {len(updated)}; failed={failed}; total={len(data['posts'])}")


if __name__ == "__main__":
    main()
