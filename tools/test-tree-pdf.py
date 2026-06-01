#!/usr/bin/env python3
"""Smoke-test PDF export (html2canvas must not throw on oklch)."""
import json
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/tree/index.html"


def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(str(exc)))

        page.goto(URL, wait_until="networkidle")
        page.evaluate(
            """
            () => {
              document.querySelectorAll('link[rel=\"stylesheet\"]').forEach((link) => {
                link.href = link.href.replace('/althawadi/', '/');
              });
            }
            """
        )
        page.reload(wait_until="networkidle")
        page.add_script_tag(url="http://127.0.0.1:8765/js/family-tree.js?v=pdf1")
        page.add_script_tag(url="http://127.0.0.1:8765/js/family-tree-pdf.js?v=pdf1")
        page.wait_for_timeout(500)

        page.evaluate(
            """
            async () => {
              await new Promise((resolve) => {
                if (window.__familyTreeLayout) window.__familyTreeLayout();
                requestAnimationFrame(() => requestAnimationFrame(resolve));
              });
              const btn = document.getElementById('family-tree-pdf-btn');
              btn.click();
              await new Promise((r) => setTimeout(r, 8000));
            }
            """
        )

        ok = page.evaluate("() => typeof window.html2canvas === 'function'")
        browser.close()

    oklch_errors = [e for e in errors if "oklch" in e.lower()]
    print(json.dumps({"html2canvasLoaded": ok, "errors": errors, "oklchErrors": oklch_errors}, ensure_ascii=False, indent=2))
    if oklch_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
