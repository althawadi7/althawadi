#!/usr/bin/env python3
import html as html_lib
import re
import urllib.request
from pathlib import Path

code = "Bv_l0deFcq2"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
html = urllib.request.urlopen(
    urllib.request.Request(f"https://www.instagram.com/p/{code}/?hl=ar", headers=headers),
    timeout=45,
).read().decode("utf-8", "ignore")
m = re.search(r'property="og:image" content="([^"]+)"', html)
if not m:
    raise SystemExit("no og:image")
url = html_lib.unescape(m.group(1))
print("url len", len(url))
data = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45).read()
print("bytes", len(data))
Path(__file__).resolve().parents[1] / "assets" / "instagram" / "history" / f"{code}.jpg"
dest = Path(__file__).resolve().parents[1] / "assets" / "instagram" / "history" / f"{code}.jpg"
dest.write_bytes(data)
print("saved", dest)
