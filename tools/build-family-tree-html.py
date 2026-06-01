#!/usr/bin/env python3
"""Generate family tree HTML — nested lists with CSS connector lines."""

import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREE_HTML = ROOT / "partials" / "family-tree-ul.html"


def node(
    name: str,
    *,
    lineage=False,
    focus=False,
    link: str | None = None,
    suffix: str | None = None,
) -> dict:
    return {
        "name": name,
        "suffix": suffix,
        "lineage": lineage,
        "focus": focus,
        "link": link,
        "children": [],
    }


def display_name(n: dict) -> str:
    if n.get("suffix"):
        return f'{n["name"]} {n["suffix"]}'
    return n["name"]


def father_line(ancestors: list[str]) -> str:
    """Patronymic line shown under the given name (who this person is son of)."""
    if not ancestors:
        return ""
    if len(ancestors) == 1:
        return f"بن {ancestors[0]}"
    return "بن " + " بن ".join(reversed(ancestors[-2:]))


def render_person(n: dict, pad: str, ancestors: list[str], *, is_root: bool = False) -> str:
    given = display_name(n)
    pat = father_line(ancestors)
    title = f"{given} {pat}".strip() if pat else given
    title_esc = escape(title)
    given_esc = escape(given)
    pat_esc = escape(pat) if pat else ""

    classes = ["family-tree-node"]
    if is_root:
        classes.append("is-root")
    if n.get("lineage"):
        classes.append("is-lineage")
    if n.get("focus"):
        classes.append("is-focus")
    if n.get("link"):
        classes.append("family-tree-node--link")
    cls = " ".join(classes)

    pat_html = f'\n{pad}    <span class="family-tree-pat">{pat_esc}</span>' if pat else ""

    inner = (
        f'{pad}    <span class="family-tree-given">{given_esc}</span>{pat_html}\n'
    )

    if n.get("link"):
        return (
            f'{pad}  <a href="{n["link"]}" class="{cls}" title="{title_esc}" dir="rtl">\n'
            f"{inner}"
            f"{pad}  </a>\n"
        )

    return (
        f'{pad}  <span class="{cls}" title="{title_esc}" dir="rtl">\n'
        f"{inner}"
        f"{pad}  </span>\n"
    )


def render_node(n: dict, indent: int, ancestors: list[str], *, is_root: bool = False) -> str:
    pad = " " * indent
    person = render_person(n, pad, ancestors, is_root=is_root)
    path = ancestors + [n["name"]]

    if not n["children"]:
        return f"{pad}<li>\n{person}{pad}</li>\n"

    given = display_name(n)
    sons_label = escape(f"أبناء {given}")
    kids = "".join(render_node(c, indent + 2, path) for c in n["children"])
    return (
        f"{pad}<li>\n"
        f"{person}"
        f'{pad}  <ul aria-label="{sons_label}">\n'
        f"{kids}"
        f"{pad}  </ul>\n"
        f"{pad}</li>\n"
    )


def render_tree(root: dict, ancestors: list[str] | None = None) -> str:
    ancestors = ancestors or []
    return (
        '<div class="tree" dir="ltr">\n'
        "  <ul>\n"
        + render_node(root, 4, ancestors, is_root=True)
        + "  </ul>\n"
        "</div>"
    )


def build_tree() -> dict:
    """Single tree: حسن → … → خليفة → علي / عيسى → all descendants."""

    hilal_abdullah = node("هلال")
    hilal_abdullah["focus"] = True

    hassan_h = node("حسن")
    ibrahim = node("ابراهيم")
    ibrahim["children"] = [node("حسن"), node("خالد")]
    hassan_h["children"] = [ibrahim, node("أحمد")]

    abdullah_h = node("عبدالله")
    abdullah_h["children"] = [
        node("هلال"),
        node("أحمد"),
        node("محمد"),
        node("فهد"),
        node("عيسى"),
    ]

    jamal = node("جمال")
    jamal["children"] = [node("خالد"), node("طلال")]

    hakim = node("عبدالحكيم")
    hakim["children"] = [node("عبدالله")]

    isa_h = node("عيسى")
    isa_h["children"] = [node("عبدالله")]

    ahmed_h = node("أحمد")
    ahmed_h["children"] = [node("سلطان")]

    hilal_abdullah["children"] = [
        hassan_h,
        node("عبدالعزيز"),
        ahmed_h,
        abdullah_h,
        jamal,
        hakim,
        isa_h,
    ]

    mohammed_1 = node("محمد", suffix="(١)")
    mohammed_1["children"] = [
        node("عبدالله"),
        node("عيسى"),
        node("أحمد"),
        node("علي"),
    ]

    # محمد (٢): سهم = ابن، قوائم أفقية = إخوة
    m2_mohammed_line = node("محمد")
    m2_mohammed_line["children"] = [node("عبدالله")]
    m2_yusuf = node("يوسف")
    m2_yusuf["children"] = [node("أحمد")]
    mohammed_2 = node("محمد", suffix="(٢)")
    mohammed_2["children"] = [
        m2_mohammed_line,
        node("عبدالله"),
        node("سعيد"),
        node("عيسى"),
        m2_yusuf,
        node("محمد"),
        node("سلطان"),
        node("علي"),
    ]

    # أحمد بن عبدالله → يوسف → (أحمد | عبدالناصر | محمد | خالد) إخوة
    ahmed_abdullah = node("أحمد")
    ahmed_bin_yusuf = node("أحمد")
    ahmed_bin_yusuf["children"] = [
        node("يوسف"),
        node("راشد"),
        node("فهد"),
    ]
    abdulnasr_bin_yusuf = node("عبدالناصر")
    abdulnasr_bin_yusuf["children"] = [node("يوسف")]
    mohammed_bin_yusuf = node("محمد")
    mohammed_bin_yusuf["children"] = [
        node("جاسم"),
        node("عبدالعزيز"),
        node("يوسف"),
    ]
    khalid_bin_yusuf = node("خالد")
    yusuf_bin_ahmed = node("يوسف")
    yusuf_bin_ahmed["children"] = [
        ahmed_bin_yusuf,
        abdulnasr_bin_yusuf,
        mohammed_bin_yusuf,
        khalid_bin_yusuf,
    ]
    ahmed_abdullah["children"] = [yusuf_bin_ahmed]

    abdullah = node("عبدالله")
    abdullah["focus"] = True
    abdullah["link"] = "/althawadi/ancestors/#abdullah-bin-isa"
    abdullah["children"] = [
        mohammed_1,
        ahmed_abdullah,
        mohammed_2,
        hilal_abdullah,
    ]

    # --- جاسم بن راشد (مخطط: سهم ↓ = ابن، أفقي = إخوة) ---
    naif_ghanm = node("نايف")
    naif_ghanm["children"] = [node("عبدالعزيز")]
    abdullah_ghanm = node("عبدالله")
    abdullah_ghanm["children"] = [naif_ghanm]
    ghanim = node("غانم")
    ghanim["children"] = [abdullah_ghanm]

    isa_ibrahim_hilal = node("عيسى")
    isa_ibrahim_hilal["children"] = [
        node("عبدالله"),
        node("هلال"),
        node("راشد"),
        node("عمر"),
        node("بدر"),
    ]
    ibrahim_hilal_j = node("ابراهيم")
    ibrahim_hilal_j["children"] = [
        node("فيصل"),
        node("سليمان"),
        node("عبدالرحمن"),
        node("عبدالله"),
        node("عبدالعزيز"),
        node("هلال"),
        node("طارق"),
        node("محمد"),
        node("وائل"),
        isa_ibrahim_hilal,
    ]
    hilal_jassim = node("هلال")
    hilal_jassim["children"] = [ibrahim_hilal_j]

    ali_hassan_j = node("علي")
    mohammed_hassan_j = node("محمد")
    mohammed_hassan_j["children"] = [node("حسن"), node("راشد")]
    ali_hassan_j["children"] = [mohammed_hassan_j, node("حسن")]

    rashid_hassan_j = node("راشد")
    rashid_hassan_j["children"] = [
        node("عيسى"),
        node("حسن"),
        node("محمد"),
        node("عصام"),
        node("عبدالرحمن"),
    ]

    abdullah_hassan_j = node("عبدالله")
    abdullah_hassan_j["children"] = [node("علي"), node("حسن")]

    mohammed2_hassan_j = node("محمد")
    mohammed2_hassan_j["children"] = [node("حسن"), node("راشد")]

    hassan_jassim = node("حسن")
    hassan_jassim["children"] = [
        ali_hassan_j,
        rashid_hassan_j,
        abdullah_hassan_j,
        mohammed2_hassan_j,
    ]

    rashid_isa_j = node("راشد")
    rashid_isa_j["children"] = [node("أحمد")]

    faisal_aref = node("فيصل")
    faisal_aref["children"] = [node("عيسى")]
    aref_j = node("عارف")
    aref_j["children"] = [faisal_aref]

    faisal_moh_j = node("فيصل")
    faisal_moh_j["children"] = [node("عبدالله")]
    mohammed_aref_j = node("محمد")
    mohammed_aref_j["children"] = [faisal_moh_j]

    yusuf_isa_j = node("يوسف")
    yusuf_isa_j["children"] = [
        aref_j,
        mohammed_aref_j,
        node("أحمد"),
        node("عبدالله"),
        node("راشد"),
    ]

    isa_ahmed_j = node("عيسى")
    isa_ahmed_j["children"] = [
        node("خليفه"),
        rashid_isa_j,
        node("ناصر"),
        node("خالد"),
        yusuf_isa_j,
    ]

    ibrahim_ahmed_j = node("ابراهيم")
    ibrahim_ahmed_j["children"] = [isa_ahmed_j]

    ahmed_jassim = node("أحمد")
    ahmed_jassim["children"] = [ibrahim_ahmed_j]

    jassim = node("جاسم")
    jassim["children"] = [
        ghanim,
        node("خليفه"),
        ahmed_jassim,
        hassan_jassim,
        hilal_jassim,
    ]

    rashid = node("راشد")
    rashid["focus"] = True
    rashid["link"] = "/althawadi/ancestors/#rashid-bin-isa"
    rashid["children"] = [
        jassim,
        node("هلال"),
        node("حسن"),
        node("أحمد"),
        node("خليفه"),
    ]

    ali = node("علي")
    ali["children"] = [node("محمد"), node("علي")]

    isa = node("عيسى", lineage=True)
    isa["children"] = [
        node("محمد"),
        node("هلال"),
        rashid,
        abdullah,
    ]

    khalifa = node("خليفة", lineage=True)
    khalifa["children"] = [ali, isa]

    hilal = node("هلال", lineage=True)
    hilal["children"] = [khalifa]

    root = node("حسن", lineage=True)
    root["children"] = [hilal]

    return root


def build_page_html() -> str:
    tree_ul = render_tree(build_tree())
    return f"""        <div class="family-tree-lineage max-w-3xl mx-auto mb-8 text-center" dir="rtl">
          <p class="text-[11px] uppercase tracking-[0.35em] text-accent font-latin mb-3">خط النسب</p>
          <p class="font-display text-lg md:text-xl text-foreground leading-relaxed">
            بني خالد — العماير — حسن — هلال — خليفة — عيسى
            <span class="text-muted-foreground mx-1" aria-hidden="true">←</span>
            <strong class="text-accent">عبدالله وراشد</strong>
          </p>
          <p class="mt-3 text-xs text-muted-foreground leading-7">
            خطوط متصلة من الأب إلى الأبناء — الاسم و<strong class="text-foreground">بن …</strong> داخل كل بطاقة.
          </p>
        </div>

        <p class="family-tree-hint">
          مرّر أفقيًا وعموديًا لاستكشاف الشجرة — البطاقات مرتبطة بخطوط CSS من الأب إلى الأبناء.
        </p>

        <div class="family-tree-controls">
          <div class="family-tree-legend" aria-label="دليل البطاقات">
            <span class="family-tree-legend-item">
              <span class="family-tree-legend-swatch family-tree-legend-swatch--root" aria-hidden="true"></span>
              الجدّ
            </span>
            <span class="family-tree-legend-item">
              <span class="family-tree-legend-swatch family-tree-legend-swatch--lineage" aria-hidden="true"></span>
              خط النسب
            </span>
            <span class="family-tree-legend-item">
              <span class="family-tree-legend-swatch family-tree-legend-swatch--focus" aria-hidden="true"></span>
              عبدالله / راشد
            </span>
          </div>
          <div class="family-tree-toolbar">
            <button type="button" id="family-tree-pdf-btn" class="family-tree-pdf-btn map-btn map-btn--primary">
              <svg class="icon h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true">
                <path d="M12 3v12"/>
                <path d="m7 10 5 5 5-5"/>
                <path d="M5 21h14"/>
              </svg>
              <span class="family-tree-pdf-label">تحميل PDF</span>
            </button>
          </div>
        </div>

        <div class="family-tree-pan" id="family-tree-pan" tabindex="0" aria-label="شجرة العائلة">
          <div class="family-tree-canvas">
{tree_ul}
          </div>
        </div>

        <p class="family-tree-pan-hint">مرّر أفقيًا وعموديًا لاستكشاف الشجرة</p>
        <div class="mt-8 notice-box max-w-2xl mx-auto w-full">
          <p class="text-sm text-muted-foreground leading-8" style="margin:0;">
            مسودة عمل — تُكمَّل بالمراجعة.
            <a href="/althawadi/references/" class="text-accent hover:underline">المراجع</a>
            · <a href="/althawadi/ancestors/" class="text-accent hover:underline">الأجداد</a>
          </p>
        </div>"""


def inject_tree_page(content_html: str) -> None:
    page = ROOT / "tree" / "index.html"
    text = page.read_text(encoding="utf-8")
    if "family-tree.js" not in text or "<!-- <script" in text:
        text = text.replace(
            '  <!-- <script src="/althawadi/js/family-tree.js" defer></script> -->',
            '  <script src="/althawadi/js/family-tree.js" defer></script>',
        )
    if "family-tree-pdf.js" not in text:
        text = text.replace(
            '  <script src="/althawadi/js/family-tree.js" defer></script>',
            '  <script src="/althawadi/js/family-tree.js" defer></script>\n  <script src="/althawadi/js/family-tree-pdf.js" defer></script>',
        )
    block = f"      <section class=\"family-tree-section mx-auto max-w-7xl w-full px-4 sm:px-6 py-12 md:py-20\">\n{content_html}\n      </section>"
    text = re.sub(
        r'      <section class="family-tree-section[\s\S]*?      </section>\n    </main>',
        block + "\n    </main>",
        text,
        count=1,
    )
    page.write_text(text, encoding="utf-8")
    print(f"Updated {page}")


def main() -> None:
    tree_ul = render_tree(build_tree())
    TREE_HTML.parent.mkdir(parents=True, exist_ok=True)
    TREE_HTML.write_text(tree_ul + "\n", encoding="utf-8")
    print(f"Wrote {TREE_HTML}")
    inject_tree_page(build_page_html())


if __name__ == "__main__":
    main()
