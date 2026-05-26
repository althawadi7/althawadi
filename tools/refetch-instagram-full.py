#!/usr/bin/env python3
"""Re-download Instagram history images at full size (media/?size=l)."""

import json
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "instagram-history.json"
ASSETS = ROOT / "assets" / "instagram" / "history"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def jpeg_size(data: bytes) -> tuple[int, int] | None:
    i = 2
    while i < len(data) - 8:
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        if marker in (0xC0, 0xC2):
            h = struct.unpack(">H", data[i + 5 : i + 7])[0]
            w = struct.unpack(">H", data[i + 7 : i + 9])[0]
            return w, h
        if marker in (0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0x01):
            i += 2
            continue
        ln = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + ln
    return None


def download_full(shortcode: str) -> tuple[bool, str]:
    url = f"https://www.instagram.com/p/{urllib.parse.quote(shortcode)}/media/?size=l"
    dest = ASSETS / f"{shortcode}.jpg"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=90).read()
        if len(data) < 5000:
            return False, f"too small ({len(data)} bytes)"
        size = jpeg_size(data)
        dest.write_bytes(data)
        kb = len(data) // 1024
        dim = f"{size[0]}x{size[1]}" if size else "?"
        return True, f"{dim} {kb}KB"
    except (urllib.error.URLError, OSError) as exc:
        return False, str(exc)


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ok = 0
    fail = []

    for i, post in enumerate(data.get("posts", []), 1):
        code = post["shortcode"]
        print(f"[{i}/{len(data['posts'])}] {code} ", end="", flush=True)
        success, msg = download_full(code)
        if success:
            ok += 1
            print(msg)
        else:
            fail.append(code)
            print("FAIL", msg)
        time.sleep(0.55)

    print(f"\nDone: {ok} ok, {len(fail)} failed")
    if fail:
        print("Failed:", ", ".join(fail))


if __name__ == "__main__":
    main()
