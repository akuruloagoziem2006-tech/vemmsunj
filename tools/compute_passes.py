"""Compute 24-hour satellite passes for every place, on GitHub's runner, and store them in Supabase.

Writes the keys the Place page and sky card read:
  passes-v1:<place id>     list of passes (sorted, capped at 100)
  passes-at-v1:<place id>  minute the calculation ran
Does not import app.py, so no schema setup or seeding runs here.
"""
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlparse

import numpy as np
import pg8000.dbapi
import requests
from skyfield.api import EarthSatellite, load, wgs84

TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle"
TLE_GROUPS = ["stations", "visual", "weather"]
PASS_MAX_SATS = 30
PASS_SLICE_SIZE = 30
MIN_ALT = 10.0
HOURS = 24
STEP_MIN = 2


def connect():
    u = urlparse(os.environ["DATABASE_URL"])
    return pg8000.dbapi.connect(
        user=unquote(u.username or ""), password=unquote(u.password or ""),
        host=u.hostname, port=u.port or 5432, database=u.path.lstrip("/"), ssl_context=True)


def fetch_group(group):
    for attempt in range(1, 4):
        try:
            r = requests.get(TLE_URL.format(group=group), timeout=30)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"TLE {group} attempt {attempt} failed: {e}", flush=True)
            time.sleep(30 * attempt)
    raise SystemExit(f"could not fetch TLE group {group}")


def parse_tle(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    out = []
    for i in range(1, len(lines) - 1):
        if lines[i].startswith("1 ") and lines[i + 1].startswith("2 "):
            out.append((lines[i - 1], lines[i], lines[i + 1]))
    return out


def get_satellites(ts):
    sats, seen = [], set()
    for group in TLE_GROUPS:
        for name, l1, l2 in parse_tle(fetch_group(group)):
            key = l1[2:7]
            if key in seen:
                continue
            seen.add(key)
            sats.append(EarthSatellite(l1, l2, name, ts))
    return sats


def passes_for(sats, ts, lat, lon, min_alt=MIN_ALT):
    """Same search as find_passes_slice in app.py, over the first PASS_MAX_SATS satellites."""
    observer = wgs84.latlon(lat, lon)
    start = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    n = int(HOURS * 60 / STEP_MIN) + 1
    offsets = [STEP_MIN * i for i in range(n)]
    times = ts.from_datetimes([start + timedelta(minutes=m) for m in offsets])
    passes = []

    def emit(sat, alt, i0, f0, i1, f1):
        t0 = start + timedelta(minutes=offsets[i0] + f0 * STEP_MIN)
        t1 = start + timedelta(minutes=offsets[i1] + f1 * STEP_MIN)
        passes.append({
            "satellite": sat.name,
            "start": t0.isoformat(timespec="minutes"),
            "end": t1.isoformat(timespec="minutes"),
            "max_altitude_deg": round(float(alt[i0:i1 + 1].max()), 1),
        })

    for sat in sats[:PASS_MAX_SATS][:PASS_SLICE_SIZE]:
        alt = np.asarray((sat - observer).at(times).altaz()[0].degrees)
        up = alt >= min_alt
        if not up.any():
            continue
        i_start, f_start = (0, 0.0) if up[0] else (None, 0.0)
        for i in range(n - 1):
            if up[i] == up[i + 1]:
                continue
            frac = float((min_alt - alt[i]) / (alt[i + 1] - alt[i]))
            if up[i + 1]:
                i_start, f_start = i, frac
            elif i_start is not None:
                emit(sat, alt, i_start, f_start, i, frac)
                i_start = None
        if i_start is not None:
            emit(sat, alt, i_start, f_start, n - 1, 0.0)
    passes.sort(key=lambda x: x["start"])
    return passes[:100]


def store(cur, key, body):
    cur.execute(
        "INSERT INTO cache_kv (key, body, fetched_at) VALUES (%s, %s, %s) "
        "ON CONFLICT (key) DO UPDATE SET body = EXCLUDED.body, fetched_at = EXCLUDED.fetched_at",
        (key, body, time.time()))


def main():
    ts = load.timescale()
    sats = get_satellites(ts)
    print(f"{len(sats)} satellites loaded, using the first {min(len(sats), PASS_MAX_SATS)}", flush=True)
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT id, latitude, longitude FROM listings ORDER BY id")
    places = cur.fetchall()
    failed = []
    for pid, lat, lon in places:
        try:
            began = time.time()
            passes = passes_for(sats, ts, lat, lon)
            now_min = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            store(cur, f"passes-v1:{pid}", json.dumps(passes))
            store(cur, f"passes-at-v1:{pid}", json.dumps(now_min.isoformat(timespec="minutes")))
            conn.commit()
            print(f"place {pid}: {len(passes)} passes in {time.time() - began:.1f}s", flush=True)
        except Exception as e:
            conn.rollback()
            failed.append(pid)
            print(f"place {pid}: failed {e.__class__.__name__}: {e}", flush=True)
    conn.close()
    if failed:
        sys.exit(f"failed places: {failed}")


if __name__ == "__main__":
    main()
