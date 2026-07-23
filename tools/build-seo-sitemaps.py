#!/usr/bin/env python3
"""Enable SEO indexing for references/gallery/ancestors and build sitemaps."""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://althawadi.org"
TODAY = date.today().isoformat()

CARDS = ROOT / "data" / "references-cards.json"
ROBOTS = ROOT / "robots.txt"
SITEMAP_XML = ROOT / "sitemap.xml"
SITEMAP_HTML_DIR = ROOT / "site-map"
SITEMAP_HTML = SITEMAP_HTML_DIR / "index.html"

SECTION_PAGES = [
    {
        "path": "/references/",
        "file": ROOT / "references" / "index.html",
        "title": "مراجع ومصادر عن عائلة الذوادي",
        "description": (
            "مراجع وكتب ووثائق ومنشورات توثّق نسب وعائلة الذوادي (الذواودة) في البحرين: "
            "بني خالد والعماير، نواخذة الغوص، ودليل الخليج وسجلات المقيمية."
        ),
        "priority": "1.0",
        "changefreq": "weekly",
    },
    {
        "path": "/gallery/",
        "file": ROOT / "gallery" / "index.html",
        "title": "معرض صور عائلة الذوادي",
        "description": (
            "معرض صور أرشيفية وحالية لأفراد عائلة الذوادي — من الأجداد إلى الأحفاد في الحد والبحرين."
        ),
        "priority": "0.9",
        "changefreq": "weekly",
    },
    {
        "path": "/ancestors/",
        "file": ROOT / "ancestors" / "index.html",
        "title": "أجداد عائلة الذوادي — سير الأعيان",
        "description": (
            "سير أعيان الذواودة: النوخذة الشيخ عبد الله بن عيسى الذوادي والشيخ راشد بن عيسى الذوادي، "
            "الغوص ودانة عبدالله ووثائق الحد التاريخية."
        ),
        "priority": "0.9",
        "changefreq": "monthly",
    },
]


def set_robots_meta(path: Path, content: str = "index, follow") -> None:
    text = path.read_text(encoding="utf-8")
    if re.search(r'<meta\s+name=["\']robots["\']', text, flags=re.I):
        text = re.sub(
            r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta name="robots" content="{content}" />',
            text,
            count=1,
            flags=re.I,
        )
    else:
        text = re.sub(
            r"(<head[^>]*>)",
            rf'\1\n  <meta name="robots" content="{content}" />',
            text,
            count=1,
            flags=re.I,
        )
    path.write_text(text, encoding="utf-8")


def strengthen_section_head(page: dict) -> None:
    path: Path = page["file"]
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    title = page["title"]
    desc = page["description"]
    url = f"{SITE}{page['path']}"

    text = re.sub(
        r"<title>[^<]*</title>",
        f"<title>{html.escape(title)}</title>",
        text,
        count=1,
    )
    if re.search(r'<meta\s+name=["\']description["\']', text, flags=re.I):
        text = re.sub(
            r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta name="description" content="{html.escape(desc, quote=True)}" />',
            text,
            count=1,
            flags=re.I,
        )
    else:
        text = re.sub(
            r"(<title>[^<]*</title>)",
            rf'\1\n  <meta name="description" content="{html.escape(desc, quote=True)}" />',
            text,
            count=1,
        )

    # Absolute OG URL + description
    if re.search(r'<meta\s+property=["\']og:url["\']', text, flags=re.I):
        text = re.sub(
            r'<meta\s+property=["\']og:url["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta property="og:url" content="{url}" />',
            text,
            count=1,
            flags=re.I,
        )
    if re.search(r'<meta\s+property=["\']og:description["\']', text, flags=re.I):
        text = re.sub(
            r'<meta\s+property=["\']og:description["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta property="og:description" content="{html.escape(desc, quote=True)}" />',
            text,
            count=1,
            flags=re.I,
        )
    else:
        text = re.sub(
            r'(<meta\s+property=["\']og:title["\'][^>]*/?>)',
            rf'\1\n  <meta property="og:description" content="{html.escape(desc, quote=True)}" />',
            text,
            count=1,
            flags=re.I,
        )

    if re.search(r'rel=["\']canonical["\']', text, flags=re.I):
        text = re.sub(
            r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
            f'<link rel="canonical" href="{page["path"]}" />',
            text,
            count=1,
            flags=re.I,
        )

    # JSON-LD CollectionPage (insert once)
    if "application/ld+json" not in text:
        ld = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": desc,
            "url": url,
            "isPartOf": {"@type": "WebSite", "name": "الذواودة — AL Thawadi", "url": SITE},
            "inLanguage": "ar",
        }
        ld_tag = (
            '  <script type="application/ld+json">\n'
            f"  {json.dumps(ld, ensure_ascii=False)}\n"
            "  </script>"
        )
        text = re.sub(r"</head>", ld_tag + "\n</head>", text, count=1, flags=re.I)

    path.write_text(text, encoding="utf-8")
    set_robots_meta(path, "index, follow")


def reference_item_urls() -> list[dict]:
    if not CARDS.exists():
        return []
    cards = json.loads(CARDS.read_text(encoding="utf-8"))
    out = []
    for card in cards:
        slug = card.get("slug") or ""
        if not slug:
            continue
        # Skip orphaned ghost pages from earlier broken builds
        if re.fullmatch(r"ref-(2[0-9]|30)", slug):
            continue
        item_dir = ROOT / "references" / "item" / slug / "index.html"
        if not item_dir.exists():
            continue
        set_robots_meta(item_dir, "index, follow")
        # Strengthen detail meta robots already done; ensure absolute og:url if relative
        text = item_dir.read_text(encoding="utf-8")
        abs_item = f"{SITE}/references/item/{slug}/"
        text = re.sub(
            r'<meta\s+property=["\']og:url["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta property="og:url" content="{abs_item}" />',
            text,
            count=1,
            flags=re.I,
        )
        item_dir.write_text(text, encoding="utf-8")
        out.append(
            {
                "path": f"/references/item/{slug}/",
                "title": card.get("title") or slug,
                "priority": "0.7",
                "changefreq": "monthly",
            }
        )
    return out


def write_robots() -> None:
    ROBOTS.write_text(
        "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                "",
                "# Prefer these public documentation sections",
                "Allow: /references/",
                "Allow: /gallery/",
                "Allow: /ancestors/",
                "Allow: /site-map/",
                "Allow: /seo/",
                "",
                f"Sitemap: {SITE}/sitemap.xml",
                f"Sitemap: {SITE}/seo/sitemap.xml",
                "",
            ]
        ),
        encoding="utf-8",
    )


def write_sitemap_xml(urls: list[dict]) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        loc = f"{SITE}{u['path']}"
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(loc)}</loc>",
                f"    <lastmod>{TODAY}</lastmod>",
                f"    <changefreq>{u.get('changefreq', 'monthly')}</changefreq>",
                f"    <priority>{u.get('priority', '0.5')}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    lines.append("")
    body = "\n".join(lines)
    SITEMAP_XML.write_text(body, encoding="utf-8")
    # Duplicate path (avoids rare root path caching issues in Search Console)
    seo_dir = ROOT / "seo"
    seo_dir.mkdir(parents=True, exist_ok=True)
    (seo_dir / "sitemap.xml").write_text(body, encoding="utf-8")


def write_sitemap_html(urls: list[dict]) -> None:
    SITEMAP_HTML_DIR.mkdir(parents=True, exist_ok=True)
    groups = {
        "الصفحات الرئيسية": [],
        "صفحات المراجع التفصيلية": [],
    }
    for u in urls:
        if u["path"].startswith("/references/item/"):
            groups["صفحات المراجع التفصيلية"].append(u)
        else:
            groups["الصفحات الرئيسية"].append(u)

    sections = []
    for heading, items in groups.items():
        lis = "\n".join(
            f'            <li><a href="{html.escape(i["path"])}">{html.escape(i["title"])}</a>'
            f' <span class="text-muted-foreground font-latin text-xs">{html.escape(SITE + i["path"])}</span></li>'
            for i in items
        )
        sections.append(
            f"""        <section class="mt-10">
          <h2 class="font-display text-2xl text-foreground">{html.escape(heading)}</h2>
          <p class="text-sm text-muted-foreground mt-2">{len(items)} رابطًا</p>
          <ul class="mt-4 space-y-2 text-sm leading-7">
{lis}
          </ul>
        </section>"""
        )

    page = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="index, follow" />
  <title>خريطة الموقع — الذواودة AL Thawadi</title>
  <meta name="description" content="خريطة صفحات موقع عائلة الذوادي القابلة للفهرسة: المراجع، المعرض، والأجداد." />
  <link rel="canonical" href="/site-map/" />
  <meta property="og:title" content="خريطة الموقع — الذواودة" />
  <meta property="og:url" content="{SITE}/site-map/" />
  <link rel="stylesheet" href="/css/styles.css" />
  <script src="/js/url-clean.js"></script>
  <script src="/js/main.js" defer></script>
</head>
<body>
  <div class="min-h-screen flex flex-col">
    <header class="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur">
      <div class="site-header-inner mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-4">
        <a href="/" data-home class="flex items-center gap-3 group">
          <span class="site-logo-text leading-tight">
            <span class="block font-display text-lg text-foreground">الذوادي</span>
            <span class="block text-[11px] uppercase tracking-[0.25em] text-muted-foreground font-latin">AL Thawadi</span>
          </span>
        </a>
        <nav class="hidden lg:flex items-center gap-7 text-sm">
          <a href="/ancestors/" class="nav-link text-foreground/70 hover:text-foreground">الأجداد</a>
          <a href="/gallery/" class="nav-link text-foreground/70 hover:text-foreground">الصور</a>
          <a href="/references/" class="nav-link text-foreground/70 hover:text-foreground">مراجع</a>
        </nav>
      </div>
    </header>
    <main class="flex-1 mx-auto max-w-3xl px-4 sm:px-6 py-12 w-full">
      <p class="text-xs uppercase tracking-[0.3em] text-accent font-latin">Sitemap</p>
      <h1 class="font-display text-3xl md:text-4xl text-foreground mt-3">خريطة الموقع</h1>
      <p class="mt-4 text-muted-foreground leading-7">
        صفحات مفهرسة لمحركات البحث. ملف XML لتقديمه في Google Search Console:
        <a class="text-accent hover:underline font-latin" href="/sitemap.xml">{SITE}/sitemap.xml</a>
      </p>
{''.join(sections)}
    </main>
  </div>
</body>
</html>
"""
    SITEMAP_HTML.write_text(page, encoding="utf-8")


def main() -> None:
    urls: list[dict] = []
    for page in SECTION_PAGES:
        strengthen_section_head(page)
        urls.append(
            {
                "path": page["path"],
                "title": page["title"],
                "priority": page["priority"],
                "changefreq": page["changefreq"],
            }
        )

    item_urls = reference_item_urls()
    urls.extend(item_urls)

    # HTML sitemap itself
    urls.append(
        {
            "path": "/site-map/",
            "title": "خريطة الموقع",
            "priority": "0.3",
            "changefreq": "weekly",
        }
    )

    write_robots()
    write_sitemap_xml(urls)
    write_sitemap_html(urls)
    print(f"SEO enabled. Sitemap URLs: {len(urls)}")
    print(f"  XML: {SITEMAP_XML}")
    print(f"  HTML: {SITEMAP_HTML}")
    print(f"  Submit in GSC: {SITE}/sitemap.xml")


if __name__ == "__main__":
    main()
