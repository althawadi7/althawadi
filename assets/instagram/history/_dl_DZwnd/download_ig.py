import hashlib
import html
import re
import urllib.request
from pathlib import Path

raw = Path("embed.html").read_text(encoding="utf-8", errors="replace")
i = raw.find("video_url")
region = raw[i : i + 8000]
m = re.search(r"https(?::|\\:)+[^\"']+?\.mp4[^\"']*", region)
u = m.group(0)
while "\\/" in u or "\\\\/" in u:
    u = u.replace("\\\\\\/", "/").replace("\\/", "/")
u = u.replace("\\u0026", "&")
u = html.unescape(u)
# trim trailing junk if any
u = u.split("\\")[0]
print("URL len", len(u))
print(u[:220])

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.instagram.com/",
    "Origin": "https://www.instagram.com",
    "Accept": "*/*",
}
req = urllib.request.Request(u, headers=headers)
with urllib.request.urlopen(req, timeout=180) as resp:
    data = resp.read()
    print("status", getattr(resp, "status", None), "bytes", len(data))

Path("ig-download.mp4").write_bytes(data)
ex = Path("../DZwndVCtV4L.mp4").read_bytes()
print("same as local?", hashlib.sha256(data).hexdigest() == hashlib.sha256(ex).hexdigest())
print("ig", len(data), "local", len(ex))
