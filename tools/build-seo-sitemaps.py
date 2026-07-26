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
    # Hidden for now (page kept on disk; restore later):
    # {
    #     "path": "/tree/",
    #     "file": ROOT / "tree" / "index.html",
    #     "title": "شجرة عائلة الذوادي",
    #     "description": "شجرة نسب ذرية عبدالله وراشد أبناء عيسى بن خليفة بن هلال بن حسن الذوادي.",
    #     "priority": "0.9",
    #     "changefreq": "monthly",
    #     "group": "main",
    # },
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
            f'<link rel="canonical" href="{url}" />',
            text,
            count=1,
            flags=re.I,
        )
    # Arabic-only hreflang (no EN mirrors)
    from site_chrome import hreflang_tags_for

    if 'hreflang="x-default"' not in text or 'hreflang="en"' in text:
        text = re.sub(
            r'\s*<link\s+rel=["\']alternate["\']\s+hreflang=["\'][^"\']+["\']\s+href=["\'][^"\']+["\']\s*/?>',
            "",
            text,
            flags=re.I,
        )
        text = re.sub(
            r'\s*<meta\s+property=["\']og:locale:alternate["\']\s+content=["\'][^"\']*["\']\s*/?>',
            "",
            text,
            flags=re.I,
        )
        tags = hreflang_tags_for("ar", page["path"])
        text = re.sub(r"(</head>)", tags + "\n\\1", text, count=1, flags=re.I)
    path.write_text(text, encoding="utf-8")
    set_robots_meta(path, "index, follow")


def _page_title(html_path: Path, fallback: str) -> str:
    try:
        text = html_path.read_text(encoding="utf-8")
    except OSError:
        return fallback
    m = re.search(r"<title>(.*?)</title>", text, flags=re.I | re.S)
    if not m:
        return fallback
    title = re.sub(r"\s+", " ", m.group(1)).strip()
    title = re.sub(r"\s*[—\-]\s*مراجع الذوادي\s*$", "", title).strip()
    return title or fallback


def _lastmod_for(path: Path) -> str:
    try:
        return date.fromtimestamp(path.stat().st_mtime).isoformat()
    except OSError:
        return TODAY


def reference_item_urls() -> list[dict]:
    """Every /references/item/*/ page on disk — no skips."""
    items_dir = ROOT / "references" / "item"
    if not items_dir.exists():
        return []

    titles: dict[str, str] = {}
    if CARDS.exists():
        for card in json.loads(CARDS.read_text(encoding="utf-8")):
            slug = card.get("slug") or ""
            if slug:
                titles[slug] = card.get("title") or slug

    out = []
    for item_dir in sorted(items_dir.iterdir(), key=lambda p: p.name.lower()):
        page = item_dir / "index.html"
        if not item_dir.is_dir() or not page.exists():
            continue
        slug = item_dir.name
        set_robots_meta(page, "index, follow")
        title = titles.get(slug) or _page_title(page, slug)
        out.append(
            {
                "path": f"/references/item/{slug}/",
                "title": title,
                "priority": "0.9",
                "changefreq": "weekly",
                "group": "references",
                "lastmod": _lastmod_for(page),
                "file": page,
            }
        )
    return out


def news_item_urls() -> list[dict]:
    items_dir = ROOT / "news" / "item"
    if not items_dir.exists():
        return []

    captions: dict[str, str] = {}
    if NEWS_DATA.exists():
        for post in json.loads(NEWS_DATA.read_text(encoding="utf-8")).get("posts", []):
            code = post.get("shortcode") or ""
            if not code:
                continue
            caption = (post.get("caption") or post.get("text") or code).strip()
            captions[code] = caption.split("\n")[0][:100]

    out = []
    for item_dir in sorted(items_dir.iterdir(), key=lambda p: p.name.lower()):
        page = item_dir / "index.html"
        if not item_dir.is_dir() or not page.exists():
            continue
        code = item_dir.name
        set_robots_meta(page, "index, follow")
        out.append(
            {
                "path": f"/news/item/{code}/",
                "title": captions.get(code) or _page_title(page, code),
                "priority": "0.7",
                "changefreq": "weekly",
                "group": "news",
                "lastmod": _lastmod_for(page),
                "file": page,
            }
        )
    return out


def write_robots() -> None:
    ROBOTS.write_text(
        "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                "# Arabic-only site (English mirrors disabled)",
                "Disallow: /en/",
                "# Family tree page temporarily hidden",
                "Disallow: /tree/",
                "",
                "# Single sitemap (all pages)",
                f"Sitemap: {SITE}/sitemap.xml",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _url_entry(u: dict) -> list[str]:
    loc = html.escape(SITE + u["path"])
    lastmod = u.get("lastmod") or TODAY
    return [
        "  <url>",
        f"    <loc>{loc}</loc>",
        f"    <lastmod>{lastmod}</lastmod>",
        f"    <changefreq>{u.get('changefreq', 'monthly')}</changefreq>",
        f"    <priority>{u.get('priority', '0.5')}</priority>",
        "  </url>",
    ]


def _write_urlset(path: Path, urls: list[dict]) -> bytes:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        lines.extend(_url_entry(u))
    lines.append("</urlset>")
    lines.append("")
    body = "\n".join(lines).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return body


def write_sitemap_xml(urls: list[dict]) -> None:
    """One flat urlset only: /sitemap.xml (mirrored under /seo/sitemap.xml)."""
    SEO_DIR.mkdir(parents=True, exist_ok=True)

    ar_urls = [u for u in urls if not str(u["path"]).startswith("/en")]
    body = _write_urlset(SITEMAP_XML, ar_urls)
    # Same file under /seo/ for old GSC bookmarks
    _write_urlset(SEO_SITEMAP, ar_urls)
    _write_urlset(SEO_DIR / "sitemap-ar.xml", ar_urls)

    txt = "\n".join(SITE + u["path"] for u in ar_urls) + "\n"
    (ROOT / "sitemap.txt").write_text(txt, encoding="utf-8")
    (SEO_DIR / "sitemap.txt").write_text(txt, encoding="utf-8")

    # Index also points only at the single flat sitemap
    index_body = "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            "  <sitemap>",
            f"    <loc>{SITE}/sitemap.xml</loc>",
            f"    <lastmod>{TODAY}</lastmod>",
            "  </sitemap>",
            "</sitemapindex>",
            "",
        ]
    ).encode("utf-8")
    SITEMAP_INDEX.write_bytes(index_body)
    (SEO_DIR / "sitemap-index.xml").write_bytes(index_body)

    # Remove old split sitemaps so nothing competes
    for name in (
        "sitemap-references.xml",
        "sitemap-references.txt",
        "sitemap-news.xml",
        "sitemap-main.xml",
        "sitemap-en.xml",
    ):
        p = SEO_DIR / name
        if p.exists():
            p.unlink()

    print(f"  ONE sitemap: {SITE}/sitemap.xml  ({len(ar_urls)} urls, {len(body)} bytes)")
    print(f"  Mirror:      {SITE}/seo/sitemap.xml")


def inject_references_itemlist(ref_urls: list[dict]) -> None:
    """Embed ItemList JSON-LD on /references/ so Google sees every detail URL."""
    path = ROOT / "references" / "index.html"
    if not path.exists() or not ref_urls:
        return
    elements = []
    for i, u in enumerate(ref_urls, start=1):
        elements.append(
            {
                "@type": "ListItem",
                "position": i,
                "url": SITE + u["path"],
                "name": u.get("title") or u["path"],
            }
        )
    payload = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "مراجع ومصادر عن عائلة الذوادي",
        "description": (
            "مراجع وكتب ووثائق ومنشورات توثّق نسب وعائلة الذوادي (الذواودة) في البحرين: "
            "بني خالد والعماير، نواخذة الغوص، ودليل الخليج وسجلات المقيمية."
        ),
        "url": f"{SITE}/references/",
        "inLanguage": "ar",
        "isPartOf": {
            "@type": "WebSite",
            "name": "الذواودة — AL Thawadi",
            "url": SITE,
        },
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(elements),
            "itemListElement": elements,
        },
    }
    script = (
        '  <script type="application/ld+json" id="althawadi-ref-itemlist">\n  '
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + "\n  </script>"
    )
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'\s*<script type="application/ld\+json"[^>]*>[\s\S]*?</script>',
        "",
        text,
        count=1,
    )
    text = re.sub(r"(</head>)", script + "\n\\1", text, count=1, flags=re.I)
    path.write_text(text, encoding="utf-8")
    print(f"  JSON-LD ItemList on /references/ ({len(elements)} items)")

def write_sitemap_html(urls: list[dict]) -> None:
    from site_chrome import footer_html, header_html, hreflang_tags_for

    SITEMAP_HTML_DIR.mkdir(parents=True, exist_ok=True)
    groups = [
        ("الصفحات الرئيسية", "main"),
        ("صفحات المراجع التفصيلية", "references"),
        ("أخبار أفراد العائلة", "news"),
        # English mirrors disabled (Arabic-only site):
        # ("Main pages (English)", "main-en"),
        # ("Reference detail pages (English)", "references-en"),
        # ("Family news (English)", "news-en"),
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

    hreflang = hreflang_tags_for("ar", "/site-map/")
    page = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="index, follow" />
  <title>خريطة الموقع — الذواودة AL Thawadi</title>
  <meta name="description" content="خريطة كاملة لجميع صفحات موقع عائلة الذوادي القابلة للفهرسة." />
  <link rel="canonical" href="{SITE}/site-map/" />
  <meta property="og:title" content="خريطة الموقع — الذواودة" />
  <meta property="og:url" content="{SITE}/site-map/" />
{hreflang}
  <link rel="stylesheet" href="/css/styles.css" />
  <script src="/js/url-clean.js"></script>
  <script src="/js/main.js" defer></script>
</head>
<body>
  <div class="min-h-screen flex flex-col">
{header_html("ar", "/site-map/")}
    <main class="flex-1 mx-auto max-w-3xl px-4 sm:px-6 py-12 w-full">
      <p class="text-xs uppercase tracking-[0.3em] text-accent font-latin">Sitemap</p>
      <h1 class="font-display text-3xl md:text-4xl text-foreground mt-3">خريطة الموقع</h1>
      <p class="mt-4 text-muted-foreground leading-7">
        جميع صفحات الموقع المفهرسة بالعربية. ملف XML لـ Google Search Console
        (أرسِل هذا الرابط فقط):
        <a class="text-accent hover:underline font-latin" href="/sitemap.xml">{SITE}/sitemap.xml</a>
      </p>
{''.join(sections)}
    </main>
{footer_html("ar")}
  </div>
</body>
</html>
"""
    SITEMAP_HTML.write_text(page, encoding="utf-8")


def en_mirror_urls(ar_urls: list[dict]) -> list[dict]:
    out = []
    for u in ar_urls:
        path = u["path"]
        en_path = "/en/" if path == "/" else "/en" + path
        group = u.get("group", "main")
        if not group.endswith("-en"):
            group = f"{group}-en"
        title = u.get("title") or en_path
        # Prefer English titles for main pages
        en_titles = {
            "/en/": "AL Thawadi — Family Majlis",
            "/en/about/": "About AL Thawadi",
            # "/en/tree/": "AL Thawadi Family Tree",  # hidden for now
            "/en/ancestors/": "AL Thawadi Ancestors",
            "/en/gallery/": "AL Thawadi Gallery",
            "/en/news/": "AL Thawadi Majlis News",
            "/en/references/": "AL Thawadi References & Sources",
            "/en/contact/": "Contact AL Thawadi",
            "/en/site-map/": "Sitemap — AL Thawadi",
        }
        out.append(
            {
                "path": en_path,
                "title": en_titles.get(en_path, title),
                "priority": u.get("priority", "0.5"),
                "changefreq": u.get("changefreq", "monthly"),
                "group": group,
            }
        )
    return out


def main() -> None:
    urls: list[dict] = []
    for page in CORE_PAGES:
        strengthen_page_head(page)
        entry = {
            "path": page["path"],
            "title": page["title"],
            "priority": page["priority"],
            "changefreq": page["changefreq"],
            "group": page["group"],
            "lastmod": _lastmod_for(page["file"]) if page["file"].exists() else TODAY,
        }
        urls.append(entry)

    ref_urls = reference_item_urls()
    news_urls = news_item_urls()
    urls.extend(ref_urls)
    urls.extend(news_urls)

    write_robots()
    write_sitemap_xml(urls)
    inject_references_itemlist(ref_urls)
    write_sitemap_html(urls)
    set_robots_meta(SITEMAP_HTML, "index, follow")
    print(f"Full-site SEO sitemap: {len(urls)} URLs")
    print(f"  Submit in GSC: {SITE}/sitemap.xml")


if __name__ == "__main__":
    main()
