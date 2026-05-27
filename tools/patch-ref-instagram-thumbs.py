#!/usr/bin/env python3
"""Patch Instagram card thumbnails in references/index.html from JSON data."""

import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "build_ref_instagram_html", ROOT / "tools" / "build-ref-instagram-html.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
thumb_html = mod.thumb_html

DATA = ROOT / "data" / "instagram-history.json"
TARGETS = [
    ROOT / "references" / "index.html",
    ROOT / "partials" / "ref-instagram-posts.html",
]


def patch_file(path: Path, posts: list[dict]) -> int:
    text = path.read_text(encoding="utf-8")
    updated = 0
    for post in posts:
        code = post["shortcode"]
        thumb = thumb_html(post)
        pattern = (
            rf'(<li class="ref-ig-card" id="ig-{re.escape(code)}"[^>]*>\s*)'
            rf'(?:<button[\s\S]*?</button>|<div class="ref-ig-thumb ref-ig-thumb--empty"[\s\S]*?</div>)'
        )
        new_text, n = re.subn(pattern, rf"\1{thumb}", text, count=1, flags=re.I)
        if n:
            text = new_text
            updated += 1
    if updated:
        path.write_text(text, encoding="utf-8")
    return updated


def main() -> None:
    posts = json.loads(DATA.read_text(encoding="utf-8"))["posts"]
    for path in TARGETS:
        if not path.exists():
            print(f"skip missing {path}")
            continue
        n = patch_file(path, posts)
        print(f"{path.name}: updated {n} thumbs")


if __name__ == "__main__":
    main()
