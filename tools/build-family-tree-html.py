#!/usr/bin/env python3
"""Generate family tree HTML — single unified tree with father→son arrows."""

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


def render_node(n: dict, indent: int, ancestors: list[str], *, is_root: bool = False) -> str:
    pad = " " * indent
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

    if n.get("link"):
        inner = (
            f'{pad}  <a href="{n["link"]}" class="{cls}" title="{title_esc}">\n'
            f'{pad}    <span class="family-tree-given">{given_esc}</span>{pat_html}\n'
            f"{pad}  </a>\n"
        )
    else:
        inner = (
            f'{pad}  <div class="{cls}" title="{title_esc}">\n'
            f'{pad}    <span class="family-tree-given">{given_esc}</span>{pat_html}\n'
            f"{pad}  </div>\n"
        )

    path = ancestors + [n["name"]]
    if not n["children"]:
        return f"{pad}<li>\n{inner}{pad}</li>\n"

    sons_label = escape(f"أبناء {given}")
    kids = "".join(render_node(c, indent + 4, path) for c in n["children"])
    return (
        f"{pad}<li>\n"
        f"{inner}"
        f'{pad}  <ul class="family-tree-children" aria-label="{sons_label}">\n'
        f"{kids}"
        f'{pad}  </ul>\n'
        f"{pad}</li>\n"
    )


def render_tree(root: dict, ancestors: list[str] | None = None) -> str:
    ancestors = ancestors or []
    return (
        '<ul class="family-tree">\n'
        + render_node(root, 4, ancestors, is_root=True)
        + "</ul>"
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

    abdullah = node("عبدالله")
    abdullah["focus"] = True
    abdullah["link"] = "/althawadi/ancestors/#abdullah-bin-isa"
    abdullah["children"] = [
        node("محمد", suffix="(١)"),
        node("أحمد"),
        node("محمد", suffix="(٢)"),
        hilal_abdullah,
    ]

    rashid = node("راشد")
    rashid["focus"] = True
    rashid["link"] = "/althawadi/ancestors/#rashid-bin-isa"
    rashid["children"] = [
        node("جاسم"),
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
          مرّر أفقيًا وعموديًا — كل بطاقة متصلة بأبها بخطوط زاوية مثل المخطط المرجعي.
        </p>

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
            "  <!-- <script src=\"/althawadi/js/family-tree.js\" defer></script> -->",
            '  <script src="/althawadi/js/family-tree.js" defer></script>',
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
