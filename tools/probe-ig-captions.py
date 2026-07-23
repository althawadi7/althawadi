#!/usr/bin/env python3
"""Try alternate Instagram caption sources when API/Instaloader are blocked."""

import html as html_lib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODES = [
    "DaanHrxsWB5",
    "DalEy-tgkDn",
    "Da0dbXTgWDr",
    "DaIyTwcg3d1",
    "DaNLL_xAuXx",
    "DaU754bAgdT",
]
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ar,en;q=0.9",
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def clean_caption(raw: str) -> str:
    text = html_lib.unescape(raw)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").strip()
    # Drop likes/comments prefix if present
    text = re.sub(
        r"^[\u200f\u200e\s\d,]+likes?.*?althawadi_majlis[\u200f\u200e\s]+"
        r"(?:في|on)[\u200f\u200e\s]+[^:\n]+:\s*\"?",
        "",
        text,
        flags=re.I,
    )
    text = text.strip().strip('"').strip()
    return text


def from_embed(code: str) -> str:
    html = fetch(f"https://www.instagram.com/p/{code}/embed/captioned/")
    # Caption body often in .Caption class
    m = re.search(
        r'class="Caption"[^>]*>[\s\S]*?<div[^>]*class="CaptionContent"[^>]*>([\s\S]*?)</div>',
        html,
        flags=re.I,
    )
    if m:
        return clean_caption(m.group(1))
    m = re.search(r'class="Caption"[^>]*>([\s\S]*?)</div>\s*<div class="CaptionUsername"', html, flags=re.I)
    if m:
        return clean_caption(m.group(1))
    # fallback: Username + caption text near end
    m = re.search(r"@althawadi_majlis</a></span>\s*([\s\S]*?)</div>\s*</blockquote>", html, flags=re.I)
    if m:
        return clean_caption(m.group(1))
    Path(ROOT / "data" / f"_debug-embed-{code}.html").write_text(html[:20000], encoding="utf-8")
    return ""


def from_oembed(code: str) -> str:
    url = (
        "https://api.instagram.com/oembed/?url="
        + urllib.parse.quote(f"https://www.instagram.com/p/{code}/")
    )
    try:
        data = json.loads(fetch(url))
    except Exception as exc:
        print(f"  oembed fail: {exc}")
        return ""
    title = data.get("title") or ""
    return clean_caption(title)


def main() -> None:
    for code in CODES:
        print(f"=== {code}")
        cap = ""
        try:
            cap = from_embed(code)
            print(f"  embed: {len(cap)} chars")
        except Exception as exc:
            print(f"  embed err: {exc}")
        if len(cap) < 40:
            try:
                cap2 = from_oembed(code)
                print(f"  oembed: {len(cap2)} chars")
                if len(cap2) > len(cap):
                    cap = cap2
            except Exception as exc:
                print(f"  oembed err: {exc}")
        print("  preview:", repr(cap[:180]))


if __name__ == "__main__":
    main()
