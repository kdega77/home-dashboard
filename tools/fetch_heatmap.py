#!/usr/bin/env python3
"""Fetch fresh heatmap data (today's % move per stock) from Yahoo Finance.

The treemap page (heatmap-preview.html) used to carry a hardcoded snapshot
from Nov 5, 2026. This module refreshes that data so the page can show the
current day instead. It is called from tools/fetch_headlines.py, whose output
(headlines.json) the headlines workflow already commits every run -- so no
workflow-file change is needed. The heatmap rides inside headlines.json
under the "heatmap" key.

Design notes:
- Market-cap weights ("cap") and sectors ("sec") are static: they change
  slowly and only set tile sizes, so they stay as listed here.
- Only the daily % change ("chg") is refreshed, from Yahoo v8 chart
  (regularMarketPrice vs chartPreviousClose). The v7 quote API is blocked.
- Throttle: at most one refresh per 60 minutes. The headlines bot runs
  every ~30 min; without the throttle it would hammer Yahoo with 99 calls
  a run. The refresh reuses the previous data while it is fresh.
- Never break headlines: on any failure this returns the previous data
  (or None on a first run), and the caller must keep the old key.
- A refresh is only used when >=80% of symbols got fresh values; a
  half-empty refresh keeps the old data instead.
"""
import json
import time
import urllib.request
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
    TORONTO = ZoneInfo("America/Toronto")
except Exception:  # pragma: no cover - very old Python
    TORONTO = timezone.utc

# (short label, Yahoo symbol, sector, cap weight) -- caps/sectors copied
# from the Nov 5, 2026 snapshot that shipped in heatmap-preview.html.
STOCKS = {
    "sp": [
        ("NVDA", "NVDA", "Technology", 4500), ("MSFT", "MSFT", "Technology", 3900),
        ("AAPL", "AAPL", "Technology", 3800), ("AVGO", "AVGO", "Technology", 1000),
        ("PLTR", "PLTR", "Technology", 400), ("ORCL", "ORCL", "Technology", 900),
        ("CRM", "CRM", "Technology", 300), ("AMD", "AMD", "Technology", 350),
        ("MU", "MU", "Technology", 300), ("CSCO", "CSCO", "Technology", 300),
        ("IBM", "IBM", "Technology", 250), ("ADBE", "ADBE", "Technology", 250),
        ("GOOGL", "GOOGL", "Communication", 3400), ("META", "META", "Communication", 1900),
        ("NFLX", "NFLX", "Communication", 500), ("AMZN", "AMZN", "Consumer Cyclical", 2600),
        ("TSLA", "TSLA", "Consumer Cyclical", 450), ("HD", "HD", "Consumer Cyclical", 350),
        ("JPM", "JPM", "Financials", 850), ("V", "V", "Financials", 650),
        ("MA", "MA", "Financials", 550), ("LLY", "LLY", "Healthcare", 700),
        ("UNH", "UNH", "Healthcare", 300), ("ABT", "ABT", "Healthcare", 200),
        ("TMO", "TMO", "Healthcare", 200), ("JNJ", "JNJ", "Healthcare", 350),
        ("MRK", "MRK", "Healthcare", 250), ("ABBV", "ABBV", "Healthcare", 500),
        ("COST", "COST", "Consumer Defensive", 450), ("WMT", "WMT", "Consumer Defensive", 800),
        ("PEP", "PEP", "Consumer Defensive", 200), ("KO", "KO", "Consumer Defensive", 400),
        ("PG", "PG", "Consumer Defensive", 400), ("XOM", "XOM", "Energy", 550),
        ("BRK.B", "BRK-B", "Financials", 1000), ("QCOM", "QCOM", "Technology", 250),
        ("AMAT", "AMAT", "Technology", 200), ("LRCX", "LRCX", "Technology", 150),
        ("ISRG", "ISRG", "Healthcare", 180), ("SYK", "SYK", "Healthcare", 120),
    ],
    "nse": [
        ("HDFC", "HDFCBANK.NS", "Financials", 190), ("ICICI", "ICICIBANK.NS", "Financials", 130),
        ("SBI", "SBIN.NS", "Financials", 95), ("KOTAK", "KOTAKBANK.NS", "Financials", 55),
        ("AXIS", "AXISBANK.NS", "Financials", 55), ("BAJAJ", "BAJFINANCE.NS", "Financials", 65),
        ("TCS", "TCS.NS", "Technology", 170), ("INFY", "INFY.NS", "Technology", 85),
        ("HCL", "HCLTECH.NS", "Technology", 60), ("WIPRO", "WIPRO.NS", "Technology", 35),
        ("TECHM", "TECHM.NS", "Technology", 25), ("RELIANCE", "RELIANCE.NS", "Energy", 240),
        ("ONGC", "ONGC.NS", "Energy", 45), ("BHARTI", "BHARTIARTL.NS", "Telecom", 140),
        ("ITC", "ITC.NS", "Consumer", 70), ("HUL", "HINDUNILVR.NS", "Consumer", 60),
        ("MARUTI", "MARUTI.NS", "Consumer", 55), ("LT", "LT.NS", "Industrials", 75),
        ("ADANI", "ADANIENT.NS", "Industrials", 35), ("ULTRA", "ULTRACEMCO.NS", "Industrials", 35),
        ("SUN", "SUNPHARMA.NS", "Pharma", 50), ("TATASTEEL", "TATASTEEL.NS", "Materials", 35),
        ("NTPC", "NTPC.NS", "Utilities", 45), ("POWER", "POWERGRID.NS", "Utilities", 40),
        ("TITAN", "TITAN.NS", "Consumer", 35), ("NESTLE", "NESTLEIND.NS", "Consumer", 30),
        ("ASIAN", "ASIANPAINT.NS", "Consumer", 25), ("TRENT", "TRENT.NS", "Consumer", 25),
        ("BEL", "BEL.NS", "Industrials", 40), ("EICHER", "EICHERMOT.NS", "Consumer", 20),
    ],
    "tsx": [
        ("RY", "RY.TO", "Financials", 140), ("TD", "TD.TO", "Financials", 110),
        ("BMO", "BMO.TO", "Financials", 95), ("BNS", "BNS.TO", "Financials", 85),
        ("CM", "CM.TO", "Financials", 70), ("MFC", "MFC.TO", "Financials", 55),
        ("SLF", "SLF.TO", "Financials", 40), ("BAM", "BAM.TO", "Financials", 70),
        ("SHOP", "SHOP.TO", "Technology", 110), ("CSU", "CSU.TO", "Technology", 75),
        ("TRI", "TRI.TO", "Technology", 85), ("ENB", "ENB.TO", "Energy", 110),
        ("CNQ", "CNQ.TO", "Energy", 90), ("TRP", "TRP.TO", "Energy", 75),
        ("SU", "SU.TO", "Energy", 65), ("CNR", "CNR.TO", "Industrials", 95),
        ("CP", "CP.TO", "Industrials", 85), ("WCN", "WCN.TO", "Industrials", 45),
        ("ATD", "ATD.TO", "Industrials", 70), ("AEM", "AEM.TO", "Materials", 60),
        ("ABX", "ABX.TO", "Materials", 55), ("FTS", "FTS.TO", "Utilities", 45),
        ("QSR", "QSR.TO", "Consumer", 40), ("IFC", "IFC.TO", "Financials", 35),
        ("NA", "NA.TO", "Financials", 35), ("POW", "POW.TO", "Financials", 25),
        ("DOL", "DOL.TO", "Consumer", 30), ("L", "L.TO", "Consumer", 25),
        ("WSP", "WSP.TO", "Industrials", 20),
    ],
}

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
REFRESH_EVERY_S = 60 * 60  # at most one Yahoo sweep per hour
DEADLINE_S = 240  # never spend more than 4 minutes on the sweep


def _chg(sym):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?interval=1d&range=1d" % sym
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.load(r)
            res = d["chart"]["result"][0]
            meta = res["meta"]
            price = meta.get("regularMarketPrice")
            prev = meta.get("chartPreviousClose")
            if price is None or not prev:
                return None
            return round((price - prev) / prev * 100, 2)
        except Exception as e:
            print("heatmap quote failed:", sym, "attempt", attempt + 1, e)
            time.sleep(2)
    return None


def _old_heatmap(path):
    try:
        with open(path) as fh:
            return json.load(fh).get("heatmap")
    except Exception:
        return None


def _label(now_utc):
    local = now_utc.astimezone(TORONTO)
    return local.strftime("%a %b %-d, %Y") + " \u00b7 " + local.strftime("%-I:%M %p").lower() + " ET"


def refresh(path="headlines.json"):
    """Return fresh heatmap payload, the previous one if still fresh or the
    sweep failed, or None when there is no usable data at all."""
    old = _old_heatmap(path)
    now = datetime.now(timezone.utc)
    if old and old.get("updated"):
        try:
            age = (now - datetime.fromisoformat(old["updated"])).total_seconds()
            if age < REFRESH_EVERY_S:
                print("heatmap fresh (age %ds), skipping sweep" % int(age))
                return old
        except Exception:
            pass
    old_by_key = {}
    if old:
        for tab, rows in old.items():
            if isinstance(rows, list):
                for row in rows:
                    old_by_key[(tab, row.get("s"))] = row.get("chg")
    started = time.time()
    out = {}
    fresh = 0
    total = 0
    for tab, rows in STOCKS.items():
        items = []
        for short, sym, sec, cap in rows:
            total += 1
            chg = None
            if time.time() - started < DEADLINE_S:
                chg = _chg(sym)
                time.sleep(0.15)
            if chg is None:
                chg = old_by_key.get((tab, short))
            else:
                fresh += 1
            items.append({"s": short, "sec": sec, "cap": cap, "chg": chg})
        out[tab] = items
    if total and fresh < 0.8 * total:
        print("heatmap sweep too stale (%d/%d fresh), keeping old data" % (fresh, total))
        return old
    payload = {
        "updated": now.isoformat(timespec="seconds"),
        "label": _label(now),
        "sp": out["sp"],
        "nse": out["nse"],
        "tsx": out["tsx"],
    }
    print("heatmap refreshed: %d/%d fresh" % (fresh, total))
    return payload


if __name__ == "__main__":
    data = refresh()
    print(json.dumps({"updated": data["updated"], "label": data["label"]}, indent=1) if data else "no heatmap data")
