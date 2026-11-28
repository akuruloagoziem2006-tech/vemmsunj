"""Build data/sat_photos.json: one freely licensed Wikimedia Commons photo per satellite.
Only public domain, CC0 or CC BY(-SA) files are kept, with their artist and licence.
Fails closed: a satellite with no acceptable result keeps its previous entry."""
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

import requests

API = "https://commons.wikimedia.org/w/api.php"
HDR = {"User-Agent": "VEMMSUNJ/1.0 (sky-watching site; github.com/akuruloagoziem2006-tech/vemmsunj)"}
OUT = Path("data/sat_photos.json")
QUERIES = {
    "iss": "International Space Station",
    "tiangong": "Tiangong space station",
    "hubble": "Hubble Space Telescope in orbit",
    "sentinel-2": "Sentinel-2 satellite",
    "landsat-8": "Landsat 8 satellite",
    "terra": "Terra satellite NASA",
    "aqua": "Aqua satellite NASA",
}
ALLOWED = ("public domain", "cc0", "cc by")


def meta(m, k):
    return re.sub(r"<[^>]+>", "", (m.get(k, {}).get("value") or "")).strip()


def find(query):
    for attempt in range(3):
        try:
            r = requests.get(API, params={
                "action": "query", "generator": "search", "gsrsearch": query,
                "gsrnamespace": 6, "gsrlimit": 6, "prop": "imageinfo",
                "iiprop": "url|extmetadata", "iiurlwidth": 600, "format": "json"},
                headers=HDR, timeout=60)
            r.raise_for_status()
            break
        except requests.RequestException as e:
            print(f"retry {attempt + 1} {query}: {e}", flush=True)
            time.sleep(20)
    else:
        return None, "search failed"
    pages = (r.json().get("query", {}) or {}).get("pages", {}) or {}
    for p in sorted(pages.values(), key=lambda x: x.get("index", 99)):
        for ii in p.get("imageinfo", []):
            m = ii.get("extmetadata", {})
            lic = meta(m, "LicenseShortName")
            if not lic.lower().startswith(ALLOWED):
                continue
            image = ii.get("thumburl") or ii.get("url")
            if not image:
                continue
            return {"image": image, "page": ii.get("descriptionurl") or "",
                    "licence": lic, "credit": meta(m, "Artist") or "Wikimedia Commons",
                    "title": p.get("title", "")}, None
    return None, "no freely licensed image found"


def main():
    prev = json.loads(OUT.read_text())["photos"] if OUT.exists() else {}
    photos, report = dict(prev), []
    for key, q in QUERIES.items():
        entry, why = find(q)
        if entry:
            photos[key] = entry
            report.append(f"{key}: {entry['licence']} ({entry['title']})")
        else:
            report.append(f"{key}: kept previous ({why})" if key in prev else f"{key}: none ({why})")
        time.sleep(2)
    print("\n".join(report), flush=True)
    if not photos:
        print("no photos at all; keeping the previous file", flush=True)
        sys.exit(1)
    data = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
            "source": "Wikimedia Commons (freely licensed files only)", "photos": photos}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1))
    tmp.replace(OUT)
    print("written", OUT, flush=True)


if __name__ == "__main__":
    main()
