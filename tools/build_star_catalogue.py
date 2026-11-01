"""Build a trimmed star catalogue from the Yale Bright Star Catalogue (BSC5) fixed-width file.

Usage: python3 tools/build_star_catalogue.py [magnitude_limit]
Reads bsc5/catalog.txt and writes public/data/bright_stars.json.
Positions are J2000 right ascension (degrees) and declination (degrees).
"""
import json
import sys
from pathlib import Path

SOURCE = Path("bsc5/catalog.txt")
OUT = Path("public/data/bright_stars.json")
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0

stars, skipped = [], 0
for line in SOURCE.open(encoding="latin-1"):
    try:
        hr = int(line[0:4])
    except ValueError:
        continue
    try:
        ra = line[75:83].strip()
        dec = line[83:90].strip()
        ra_deg = (int(ra[0:2]) + int(ra[2:4]) / 60 + float(ra[4:]) / 3600) * 15
        sign = -1 if dec[0] == "-" else 1
        dec_deg = sign * (int(dec[1:3]) + int(dec[3:5]) / 60 + int(dec[5:7]) / 3600)
        mag = float(line[102:107])
    except ValueError:
        skipped += 1
        continue
    if mag > limit:
        continue
    stars.append([hr, line[4:14].strip(), round(ra_deg, 4), round(dec_deg, 4), mag])

stars.sort(key=lambda s: s[4])
payload = {
    "source": "Yale Bright Star Catalogue, 5th revised edition (Hoffleit and Warren, 1991)",
    "magnitude_limit": limit,
    "count": len(stars),
    "fields": ["hr", "name", "ra_deg_j2000", "dec_deg_j2000", "visual_mag"],
    "stars": stars,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, separators=(",", ":")))
print(f"wrote {len(stars)} stars at magnitude {limit} or brighter to {OUT}; skipped {skipped} lines")
