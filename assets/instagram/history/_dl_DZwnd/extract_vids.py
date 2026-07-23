import html
import re
from pathlib import Path

raw = Path("embed.html").read_text(encoding="utf-8", errors="replace")
# Find shortcode_media / gql region
idx = raw.find("shortcode_media")
print("idx", idx)
chunk = raw[max(0, idx - 200) : idx + 250000]
Path("chunk.txt").write_text(chunk, encoding="utf-8")

# Unescape for searching
unesc = chunk.encode("utf-8").decode("unicode_escape")
unesc = html.unescape(unesc)
Path("chunk_unesc.txt").write_text(unesc[:100000], encoding="utf-8")

print("GraphSidecar", "GraphSidecar" in unesc)
print("edge_sidecar", "edge_sidecar" in unesc)
print("video_url", unesc.count("video_url"))
print("mp4", unesc.count(".mp4"))

urls = re.findall(r"https://[^\"'\\]+\.mp4[^\"'\\]*", unesc)
print("urls found", len(urls))
seen = set()
uniq = []
for u in urls:
    u = u.replace("\\u0026", "&").replace("&amp;", "&")
    base = u.split("?")[0]
    if base not in seen:
        seen.add(base)
        uniq.append(u)
for i, u in enumerate(uniq):
    print(i, u[:220])
Path("video_urls.txt").write_text("\n\n".join(uniq), encoding="utf-8")
