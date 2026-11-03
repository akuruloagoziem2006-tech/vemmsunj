"""Check public/data/bright_stars.json for problems that would break the sky charts.

Usage: python3 tools/validate_star_catalogue.py
Exits with status 1 if any row is invalid.
"""
import json
import math
import sys
from pathlib import Path

path = Path("public/data/bright_stars.json")
data = json.loads(path.read_text(encoding="utf-8"))
problems = []
seen_hr = set()
rows = data.get("stars", [])

if data.get("count") != len(rows):
    problems.append(f"count field says {data.get('count')} but there are {len(rows)} rows")

for i, st in enumerate(rows, start=1):
    if len(st) != 5:
        problems.append(f"row {i}: expected 5 fields, found {len(st)}")
        continue
    hr, name, ra, dec, mag = st
    if not isinstance(hr, int) or hr <= 0:
        problems.append(f"row {i}: HR number {hr!r} is not a positive integer")
    elif hr in seen_hr:
        problems.append(f"row {i}: duplicate HR number {hr}")
    else:
        seen_hr.add(hr)
    if not isinstance(ra, (int, float)) or not math.isfinite(ra) or not (0 <= ra < 360):
        problems.append(f"row {i} (HR {hr}): right ascension {ra!r} is outside 0 to 360 degrees")
    if not isinstance(dec, (int, float)) or not math.isfinite(dec) or not (-90 <= dec <= 90):
        problems.append(f"row {i} (HR {hr}): declination {dec!r} is outside -90 to 90 degrees")
    if not isinstance(mag, (int, float)) or not math.isfinite(mag) or not (-2 <= mag <= 7):
        problems.append(f"row {i} (HR {hr}): magnitude {mag!r} is not a plausible value")

if problems:
    print(f"{len(problems)} problem(s):")
    for line in problems[:50]:
        print(" -", line)
    sys.exit(1)
print(f"ok: {len(rows)} stars, all with valid positions and magnitudes, no duplicate HR numbers")
