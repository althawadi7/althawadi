#!/usr/bin/env python3
"""Build /en/ mirror pages + patch Arabic pages with lang toggle & hreflang."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from site_chrome import (
    SITE,
    en_path_from_ar,
    footer_html,
    header_html,
    href,
    hreflang_tags_for,
    normalize_path,
    page_shell,
)
from en_i18n import (
    PLURAL,
    SINGULAR,
    fix_family_names,
    localize_gallery_html,
    localize_ui,
    transliterate_caption,
)

ROOT = Path(__file__).resolve().parents[1]
EN_ROOT = ROOT / "en"

MAIN_PAGES = [
    "/",
    "/about/",
    # "/tree/",  # Hidden for now (page kept; restore later)
    "/ancestors/",
    "/gallery/",
    "/news/",
    "/references/",
    "/contact/",
    "/site-map/",
]


def ar_file_for(path: str) -> Path:
    path = normalize_path(path)
    if path == "/":
        return ROOT / "index.html"
    return ROOT / path.strip("/") / "index.html"


def en_file_for(path: str) -> Path:
    path = normalize_path(path)
    if path == "/en/" or path == "/":
        return EN_ROOT / "index.html"
    # path like /en/about/
    rel = path[len("/en/") :] if path.startswith("/en/") else path.strip("/")
    return EN_ROOT / rel.strip("/") / "index.html"


def extract_main(html_text: str) -> str:
    m = re.search(r"<main\b[^>]*>([\s\S]*?)</main>", html_text, flags=re.I)
    return m.group(1).strip() if m else ""


def extract_article_inner(html_text: str) -> str:
    m = re.search(
        r'<article\b[^>]*class="[^"]*mx-auto[^"]*"[^>]*>([\s\S]*?)</article>',
        html_text,
        flags=re.I,
    )
    if m:
        return m.group(1).strip()
    m = re.search(r"<main\b[^>]*>([\s\S]*?)</main>", html_text, flags=re.I)
    return m.group(1).strip() if m else ""


def rewrite_links_to_en(fragment: str) -> str:
    """Rewrite absolute site paths to /en/… (skip assets, css, js, external)."""

    def repl_href(m: re.Match[str]) -> str:
        url = m.group(1)
        if url.startswith(("http://", "https://", "mailto:", "#", "data:")):
            return m.group(0)
        if url.startswith(("/assets/", "/css/", "/js/", "/seo/", "/sitemap")):
            return m.group(0)
        if url.startswith("/en/") or url == "/en":
            return m.group(0)
        if url == "/" or url == "":
            return 'href="/en/"'
        if url.startswith("/"):
            # /about/ -> /en/about/
            return f'href="/en{url}"'
        return m.group(0)

    return re.sub(r'href="([^"]+)"', repl_href, fragment)


def original_note() -> str:
    return (
        '<aside class="en-original-note" role="note">'
        "<p><strong>Original Arabic text.</strong> "
        "Names, documents, and source wording are kept in Arabic. "
        '<span lang="ar" dir="rtl">النص العربي الأصلي محفوظ كما نُشر.</span></p>'
        "</aside>"
    )


# ─── English main page bodies ───────────────────────────────────────────────


def body_home() -> str:
    return f"""      <section class="hero-banner relative overflow-hidden border-b border-border">
        <div class="absolute inset-0">
          <img src="/assets/hero-majlis.jpg" alt="AL Thawadi Family Majlis" width="1920" height="1280" class="h-full w-full object-cover" />
          <div class="absolute inset-0 hero-gradient"></div>
        </div>
        <div class="relative mx-auto max-w-7xl px-6 py-28 md:py-40">
          <div class="max-w-2xl">
            <p class="text-xs uppercase tracking-[0.5em] text-accent font-latin">AL Thawadi · Bahrain</p>
            <div class="ornament my-6 w-44"></div>
            <h1 class="font-display text-5xl md:text-7xl text-foreground leading-tight">
              {PLURAL}
              <span class="block text-3xl md:text-4xl text-primary/80 mt-3">in Al-Hidd</span>
            </h1>
            <p class="mt-8 text-lg text-muted-foreground leading-9 max-w-xl">
              The official archive documenting the descendants of
              <strong class="text-foreground">Abdullah and Rashid</strong>, sons of
              <strong class="text-foreground">Isa bin Khalifa bin Hilal bin Hasan {SINGULAR}</strong>,
              in the Kingdom of Bahrain — from the Al-‘Ama’ir of Bani Khalid —
              and preserving ancestral lives in legal records, pearling registers, and endowments.
            </p>
            <div class="mt-10 flex flex-wrap gap-3">
              <a href="{href('en', '/about/')}" class="inline-flex items-center gap-2 rounded-sm bg-primary px-6 py-3 text-sm text-primary-foreground hover:bg-primary/90 transition-colors">
                <span>Read history &amp; lineage</span>
              </a>
              <a href="{href('en', '/references/')}" class="inline-flex items-center gap-2 rounded-sm border border-border bg-background/60 px-6 py-3 text-sm hover:bg-card transition-colors">
                References &amp; sources
              </a>
            </div>
          </div>
        </div>
      </section>

      <section class="border-b border-border bg-card/30 paper-texture">
        <div class="mx-auto max-w-4xl px-6 py-20 text-center">
          <div class="ornament mx-auto w-32 mb-8"></div>
          <p class="font-display text-2xl md:text-3xl text-foreground leading-relaxed" lang="ar" dir="rtl">
            «من لم يعرف ماضيه، ضاع حاضره، وغاب عنه مستقبله.»
          </p>
          <p class="mt-6 text-sm text-muted-foreground tracking-wider">— Wisdom of the ancestors</p>
        </div>
      </section>

      <section class="border-y border-border bg-card/40">
        <div class="mx-auto max-w-7xl px-6 py-24 grid gap-12 md:grid-cols-2 items-center">
          <div class="heritage-stack relative">
            <img src="/assets/heritage.jpg" alt="Historic family houses" width="1600" height="1067" loading="lazy" class="w-full aspect-[3/2] object-cover rounded-sm shadow-xl" />
            <div class="heritage-inset absolute -bottom-6 -right-6 hidden md:block w-40 aspect-[3/4] overflow-hidden rounded-sm border-4 border-background shadow-xl">
              <img src="/assets/palm.jpg" alt="Palm" width="1200" height="1600" loading="lazy" class="w-full h-full object-cover" />
            </div>
          </div>
          <div>
            <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">Lineage</p>
            <h2 class="mt-3 font-display text-4xl text-foreground">Al-‘Ama’ir of Bani Khalid</h2>
            <p class="mt-6 text-muted-foreground leading-9">
              The sheikhly house of {PLURAL} in Bahrain belongs solidly to the
              <strong class="text-foreground">Al-‘Ama’ir</strong> of the Bani Khalid tribe —
              people of the sword and the sea — from the ‘Ama’ir islands on the eastern coast,
              through Zubarah and Fariha, to their settlement in Al-Hidd within the tribal alliance of the Al Khalifa.
            </p>
            <p class="mt-4 text-muted-foreground leading-9">
              Our ancestors took part in the Battle of Zubarah (1783 CE) and owned large pearling vessels
              that became coastal defence in times of crisis — recorded in the <em>Gazetteer of the Persian Gulf</em>
              and British Residency archives.
            </p>
            <a href="{href('en', '/about/')}" class="mt-8 inline-flex items-center gap-2 text-sm text-primary hover:gap-3 transition-all">
              <span>Read the full family history</span>
            </a>
          </div>
        </div>
      </section>

      <section class="mx-auto max-w-5xl px-6 py-24 text-center">
        <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">Follow</p>
        <h2 class="mt-3 font-display text-4xl text-foreground">AL Thawadi Majlis on Instagram</h2>
        <p class="mt-5 text-muted-foreground max-w-xl mx-auto leading-8">
          News from the majlis, gatherings, and family occasions.
        </p>
        <a href="https://www.instagram.com/althawadi_majlis/?hl=en" target="_blank" rel="noreferrer" class="mt-8 inline-flex items-center gap-3 rounded-sm border border-primary bg-background px-7 py-3 text-sm text-primary hover:bg-primary hover:text-primary-foreground transition-colors">
          <span class="font-latin tracking-wider">@althawadi_majlis</span>
        </a>
      </section>"""


def body_about() -> str:
    return f"""      <section class="border-b border-border bg-card/40 paper-texture">
        <div class="mx-auto max-w-5xl px-6 py-20 text-center">
          <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">About — {SINGULAR}</p>
          <div class="ornament my-5 mx-auto w-40"></div>
          <h1 class="font-display text-4xl md:text-5xl text-foreground">History of lineage &amp; foundation</h1>
          <p class="mt-6 max-w-2xl mx-auto text-muted-foreground leading-8">
            {PLURAL} ({SINGULAR} in the singular) of the Al-‘Ama’ir — Bani Khalid — people of the sea and trade;
            their historic home is Al-Hidd in the islands of Bahrain.
          </p>
        </div>
      </section>
      <article class="mx-auto max-w-3xl px-6 py-20">
        <div class="space-y-10 text-foreground/90 leading-9 text-lg">
          <section>
            <h2 class="font-display text-3xl text-foreground mb-4">Lineage — Al-‘Ama’ir of Bani Khalid</h2>
            <p class="text-muted-foreground">
              The family is solidly attributed to the <strong class="text-foreground">Al-‘Ama’ir</strong> branch of
              <strong class="text-foreground">Bani Khalid</strong> — among the major settled and Bedouin divisions of the tribe.
              The Al-‘Ama’ir were historically the sea-going wing of Bani Khalid.
            </p>
            <p class="text-muted-foreground mt-4">
              This site documents the descendants of <strong class="text-foreground">Abdullah and Rashid</strong>,
              sons of <strong class="text-foreground">Isa bin Khalifa bin Hilal bin Hasan {SINGULAR}</strong>,
              of Al-Hidd, Kingdom of Bahrain.
            </p>
          </section>
          <section>
            <h2 class="font-display text-3xl text-foreground mb-4">Settlement in Al-Hidd</h2>
            <p class="text-muted-foreground">
              After the tribal movements linked to Zubarah and the opening of Bahrain (1783 CE),
              {PLURAL} settled in Al-Hidd as part of the coastal social fabric —
              pearling captains (nawakhida), merchants, and community notables.
            </p>
          </section>
          <section>
            <h2 class="font-display text-3xl text-foreground mb-4">Sources</h2>
            <p class="text-muted-foreground">
              Documentation draws on Bani Khalid genealogies, the British Residency report of 1916
              (IOR/L/PS/20/E84/1), Lorimer’s Gulf Gazetteer, pearling petitions, and publications by researchers such as Bashar Al-Hadi —
              collected on our
              <a href="{href('en', '/references/')}" class="text-accent hover:underline">References</a> pages.
            </p>
          </section>
          <p class="text-sm text-muted-foreground">
            For extended Arabic quotations from the sources, see the
            <a href="/about/" class="text-accent hover:underline" hreflang="ar">Arabic About page</a>.
          </p>
        </div>
      </article>"""


def body_simple_hero(eyebrow: str, title: str, lead: str, extra: str = "") -> str:
    return f"""      <section class="border-b border-border bg-card/40 paper-texture">
        <div class="mx-auto max-w-5xl px-6 py-20 text-center">
          <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">{eyebrow}</p>
          <div class="ornament my-5 mx-auto w-40"></div>
          <h1 class="font-display text-4xl md:text-5xl text-foreground">{title}</h1>
          <p class="mt-6 max-w-2xl mx-auto text-muted-foreground leading-8">{lead}</p>
        </div>
      </section>
{extra}"""


def body_from_ar_main(ar_path: str, prepend: str = "") -> str:
    text = ar_file_for(ar_path).read_text(encoding="utf-8")
    main = extract_main(text)
    main = rewrite_links_to_en(main)
    if prepend:
        # Insert note after first section hero if possible
        main = prepend + "\n" + main
    return main


def body_contact() -> str:
    return f"""      <section class="border-b border-border bg-card/40 paper-texture">
        <div class="mx-auto max-w-5xl px-6 py-20 text-center">
          <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">Contact — AL Thawadi</p>
          <div class="ornament my-5 mx-auto w-40"></div>
          <h1 class="font-display text-4xl md:text-5xl text-foreground">The majlis door is open</h1>
        </div>
      </section>
      <section class="contact-map-section border-b border-border bg-card/20">
        <div class="mx-auto max-w-5xl px-4 sm:px-6 py-12 md:py-16">
          <p class="text-[11px] uppercase tracking-[0.3em] text-accent font-latin">Location</p>
          <h2 class="mt-2 font-display text-3xl text-foreground">AL Thawadi Majlis — Al-Hidd</h2>
          <p class="mt-3 text-sm text-muted-foreground leading-8 max-w-2xl">
            <strong class="text-foreground">6MW2+VXQ</strong>, Al-Hidd, Kingdom of Bahrain — Muharraq Governorate.
            Please arrange visits in advance via Instagram or the form below.
          </p>
          <div class="map-embed" title="AL Thawadi Majlis on the map">
            <iframe
              src="https://www.google.com/maps?q=6MW2%2BVXQ%2C+Al+Hidd%2C+Bahrain&hl=en&z=16&output=embed"
              allowfullscreen=""
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
              title="Map of AL Thawadi Majlis in Al-Hidd"
            ></iframe>
          </div>
          <div class="map-actions">
            <a href="https://www.google.com/maps/dir/?api=1&destination=6MW2%2BVXQ%2C+Al+Hidd%2C+Bahrain" target="_blank" rel="noreferrer" class="map-btn map-btn--primary">
              <span>Directions — Google Maps</span>
            </a>
          </div>
        </div>
      </section>
      <section class="mx-auto max-w-xl px-6 py-20">
        <form id="contact-form" class="space-y-6">
          <div>
            <label class="block text-sm mb-2" for="name">Name</label>
            <input id="name" name="name" required class="w-full rounded-sm border border-border bg-background px-4 py-3 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-2" for="email">Email</label>
            <input id="email" name="email" type="email" required class="w-full rounded-sm border border-border bg-background px-4 py-3 text-sm" />
          </div>
          <div>
            <label class="block text-sm mb-2" for="message">Message</label>
            <textarea id="message" name="message" rows="5" required class="w-full rounded-sm border border-border bg-background px-4 py-3 text-sm"></textarea>
          </div>
          <button type="submit" class="rounded-sm bg-primary px-6 py-3 text-sm text-primary-foreground hover:bg-primary/90">Send</button>
        </form>
        <p class="mt-8 text-sm text-muted-foreground text-center">
          Or write on Instagram:
          <a class="text-accent hover:underline font-latin" href="https://www.instagram.com/althawadi_majlis/?hl=en" target="_blank" rel="noreferrer">@althawadi_majlis</a>
        </p>
      </section>"""


def build_main_en_pages() -> None:
    pages = [
        (
            "/en/",
            "AL Thawadi — Family Majlis",
            "Official archive of AL Thawawdah — brand AL Thawadi — in Bahrain: descendants of Abdullah and Rashid, sons of Isa bin Khalifa bin Hilal bin Hasan Al Thawadi.",
            body_home(),
        ),
        (
            "/en/about/",
            "About AL Thawadi",
            "History and lineage of AL Thawawdah (singular: AL Thawadi) in Bahrain — Al-‘Ama’ir of Bani Khalid and settlement in Al-Hidd.",
            body_about(),
        ),
        # Hidden for now (page kept; restore later):
        # (
        #     "/en/tree/",
        #     "AL Thawadi Family Tree",
        #     "Genealogical tree of the descendants of Abdullah and Rashid, sons of Isa bin Khalifa bin Hilal bin Hasan Al Thawadi.",
        #     body_simple_hero(
        #         "Family Tree",
        #         "Lineage of the house",
        #         "Personal names and nasab are shown in Arabic as recorded in the family archive.",
        #     )
        #     + extract_tree_only(),
        # ),
        (
            "/en/ancestors/",
            "AL Thawadi Ancestors",
            "Lives of AL Thawawdah notables: Nawkhidha Sheikh Abdullah bin Isa Al Thawadi and Sheikh Rashid bin Isa Al Thawadi.",
            body_ancestors_en(),
        ),
        (
            "/en/gallery/",
            "AL Thawadi Gallery",
            "Archival and contemporary photographs of the AL Thawadi family (AL Thawawdah).",
            body_from_ar_with_en_hero(
                "/gallery/",
                "Gallery",
                "Pictures that remember",
                "Photographs of the family — captions in English transliteration.",
                note=False,
                gallery=True,
            ),
        ),
        (
            "/en/news/",
            "AL Thawadi Majlis News",
            "Family news and achievements from the AL Thawadi Majlis Instagram account.",
            body_from_ar_with_en_hero(
                "/news/",
                "Majlis News",
                "Family occasions & achievements",
                "UI in English; Instagram captions stay as originally published.",
                note=False,
                localize=True,
            ),
        ),
        (
            "/en/references/",
            "AL Thawadi References & Sources",
            "Books, documents, and posts documenting AL Thawawdah lineage and history in Bahrain.",
            body_from_ar_with_en_hero(
                "/references/",
                "References",
                "Our sources & references",
                "Search and navigation in English. Source titles keep their published wording (often Arabic).",
                note=False,
                localize=True,
            ),
        ),
        (
            "/en/contact/",
            "Contact AL Thawadi",
            "Contact the AL Thawadi Majlis to contribute information, photos, and documents.",
            body_contact(),
        ),
        (
            "/en/site-map/",
            "Sitemap — AL Thawadi",
            "Index of all indexable pages on the AL Thawadi family website (Arabic & English).",
            body_site_map_en(),
        ),
    ]
    for path, title, desc, body in pages:
        out = en_file_for(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        page = page_shell(
            lang="en",
            path=path,
            title=html.escape(title),
            description=html.escape(desc, quote=True),
            body=body,
        )
        out.write_text(page, encoding="utf-8")
        print("EN", path)


def extract_tree_only() -> str:
    text = ar_file_for("/tree/").read_text(encoding="utf-8")
    main = extract_main(text)
    # Drop AR hero section; keep interactive tree block
    main = re.sub(
        r'<section class="border-b border-border bg-card/40 paper-texture">[\s\S]*?</section>',
        "",
        main,
        count=1,
    )
    return rewrite_links_to_en(main)


def body_from_ar_with_en_hero(
    ar_path: str,
    eyebrow: str,
    title: str,
    lead: str,
    *,
    note: bool = False,
    localize: bool = True,
    gallery: bool = False,
) -> str:
    text = ar_file_for(ar_path).read_text(encoding="utf-8")
    main = extract_main(text)
    note_html = f"\n      {original_note()}\n" if note else "\n"
    en_hero = f"""      <section class="border-b border-border bg-card/40 paper-texture">
        <div class="mx-auto max-w-5xl px-6 py-20 text-center">
          <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">{eyebrow}</p>
          <div class="ornament my-5 mx-auto w-40"></div>
          <h1 class="font-display text-4xl md:text-5xl text-foreground">{title}</h1>
          <p class="mt-6 max-w-2xl mx-auto text-muted-foreground leading-8">{lead}</p>
        </div>
      </section>{note_html}"""
    main2, n = re.subn(
        r'<section class="border-b border-border bg-card/40 paper-texture">[\s\S]*?</section>',
        en_hero,
        main,
        count=1,
    )
    if n == 0:
        main2 = en_hero + main
    out = rewrite_links_to_en(main2)
    if gallery:
        out = localize_gallery_html(out)
    elif localize:
        out = localize_ui(out)
    return fix_family_names(out)


def body_ancestors_en() -> str:
    return f"""      <section class="border-b border-border bg-card/40 paper-texture">
        <div class="mx-auto max-w-5xl px-6 py-20 text-center">
          <p class="text-[11px] uppercase tracking-[0.4em] text-accent font-latin">Ancestors</p>
          <div class="ornament my-5 mx-auto w-40"></div>
          <h1 class="font-display text-4xl md:text-5xl text-foreground">Notables of {PLURAL}</h1>
          <p class="mt-6 max-w-2xl mx-auto text-muted-foreground leading-8">
            This site documents the descendants of
            <strong class="text-foreground">Abdullah and Rashid</strong>, sons of
            <strong class="text-foreground">Isa bin Khalifa bin Hilal bin Hasan {SINGULAR}</strong>
            — of the Al-‘Ama’ir, Bani Khalid.
          </p>
        </div>
      </section>

      <section class="mx-auto max-w-5xl px-6 pb-20">
        <ol class="timeline space-y-16 md:pl-12">
          <li class="timeline-item" id="abdullah-bin-isa">
            <span class="timeline-marker">1</span>
            <p class="text-[11px] uppercase tracking-[0.3em] text-accent font-latin">Al-Hidd — Nawkhidha &amp; sheikhly leadership</p>
            <h3 class="mt-2 font-display text-3xl text-foreground">Nawkhidha / Sheikh Abdullah bin Isa {SINGULAR}</h3>
            <p class="mt-1 text-primary italic">Sheikh and community leader of {PLURAL} — among the best-known pearling captains of Al-Hidd</p>
            <p class="mt-4 text-muted-foreground leading-9">
              One of the foremost men of {PLURAL} in Bahrain, combining
              <strong class="text-foreground">tribal sheikhly leadership</strong> in Al-Hidd with
              <strong class="text-foreground">command of pearling vessels</strong> (nawkhidha).
              He appears in the <em>Gazetteer of the Persian Gulf</em> among the leading tribes of Al-Hidd,
              in Bahrain nawakhida lists (1920–1960), in the pearling captains’ petition of 1344 AH / 1925 CE —
              where he was the <strong class="text-foreground">first signatory</strong> — and in Muharraq Municipality
              correspondence (1936–1938) on diver (jazwa) rolls and pearling fees. He is a pillar of the documented lineage.
            </p>

            <dl class="fact-grid">
              <div class="fact-item"><dt>Title</dt><dd>Nawkhidha — master and owner of a pearling vessel</dd></div>
              <div class="fact-item"><dt>Place</dt><dd>Al-Hidd — Fareej {PLURAL}, near the midaf and jalafa</dd></div>
              <div class="fact-item"><dt>Ships</dt><dd>Bashara, Musa‘id, Nayef, Umm Kulthum</dd></div>
              <div class="fact-item"><dt>Documentation</dt><dd>Petition 1925; Muharraq Municipality 1936–1938; Gulf Gazetteer</dd></div>
            </dl>

            <div class="ancestor-detail">
              <h4>Nawkhidha and sheikhly office</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                In the Gulf, the <strong class="text-foreground">nawkhidha</strong> is the ship’s master and owner —
                responsible for pearling voyages, the crew (jazwa), and disposing of the pearl catch.
                At the same time, Abdullah bin Isa was <strong class="text-foreground">sheikh and community head</strong>
                of {PLURAL} in Al-Hidd — keeper of an open majlis and a voice among the country’s notables.
                He was known for <strong class="text-foreground">financing himself</strong> without borrowing,
                and held a close friendship with the Al Khalifa — including Sheikh Hamad bin Isa, Ruler of Bahrain,
                and Sheikh Abdullah bin Isa Al Khalifa, Minister of Education.
              </p>
              <p class="mt-3 text-muted-foreground leading-9 text-sm">
                Among his well-known sailors: <strong class="text-foreground">Dhahir Al-‘Umairi</strong> and
                <strong class="text-foreground">Husain Al-Kuwaiti</strong> — the diver who found
                <strong class="text-foreground">Dana Abdullah</strong>. Among his charitable works: digging a
                <strong class="text-foreground">shared water spring</strong> for the people of Al-Hidd
                (known as “‘Ayn Al Thawadi”), which the neighbourhood used freely.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>His ships and fleet</h4>
              <ul class="content-list text-sm">
                <li><strong class="text-foreground">Bashara</strong> — the vessel on which Dana Abdullah {SINGULAR} was found</li>
                <li><strong class="text-foreground">Musa‘id</strong> — among his owned ships</li>
                <li><strong class="text-foreground">Nayef</strong> — among his owned ships</li>
                <li><strong class="text-foreground">Umm Kulthum</strong> — among his owned ships</li>
              </ul>
              <p class="mt-3 text-xs text-muted-foreground leading-7">
                Source: family biography preserved through oral history — to verify ship names and dates,
                <a href="/en/contact/" class="text-accent hover:underline">contact us</a>.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>Pearling captains’ petition — 1344 AH / October 1925</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                When the government proposed new pearling regulations, Abdullah bin Isa {SINGULAR} —
                <strong class="text-foreground">first among the signatories</strong> — submitted a petition to
                Sheikh Hamad bin Isa Al Khalifa with other nawakhida and pearl traders, objecting to clauses that
                limited the nawkhidha’s authority over selling the catch and managing the jazwa.
                The petition reached the British Political Resident, Colonel Prideaux, and amendments followed.
              </p>
              <blockquote class="doc-excerpt" lang="ar" dir="rtl">
                «…نرفع لسعادتكم شكوانا من خسارة المال واشتغال البال والسبب في ذلك النظامات الجارية في خصوص الغوص
                قد أضرت بنا… الذي نرجو من فضلكم في هذه المسألة أن يكون البيع بنظر النواخذة فهم أعلم بصنوف القماش
                وأحرص من الجزوى على حصول المصلحة…»
                <cite>Pearling captains’ petition — Rabi‘ II 1344 AH — Abdullah bin Isa {SINGULAR} (first signatory)</cite>
              </blockquote>
              <p class="mt-3 text-xs text-muted-foreground leading-7">
                Other signatories included Hamad bin Saqr Al-Buflasa, Muhanna bin Fadl Al-Nuaimi, Isa bin Hamad Al-Khatm, and others.
                <a href="/en/references/#petition-1925" class="text-accent hover:underline">Full text &amp; references</a>.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>Dana Abdullah — among Bahrain’s most famous pearls</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                It ranks among Bahrain’s most celebrated pearls after <strong class="text-foreground">Dana bin Tarif</strong>.
                In a pearling season — likely <strong class="text-foreground">1938 CE</strong> — the ship
                <strong class="text-foreground">Bashara</strong>, whose nawkhidha was
                <strong class="text-foreground">Ahmad bin Abdullah</strong> (his son), sailed to
                <strong class="text-foreground">Hair Bu‘Amama</strong>. While opening oysters,
                <strong class="text-foreground">Husain Al-Kuwaiti</strong> found an immense pearl and told Nawkhidha Ahmad,
                who informed his father Abdullah bin Isa — who rejoiced and thanked God.
              </p>
              <dl class="fact-grid mt-4">
                <div class="fact-item"><dt>Weight</dt><dd>204 jaw (traditional pearl weight)</dd></div>
                <div class="fact-item"><dt>Sale</dt><dd>34,000 rupees — to Hajj Abdulrahman Al-Qusaibi</dd></div>
                <div class="fact-item"><dt>Diver’s reward</dt><dd>300 rupees to Husain Al-Kuwaiti</dd></div>
                <div class="fact-item"><dt>Eyewitness</dt><dd>Muhammad bin Abdullah bin Isa {SINGULAR}</dd></div>
              </dl>
              <p class="mt-4 text-muted-foreground leading-9 text-sm">
                <em>Jaridat Al-Bahrain</em> (Abdullah Al-Za’id) reported it on
                <strong class="text-foreground">6 Rajab 1358 AH / 17 August 1939</strong> under the title
                “A rare pearl from the fisheries of Bahrain” — noting Al-Qusaibi bought an 18-carat pearl that
                stirred the jewellery world in Europe and India. On
                <strong class="text-foreground">10 Sha‘ban 1359 AH / 12 September 1940</strong> the paper said
                Al-Qusaibi sold it to Indian royalty for a large sum. Diver Husain Al-Kuwaiti described its size as “like a marble.”
              </p>
              <p class="mt-3 text-xs text-muted-foreground leading-7">
                It appeared after Japanese cultured pearls and the market collapse — underscoring Abdullah bin Isa’s achievement in disposing of it.
                <a href="/en/references/#danat-abdullah" class="text-accent hover:underline">Press sources</a>.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>Material heritage in Al-Hidd</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                Local memory preserves the <strong class="text-foreground">“House of Nawkhidha Abdullah bin Isa {SINGULAR}”</strong>
                in old Fareej Al-Hidd — a large house near the <strong class="text-foreground">midaf</strong> (boat landing)
                and <strong class="text-foreground">jalafa</strong> (wooden shipbuilding), in a quarter tied to the sea.
                Nearby is <strong class="text-foreground">‘Ayn Al Thawadi</strong> — the shared spring he dug for the people.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>Descendants (from available sources)</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                <strong class="text-foreground">Ahmad bin Abdullah bin Isa</strong> — nawkhidha of Bashara (season of Dana Abdullah).
                <br /><strong class="text-foreground">Muhammad bin Abdullah bin Isa</strong> — eyewitness to the pearl story;
                chosen dean of {PLURAL} in Bahrain in 2014. Sons of Muhammad include Abdullah, Isa, Ahmad, and Ali.
              </p>
            </div>
          </li>

          <li class="timeline-item" id="rashid-bin-isa">
            <span class="timeline-marker">2</span>
            <p class="text-[11px] uppercase tracking-[0.3em] text-accent font-latin">Al-Hidd — Nawkhidha &amp; clan sheikh</p>
            <h3 class="mt-2 font-display text-3xl text-foreground">Sheikh Rashid bin Isa {SINGULAR}</h3>
            <p class="mt-1 text-primary italic">Nawkhidha Rashid bin Isa bin Khalifa {SINGULAR} — sheikh of {PLURAL} in Al-Hidd</p>
            <p class="mt-4 text-muted-foreground leading-9">
              A documented notable of {PLURAL} in the majlis archive and Bahraini historical sources.
              Known for piety and wide knowledge of navigation, his voyages reached East African ports such as
              <strong class="text-foreground">Zanzibar</strong> — a source of mangrove timber and more — as his sons relate.
              He kept close ties with the <strong class="text-foreground">Al-‘Ama’ir of Bani Khalid</strong>,
              and a historical letter names him <strong class="text-foreground">sheikh of the {PLURAL} clan</strong> in Bahrain.
            </p>

            <div class="ancestor-detail">
              <h4>Fleet and pearling</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                He owned several pearling vessels, including <strong class="text-foreground">Armitha</strong>,
                <strong class="text-foreground">Malfaja</strong>, <strong class="text-foreground">Jalboot Al-‘Arida</strong>,
                and <strong class="text-foreground">Jalboot Umm Du‘aij</strong>.
                One ship was sold to the merchant Muhammad Tayyib (may God have mercy on him), who converted it to a motor launch
                and hired it out in Al-Hidd before it sailed again.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>Descendants (from available sources)</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                <strong class="text-foreground">Khalifa bin Rashid bin Isa {SINGULAR}</strong> — nawkhidha.
                <br /><strong class="text-foreground">Ahmad bin Rashid bin Isa {SINGULAR}</strong> — nawkhidha.
                <br /><strong class="text-foreground">Hasan bin Rashid bin Isa {SINGULAR}</strong> — nawkhidha.
                <br /><strong class="text-foreground">Hilal bin Rashid bin Isa {SINGULAR}</strong> — nawkhidha (his majlis in Al-Hidd beside Shanuf Mosque).
                <br /><strong class="text-foreground">Jassim bin Rashid bin Isa {SINGULAR}</strong> — nawkhidha.
                <br />And three daughters, may God have mercy on them. From the line of Abdullah bin Isa — who followed in sheikhly office and pearling —
                <a href="#abdullah-bin-isa" class="text-accent hover:underline">Nawkhidha Abdullah bin Isa {SINGULAR}</a>.
              </p>
            </div>

            <div class="ancestor-detail">
              <h4>Death</h4>
              <p class="text-muted-foreground leading-9 text-sm">
                He died after performing the Hajj and visiting Madinah, and was buried there — may God have mercy on him.
              </p>
              <p class="mt-3 text-xs text-muted-foreground leading-7">
                <a href="/en/references/#references-archive" class="text-accent hover:underline">Archive &amp; publication sources</a>
                — @althawadi_majlis posts and British Residency documents.
              </p>
            </div>
          </li>
        </ol>

        <div class="mt-20 text-center text-sm text-muted-foreground border-t border-border pt-10 leading-8">
          Sources: Al-Khalidi, Al-Wahbi, Al-Shaqha’, Lorimer, Al-Jasir, Al-Nabhani — see the
          <a href="/en/references/" class="text-accent hover:underline">full references page</a>
          — to add a verified biography, <a href="/en/contact/" class="text-accent hover:underline">contact us</a>.
        </div>
      </section>"""


def body_site_map_en() -> str:
    links = []
    for p in MAIN_PAGES:
        en_p = en_path_from_ar(p)
        label = {
            "/": "Home",
            "/about/": "About",
            "/tree/": "Family Tree",
            "/ancestors/": "Ancestors",
            "/gallery/": "Gallery",
            "/news/": "Majlis News",
            "/references/": "References",
            "/contact/": "Contact",
            "/site-map/": "Sitemap",
        }.get(p, p)
        links.append(
            f'<li><a href="{en_p}">{label}</a> '
            f'<span class="text-muted-foreground font-latin text-xs">{SITE}{en_p}</span></li>'
        )
    return f"""      <section class="mx-auto max-w-3xl px-4 sm:px-6 py-12 w-full">
        <p class="text-xs uppercase tracking-[0.3em] text-accent font-latin">Sitemap</p>
        <h1 class="font-display text-3xl md:text-4xl text-foreground mt-3">Site map</h1>
        <p class="mt-4 text-muted-foreground leading-7">
          English pages. XML for Search Console:
          <a class="text-accent hover:underline font-latin" href="/seo/sitemap.xml">{SITE}/seo/sitemap.xml</a>
        </p>
        <section class="mt-10">
          <h2 class="font-display text-2xl text-foreground">Main pages (English)</h2>
          <ul class="mt-4 space-y-2 text-sm leading-7">
            {"".join(links)}
          </ul>
        </section>
        <p class="mt-10 text-sm text-muted-foreground">
          Arabic site map:
          <a href="/site-map/" class="text-accent hover:underline" hreflang="ar">/site-map/</a>
        </p>
      </section>"""


def build_detail_en_shells() -> int:
    count = 0
    pairs = [
        (ROOT / "references" / "item", EN_ROOT / "references" / "item", "/references/item/", "References", "/en/references/"),
        (ROOT / "news" / "item", EN_ROOT / "news" / "item", "/news/item/", "Majlis News", "/en/news/"),
    ]
    for ar_dir, en_dir, ar_prefix, section_label, en_list in pairs:
        if not ar_dir.exists():
            continue
        for child in sorted(ar_dir.iterdir()):
            if not child.is_dir():
                continue
            ar_page = child / "index.html"
            if not ar_page.exists():
                continue
            slug = child.name
            ar_path = f"{ar_prefix}{slug}/"
            en_path = en_path_from_ar(ar_path)
            text = ar_page.read_text(encoding="utf-8")
            title_m = re.search(r"<title>([^<]+)</title>", text)
            desc_m = re.search(
                r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
                text,
                flags=re.I,
            )
            og_m = re.search(
                r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
                text,
                flags=re.I,
            )
            raw_title = html.unescape(title_m.group(1) if title_m else slug)
            # Strip Arabic site suffix for EN title pattern
            raw_title = re.sub(r"\s*[—\-]\s*مراجع.*$", "", raw_title).strip()
            raw_title = re.sub(r"\s*[—\-]\s*أخبار.*$", "", raw_title).strip()
            desc = html.unescape(desc_m.group(1) if desc_m else raw_title)
            article = extract_article_inner(text)
            # Soften AR-only chrome labels inside article
            article = article.replace("← مراجع ومصادر", f"← {section_label}")
            article = article.replace("← كل المراجع", f"← All {section_label.lower()}")
            article = article.replace("← أخبار المجلس", "← Majlis News")
            article = rewrite_links_to_en(article)
            article = localize_ui(article)
            article = fix_family_names(article)
            body = f"""      <nav class="ref-detail-breadcrumb mx-auto max-w-3xl px-4 sm:px-6 pt-8" aria-label="Breadcrumb">
        <a href="{en_list}" class="text-sm text-muted-foreground hover:text-accent">← {section_label}</a>
      </nav>
      <article class="mx-auto max-w-3xl px-4 sm:px-6 py-10 pb-20" lang="ar" dir="rtl">
        {original_note() if "references/item" in ar_prefix or "news/item" in ar_prefix else ""}
        {article}
      </article>"""
            # EN meta titles keep source Arabic title but brand is AL Thawadi
            en_title = f"{raw_title} — {SINGULAR}"
            en_desc = fix_family_names(desc)[:300]
            page = page_shell(
                lang="en",
                path=en_path,
                title=html.escape(en_title),
                description=html.escape(en_desc, quote=True),
                body=body,
                og_image=og_m.group(1) if og_m else "",
                og_type="article",
            )
            dest = en_dir / slug / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(page, encoding="utf-8")
            count += 1
    print(f"EN detail shells: {count}")
    return count


# ─── Patch Arabic pages ─────────────────────────────────────────────────────


def inject_hreflang(head: str, ar_path: str) -> str:
    tags = hreflang_tags_for("ar", ar_path)
    # Remove existing hreflang / og:locale we may have added
    head = re.sub(r'\n?\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+"\s*/?>', "", head)
    head = re.sub(r'\n?\s*<meta property="og:locale(?::alternate)?" content="[^"]+"\s*/?>', "", head)
    # Absolute canonical
    head = re.sub(
        r'<link\s+rel=["\']canonical["\']\s+href=["\'][^"\']*["\']\s*/?>',
        f'<link rel="canonical" href="{SITE}{normalize_path(ar_path)}" />',
        head,
        count=1,
        flags=re.I,
    )
    if "hreflang=" not in head:
        head = re.sub(r"(</head>)", tags + "\n\\1", head, count=1, flags=re.I)
    return head


def inject_lang_toggle_into_header(html_text: str, ar_path: str) -> str:
    from site_chrome import lang_toggle

    toggle = lang_toggle("ar", ar_path)
    # Remove existing lang-toggle blocks
    html_text = re.sub(
        r'\s*<nav class="lang-toggle"[^>]*>[\s\S]*?</nav>',
        "",
        html_text,
    )
    # Insert before theme-toggle in header actions
    if 'id="theme-toggle"' in html_text:
        html_text = html_text.replace(
            '<button id="theme-toggle"',
            f"{toggle}\n          <button id=\"theme-toggle\"",
            1,
        )
    # Also in mobile nav end
    if 'id="mobile-nav"' in html_text and "lang-toggle" not in html_text.split('id="mobile-nav"')[1][:800]:
        html_text = re.sub(
            r'(id="mobile-nav"[\s\S]*?<nav class="flex flex-col[^"]*">[\s\S]*?)(</nav>\s*</div>\s*</header>)',
            rf'\1          <div class="pt-2">{toggle}</div>\n        \2',
            html_text,
            count=1,
        )
    return html_text


def patch_ar_page(path: Path, ar_path: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if 'lang="en"' in text[:200]:
        return False
    # head
    def head_repl(m: re.Match[str]) -> str:
        return inject_hreflang(m.group(0), ar_path)

    new = re.sub(r"<head>[\s\S]*?</head>", head_repl, text, count=1, flags=re.I)
    new = inject_lang_toggle_into_header(new, ar_path)
    # Ensure robots index,follow
    if re.search(r'name=["\']robots["\']', new, flags=re.I):
        new = re.sub(
            r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*["\']\s*/?>',
            '<meta name="robots" content="index, follow" />',
            new,
            count=1,
            flags=re.I,
        )
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def patch_all_ar_pages() -> int:
    n = 0
    for p in MAIN_PAGES:
        f = ar_file_for(p)
        if f.exists() and patch_ar_page(f, p):
            n += 1
            print("patched AR", p)
    for section, prefix in (
        (ROOT / "references" / "item", "/references/item/"),
        (ROOT / "news" / "item", "/news/item/"),
    ):
        if not section.exists():
            continue
        for child in section.iterdir():
            page = child / "index.html"
            if page.exists():
                ap = f"{prefix}{child.name}/"
                if patch_ar_page(page, ap):
                    n += 1
    print(f"Patched {n} Arabic pages")
    return n


def update_detail_builders_note() -> None:
    """Patch reference/news builders to include lang toggle via site_chrome on next rebuild."""
    # Handled separately in builder file edits
    pass


def main() -> None:
    # English site disabled — Arabic-only. Keep this script for possible restore later.
    print("Skipped: English mirrors are disabled (Arabic-only site).")
    print("To rebuild EN later, restore this main() and re-enable EN in site_chrome / sitemaps.")
    return
    # EN_ROOT.mkdir(parents=True, exist_ok=True)
    # build_main_en_pages()
    # build_detail_en_shells()
    # patch_all_ar_pages()
    # print("Done.")


if __name__ == "__main__":
    main()
