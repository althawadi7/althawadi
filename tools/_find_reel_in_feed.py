#!/usr/bin/env python3
"""Find shortcode in althawadi_majlis feed and save caption + media URLs."""
from __future__ import annotations

import json
import ssl
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = "DZwndVCtV4L"
USER_ID = "619644424"
HEADERS = {
    "User-Agent": "Instagram 219.0.0.12.117 Android",
    "X-IG-App-ID": "936619743392459",
    "Accept-Language": "ar,en;q=0.9",
}
CTX = ssl.create_default_context()


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> None:
    # Also try web_info for shortcode via graphql-ish
    for url in [
        f"https://www.instagram.com/p/{TARGET}/?__a=1&__d=dis",
        f"https://i.instagram.com/api/v1/media/{TARGET}/info/",
    ]:
        try:
            print("TRY", url)
            data = get_json(url)
            (ROOT / "tools" / "_tmp_media_info.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2)[:200000],
                encoding="utf-8",
            )
            print("saved media info keys", list(data)[:20])
        except Exception as e:
            print(" fail", e)

    max_id = None
    found = None
    for page in range(20):
        url = f"https://www.instagram.com/api/v1/feed/user/{USER_ID}/?count=50"
        if max_id:
            url += f"&max_id={max_id}"
        print("page", page, "max_id", max_id)
        try:
            data = get_json(url)
        except Exception as e:
            print("feed fail", e)
            break
        items = data.get("items") or []
        print("  items", len(items))
        for item in items:
            code = item.get("code") or item.get("shortcode")
            if code == TARGET:
                found = item
                break
            # also print recent codes for debug
        if page == 0:
            print("  sample codes", [i.get("code") for i in items[:8]])
        if found:
            break
        max_id = data.get("next_max_id")
        if not max_id:
            break
        time.sleep(0.6)

    if not found:
        print("NOT FOUND in feed")
        return

    out = ROOT / "tools" / "_tmp_reel_item.json"
    out.write_text(json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8")
    cap = ((found.get("caption") or {}) or {}).get("text") or ""
    print("CAPTION:\n", cap[:2000])
    print("media_type", found.get("media_type"))
    # video versions
    vv = found.get("video_versions") or []
    print("video_versions", len(vv))
    if vv:
        print("video url", vv[0].get("url", "")[:180])
    # image
    cand = found.get("image_versions2", {}).get("candidates") or []
    print("images", len(cand))
    if cand:
        print("image url", cand[0].get("url", "")[:180])


if __name__ == "__main__":
    main()
