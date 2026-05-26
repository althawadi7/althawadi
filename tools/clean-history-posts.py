#!/usr/bin/env python3
"""Clean captions and download images from instagram-history.json CDN URLs."""

import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "instagram-history.json"
ASSETS = ROOT / "assets" / "instagram" / "history"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def clean_caption(raw: str) -> str:
    t = html.unescape(raw)
    # Extract quoted caption from og:description format
    m = re.search(r':\s*"(.+)"\.?\s*[\u200f\u200e]*$', t, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: strip leading likes/comments line
    t = re.sub(
        r'^[\u200f\u200e\s\d,]+likes.*?althawadi_majlis[\u200f\u200e\s]+(?:في|on)[\u200f\u200e\s]+[^:\n]+:\s*"?',
        "",
        t,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return t.strip('"').strip()


def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        return True
    except Exception as exc:
        print(f"  FAIL {dest.name}: {exc}")
        return False


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads(OUT.read_text(encoding="utf-8"))
    ok = fail = 0

    for p in data["posts"]:
        p["caption"] = clean_caption(p.get("caption", ""))
        code = p["shortcode"]
        existing = sorted(ASSETS.glob(f"{code}*.jpg"))
        if existing:
            local = [f"assets/instagram/history/{f.name}" for f in existing]
            p["local_images"] = local
            p["cover"] = local[0]
            p["image_count"] = len(local)
            continue

        urls = p.get("images") or []
        if not urls and isinstance(p.get("cover"), str) and p["cover"].startswith("http"):
            urls = [p["cover"]]
        local = []
        for i, u in enumerate(urls):
            u = html.unescape(str(u)).replace("&amp;", "&")
            suffix = f"_{i}" if i else ""
            dest = ASSETS / f"{code}{suffix}.jpg"
            if not dest.exists():
                if download(u, dest):
                    ok += 1
                else:
                    fail += 1
                    continue
            local.append(f"assets/instagram/history/{code}{suffix}.jpg")
        p["local_images"] = local
        p["cover"] = local[0] if local else None
        p["image_count"] = len(local)
        p.pop("images", None)

    data["failed"] = data.get("failed", [])
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"posts={len(data['posts'])} downloaded={ok} failed={fail}")


if __name__ == "__main__":
    main()
