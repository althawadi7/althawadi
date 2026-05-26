#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
refs_path = ROOT / "references.html"
partial = (ROOT / "partials" / "ref-instagram-posts.html").read_text(encoding="utf-8")
refs = refs_path.read_text(encoding="utf-8")

marker_old = '        <h2 class="ref-section-title">٥ — مجلس العائلة — تواصل رسمي</h2>'
marker_end = '        <div class="mt-16 border-t border-border pt-10 text-center">'

contact = """        <h2 class="ref-section-title">٦ — مجلس العائلة — تواصل رسمي</h2>
        <ul class="space-y-6" style="list-style:none;padding:0;margin:0;">
          <li>
            <a href="https://www.instagram.com/althawadi_majlis/?hl=ar" target="_blank" rel="noreferrer" class="group block border border-border rounded-sm p-6 bg-card/40 hover:bg-card transition-colors">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <h3 class="font-display text-xl text-foreground group-hover:text-accent transition-colors">حساب مجلس الذوادي على إنستغرام</h3>
                  <p class="mt-2 text-sm text-muted-foreground leading-7">الحساب الرسمي لمجلس بيت العود — أخبار المجلس، المناسبات، والمساهمات العائلية.</p>
                  <span class="mt-3 inline-block text-xs text-primary font-latin break-all">https://www.instagram.com/althawadi_majlis/?hl=ar</span>
                </div>
                <svg class="icon h-5 w-5 text-muted-foreground group-hover:text-accent transition-colors shrink-0 mt-1" viewBox="0 0 24 24" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" x2="21" y1="14" y2="3"/></svg>
              </div>
            </a>
          </li>
        </ul>

"""

start = refs.index(marker_old)
end = refs.index(marker_end)
new = refs[:start] + partial + "\n" + contact + refs[end:]
refs_path.write_text(new, encoding="utf-8")
print(f"Updated {refs_path} ({len(new)} chars)")
