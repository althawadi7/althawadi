#!/usr/bin/env python3
import instaloader
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "instagram-history.json").read_text(encoding="utf-8"))
L = instaloader.Instaloader()

for p in DATA["posts"]:
    code = p["shortcode"]
    try:
        post = instaloader.Post.from_shortcode(L.context, code)
        count = post.mediacount
        kind = post.typename
        if count > 1 or kind == "GraphSidecar":
            print(f"{code}: {kind} slides={count}")
    except Exception as exc:
        print(f"{code}: ERR {exc}")
