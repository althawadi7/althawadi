#!/usr/bin/env python3
"""Shared AR/EN site chrome: header, footer, hreflang, lang toggle."""

from __future__ import annotations

SITE = "https://althawadi.org"

NAV = {
    "ar": {
        "home": "الرئيسية",
        "about": "عن العائلة",
        "tree": "شجرة العائلة",
        "ancestors": "الأجداد",
        "gallery": "الصور",
        "news": "أخبار المجلس",
        "references": "مراجع",
        "contact": "تواصل",
        "menu": "القائمة",
        "theme_dark": "تفعيل الوضع الليلي",
        "theme_light": "تفعيل الوضع الفاتح",
        "theme_title_dark": "الوضع الليلي",
        "theme_title_light": "الوضع الفاتح",
    },
    "en": {
        "home": "Home",
        "about": "About",
        "tree": "Family Tree",
        "ancestors": "Ancestors",
        "gallery": "Gallery",
        "news": "Majlis News",
        "references": "References",
        "contact": "Contact",
        "menu": "Menu",
        "theme_dark": "Enable dark mode",
        "theme_light": "Enable light mode",
        "theme_title_dark": "Dark mode",
        "theme_title_light": "Light mode",
    },
}

FOOTER = {
    "ar": {
        "site": "الموقع",
        "family": "العائلة",
        "content": "المحتوى",
        "contact": "تواصل",
        "references_full": "مراجع ومصادر",
        "sitemap": "خريطة الموقع",
        "brand_blurb": "بيت من الذكريات، وصفحة من التاريخ. نوثّق هنا نسب عائلتنا، وسير أجدادنا، وصورًا تحكي مسيرتنا جيلًا بعد جيل.",
        "contact_blurb": 'للتواصل والمساهمة بالمعلومات والصور: <a href="{base}/contact/" class="text-accent hover:underline">صفحة التواصل</a>',
        "rights": "الذواودة — جميع الحقوق محفوظة",
        "brand_name": "الذواودة",
    },
    "en": {
        "site": "Site",
        "family": "Family",
        "content": "Content",
        "contact": "Contact",
        "references_full": "References & Sources",
        "sitemap": "Sitemap",
        "brand_blurb": "An archive of AL Thawawdah — descendants of Abdullah and Rashid, sons of Isa bin Khalifa bin Hilal bin Hasan Al Thawadi — Al-‘Ama’ir of Bani Khalid.",
        "contact_blurb": 'To contribute information or photos: <a href="{base}/contact/" class="text-accent hover:underline">Contact page</a>',
        "rights": "AL Thawadi Family — All rights reserved",
        "brand_name": "AL Thawadi",
    },
}

NAV_PATHS = [
    ("home", "/"),
    ("about", "/about/"),
    ("tree", "/tree/"),
    ("ancestors", "/ancestors/"),
    ("gallery", "/gallery/"),
    ("news", "/news/"),
    ("references", "/references/"),
    ("contact", "/contact/"),
]

IG_ICON = (
    '<svg class="icon h-3.5 w-3.5" viewBox="0 0 24 24" aria-hidden="true">'
    '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/>'
    '<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>'
    '<line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>'
)
IG_ICON_LG = IG_ICON.replace("h-3.5 w-3.5", "h-4 w-4")
THEME_SVGS = (
    '<svg class="icon theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.75" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
    '<svg class="icon theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="12" r="4"/>'
    '<path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
)
MENU_SVGS = (
    '<svg id="menu-icon" class="icon h-5 w-5" viewBox="0 0 24 24" aria-hidden="true">'
    '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/>'
    '<line x1="4" x2="20" y1="18" y2="18"/></svg>'
    '<svg id="close-icon" class="icon h-5 w-5" viewBox="0 0 24 24" aria-hidden="true" style="display:none">'
    '<path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>'
)


def normalize_path(path: str) -> str:
    if not path or path == "/":
        return "/"
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return path


def ar_path_from_en(en_path: str) -> str:
    p = normalize_path(en_path)
    if p.startswith("/en/"):
        rest = p[4:]
        return "/" if rest in ("", "/") else "/" + rest.lstrip("/")
    return p


def en_path_from_ar(ar_path: str) -> str:
    p = normalize_path(ar_path)
    if p.startswith("/en/"):
        return p
    return "/en/" if p == "/" else "/en" + p


def lang_base(lang: str) -> str:
    return "/en" if lang == "en" else ""


def href(lang: str, path: str) -> str:
    """path like '/' or '/about/' relative to language root."""
    base = lang_base(lang)
    p = normalize_path(path)
    if p == "/":
        return base + "/" if base else "/"
    return f"{base}{p}"


def alternate_path(lang: str, current_path: str) -> str:
    """Return the twin path for the other language."""
    current_path = normalize_path(current_path)
    if lang == "ar":
        return en_path_from_ar(current_path)
    return ar_path_from_en(current_path)


def hreflang_tags(ar_path: str) -> str:
    """ar_path is the Arabic canonical path (e.g. /, /about/, /references/item/x/)."""
    ar_path = normalize_path(ar_path)
    en_path = en_path_from_ar(ar_path)
    return "\n".join(
        [
            f'  <link rel="alternate" hreflang="ar" href="{SITE}{ar_path}" />',
            f'  <link rel="alternate" hreflang="en" href="{SITE}{en_path}" />',
            f'  <link rel="alternate" hreflang="x-default" href="{SITE}{ar_path}" />',
            f'  <meta property="og:locale" content="{"ar_BH" if True else "en_US"}" />',
        ]
    )


def hreflang_tags_for(lang: str, path: str) -> str:
    """path is the path of the current page in its language."""
    path = normalize_path(path)
    if lang == "en":
        ar = ar_path_from_en(path)
        en = path
        og_locale = "en_US"
        og_alt = "ar_BH"
    else:
        ar = path
        en = en_path_from_ar(path)
        og_locale = "ar_BH"
        og_alt = "en_US"
    return "\n".join(
        [
            f'  <link rel="alternate" hreflang="ar" href="{SITE}{ar}" />',
            f'  <link rel="alternate" hreflang="en" href="{SITE}{en}" />',
            f'  <link rel="alternate" hreflang="x-default" href="{SITE}{ar}" />',
            f'  <meta property="og:locale" content="{og_locale}" />',
            f'  <meta property="og:locale:alternate" content="{og_alt}" />',
        ]
    )


def lang_toggle(lang: str, current_path: str) -> str:
    """Compact AR · EN control. current_path is path in current language."""
    current_path = normalize_path(current_path)
    if lang == "ar":
        ar_href = current_path
        en_href = en_path_from_ar(current_path)
        ar_cls = "lang-toggle__link is-active"
        en_cls = "lang-toggle__link"
    else:
        en_href = current_path
        ar_href = ar_path_from_en(current_path)
        ar_cls = "lang-toggle__link"
        en_cls = "lang-toggle__link is-active"
    return (
        f'<nav class="lang-toggle" aria-label="Language">'
        f'<a href="{ar_href}" class="{ar_cls}" lang="ar" hreflang="ar">AR</a>'
        f'<span class="lang-toggle__sep" aria-hidden="true">·</span>'
        f'<a href="{en_href}" class="{en_cls}" lang="en" hreflang="en">EN</a>'
        f"</nav>"
    )


def header_html(lang: str, current_path: str) -> str:
    n = NAV[lang]
    base = lang_base(lang)
    home = href(lang, "/")
    desktop_links = []
    mobile_links = []
    for key, path in NAV_PATHS:
        link_href = href(lang, path)
        label = n[key]
        home_attr = ' data-home' if key == "home" else ""
        desktop_links.append(
            f'<a href="{link_href}"{home_attr} class="nav-link text-foreground/70 hover:text-foreground transition-colors">{label}</a>'
        )
        mobile_links.append(
            f'<a href="{link_href}"{home_attr} class="nav-link py-1 text-foreground/80">{label}</a>'
        )
    ig_hl = "en" if lang == "en" else "ar"
    return f"""    <header class="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur">
      <div class="site-header-inner mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-4">
        <a href="{home}" data-home class="flex items-center gap-3 group">
          <span class="site-logo-text leading-tight">
            <span class="block font-display text-lg text-foreground">الذوادي</span>
            <span class="block text-[11px] uppercase tracking-[0.25em] text-muted-foreground font-latin">AL Thawadi</span>
          </span>
        </a>
        <nav class="hidden lg:flex items-center gap-7 text-sm">
          {" ".join(desktop_links)}
        </nav>
        <div class="flex items-center gap-3">
          {lang_toggle(lang, current_path)}
          <a href="https://www.instagram.com/althawadi_majlis/?hl={ig_hl}" target="_blank" rel="noreferrer" class="hidden sm:inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs text-foreground/80 hover:bg-card transition-colors">
            {IG_ICON}
            <span class="font-latin tracking-wide">@althawadi_majlis</span>
          </a>
          <button id="theme-toggle" type="button" class="theme-toggle" aria-label="{n['theme_dark']}" aria-pressed="false" title="{n['theme_title_dark']}">
            {THEME_SVGS}
          </button>
          <button id="menu-toggle" type="button" class="lg:hidden p-2 rounded-md hover:bg-card" aria-label="{n['menu']}">
            {MENU_SVGS}
          </button>
        </div>
      </div>
      <div id="mobile-nav" class="lg:hidden border-t border-border bg-background">
        <nav class="flex flex-col px-6 py-4 gap-3 text-sm">
          {" ".join(mobile_links)}
          <div class="pt-2">{lang_toggle(lang, current_path)}</div>
        </nav>
      </div>
    </header>"""


def footer_nav_cols(lang: str = "ar", base: str | None = None) -> str:
    if base is None:
        base = lang_base(lang)
    f = FOOTER[lang]
    n = NAV[lang]
    return f"""        <div class="footer-nav-col">
          <h4 class="footer-nav-heading">{f['site']}</h4>
          <ul class="footer-nav-list">
            <li><a href="{base}/" data-home class="hover:text-accent">{n['home']}</a></li>
            <li><a href="{base}/about/" class="hover:text-accent">{n['about']}</a></li>
            <li><a href="{base}/contact/" class="hover:text-accent">{n['contact']}</a></li>
          </ul>
        </div>
        <div class="footer-nav-col">
          <h4 class="footer-nav-heading">{f['family']}</h4>
          <ul class="footer-nav-list">
            <li><a href="{base}/tree/" class="hover:text-accent">{n['tree']}</a></li>
            <li><a href="{base}/ancestors/" class="hover:text-accent">{n['ancestors']}</a></li>
          </ul>
        </div>
        <div class="footer-nav-col">
          <h4 class="footer-nav-heading">{f['content']}</h4>
          <ul class="footer-nav-list">
            <li><a href="{base}/gallery/" class="hover:text-accent">{n['gallery']}</a></li>
            <li><a href="{base}/news/" class="hover:text-accent">{n['news']}</a></li>
            <li><a href="{base}/references/" class="hover:text-accent">{f['references_full']}</a></li>
            <li><a href="{base}/site-map/" class="hover:text-accent">{f['sitemap']}</a></li>
          </ul>
        </div>"""


def footer_contact_col(lang: str = "ar", base: str | None = None) -> str:
    if base is None:
        base = lang_base(lang)
    f = FOOTER[lang]
    ig_hl = "en" if lang == "en" else "ar"
    blurb = f["contact_blurb"].format(base=base or "")
    return f"""        <div class="footer-contact-col">
          <h4 class="footer-nav-heading font-latin">{f['contact']}</h4>
          <a href="https://www.instagram.com/althawadi_majlis/?hl={ig_hl}" target="_blank" rel="noreferrer" class="mt-4 inline-flex items-center gap-2 text-sm text-foreground/80 hover:text-accent">
            {IG_ICON_LG}
            <span class="font-latin">@althawadi_majlis</span>
          </a>
          <p class="mt-4 text-sm text-muted-foreground leading-7">{blurb}</p>
        </div>"""


def footer_html(lang: str, brand_blurb: str | None = None) -> str:
    f = FOOTER[lang]
    base = lang_base(lang)
    home = href(lang, "/")
    blurb = brand_blurb or f["brand_blurb"]
    brand = f["brand_name"]
    rights = f["rights"]
    return f"""    <footer class="mt-24 border-t border-border bg-card/40">
      <div class="mx-auto max-w-7xl px-6 py-14 footer-grid">
        <div class="footer-brand">
          <a href="{home}" data-home class="font-display text-2xl text-foreground hover:text-accent">{brand}</a>
          <p class="mt-3 text-sm text-muted-foreground leading-7 max-w-sm">{blurb}</p>
        </div>
{footer_nav_cols(lang, base)}
{footer_contact_col(lang, base)}
      </div>
      <div class="border-t border-border/60">
        <div class="footer-bar mx-auto max-w-7xl px-4 sm:px-6 py-5 text-xs text-muted-foreground flex flex-wrap justify-between gap-3">
          <span>© <span id="footer-year"></span> {rights}</span>
          <span class="font-latin tracking-[0.2em] uppercase">AL Thawadi Family</span>
        </div>
      </div>
    </footer>"""


def page_shell(
    *,
    lang: str,
    path: str,
    title: str,
    description: str,
    body: str,
    og_image: str = "",
    og_type: str = "website",
    brand_blurb: str | None = None,
    extra_head: str = "",
) -> str:
    path = normalize_path(path)
    canonical = f"{SITE}{path}"
    dir_attr = "rtl" if lang == "ar" else "ltr"
    og_img = f'  <meta property="og:image" content="{og_image}" />\n' if og_image else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}" dir="{dir_attr}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="index, follow" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:site_name" content="AL Thawadi" />
{og_img}  <link rel="canonical" href="{canonical}" />
{hreflang_tags_for(lang, path)}
  <link rel="stylesheet" href="/css/styles.css" />
  <script src="/js/url-clean.js"></script>
  <script src="/js/main.js" defer></script>
{extra_head}</head>
<body>
  <div class="min-h-screen flex flex-col">
{header_html(lang, path)}

    <main class="flex-1">
{body}
    </main>

{footer_html(lang, brand_blurb)}
  </div>
</body>
</html>
"""


# Backwards-compatible aliases for existing builders
def footer_nav_cols_ar(base: str = "") -> str:
    return footer_nav_cols("ar", base)


def footer_contact_col_ar(base: str = "") -> str:
    return footer_contact_col("ar", base or "")
