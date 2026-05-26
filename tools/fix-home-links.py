#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

for p in ROOT.rglob("*.html"):
    t = p.read_text(encoding="utf-8")
    o = t
    t = t.replace(
        'href="./" class="flex items-center gap-3 group"',
        'href="/althawadi/" data-home class="flex items-center gap-3 group"',
    )
    t = t.replace(
        'href="../" class="flex items-center gap-3 group"',
        'href="/althawadi/" data-home class="flex items-center gap-3 group"',
    )
    t = t.replace('href="./" class="nav-link', 'href="/althawadi/" data-home class="nav-link')
    t = t.replace('href="../" class="nav-link', 'href="/althawadi/" data-home class="nav-link')
    t = t.replace(
        'href="./" class="mt-6 inline-block rounded-md bg-primary',
        'href="/althawadi/" data-home class="mt-6 inline-block rounded-md bg-primary',
    )
    t = t.replace(
        '<link rel="canonical" href="./" />',
        '<link rel="canonical" href="https://althawadi7.github.io/althawadi/" />',
    )
    if t != o:
        p.write_text(t, encoding="utf-8")
        print(p.relative_to(ROOT))
