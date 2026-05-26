#!/usr/bin/env python3
"""Old *.html URLs at repo root → redirect to clean folder URLs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("about", "tree", "ancestors", "gallery", "news", "references", "contact")

TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta http-equiv="refresh" content="0; url={target}" />
  <link rel="canonical" href="{target}" />
  <script>location.replace("{target}");</script>
  <title>جاري التحويل…</title>
</head>
<body>
  <p><a href="{target}">متابعة</a></p>
</body>
</html>
"""


def main() -> None:
    for page in PAGES:
        target = f"/althawadi/{page}/"
        path = ROOT / f"{page}.html"
        path.write_text(TEMPLATE.format(target=target), encoding="utf-8")
        print("created", path.name)

    # index.html at root stays; optional redirect from /althawadi/index.html handled in JS


if __name__ == "__main__":
    main()
