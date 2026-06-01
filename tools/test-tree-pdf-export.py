#!/usr/bin/env python3
"""Check PDF capture dimensions vs broken layout."""
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
    page.add_script_tag(url="http://127.0.0.1:8765/js/family-tree.js")
    page.add_script_tag(url="http://127.0.0.1:8765/js/family-tree-pdf.js")
    page.wait_for_timeout(1000)

    stats = page.evaluate(
        """
        async () => {
          const pan = document.querySelector('.family-tree-pan');
          const canvas = pan.querySelector('.family-tree-canvas');
          window.__althawadiBase = '../';
          document.querySelectorAll('link[rel=stylesheet]').forEach((l) => {
            if (l.href.includes('styles.css')) l.disabled = true;
          });
          const link = document.createElement('link');
          link.rel = 'stylesheet';
          link.href = '../css/family-tree-pdf-critical.css';
          document.head.appendChild(link);
          await new Promise((r) => (link.onload = link.onerror = r));
          pan.classList.add('family-tree-pdf-exporting');
          pan.scrollTop = 0;
          pan.scrollLeft = 0;
          window.__familyTreeLayout();
          await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
          const nodes = canvas.querySelectorAll('.family-tree-node');
          const lines = canvas.querySelectorAll('.family-tree-lines line');
          const first = nodes[0].getBoundingClientRect();
          const last = nodes[nodes.length - 1].getBoundingClientRect();
          const cr = canvas.getBoundingClientRect();
          return {
            nodeCount: nodes.length,
            lineCount: lines.length,
            canvasW: canvas.scrollWidth,
            canvasH: canvas.scrollHeight,
            spreadY: last.bottom - first.top,
            flexChild: getComputedStyle(canvas.querySelector('.family-tree-children')).display,
          };
        }
        """
    )
    print(json.dumps(stats, indent=2))
    browser.close()
