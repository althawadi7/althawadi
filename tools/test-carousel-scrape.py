#!/usr/bin/env python3
import struct
import urllib.request

code = "DYg1frRABy6"
headers = {"User-Agent": "Mozilla/5.0"}


def jpeg_size(data):
    i = 2
    while i < len(data) - 8:
        if data[i] != 0xFF:
            return None
        m = data[i + 1]
        if m in (0xC0, 0xC2):
            h = struct.unpack(">H", data[i + 5 : i + 7])[0]
            w = struct.unpack(">H", data[i + 7 : i + 9])[0]
            return w, h
        if m in (0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0x01):
            i += 2
            continue
        ln = struct.unpack(">H", data[i + 2 : i + 4])[0]
        i += 2 + ln
    return None


i = 1
while True:
    url = f"https://www.instagram.com/p/{code}/media/?size=l&index={i}"
    try:
        data = urllib.request.urlopen(
            urllib.request.Request(url, headers=headers), timeout=45
        ).read()
    except Exception:
        break
    if len(data) < 5000:
        print(f"index {i}: stop ({len(data)} bytes)")
        break
    s = jpeg_size(data)
    print(f"index {i}: {s} {len(data)//1024}KB")
    i += 1
