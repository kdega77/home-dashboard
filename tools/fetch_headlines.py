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


INDICES = [
    ("TSX", "%5EGSPTSE"),
    ("S&P 500", "%5EGSPC"),
    ("NIFTY", "%5ENSEI"),
]


def quotes(pairs):
    out = []
    for label, sym in pairs:
        try:
            # 1-month daily closes feed the sparkline area cards on the dashboard.
            # The page draws the sparkline from "closes" and never dims a card
            # when its market is closed, so closes are kept even for closed markets.
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=1d&range=1mo" % sym
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)
            res = d["chart"]["result"][0]
            meta = res["meta"]
            price = meta.get("regularMarketPrice")
            prev = meta.get("chartPreviousClose")
            if price is None or not prev:
                continue
            closes = [c for c in (res.get("indicators", {}).get("quote", [{}])[0].get("close") or []) if c is not None]
            entry = {
                "sym": label,
                "ccy": meta.get("currency", ""),
                "price": price,
                "chg": round((price - prev) / prev * 100, 2),
                "closes": [round(c, 2) for c in closes],
            }
            # YTD: latest price vs the FIRST trading day of this year (the first
            # close in the YTD range, i.e. Jan 2026), NOT the Dec 31, 2025 close
            # (chartPreviousClose). Falls back to chartPreviousClose if the
            # closes list is missing.
            try:
                yurl = "https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=1d&range=ytd" % sym
                yreq = urllib.request.Request(yurl, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
                with urllib.request.urlopen(yreq, timeout=20) as yr:
                    yd = json.load(yr)
                yres = yd["chart"]["result"][0]
                ymeta = yres["meta"]
                yprice = ymeta.get("regularMarketPrice")
                ycloses = [c for c in (yres.get("indicators", {}).get("quote", [{}])[0].get("close") or []) if c is not None]
                ybase = ycloses[0] if ycloses else ymeta.get("chartPreviousClose")
                if yprice is not None and ybase:
                    entry["ytd"] = round((yprice - ybase) / ybase * 100, 2)
            except Exception as e:
                print("ytd failed:", sym, e)
            out.append(entry)
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
    idx = quotes(INDICES)
    if not idx:
        try:
            with open("headlines.json") as fh:
                idx = json.load(fh).get("indices", [])
        except Exception:
            idx = []
    payload = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "headlines": merged,
        "indices": idx,
    }
    with open("headlines.json", "w") as fh:
        json.dump(payload, fh, indent=1)
    print("wrote", len(merged), "headlines")


if __name__ == "__main__":
    main()
