#!/usr/bin/env python3
"""Fetch CBC + BBC headlines into headlines.json (served same-origin to the dashboards)."""
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    "https://www.cbc.ca/webfeed/rss/rss-topstories",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
]
PER_FEED = 8


def titles(url):
    req = urllib.request.Request(url, headers={"User-Agent": "home-dashboard-headlines/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = r.read()
    root = ET.fromstring(data)
    out = []
    for item in root.iter("item"):
        t = item.find("title")
        if t is not None and t.text:
            txt = " ".join(t.text.split())
            if txt and txt not in out:
                out.append(txt)
        if len(out) >= PER_FEED:
            break
    return out


def main():
    blocks = []
    for f in FEEDS:
        try:
            blocks.append(titles(f))
        except Exception as e:
            print("feed failed:", f, e)
            blocks.append([])
    merged = []
    for i in range(PER_FEED):
        for b in blocks:
            if i < len(b):
                merged.append(b[i])
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "headlines": merged,
    }
    with open("headlines.json", "w") as fh:
        json.dump(payload, fh, indent=1)
    print("wrote", len(merged), "headlines")


if __name__ == "__main__":
    main()
