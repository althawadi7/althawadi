#!/usr/bin/env python3
"""Quick layout probe for family tree width."""
import json
from playwright.sync_api import sync_playwright

EVAL = """
() => {
  const canvas = document.querySelector('.family-tree-canvas');
  const rows = Array.from(canvas.querySelectorAll('.family-tree-children')).map(ul => {
    const items = Array.from(ul.querySelectorAll(':scope > li'));
    const total = items.reduce((s, li) => s + parseFloat(li.style.width || 0), 0);
    return {
      label: ul.getAttribute('aria-label') || '',
      ulW: ul.style.width,
      itemCount: items.length,
      sumLiW: Math.round(total),
      items: items.slice(0, 8).map(li => ({ left: li.style.left, width: li.style.width }))
    };
  }).sort((a, b) => parseFloat(b.ulW || 0) - parseFloat(a.ulW || 0));
  return {
    jsLoaded: typeof window.__familyTreeLayout === 'function',
    canvasScrollW: canvas ? canvas.scrollWidth : null,
    topRows: rows.slice(0, 10)
  };
}
"""


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto("http://127.0.0.1:8765/tree/index.html", wait_until="networkidle")
        before = page.evaluate(EVAL)

        page.add_script_tag(url="http://127.0.0.1:8765/js/family-tree.js")
        page.wait_for_timeout(800)
        page.evaluate("() => { if (window.__familyTreeLayout) window.__familyTreeLayout(); }")
        page.wait_for_timeout(400)
        after = page.evaluate(EVAL)

        print("BEFORE JS:")
        print(json.dumps(before, ensure_ascii=False, indent=2))
        print("\nAFTER JS:")
        print(json.dumps(after, ensure_ascii=False, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
