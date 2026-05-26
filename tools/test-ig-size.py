#!/usr/bin/env python3
import json
import re
import urllib.request

code = "DYg1frRABy6"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-IG-App-ID": "936619743392459",
}
url = f"https://www.instagram.com/p/{code}/?hl=ar"
html = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45).read().decode("utf-8", "ignore")

print("len html", len(html))
for pat in [
    r'"display_url":"([^"]+)"',
    r'"og:image" content="([^"]+)"',
    r'property="og:image" content="([^"]+)"',
]:
    ms = re.findall(pat, html)
    print(pat, len(ms))
    if ms:
        u = ms[0].encode().decode("unicode_escape") if "display" in pat else ms[0]
        print(" ", u[:120])

# all scontent urls with dimensions in nearby json
dims = re.findall(r'"width":(\d+),"height":(\d+)[^}]{0,200}"url":"(https:[^"]+)"', html)
print("dim urls", len(dims))
if dims:
    dims = [(int(w), int(h), u.encode().decode("unicode_escape")) for w, h, u in dims]
    dims.sort(key=lambda x: x[0] * x[1])
    print("smallest", dims[0][0], dims[0][1])
    print("largest", dims[-1][0], dims[-1][1])

urls = set(re.findall(r'https://scontent[^"\\]+', html))
print("scontent urls", len(urls))
# find jpg/png not heic
for u in sorted(urls, key=len, reverse=True)[:15]:
    if "heic" in u.lower():
        continue
    print(" ", u[:150])
