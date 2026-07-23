#!/usr/bin/env python3
"""Build full-site sitemap + enable index,follow on all public pages."""

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
NEWS_DATA = ROOT / "data" / "family-news.json"
ROBOTS = ROOT / "robots.txt"
SITEMAP_XML = ROOT / "sitemap.xml"
SITEMAP_INDEX = ROOT / "sitemap-index.xml"
SITEMAP_HTML_DIR = ROOT / "site-map"
SITEMAP_HTML = SITEMAP_HTML_DIR / "index.html"
SEO_DIR = ROOT / "seo"
SEO_SITEMAP = SEO_DIR / "sitemap.xml"

# Main public pages (all indexed)
CORE_PAGES = [
    {
        "path": "/",
        "file": ROOT / "index.html",
        "title": "الذواودة — مجلس عائلة الذوادي",
        "description": (
            "الموقع الرسمي لعائلة الذوادي (الذواودة) في البحرين — توثيق ذرية عبدالله وراشد "
            "أبناء عيسى بن خليفة بن هلال بن حسن الذوادي من العماير بني خالد."
        ),
        "priority": "1.0",
        "changefreq": "weekly",
        "group": "main",
    },
    {
        "path": "/about/",
        "file": ROOT / "about" / "index.html",
        "title": "عن عائلة الذوادي",
        "description": "تاريخ ونسب عائلة الذوادي في البحرين — العماير من بني خالد واستقرارهم في الحد.",
        "priority": "0.9",
        "changefreq": "monthly",
        "group": "main",
    },
    {
        "path": "/tree/",
        "file": ROOT / "tree" / "index.html",
        "title": "شجرة عائلة الذوادي",
        "description": "شجرة نسب ذرية عبدالله وراشد أبناء عيسى بن خليفة بن هلال بن حسن الذوادي.",
        "priority": "0.9",
        "changefreq": "monthly",
        "group": "main",
    },
    {
        "path": "/ancestors/",
        "file": ROOT / "ancestors" / "index.html",
        "title": "أجداد عائلة الذوادي — سير الأعيان",
        "description": (
            "سير أعيان الذواودة: النوخذة الشيخ عبد الله بن عيسى الذوادي والشيخ راشد بن عيسى الذوادي."
        ),
        "priority": "0.9",
        "changefreq": "monthly",
        "group": "main",
    },
    {
        "path": "/gallery/",
        "file": ROOT / "gallery" / "index.html",
        "title": "معرض صور عائلة الذوادي",
        "description": "معرض صور أرشيفية وحالية لأفراد عائلة الذوادي — من الأجداد إلى الأحفاد.",
        "priority": "0.9",
        "changefreq": "weekly",
        "group": "main",
    },
    {
        "path": "/news/",
        "file": ROOT / "news" / "index.html",
        "title": "أخبار عائلة الذوادي",
        "description": "أخبار أفراد عائلة الذوادي وإنجازاتهم من حساب مجلس الذواودة على إنستغرام.",
        "priority": "0.8",
        "changefreq": "weekly",
        "group": "main",
    },
    {
        "path": "/references/",
        "file": ROOT / "references" / "index.html",
        "title": "مراجع ومصادر عن عائلة الذوادي",
        "description": (
            "مراجع وكتب ووثائق ومنشورات توثّق نسب وعائلة الذوادي في البحرين: بني خالد والعماير ونواخذة الغوص."
        ),
        "priority": "1.0",
        "changefreq": "weekly",
        "group": "main",
    },
    {
        "path": "/contact/",
        "file": ROOT / "contact" / "index.html",
        "title": "تواصل مع عائلة الذوادي",
        "description": "تواصل مع مجلس الذواودة للمساهمة بالمعلومات والصور والوثائق العائلية.",
        "priority": "0.6",
        "changefreq": "yearly",
        "group": "main",
    },
    {
        "path": "/site-map/",
        "file": ROOT / "site-map" / "index.html",
        "title": "خريطة الموقع — الذواودة",
        "description": "خريطة كاملة لصفحات موقع عائلة الذوادي القابلة للفهرسة.",
        "priority": "0.3",
        "changefreq": "weekly",
        "group": "main",
    },
]


def set_robots_meta(path: Path, content: str = "index, follow") -> None:
    if not path.exists():
        return
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


def strengthen_page_head(page: dict) -> None:
    path: Path = page["file"]
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    title = page["title"]
    desc = page["description"]
    url = f"{SITE}{page['path']}"

    text = re.sub(r"<title>[^<]*</title>", f"<title>{html.escape(title)}</title>", text, count=1)
    if re.search(r'<meta\s+name=["\']description["\']', text, flags=re.I):
        text = re.sub(
            r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta name="description" content="{html.escape(desc, quote=True)}" />',
            text,
            count=1,
            flags=re.I,
        )
    if re.search(r'<meta\s+property=["\']og:url["\']', text, flags=re.I):
        text = re.sub(
            r'<meta\s+property=["\']og:url["\']\s+content=["\'][^"\']*["\']\s*/?>',
            f'<meta property="og:url" content="{url}" />',
            text,
            count=1,
            flags=re.I,
        )
    else:
        text = re.sub(
            r"(</head>)",
            f'  <meta property="og:url" content="{url}" />\n\\1',
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
    path.write_text(text, encoding="utf-8")
    set_robots_meta(path, "index, follow")


def reference_item_urls() -> list[dict]:
    if not CARDS.exists():
        return []
    out = []
    for card in json.loads(CARDS.read_text(encoding="utf-8")):
        slug = card.get("slug") or ""
        if not slug or re.fullmatch(r"ref-(2[0-9]|30)", slug):
            continue
        item = ROOT / "references" / "item" / slug / "index.html"
        if not item.exists():
            continue
        set_robots_meta(item, "index, follow")
        out.append(
            {
                "path": f"/references/item/{slug}/",
                "title": card.get("title") or slug,
                "priority": "0.7",
                "changefreq": "monthly",
                "group": "references",
            }
        )
    return out


def news_item_urls() -> list[dict]:
    if not NEWS_DATA.exists():
        return []
    out = []
    for post in json.loads(NEWS_DATA.read_text(encoding="utf-8")).get("posts", []):
        code = post.get("shortcode") or ""
        if not code:
            continue
        item = ROOT / "news" / "item" / code / "index.html"
        if not item.exists():
            continue
        set_robots_meta(item, "index, follow")
        caption = (post.get("caption") or post.get("text") or code).strip()
        title = caption.split("\n")[0][:100]
        out.append(
            {
                "path": f"/news/item/{code}/",
                "title": title,
                "priority": "0.6",
                "changefreq": "monthly",
                "group": "news",
            }
        )
    return out


def write_robots() -> None:
    # Prefer /seo/sitemap.xml first: GitHub Pages historically 500s when a
    # /sitemap/ HTML folder collides with /sitemap.xml (GSC "General HTTP error").
    ROBOTS.write_text(
        "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                "",
                "# Primary (conflict-safe path on GitHub Pages)",
                f"Sitemap: {SITE}/seo/sitemap.xml",
                f"Sitemap: {SITE}/sitemap-index.xml",
                f"Sitemap: {SITE}/sitemap.xml",
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
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(SITE + u['path'])}</loc>",
                f"    <lastmod>{TODAY}</lastmod>",
                f"    <changefreq>{u.get('changefreq', 'monthly')}</changefreq>",
                f"    <priority>{u.get('priority', '0.5')}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    lines.append("")
    body = "\n".join(lines)
    # UTF-8 without BOM — Google is picky about leading BOM on some parsers
    SITEMAP_XML.write_bytes(body.encode("utf-8"))
    SEO_DIR.mkdir(parents=True, exist_ok=True)
    SEO_SITEMAP.write_bytes(body.encode("utf-8"))

    # Sitemap index — GSC-friendly alternate entry point
    index_body = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            "  <sitemap>",
            f"    <loc>{SITE}/seo/sitemap.xml</loc>",
            f"    <lastmod>{TODAY}</lastmod>",
            "  </sitemap>",
            "  <sitemap>",
            f"    <loc>{SITE}/sitemap.xml</loc>",
            f"    <lastmod>{TODAY}</lastmod>",
            "  </sitemap>",
            "</sitemapindex>",
            "",
        ]
    )
    SITEMAP_INDEX.write_bytes(index_body.encode("utf-8"))
    (SEO_DIR / "sitemap-index.xml").write_bytes(index_body.encode("utf-8"))

def write_sitemap_html(urls: list[dict]) -> None:
    SITEMAP_HTML_DIR.mkdir(parents=True, exist_ok=True)
    groups = [
        ("الصفحات الرئيسية", "main"),
        ("صفحات المراجع التفصيلية", "references"),
        ("أخبار أفراد العائلة", "news"),
    ]
    sections = []
    for heading, key in groups:
        items = [u for u in urls if u.get("group") == key]
        if not items:
            continue
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
  <meta name="description" content="خريطة كاملة لجميع صفحات موقع عائلة الذوادي القابلة للفهرسة." />
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
          <a href="/" data-home class="nav-link text-foreground/70 hover:text-foreground">الرئيسية</a>
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
        جميع صفحات الموقع المفهرسة. ملف XML لـ Google Search Console:
        <a class="text-accent hover:underline font-latin" href="/seo/sitemap.xml">{SITE}/seo/sitemap.xml</a>
        ·
        <a class="text-accent hover:underline font-latin" href="/sitemap.xml">{SITE}/sitemap.xml</a>
      </p>
{''.join(sections)}
    </main>
    <footer class="mt-24 border-t border-border bg-card/40">
      <div class="mx-auto max-w-7xl px-6 py-10 text-sm text-muted-foreground">
        <a href="/" class="hover:text-accent">الرئيسية</a>
        <span class="mx-2">·</span>
        <a href="/references/" class="hover:text-accent">المراجع</a>
        <span class="mx-2">·</span>
        <a href="/contact/" class="hover:text-accent">تواصل</a>
      </div>
    </footer>
  </div>
</body>
</html>
"""
    SITEMAP_HTML.write_text(page, encoding="utf-8")


def main() -> None:
    urls: list[dict] = []
    for page in CORE_PAGES:
        strengthen_page_head(page)
        urls.append(
            {
                "path": page["path"],
                "title": page["title"],
                "priority": page["priority"],
                "changefreq": page["changefreq"],
                "group": page["group"],
            }
        )

    urls.extend(reference_item_urls())
    urls.extend(news_item_urls())

    write_robots()
    write_sitemap_xml(urls)
    write_sitemap_html(urls)
    # Ensure HTML sitemap page itself is indexed after rewrite
    set_robots_meta(SITEMAP_HTML, "index, follow")
    print(f"Full-site SEO sitemap: {len(urls)} URLs")
    print(f"  XML: {SITEMAP_XML}")
    print(f"  HTML: {SITEMAP_HTML}")


if __name__ == "__main__":
    main()
