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


STOCKS = [
    ("XEQT", "XEQT.TO"),
    ("VFV", "VFV.TO"),
    ("INFY", "INFY.NS"),
    ("NIFTYBEES", "NIFTYBEES.NS"),
]

INDICES = [
    ("TSX", "%5EGSPTSE"),
    ("NIFTY", "%5ENSEI"),
]


def quotes(pairs):
    out = []
    for label, sym in pairs:
        try:
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=1d&range=1d" % sym
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)
            meta = d["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice")
            prev = meta.get("chartPreviousClose")
            if price is None or not prev:
                continue
            out.append({
                "sym": label,
                "ccy": meta.get("currency", ""),
                "price": price,
                "chg": round((price - prev) / prev * 100, 2),
            })
        except Exception as e:
            print("stock failed:", sym, e)
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
    stk = quotes(STOCKS)
    idx = quotes(INDICES)
    if not stk or not idx:
        try:
            with open("headlines.json") as fh:
                prev_payload = json.load(fh)
            if not stk:
                stk = prev_payload.get("stocks", [])
            if not idx:
                idx = prev_payload.get("indices", [])
        except Exception:
            pass
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "headlines": merged,
        "stocks": stk,
        "indices": idx,
    }
    with open("headlines.json", "w") as fh:
        json.dump(payload, fh, indent=1)
    print("wrote", len(merged), "headlines")


if __name__ == "__main__":
    main()
