#!/usr/bin/env python3
"""Insert theme toggle button into site headers (idempotent)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOGGLE = """          <button id="theme-toggle" type="button" class="theme-toggle" aria-label="تفعيل الوضع الليلي" aria-pressed="false" title="الوضع الليلي">
            <svg class="icon theme-icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
            <svg class="icon theme-icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>
          </button>
"""

MARKER = 'id="theme-toggle"'
INSERT_BEFORE = '          <button id="menu-toggle"'


def main() -> None:
    updated = 0
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if MARKER in text or INSERT_BEFORE not in text:
            continue
        text = text.replace(INSERT_BEFORE, TOGGLE + INSERT_BEFORE, 1)
        path.write_text(text, encoding="utf-8")
        updated += 1
    print(f"Updated {updated} HTML files with theme toggle.")


if __name__ == "__main__":
    main()
