"""Build data/moons.json from JPL SPICE satellite kernels (NAIF body IDs).
Each kernel is downloaded, read, and deleted before the next one, so the whole set
fits on the runner's disk. Orbits are computed from each moon's state at a fixed epoch.
Fails closed: if any planet falls below 90% of its published total, the previous file is kept."""
import json
import math
import os
import re
import sys
import time
import datetime as dt
from pathlib import Path

import requests
import spiceypy as spice

SEP = "https://ssd.jpl.nasa.gov/sats/elem/sep.html"
KERNEL_BASE = "https://ssd.jpl.nasa.gov/ftp/eph/satellites/bsp/"
OUT = Path("data/moons.json")
WORK = Path("kernels_tmp")
EPOCH_ET = 0.0            # 2000-01-01 12:00 TDB
EPOCH_JD = 2451545.0

# planet: (barycentre ID, GM km^3/s^2, published moon total)
PLANETS = {
    "Mars": (4, 42828.4, 2),
    "Jupiter": (5, 126686534.0, 101),
    "Saturn": (6, 37931187.0, 285),
    "Uranus": (7, 5793939.0, 29),
    "Neptune": (8, 6836529.0, 16),
}
# planets not covered by the kernels: keep their entries from the previous file
CARRY = {"Mercury": 0, "Venus": 0, "Earth": 1}
DIGITS = {"4": "Mars", "5": "Jupiter", "6": "Saturn", "7": "Uranus", "8": "Neptune"}


def planet_of(i):
    """Numbered moons only. Planet centres (x99) and barycentres are excluded."""
    if i >= 10000:
        return DIGITS.get(str(i)[0])
    if i >= 100 and i % 100 != 99:
        return DIGITS.get(str(i // 100))
    return None


def name_of(i):
    try:
        return spice.bodc2n(i)
    except Exception:
        return f"NAIF {i}"


def fetch(name):
    path = WORK / name
    for attempt in range(3):
        try:
            with requests.get(KERNEL_BASE + name, stream=True, timeout=(30, 900)) as r:
                r.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            return path
        except requests.RequestException as e:
            print(f"retry {attempt + 1} {name}: {e}", flush=True)
            time.sleep(30)
    raise requests.RequestException(f"could not download {name}")


def orbit_of(i, planet):
    bary, gm, _ = PLANETS[planet]
    try:
        state, _ = spice.spkezr(str(i), EPOCH_ET, "J2000", "NONE", str(bary))
    except Exception:
        return None
    elts = spice.oscltx(state, EPOCH_ET, gm)
    a, e, inc = elts[9], elts[1], elts[2]
    if a <= 0 or e >= 1:
        return None
    period_d = 2 * math.pi * math.sqrt(a ** 3 / gm) / 86400
    return {"a_km": round(a, 1), "e": round(e, 6), "period_days": round(period_d, 4),
            "tp_jd": EPOCH_JD, "retrograde": inc > math.pi / 2}


def main():
    html = requests.get(SEP, timeout=60).text
    names = sorted(set(os.path.basename(h) for h in re.findall(r'href="([^"]+\.bsp)"', html)))
    WORK.mkdir(exist_ok=True)
    found, errors = {}, []
    for k in names:
        try:
            path = fetch(k)
        except requests.RequestException as e:
            errors.append(f"{k}: download failed ({e})")
            continue
        try:
            spice.furnsh(str(path))
            for i in sorted(set(int(x) for x in spice.spkobj(str(path)))):
                if i in found:
                    continue
                planet = planet_of(i)
                if not planet:
                    continue
                orb = orbit_of(i, planet)
                if orb:
                    found[i] = {"name": name_of(i), "planet": planet, "orbit": orb, "kernel": k}
        except Exception as e:
            errors.append(f"{k}: could not read ({e.__class__.__name__}: {e})")
        finally:
            try:
                spice.unload(str(path))
            except Exception:
                pass
            path.unlink(missing_ok=True)
    spice.kclear()

    prev = json.loads(OUT.read_text()) if OUT.exists() else {"planets": []}
    prev_by = {p["planet"]: p for p in prev.get("planets", [])}
    planets_out, failures = [], []
    for planet, (_, _, published) in PLANETS.items():
        moons = sorted(({"name": v["name"], "orbit": v["orbit"]}
                        for v in found.values() if v["planet"] == planet), key=lambda m: m["name"])
        planets_out.append({"planet": planet, "published": published, "count": len(moons),
                            "with_orbit": len(moons), "moons": moons})
        print(f"{planet}: {len(moons)} moons with orbits (published {published})", flush=True)
        if len(moons) < 0.9 * published:
            failures.append(planet)
    for planet, published in CARRY.items():
        old = prev_by.get(planet)
        moons = old["moons"] if old else []
        planets_out.append({"planet": planet, "published": published, "count": len(moons),
                            "with_orbit": sum(1 for m in moons if m.get("orbit")), "moons": moons})
        if len(moons) < 0.9 * published:
            failures.append(planet)

    if errors:
        print("kernel problems:", *errors, sep="\n  ", flush=True)
    if failures:
        print("FAILED count check for", failures, "- keeping the previous data/moons.json", flush=True)
        sys.exit(1)

    data = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
            "sources": ["JPL Planetary Satellite Mean Elements index (sep.html)",
                        "JPL/NAIF satellite SPICE kernels (SPK)"],
            "note": "Orbits are computed from JPL SPICE ephemerides at a fixed epoch. "
                    "Small moons are recent discoveries and may be revised. Unnamed moons appear as NAIF IDs.",
            "planets": planets_out}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1))
    tmp.replace(OUT)
    print("written", OUT, flush=True)


if __name__ == "__main__":
    main()
