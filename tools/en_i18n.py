#!/usr/bin/env python3
"""English UI + caption helpers for /en/ pages.

Naming convention (site standard):
  - Plural / clan: AL Thawawdah  (الذواودة) — use *th*, never *dh*
  - Singular / brand: AL Thawadi (الذوادي)
Historical British spellings (Dawāudah, etc.) may appear only when quoting a source,
with a clarifying “AL Thawawdah” beside them.
"""

from __future__ import annotations

import html
import re

# Preferred Latin forms
PLURAL = "AL Thawawdah"
BRAND = "AL Thawadi"  # logo / site signal (singular)
SINGULAR = "Al Thawadi"  # in running English names

# Wrong → correct (order matters: longer first)
NAME_FIXES = [
    ("Al-Dhawawdah", PLURAL),
    ("al-Dhawawdah", PLURAL),
    ("Al Dhawawdah", PLURAL),
    ("Dhawawdah", "Thawawdah"),
    ("Dawāudah", "Thawawdah"),
    ("Dawaudah", "Thawawdah"),
    ("Dawāudeh", "Thawawdah"),
    ("Thawāwdeh", "Thawawdah"),
    ("Thawawdeh", "Thawawdah"),
]


def fix_family_names(text: str) -> str:
    for bad, good in NAME_FIXES:
        text = text.replace(bad, good)
    return text


# Arabic UI → English (references / news / gallery chrome)
UI_REPLACEMENTS = [
    ("أرشيف المراجع والمنشورات", "References & posts archive"),
    ("بحث في المراجع والمنشورات", "Search references and posts"),
    ("ابحث في كل المراجع والمنشورات… (مثال: عبدالله، غوص، الخالدي)", "Search all references and posts… (e.g. Abdullah, pearling, Al-Khalidi)"),
    ("ابحث في كل المراجع والمنشورات", "Search all references and posts"),
    ("لا توجد نتائج مطابقة للبحث.", "No matching results."),
    ("اقرأ التفاصيل ←", "Read details →"),
    ("عرض التفاصيل والفيديو", "View details and video"),
    ("عرض التفاصيل", "View details"),
    ("هل تعرف مصدرًا أو وثيقةً تُثبت نسبًا أو حدثًا من تاريخ الذواودة في البحرين؟", f"Do you know a source or document that confirms a lineage or event in the history of {PLURAL} in Bahrain?"),
    ("تواصل معنا لمراجعتها وإضافتها بعد التحقق.", "Contact us to review it and add it after verification."),
    (">مرجع<", ">Source<"),
    ("سياق الذكر:", "Mention context:"),
    ("فيديو 1", "Video 1"),
    ("فيديو 2", "Video 2"),
    ("المقطع المختصر", "Short clip"),
    ("النسخة الكاملة", "Full version"),
    ("صورة 1", "Image 1"),
    ("صورة 2", "Image 2"),
    ("صورة 3", "Image 3"),
    ("تكبير الصورة", "Expand image"),
    ("الصورة السابقة", "Previous image"),
    ("الصورة التالية", "Next image"),
    ("اختيار صورة", "Choose image"),
    ('aria-label="فيديو"', 'aria-label="Video"'),
    ('aria-label="صورة"', 'aria-label="Image"'),
    ('aria-label="معرض صور"', 'aria-label="Photo gallery"'),
    ("← كل المراجع", "← All references"),
    ("← أخبار المجلس", "← Majlis news"),
]

# Caption / name phrase map (gallery & similar)
CAPTION_PHRASES = [
    ("المرحوم بأذن الله تعالى", "The late"),
    ("المرحوم بإذن الله تعالى", "The late"),
    ("المرحوم باذن الله تعالى", "The late"),
    ("المرحوم بأذن الله", "The late"),
    ("المرحوم بإذن الله", "The late"),
    ("المرحوم باذن الله", "The late"),
    ("المغفور له بإذن الله", "The late"),
    ("المغفور له باذن الله", "The late"),
    ("المغفور له بأذن الله", "The late"),
    ("رحمة الله عليه", "(may God have mercy on him)"),
    ("رحمة الله علية", "(may God have mercy on him)"),
    ("الله يرحمه ويغفرله", "(may God have mercy on him)"),
    ("الله يرحمه ويغفر له", "(may God have mercy on him)"),
    ("الله يحفظه ويطول بعمره", "(may God protect him)"),
    ("النوخذة / الشيخ", "Nawkhidha / Sheikh"),
    ("النوخذة", "Nawkhidha"),
    ("النوخذه", "Nawkhidha"),
    ("النوخذا", "Nawkhidha"),
    ("الشيخ ", "Sheikh "),
    ("الذواودة", PLURAL),
    ("الذواوده", PLURAL),
    ("الذوادي", SINGULAR),
    ("أخ الشيخ", "brother of Sheikh"),
    ("أخ ", "brother of "),
    ("أبناء ", "sons of "),
    ("ابن ", "bin "),
    ("بن ", "bin "),
    ("أثناء زيارة مجلس الحسن الخالدي في عنك بالسعودية في سنة", "during a visit to the Al-Hasan Al-Khalidi majlis in Anak, Saudi Arabia, in"),
    ("صورة أرشيفية للنوخذا", "Archival photo of Nawkhidha"),
    ("صورة أرشيفية", "Archival photo"),
    ("من النواخذا المشهورين في مدينة الحد — صورة أرشيفية", "Among the well-known nawakhida of Al-Hidd — archival photo"),
    ("مأخوذة من فيلم", "from the film"),
    ("(إنتاج والت ديزني ١٩٦٩م)", "(Walt Disney production, 1969)"),
    ("(إنتاج والت ديزني 1969م)", "(Walt Disney production, 1969)"),
    ("من اليمين،", "From the right:"),
    ("من اليمين، ", "From the right: "),
]


# Common given names (Arabic → Latin)
GIVEN_NAMES = [
    ("عبدالله", "Abdullah"),
    ("عبد الله", "Abdullah"),
    ("عبدالحكيم", "Abdulhakim"),
    ("عبد الحكيم", "Abdulhakim"),
    ("عبدالعزيز", "Abdulaziz"),
    ("عبد العزيز", "Abdulaziz"),
    ("عبدالناصر", "Abdulnasser"),
    ("عبد الرحمن", "Abdulrahman"),
    ("عبدالرحمن", "Abdulrahman"),
    ("محمد", "Muhammad"),
    ("أحمد", "Ahmad"),
    ("احمد", "Ahmad"),
    ("راشد", "Rashid"),
    ("رشيد", "Rashid"),
    ("عيسى", "Isa"),
    ("خليفة", "Khalifa"),
    ("هلال", "Hilal"),
    ("حسن", "Hasan"),
    ("حسين", "Husain"),
    ("جاسم", "Jassim"),
    ("غانم", "Ghanim"),
    ("يوسف", "Yusuf"),
    ("إبراهيم", "Ibrahim"),
    ("ابراهيم", "Ibrahim"),
    ("علي", "Ali"),
    ("خالد", "Khalid"),
    ("طارق", "Tariq"),
    ("ناصر", "Nasser"),
    ("بدر", "Badr"),
    ("عمر", "Omar"),
    ("عادل", "Adel"),
    ("عارف", "Aref"),
    ("جمال", "Jamal"),
    ("طلال", "Talal"),
    ("سلطان", "Sultan"),
    ("فهد", "Fahad"),
    ("فيصل", "Faisal"),
    ("سلمان", "Salman"),
    ("نايف", "Nayef"),
    ("مشعل", "Mishaal"),
    ("البراء", "Al-Baraa"),
    ("سعيد", "Saeed"),
    ("حمد", "Hamad"),
    ("وحمد", "and Hamad"),
]


def localize_ui(text: str) -> str:
    text = fix_family_names(text)
    for ar, en in UI_REPLACEMENTS:
        text = text.replace(ar, en)
    # Badge / count patterns
    text = re.sub(r">(\d+)\s*صور<", r">\1 photos<", text)
    text = re.sub(r">فيديو<", ">Video<", text)
    text = re.sub(r'aria-label="أرشيف[^"]*"', 'aria-label="References & posts archive"', text)
    return text


def transliterate_caption(ar: str) -> str:
    """Best-effort Latin caption for gallery member names."""
    if not ar or not ar.strip():
        return ar
    t = ar.strip()
    t = fix_family_names(t)
    for ar_p, en_p in CAPTION_PHRASES:
        t = t.replace(ar_p, en_p)
    # Longer names first
    for ar_n, en_n in sorted(GIVEN_NAMES, key=lambda x: -len(x[0])):
        t = t.replace(ar_n, en_n)
    # Clean leftover Arabic digits markers etc.
    t = t.replace("،", ",")
    t = re.sub(r"\s{2,}", " ", t).strip(" .")
    # Capitalize after sentence breaks
    t = re.sub(r"([.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), t)
    if t and t[0].islower():
        t = t[0].upper() + t[1:]
    # If still mostly Arabic, keep original (don't invent)
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", t))
    if arabic_chars > max(3, len(t) // 3):
        # Fall back: append family Latin form only where الذوادي remained unreplaced
        return fix_family_names(ar.strip())
    return t


def localize_gallery_html(html_text: str) -> str:
    """Replace Arabic gallery titles/alts/aria with Latin captions."""

    def repl_attr(m: re.Match[str]) -> str:
        attr, val = m.group(1), m.group(2)
        return f'{attr}="{html.escape(transliterate_caption(html.unescape(val)), quote=True)}"'

    out = html_text
    for attr in ("data-title", "alt", "aria-label"):
        out = re.sub(
            rf'({attr})="([^"]*)"',
            repl_attr,
            out,
        )
    # figcaption titles
    def repl_caption(m: re.Match[str]) -> str:
        inner = m.group(1)
        return f'<p class="gallery-member-title">{html.escape(transliterate_caption(html.unescape(inner)))}</p>'

    out = re.sub(
        r'<p class="gallery-member-title">([^<]*)</p>',
        repl_caption,
        out,
    )
    out = re.sub(r">عرض ([^<]+)<", lambda m: f'>View {transliterate_caption(m.group(1))}<', out)
    return localize_ui(out)
