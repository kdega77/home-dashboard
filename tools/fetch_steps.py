#!/usr/bin/env python3
"""Publish today's step count to steps.json for the entrance dashboard.

Reads Apple Health via the health-cli (step_count, today, America/Toronto)
and writes {"date": ..., "steps": ..., "updated": ...} next to the site.
On any failure the existing steps.json is left untouched and we exit 1.
"""
import json
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Toronto")
today = datetime.now(TZ).strftime("%Y-%m-%d")

cmd = [
    "/opt/hatch/bin/health-cli", "query", "metrics",
    "--provider", "healthkit",
    "--start-date", today, "--end-date", today,
    "--interval", "daily", "--fields", "step_count",
]
try:
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    data = json.loads(out.stdout)
    records = data.get("records") or []
    steps = None
    for r in records:
        if r.get("date") == today and r.get("step_count") is not None:
            steps = int(r["step_count"])
    if steps is None:
        print("no step_count for", today)
        sys.exit(1)
except Exception as e:
    print("steps fetch failed:", e)
    sys.exit(1)

payload = {
    "date": today,
    "steps": steps,
    "updated": datetime.now(TZ).isoformat(timespec="seconds"),
}
with open("steps.json", "w") as fh:
    json.dump(payload, fh, indent=1)
print("steps:", steps)
