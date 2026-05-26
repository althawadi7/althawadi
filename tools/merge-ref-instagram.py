#!/usr/bin/env python3
"""Re-merge Instagram partial into references.html."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
refs_path = ROOT / "references.html"
partial = (ROOT / "partials" / "ref-instagram-posts.html").read_text(encoding="utf-8")
refs = refs_path.read_text(encoding="utf-8")

start_markers = [
    '        <div class="ref-archive-section" id="instagram-archive">',
    '        <h2 class="ref-section-title" id="instagram-archive">',
]
end_marker = '        <h2 class="ref-section-title">٦ — مجلس العائلة — تواصل رسمي</h2>'

start = -1
for m in start_markers:
    if m in refs:
        start = refs.index(m)
        break
if start < 0:
    raise SystemExit("Could not find instagram archive start marker")

end = refs.index(end_marker)
contact = refs[end:]
new = refs[:start] + partial + "\n" + contact
refs_path.write_text(new, encoding="utf-8")
print(f"Updated {refs_path}")
