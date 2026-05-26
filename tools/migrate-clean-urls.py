#!/usr/bin/env python3
"""Move *.html pages into folders for clean URLs; add base href; rewrite links."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_HREF = "/althawadi/"
PAGES = ("about", "tree", "ancestors", "gallery", "news", "references", "contact")
KEEP_ROOT = ("index.html", "404.html")

LINK_MAP = {
    "index.html": "./",
    "about.html": "about/",
    "tree.html": "tree/",
    "ancestors.html": "ancestors/",
    "gallery.html": "gallery/",
    "news.html": "news/",
    "references.html": "references/",
    "contact.html": "contact/",
}


def add_base_tag(html: str) -> str:
    if "<base " in html:
        html = re.sub(
            r'<base\s+href="[^"]*"\s*/?>',
            f'<base href="{BASE_HREF}" />',
            html,
            count=1,
        )
        return html
    return html.replace(
        '<meta charset="utf-8" />',
        f'<meta charset="utf-8" />\n  <base href="{BASE_HREF}" />',
        1,
    )


def rewrite_links(html: str) -> str:
    for old, new in LINK_MAP.items():
        html = html.replace(f'href="{old}"', f'href="{new}"')
        html = html.replace(f"href='{old}'", f"href='{new}'")
    # anchors: references.html#x -> references/#x
    html = re.sub(
        r'href="([a-z]+)\.html(#[^"]*)"',
        lambda m: f'href="{m.group(1)}/{m.group(2)}"',
        html,
    )
    # canonical / og:url
    html = re.sub(
        r'<link rel="canonical" href="[^"]*"',
        lambda m: m.group(0),  # handled per-file below
        html,
    )
    return html


def canonical_for(rel_path: str) -> str:
    if rel_path == "index.html":
        return BASE_HREF
    name = Path(rel_path).parent.name if rel_path.endswith("index.html") else rel_path.replace(".html", "")
    return f"{BASE_HREF}{name}/"


def set_canonical(html: str, canonical: str) -> str:
    if '<link rel="canonical"' in html:
        return re.sub(
            r'<link rel="canonical" href="[^"]*"',
            f'<link rel="canonical" href="{canonical}"',
            html,
            count=1,
        )
    return html


def set_og_url(html: str, canonical: str) -> str:
    if '<meta property="og:url"' in html:
        return re.sub(
            r'<meta property="og:url" content="[^"]*"',
            f'<meta property="og:url" content="{canonical}"',
            html,
            count=1,
        )
    return html


def process_file(path: Path, rel: str) -> None:
    html = path.read_text(encoding="utf-8")
    html = add_base_tag(html)
    html = rewrite_links(html)
    canon = canonical_for(rel)
    html = set_canonical(html, canon)
    html = set_og_url(html, canon)
    path.write_text(html, encoding="utf-8")
    print(f"  updated {rel}")


def main() -> None:
    for name in PAGES:
        src = ROOT / f"{name}.html"
        if not src.exists():
            print(f"skip missing {name}.html")
            continue
        dest_dir = ROOT / name
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / "index.html"
        if dest.exists():
            dest.unlink()
        src.rename(dest)
        print(f"moved {name}.html -> {name}/index.html")

    for rel in ["index.html", "404.html"] + [f"{p}/index.html" for p in PAGES]:
        path = ROOT / rel
        if path.exists():
            process_file(path, rel)

    print("done.")


if __name__ == "__main__":
    main()
