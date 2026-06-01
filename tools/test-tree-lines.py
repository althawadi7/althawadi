#!/usr/bin/env python3
import json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto("http://127.0.0.1:8765/tree/index.html", wait_until="networkidle")
    page.evaluate(
        "document.getElementById('althawadi-main-css').href = '../css/styles.css'"
    )
    page.reload(wait_until="networkidle")
    page.add_script_tag(url="http://127.0.0.1:8765/js/family-tree.js?v=5")
    page.wait_for_timeout(1500)
    page.evaluate("window.__familyTreeLayout()")

    data = page.evaluate(
        """
        () => {
          const c = document.querySelector('.family-tree-canvas');
          const lines = [...c.querySelectorAll('.family-tree-lines line')];
          const vert = lines.filter((l) => {
            const y1 = parseFloat(l.getAttribute('y1'));
            const y2 = parseFloat(l.getAttribute('y2'));
            return Math.abs(y2 - y1) > 8;
          });
          const horiz = lines.filter((l) => {
            const x1 = parseFloat(l.getAttribute('x1'));
            const x2 = parseFloat(l.getAttribute('x2'));
            const y1 = parseFloat(l.getAttribute('y1'));
            const y2 = parseFloat(l.getAttribute('y2'));
            return Math.abs(x2 - x1) > 8 && Math.abs(y2 - y1) < 2;
          });
          return {
            total: lines.length,
            vertical: vert.length,
            horizontal: horiz.length,
            canvasH: c.scrollHeight,
            js: !!window.__familyTreeLayout,
          };
        }
        """
    )
    page.evaluate(
        """
        () => {
          const pan = document.querySelector('.family-tree-pan');
          pan.scrollTop = 400;
          window.__familyTreeLayout();
        }
        """
    )
    page.wait_for_timeout(200)
    scrolled = page.evaluate(
        """
        () => {
          const c = document.querySelector('.family-tree-canvas');
          const root = c.querySelector('.family-tree-node.is-root');
          const lines = [...c.querySelectorAll('.family-tree-lines line')];
          const cr = c.getBoundingClientRect();
          const rr = root.getBoundingClientRect();
          const pan = c.closest('.family-tree-pan');
          const st = pan.scrollTop;
          const rootY = rr.top - cr.top + st;
          const stem = lines.find((l) => {
            const y1 = parseFloat(l.getAttribute('y1'));
            const y2 = parseFloat(l.getAttribute('y2'));
            return Math.abs(y1 - rootY) < 15 && y2 > y1;
          });
          return {
            scrollTop: st,
            rootYInCanvas: rootY,
            stemFound: !!stem,
            lineCount: lines.length,
          };
        }
        """
    )
    print(json.dumps({"initial": data, "scrolled": scrolled}, indent=2))
    browser.close()
