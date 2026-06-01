#!/usr/bin/env python3
"""Generate family tree <ul> HTML from structured data."""

import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TREE_HTML = ROOT / "partials" / "family-tree-ul.html"


def node(name: str, *, lineage=False, focus=False, link: str | None = None) -> dict:
    return {
        "name": name,
        "lineage": lineage,
        "focus": focus,
        "link": link,
        "children": [],
    }


def render_node(n: dict, indent: int, *, is_root: bool = False) -> str:
    pad = " " * indent
    title = escape(n["name"])
    given = escape(n["name"].split()[0])
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

    if n.get("link"):
        inner = (
            f'{pad}  <a href="{n["link"]}" class="{cls}" title="{title}">\n'
            f'{pad}    <span class="family-tree-given">{given}</span>\n'
            f"{pad}  </a>\n"
        )
    else:
        inner = (
            f'{pad}  <div class="{cls}" title="{title}">\n'
            f'{pad}    <span class="family-tree-given">{given}</span>\n'
            f"{pad}  </div>\n"
        )

    if not n["children"]:
        return f"{pad}<li>\n{inner}{pad}</li>\n"

    kids = "".join(render_node(c, indent + 4) for c in n["children"])
    return (
        f"{pad}<li>\n"
        f"{inner}"
        f'{pad}  <ul class="family-tree-children">\n'
        f"{kids}"
        f'{pad}  </ul>\n'
        f"{pad}</li>\n"
    )


def build_tree() -> dict:
    # هلال بن عبدالله بن عيسى branch
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
        node("محمد"),
        node("أحمد"),
        node("محمد"),
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

    isa = node("عيسى", lineage=True)
    isa["children"] = [
        node("محمد"),
        node("هلال"),
        rashid,
        abdullah,
    ]

    ali_branch = node("علي")
    ali_branch["children"] = [
        node("محمد"),
        node("علي"),
    ]

    khalifa = node("خليفة", lineage=True)
    khalifa["children"] = [ali_branch, isa]

    hilal_ancestor = node("هلال", lineage=True)
    hilal_ancestor["children"] = [khalifa]

    root = node("حسن", lineage=True)
    root["children"] = [hilal_ancestor]
    return root


def inject_tree_page(ul_html: str) -> None:
    page = ROOT / "tree" / "index.html"
    text = page.read_text(encoding="utf-8")
    text = text.replace(
        "  <!-- <script src=\"/althawadi/js/family-tree.js\" defer></script> -->",
        '  <script src="/althawadi/js/family-tree.js" defer></script>',
    )
    indented = "\n".join("          " + line if line.strip() else line for line in ul_html.splitlines())
    block = f"""      <section class="family-tree-section mx-auto max-w-7xl w-full max-w-full px-4 sm:px-6 py-12 md:py-20">
        <div class="family-tree-lineage max-w-3xl mx-auto mb-10 text-center" dir="rtl">
          <p class="text-[11px] uppercase tracking-[0.35em] text-accent font-latin mb-3">خط النسب</p>
          <p class="font-display text-lg md:text-xl text-foreground leading-relaxed">
            بني خالد — العماير
            <span class="text-muted-foreground mx-1" aria-hidden="true">←</span>
            حسن
            <span class="text-muted-foreground mx-1" aria-hidden="true">←</span>
            هلال
            <span class="text-muted-foreground mx-1" aria-hidden="true">←</span>
            خليفة
            <span class="text-muted-foreground mx-1" aria-hidden="true">←</span>
            عيسى
            <span class="text-muted-foreground mx-1" aria-hidden="true">←</span>
            <strong class="text-accent">عبدالله وراشد</strong>
          </p>
          <p class="mt-3 text-xs text-muted-foreground leading-7">
            مسودة عمل — تُكمَّل بالمراجعة. الأسماء من مشجرة العائلة قيد التحديث.
          </p>
        </div>

        <p class="family-tree-hint">
          الاسم الأول فقط — الأب هو البطاقة فوقه. قرّب أو بعّد الشاشة، أو اسحب لاستكشاف الشجرة.
        </p>
        <div class="family-tree-pan" id="family-tree-pan" tabindex="0" aria-label="شجرة العائلة">
          <div class="family-tree-canvas" id="family-tree-canvas">
{indented}
          </div>
        </div>
        <p class="family-tree-pan-hint">الشجرة تتوسّط تلقائيًا — قرّب أو بعّد الشاشة، أو اسحب إن احتجت</p>
        <div class="mt-8 notice-box max-w-2xl mx-auto w-full">
          <p class="text-sm text-muted-foreground leading-8" style="margin:0;">
            هذا الموقع يوثّق <strong class="text-foreground">ذرية عبدالله وراشد</strong> أبناء
            <strong class="text-foreground">عيسى بن خليفة بن هلال بن حسن الذوادي</strong>.
            للمراجع: <a href="/althawadi/references/" class="text-accent hover:underline">صفحة المراجع</a>
            — <a href="/althawadi/ancestors/" class="text-accent hover:underline">سير الأجداد</a>.
          </p>
        </div>
      </section>"""
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
    html = '<ul class="family-tree">\n' + render_node(root, 2, is_root=True) + "</ul>\n"
    TREE_HTML.parent.mkdir(parents=True, exist_ok=True)
    TREE_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {TREE_HTML}")
    inject_tree_page(html)


if __name__ == "__main__":
    main()
