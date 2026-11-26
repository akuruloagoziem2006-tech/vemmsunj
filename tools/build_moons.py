"""Build data/moons.json: every catalogued moon of the eight planets.
Names come from the MPC natural-satellites page plus Horizons' major-bodies list.
Orbits come from JPL Horizons where it has one. Fails closed: if a planet's count is
far below its published total, the previous data/moons.json is kept."""
import datetime as dt
import json
import math
import re
import sys
import time
from pathlib import Path

import requests

HORIZONS = "https://ssd.jpl.nasa.gov/api/horizons.api"
MPC = "https://www.minorplanetcenter.net/iau/NatSats/NaturalSatellites.html"
OUT = Path("data/moons.json")
# planet, Horizons planet-centre ID, GM (km^3/s^2), published moon count
PLANETS = [
    ("Mercury", "199", 22031.9, 0),
    ("Venus", "299", 324858.6, 0),
    ("Earth", "399", 398600.4, 1),
    ("Mars", "499", 42828.4, 2),
    ("Jupiter", "599", 126686534.0, 101),
    ("Saturn", "699", 37931187.0, 285),
    ("Uranus", "799", 5793939.0, 29),
    ("Neptune", "899", 6836529.0, 16),
]
LETTER = {"J": "Jupiter", "S": "Saturn", "U": "Uranus", "N": "Neptune"}


def key(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def get(url, params=None):
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"retry {attempt + 1} {url}: {e}", flush=True)
            time.sleep(20)
    raise SystemExit(f"source unavailable: {url}")


def horizons_ids(prefix, planet_id):
    """key -> (Horizons ID, name) for the moons of one planet."""
    ids = {}
    for line in get(HORIZONS, {"format": "text", "COMMAND": "MB"}).splitlines():
        m = re.match(r"^\s*(\d{3})\s{2,}(\S.*?)(?:\s{2,}|$)", line)
        if not m or m.group(1)[0] != prefix or m.group(1) == planet_id:
            continue
        name = m.group(2).split()[0]
        ids.setdefault(key(name), (m.group(1), name))
    return ids


def mpc_entries():
    """planet -> {key: display name}, from numbered names and S/yyyy X n designations."""
    text = re.sub(r"<[^>]+>", "\n", get(MPC))
    found = {}
    for planet, name in re.findall(r"(Jupiter|Saturn|Uranus|Neptune|Mars) \d+ \(([^)]+)\)", text):
        found.setdefault(planet, {})[key(name)] = name
    for m in re.finditer(r"S/(\d{4}) ([JSUN]) (\d+)", text):
        found.setdefault(LETTER[m.group(2)], {})[key(m.group(0))] = m.group(0)
    return found


def orbit(bid, planet_id, gm):
    txt = get(HORIZONS, {"format": "text", "COMMAND": f"'{bid}'", "OBJ_DATA": "NO",
                         "MAKE_EPHEM": "YES", "EPHEM_TYPE": "ELEMENTS",
                         "CENTER": f"'500@{planet_id}'", "START_TIME": "2026-01-01",
                         "STOP_TIME": "2026-01-02", "STEP_SIZE": "1d", "REF_PLANE": "ECLIPTIC"})
    if "$$SOE" not in txt:
        return None
    block = txt.split("$$SOE", 1)[1].split("$$EOE", 1)[0]

    def val(k):
        m = re.search(r"\b" + k + r"\s*=\s*([-+]?\d+\.?\d*(?:E[-+]?\d+)?)", block)
        return float(m.group(1)) if m else None

    qr, ec, inc, tp = val("QR"), val("EC"), val("IN"), val("Tp")
    if None in (qr, ec, inc, tp) or ec >= 1:
        return None
    a = qr / (1 - ec)
    period_d = 2 * math.pi * math.sqrt(a ** 3 / gm) / 86400
    return {"a_km": round(a, 1), "e": round(ec, 6), "period_days": round(period_d, 4),
            "tp_jd": round(tp, 6), "retrograde": inc > 90}


def main():
    found = mpc_entries()
    planets_out, report, failures = [], [], []
    for name, pid, gm, published in PLANETS:
        hz = horizons_ids(pid[0], pid)
        entries = dict(found.get(name, {}))
        for k, (_, disp) in hz.items():
            entries.setdefault(k, disp)
        moons = []
        for k, disp in sorted(entries.items(), key=lambda kv: kv[1]):
            orb = None
            if k in hz:
                try:
                    orb = orbit(hz[k][0], pid, gm)
                except requests.RequestException:
                    orb = None
                time.sleep(0.5)
            moons.append({"name": disp, "orbit": orb})
        with_orbit = sum(1 for m in moons if m["orbit"])
        line = f"{name}: {len(moons)} moons listed (published {published}), {with_orbit} with orbits"
        print(line, flush=True)
        report.append(line)
        if len(moons) < 0.9 * published:
            failures.append(name)
        planets_out.append({"planet": name, "published": published, "count": len(moons),
                            "with_orbit": with_orbit, "moons": moons})
    if failures:
        print("FAILED count check for", failures, "- keeping the previous data/moons.json", flush=True)
        sys.exit(1)
    data = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
            "sources": ["IAU Minor Planet Center natural satellites list", "JPL Horizons orbital elements"],
            "note": "Small moons are recent discoveries and may be revised. Moons without an orbit are shown at an estimated distance.",
            "planets": planets_out}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1))
    tmp.replace(OUT)
    print("written", OUT, flush=True)


if __name__ == "__main__":
    main()
