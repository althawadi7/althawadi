#!/usr/bin/env python3
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FETCHED = Path(
    r"C:\Users\Rashid AlAwadhi\.cursor\projects\j-altahwadi\agent-tools\a568f82c-2b74-4259-864c-125cb26b686a.txt"
)
PAGE = ROOT / "references" / "item" / "ref-12" / "index.html"
CARDS = ROOT / "data" / "references-cards.json"

THAWADI = re.compile(
    r"(الذوادي|عبد\s*الله\s*(?:بن\s*عيسى\s*)?الذوادي|الحاج\s+عبد\s*الله(?:\s+بن\s+عيسى)?\s+الذوادي)",
    re.I,
)

RELATED = """<aside class="ref-thawadi-related" aria-label="ما يخص عائلة الذوادي">
<h2 class="ref-thawadi-related-title">سفن النوخذة عبد الله بن عيسى الذوادي</h2>
<ul class="ref-thawadi-related-list">
<li><strong>مساعد</strong> — سنبوك، للحاج عبد الله الذوادي <span class="ref-ship-ref">(رقم 10 — قائمة الشملان)</span></li>
<li><strong>بشارة</strong> — جالبوت، للحاج عبد الله بن عيسى الذوادي <span class="ref-ship-ref">(رقم 21 — قائمة الشملان)</span></li>
<li><strong>دلال</strong> — جالبوت، للذوادي <span class="ref-ship-ref">(رقم 13 — استدراك العماري)</span></li>
</ul>
<p class="ref-thawadi-related-note">العبارات المتعلقة بالذوادي <mark class="ref-thawadi-mark">مظلّلة</mark> في نص المقال.</p>
</aside>"""


def hi(text: str) -> str:
    return THAWADI.sub(
        r'<mark class="ref-thawadi-mark">\1</mark>',
        html.escape(text.strip()),
    )


def para(text: str) -> str:
    text = text.strip()
    return f"<p>{hi(text)}</p>" if text else ""


def h2(text: str) -> str:
    return f'<h2 class="ref-article-h2">{html.escape(text.strip(" :"))}</h2>'


def h3(text: str) -> str:
    return f'<h3 class="ref-article-h3">{html.escape(text.strip(" :"))}</h3>'


def ship_list(block: str) -> str:
    items = re.findall(r"\d+-.*?(?=\d+-|$)", block.strip(), re.S)
    lis = []
    for item in items:
        item = item.strip().rstrip(".")
        cls = "ref-ship-item"
        if THAWADI.search(item):
            cls += " ref-ship-item--thawadi"
        lis.append(f'<li class="{cls}">{hi(item)}</li>')
    return f'<ol class="ref-ship-list">{"".join(lis)}</ol>'


def prose(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    chunks = re.split(r"(?<=[.!؟])\s+", text)
    return "".join(para(c) for c in chunks if c.strip())


def find_labels(article: str) -> list[str]:
    labels = []
    for needle in (
        "\u0645\u0646 \u0623\u0642\u062f\u0645",
        "\u0623\u0639\u062f\u0627\u062f",
        "\u0623\u0637\u0648\u0644",
        "\u0623\u0633\u0631\u0639",
        "\u0623\u0633\u0645\u0627\u0621 \u0627\u0644\u0633\u0641\u0646 \u0627\u0644\u0634\u0631\u0627\u0639\u064a\u0629",
        "\u0623\u0633\u0645\u0627\u0621 \u0627\u0644\u0633\u0641\u0646 \u0643\u0645\u0627",
    ):
        idx = article.find(needle)
        if idx < 0:
            continue
        end = article.find(":", idx)
        if end < 0:
            continue
        labels.append(article[idx : end + 1])
    return labels


def split_list(text: str) -> tuple[str, str]:
    m = re.search(r"(?=\d+-)", text)
    if not m:
        return text, ""
    return text[: m.start()].strip(), text[m.start() :].strip()


def section_slices(text: str, labels: list[str]) -> list[tuple[str, str]]:
    hits = [(text.index(label), label) for label in labels if label in text]
    hits.sort()
    out = []
    for i, (start, label) in enumerate(hits):
        end = hits[i + 1][0] if i + 1 < len(hits) else len(text)
        out.append((label.strip(" :"), text[start + len(label) : end].strip()))
    return out


def build_body(article: str) -> str:
    parts = [
        RELATED,
        h2("\u0623\u0633\u0645\u0627\u0621 \u0633\u0641\u0646 \u0627\u0644\u0628\u062d\u0631\u064a\u0646 \u0627\u0644\u0634\u0631\u0627\u0639\u064a\u0629"),
        para("\u0628\u0642\u0644\u0645 \u0628\u0634\u0627\u0631 \u0627\u0644\u062d\u0627\u062f\u064a"),
    ]

    chunks = [c.strip() for c in re.split(r"\* \* \*", article) if c.strip()]
    main = chunks[0]
    rest = chunks[1] if len(chunks) > 1 else ""
    omari_chunk = chunks[2] if len(chunks) > 2 else ""

    labels = find_labels(main)
    intro_end = main.find(labels[0]) if labels else 0
    intro = main[:intro_end]
    intro = re.sub(
        r"^\s*\u0628\u0642\u0644\u0645\s+\u0628\u0634\u0627\u0631\s+\u0627\u0644\u062d\u0627\u062f\u064a\s*",
        "",
        intro,
    )
    parts.append(prose(intro))

    sections = section_slices(main[intro_end:], labels)
    for title, body in sections[:-1]:
        parts.append(h3(title))
        parts.append(prose(body))

    last_title, last_body = sections[-1]
    parts.append(h3(last_title))
    sh_prose, sh_list = split_list(last_body)
    parts.append(prose(sh_prose))
    if sh_list:
        parts.append(ship_list(sh_list))

    if rest:
        hadi_title = "\u0627\u0644\u0627\u0633\u062a\u062f\u0631\u0627\u0643 \u0639\u0644\u0649 \u0628\u062d\u062b \u0633\u064a\u0641 \u0628\u0646 \u0645\u0631\u0632\u0648\u0642 \u0627\u0644\u0634\u0645\u0644\u0627\u0646"
        src_title = "\u0645\u0635\u0627\u062f\u0631 \u0627\u0644\u0645\u0627\u062f\u0629"
        omari_title = "\u062a\u0639\u0642\u064a\u0628 \u0627\u0644\u0639\u0645\u0627\u0631\u064a \u0639\u0644\u0649 \u0628\u062d\u062b \u0627\u0644\u062d\u0627\u062f\u064a"

        idx_hadi = rest.find(hadi_title)
        idx_src = rest.find(src_title)
        idx_omari = rest.find("\u062a\u0639\u0642\u064a\u0628 \u0627\u0644\u0639\u0645\u0627\u0631\u064a")

        if idx_hadi >= 0:
            end = idx_src if idx_src >= 0 else (idx_omari if idx_omari >= 0 else len(rest))
            hadi_block = rest[idx_hadi:end]
            parts.append(h2(hadi_title))
            hadi_prose, hadi_list = split_list(hadi_block[len(hadi_title) :])
            parts.append(prose(hadi_prose))
            if hadi_list:
                parts.append(ship_list(hadi_list))

        if idx_src >= 0:
            end = idx_omari if idx_omari >= 0 else len(rest)
            src_block = rest[idx_src:end]
            parts.append(h3(src_title))
            _, src_list = split_list(src_block[len(src_title) :])
            if src_list:
                parts.append(ship_list(src_list))

        if idx_omari >= 0:
            omari_block = rest[idx_omari:]
            omari_heading_end = omari_block.find("\u0647\u0630\u0647 \u0623\u0633\u0645\u0627\u0621")
            if omari_heading_end < 0:
                omari_heading_end = omari_block.find("\u0628\u0642\u0644\u0645")
            heading = omari_block[:omari_heading_end] if omari_heading_end > 0 else omari_title
            parts.append("<hr class='ref-article-divider' />")
            parts.append(h2(heading.strip()))
            omari_body = omari_block[omari_heading_end:] if omari_heading_end > 0 else omari_block[len(omari_title):]
            pre, post = re.split(r"(?=\d+-)", omari_body, maxsplit=1)
            parts.append(prose(pre))
            if post:
                parts.append(ship_list(post))
        elif omari_chunk:
            omari_block = omari_chunk
            omari_heading_end = omari_block.find("\u0647\u0630\u0647 \u0623\u0633\u0645\u0627\u0621")
            heading = omari_block[:omari_heading_end].strip() if omari_heading_end > 0 else omari_title
            parts.append("<hr class='ref-article-divider' />")
            parts.append(h2(heading))
            omari_body = omari_block[omari_heading_end:] if omari_heading_end > 0 else omari_block
            pre, post = re.split(r"(?=\d+-)", omari_body, maxsplit=1)
            parts.append(prose(pre))
            if post:
                parts.append(ship_list(post))

    parts.append(
        '<p class="ref-source-url mt-8"><strong>\u0627\u0644\u0645\u0631\u062c\u0639 \u0627\u0644\u0623\u0635\u0644\u064a:</strong> '
        '<a href="https://bashaaralhadi.blogspot.com/2010/04/blog-post_7829.html" '
        'target="_blank" rel="noreferrer" class="text-accent hover:underline font-latin break-all">'
        "bashaaralhadi.blogspot.com \u2014 \u0623\u0633\u0645\u0627\u0621 \u0633\u0641\u0646 \u0627\u0644\u0628\u062d\u0631\u064a\u0646 \u0627\u0644\u0634\u0631\u0627\u0639\u064a\u0629</a></p>"
    )
    return "\n".join(p for p in parts if p)


def load_article() -> str:
    lines = FETCHED.read_text(encoding="utf-8").splitlines()
    article = lines[4] if len(lines) > 4 else ""
    if len(lines) > 6 and lines[6].strip():
        article = article + "\n* * *\n" + lines[6]
    return article


def main() -> None:
    article = load_article()
    body = build_body(article)
    page = PAGE.read_text(encoding="utf-8")
    page = re.sub(
        r'(<div class="ref-detail-body[^"]*">)([\s\S]*?)(</div>\s*<footer)',
        lambda m: m.group(1) + "\n" + body + "\n        " + m.group(3),
        page,
        count=1,
    )
    PAGE.write_text(page, encoding="utf-8")

    if CARDS.exists():
        data = json.loads(CARDS.read_text(encoding="utf-8"))
        for card in data:
            if card.get("slug") == "ref-12":
                card["fulltext"] = body
                break
        CARDS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {PAGE} ({len(body)} chars)")


if __name__ == "__main__":
    main()
