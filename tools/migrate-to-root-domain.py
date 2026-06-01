#!/usr/bin/env python3
"""Rewrite /althawadi/ asset and nav paths for root domain (althawadi.org)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (old, new)
REPLACEMENTS = [
    ("https://althawadi7.github.io/althawadi/", "https://althawadi.org/"),
    ("/althawadi/", "/"),
]

GLOBS = ("*.html", "*.js", "*.json", "*.py", "*.md", "*.css")


def should_skip(path: Path) -> bool:
    if path.name == "migrate-to-root-domain.py":
        return True
    if ".git" in path.parts:
        return True
    if "node_modules" in path.parts:
        return True
    if path.suffix == ".min.js":
        return True
    return False


def migrate_text(text: str) -> tuple[str, int]:
    count = 0
    for old, new in REPLACEMENTS:
        if old in text:
            n = text.count(old)
            text = text.replace(old, new)
            count += n
    return text, count


def main() -> None:
    total = 0
    files = 0
    for pattern in GLOBS:
        for path in ROOT.rglob(pattern):
            if should_skip(path):
                continue
            raw = path.read_text(encoding="utf-8")
            new, n = migrate_text(raw)
            if n:
                path.write_text(new, encoding="utf-8")
                print(f"{path.relative_to(ROOT)} ({n})")
                total += n
                files += 1
    print(f"Updated {files} files, {total} replacements.")


if __name__ == "__main__":
    main()
