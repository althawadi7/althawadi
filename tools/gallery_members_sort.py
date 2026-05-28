#!/usr/bin/env python3
"""Sort gallery member posts by lineage, keeping close relatives adjacent."""

from __future__ import annotations

import re
from html import unescape

ROOT_ANCESTOR_TOKENS = {"عيسى"}

STRIP_PREFIXES = (
    r"الشيخ\s+",
    r"النوخذة\s+",
    r"النوخذه\s+",
    r"عميد\s+الذواودة\s+",
    r"عميد\s+الذوادي\s+",
    r"من\s+سكنة\s+مدينة\s+الحد\s*",
)


def clean_display_name(text: str) -> str:
    t = unescape(text or "")
    t = re.sub(r"[\u200e\u200f\u202a-\u202e\t]", "", t)
    m = re.search(r':\s*"([^"]+)"', t)
    if m:
        t = m.group(1)
    t = re.sub(r"#\S+", " ", t)
    t = re.sub(r"المرحوم[^.]*?(?:عليه|تعالى)", " ", t)
    t = re.sub(r"الله\s+يحفظه[^.]*", " ", t)
    t = re.sub(r"الله\s+يطول\s+بعمره[^.]*", " ", t)
    t = re.sub(r"رحمة\s+الله[^.]*", " ", t)
    t = re.sub(r"أخ\s+الشيخ[^.#]*", " ", t)
    t = re.sub(r"[\u2066-\u2069\u202a-\u202e]", "", t)
    for pat in STRIP_PREFIXES:
        t = re.sub(pat, " ", t, flags=re.I)
    t = t.replace("الذواودة", " ").replace("الذوادي", " ")
    t = " ".join(t.split()).strip(" .،\"'")
    if " الذوادي" in t:
        t = t.split(" الذوادي", 1)[0].strip()
    return t


def patronymic_parts(text: str) -> list[str]:
    name = clean_display_name(text)
    if not name:
        return []
    return [p.strip() for p in re.split(r"\s+بن\s+", name) if p.strip()]


def lineage_tokens(post: dict) -> tuple[str, ...]:
    raw = post.get("caption") or post.get("text") or ""
    parts = patronymic_parts(raw)

    if not parts:
        return ()

    # Convert "X بن Y بن Z" into lineage path oldest -> youngest.
    # Sorting by this path keeps relatives adjacent:
    # - brothers share the same ancestry prefix
    # - sons appear right after their father's branch
    lineage_list = list(reversed(parts))
    # Some captions include extra root ancestors (e.g. "... بن عيسى") while
    # others omit them; trimming shared root tokens keeps close relatives adjacent.
    while lineage_list and lineage_list[0] in ROOT_ANCESTOR_TOKENS:
        lineage_list.pop(0)
    return tuple(lineage_list) if lineage_list else tuple(reversed(parts))


def sort_posts(posts: list[dict]) -> list[dict]:
    # Root branch order follows first appearance in data (instead of forcing
    # عبدالله before راشد), which avoids pushing an entire branch to the bottom.
    root_order: dict[str, int] = {}
    for post in posts:
        lineage = lineage_tokens(post)
        root = lineage[0] if lineage else "~"
        if root not in root_order:
            root_order[root] = len(root_order)

    def member_sort_key(post: dict) -> tuple:
        lineage = lineage_tokens(post)
        root = lineage[0] if lineage else "~"
        # Fewer lineage tokens => older generation, so they should appear first.
        generation_depth = len(lineage) if lineage else 999
        posted = post.get("posted_at") or post.get("timestamp") or 0
        return (
            generation_depth,
            root_order.get(root, 999),
            lineage or ("~",),
            posted,
            post.get("shortcode", ""),
        )

    return sorted(posts, key=member_sort_key)
