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


def count_nodes(n: dict) -> int:
    return 1 + sum(count_nodes(c) for c in n.get("children", []))


def set_sons(parent: dict, *children: dict) -> dict:
    """Direct sons of parent — same row in the tree (brothers under one father)."""
    parent["children"] = list(children)
    return parent


def validate_direct_sons(parent: dict, ancestors: list[str]) -> None:
    """Ensure each child's patronymic names this parent (catches nested-by-mistake)."""
    parent_name = parent["name"]
    path = ancestors + [parent_name]
    for child in parent.get("children", []):
        pat = father_line(path)
        if pat and not pat.startswith(f"بن {parent_name}"):
            raise ValueError(
                f"{display_name(child)} should be son of {parent_name}, got {pat}"
            )
        validate_direct_sons(child, path)


def build_hilal_abdullah_branch() -> dict:
    """§7 — سبعة أبناء هلال بن عبدالله (إخوة مباشرون)."""
    hassan_h = set_sons(
        node("حسن"),
        set_sons(node("ابراهيم"), node("حسن"), node("خالد")),
        node("أحمد"),
    )
    abdullah_h = set_sons(
        node("عبدالله"),
        node("هلال"),
        node("أحمد"),
        node("محمد"),
        node("فهد"),
        node("عيسى"),
    )
    hilal = node("هلال")
    hilal["focus"] = True
    return set_sons(
        hilal,
        hassan_h,
        node("عبدالعزيز"),
        set_sons(node("أحمد"), node("سلطان")),
        abdullah_h,
        set_sons(node("جمال"), node("خالد"), node("طلال")),
        set_sons(node("عبدالحكيم"), node("عبدالله")),
        set_sons(node("عيسى"), node("عبدالله")),
    )


def build_mohammed_2_branch() -> dict:
    """محمد (٢) — كل القوائم الأفقية في المخطط = إخوة تحت محمد (٢)."""
    m2_mohammed_line = set_sons(node("محمد"), node("عبدالله"))
    m2_yusuf = set_sons(node("يوسف"), node("أحمد"))
    return set_sons(
        node("محمد", suffix="(٢)"),
        m2_mohammed_line,
        node("عبدالله"),
        node("سعيد"),
        node("عيسى"),
        m2_yusuf,
        node("محمد"),
        node("سلطان"),
        node("علي"),
    )


def build_ahmed_abdullah_branch() -> dict:
    """أحمد بن عبدالله → يوسف → أربعة إخوة."""
    yusuf = set_sons(
        node("يوسف"),
        set_sons(node("أحمد"), node("يوسف"), node("راشد"), node("فهد")),
        set_sons(node("عبدالناصر"), node("يوسف")),
        set_sons(
            node("محمد"),
            node("جاسم"),
            node("عبدالعزيز"),
            node("يوسف"),
        ),
        node("خالد"),
    )
    return set_sons(node("أحمد"), yusuf)


def build_abdullah_bin_isa_branch() -> dict:
    """§6 — أربعة أبناء عبدالله بن عيسى (إخوة)."""
    mohammed_1 = set_sons(
        node("محمد", suffix="(١)"),
        node("عبدالله"),
        node("عيسى"),
        node("أحمد"),
        node("علي"),
    )
    abdullah = node("عبدالله")
    abdullah["focus"] = True
    abdullah["link"] = "/ancestors/#abdullah-bin-isa"
    return set_sons(
        abdullah,
        mohammed_1,
        build_ahmed_abdullah_branch(),
        build_mohammed_2_branch(),
        build_hilal_abdullah_branch(),
    )


def build_ghanim_bin_rashid() -> dict:
    return set_sons(
        node("غانم"),
        set_sons(node("عبدالله"), set_sons(node("نايف"), node("عبدالعزيز"))),
    )


def build_hilal_bin_rashid() -> dict:
    isa_ibrahim = set_sons(
        node("عيسى"),
        node("عبدالله"),
        node("هلال"),
        node("راشد"),
        node("عمر"),
        node("بدر"),
    )
    ibrahim = set_sons(
        node("ابراهيم"),
        node("فيصل"),
        node("سليمان"),
        node("عبدالرحمن"),
        node("عبدالله"),
        node("عبدالعزيز"),
        node("هلال"),
        node("طارق"),
        node("محمد"),
        node("وائل"),
        isa_ibrahim,
    )
    return set_sons(node("هلال"), ibrahim)


def build_hassan_bin_rashid() -> dict:
    """حسن بن راشد — علي، راشد، عبدالله، محمد (أربعة أبناء مباشرون)."""
    ali = set_sons(
        node("علي"),
        set_sons(node("محمد"), node("حسن"), node("راشد")),
        node("حسن"),
    )
    rashid_h = set_sons(
        node("راشد"),
        node("عيسى"),
        node("حسن"),
        node("محمد"),
        node("عصام"),
        node("عبدالرحمن"),
    )
    abdullah_h = set_sons(node("عبدالله"), node("علي"), node("حسن"))
    mohammed_h = set_sons(node("محمد"), node("حسن"), node("راشد"))
    return set_sons(node("حسن"), ali, rashid_h, abdullah_h, mohammed_h)


def build_ahmed_bin_rashid() -> dict:
    yusuf = set_sons(
        node("يوسف"),
        set_sons(node("عارف"), set_sons(node("فيصل"), node("عيسى"))),
        set_sons(node("محمد"), set_sons(node("فيصل"), node("عبدالله"))),
        node("أحمد"),
        node("عبدالله"),
        node("راشد"),
    )
    isa = set_sons(
        node("عيسى"),
        node("خليفة"),
        set_sons(node("راشد"), node("أحمد")),
        node("ناصر"),
        node("خالد"),
        yusuf,
    )
    ibrahim = set_sons(node("ابراهيم"), isa)
    return set_sons(node("أحمد"), ibrahim)


def build_rashid_branch() -> dict:
    """§5 — ستة أبناء راشد (إخوة — كلهم ابن راشد مباشرة، لا تحت جاسم)."""
    rashid = node("راشد")
    rashid["focus"] = True
    rashid["link"] = "/ancestors/#rashid-bin-isa"
    return set_sons(
        rashid,
        node("جاسم"),
        build_hilal_bin_rashid(),
        build_hassan_bin_rashid(),
        build_ahmed_bin_rashid(),
        node("خليفة"),
        build_ghanim_bin_rashid(),
    )


def build_isa_bin_khalifa_branch() -> dict:
    """أبناء عيسى بن خليفة — محمد، هلال، راشد، عبدالله (إخوة)."""
    return set_sons(
        node("عيسى", lineage=True),
        node("محمد"),
        node("هلال"),
        build_rashid_branch(),
        build_abdullah_bin_isa_branch(),
    )


def build_tree() -> dict:
    """Single tree: حسن → … → خليفة → علي / عيسى → all descendants."""
    ali = set_sons(node("علي"), node("محمد"), node("علي"))
    khalifa = set_sons(node("خليفة", lineage=True), ali, build_isa_bin_khalifa_branch())
    hilal = set_sons(node("هلال", lineage=True), khalifa)
    root = set_sons(node("حسن", lineage=True), hilal)
    validate_direct_sons(root, [])
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
          <p class="family-tree-member-count" id="family-tree-member-count" dir="rtl" aria-live="polite">
            <span class="family-tree-member-count-label">إجمالي الأفراد في الشجرة:</span>
            <strong class="family-tree-member-count-num">—</strong>
          </p>
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
            <a href="/references/" class="text-accent hover:underline">المراجع</a>
            · <a href="/ancestors/" class="text-accent hover:underline">الأجداد</a>
          </p>
        </div>"""


def inject_tree_page(content_html: str) -> None:
    page = ROOT / "tree" / "index.html"
    text = page.read_text(encoding="utf-8")
    if "family-tree.js" not in text or "<!-- <script" in text:
        text = text.replace(
            '  <!-- <script src="/js/family-tree.js" defer></script> -->',
            '  <script src="/js/family-tree.js" defer></script>',
        )
    if "family-tree-pdf.js" not in text:
        text = text.replace(
            '  <script src="/js/family-tree.js" defer></script>',
            '  <script src="/js/family-tree.js" defer></script>\n  <script src="/js/family-tree-pdf.js" defer></script>',
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
    root = build_tree()
    total = count_nodes(root)
    tree_ul = render_tree(root)
    TREE_HTML.parent.mkdir(parents=True, exist_ok=True)
    TREE_HTML.write_text(tree_ul + "\n", encoding="utf-8")
    print(f"Wrote {TREE_HTML} ({total} members)")
    inject_tree_page(build_page_html())


if __name__ == "__main__":
    main()
