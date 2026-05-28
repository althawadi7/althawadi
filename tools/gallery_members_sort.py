#!/usr/bin/env python3
"""Sort gallery member posts: older generations first, then branch (عبدالله before راشد)."""

from __future__ import annotations

import re
from html import unescape

BRANCH_ORDER = {
    "عبدالله": 0,
    "راشد": 1,
    "خليفة": 2,
    "محمد": 3,
    "حسن": 4,
    "هلال": 5,
}

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


def branch_rank(parts: list[str]) -> int:
    if not parts:
        return 99
    if parts[-1].startswith("عيسى") and len(parts) >= 2:
        return BRANCH_ORDER.get(parts[-2], 50)
    for part in reversed(parts):
        if part in BRANCH_ORDER:
            return BRANCH_ORDER[part]
    return 50


def member_sort_key(post: dict) -> tuple:
    raw = post.get("caption") or post.get("text") or ""
    parts = patronymic_parts(raw)
    posted = post.get("posted_at") or post.get("timestamp") or 0

    if not parts:
        return (99, ("~",), posted, post.get("shortcode", ""))

    # Convert "X بن Y بن Z" into lineage path oldest -> youngest.
    # Sorting by this path keeps relatives adjacent:
    # - brothers share the same ancestry prefix
    # - sons appear right after their father's branch
    lineage = tuple(reversed(parts))
    branch = branch_rank(parts)
    return (branch, lineage, posted, post.get("shortcode", ""))


def sort_posts(posts: list[dict]) -> list[dict]:
    return sorted(posts, key=member_sort_key)
