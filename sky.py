"""Bright-star sky chart.

Star positions are J2000 right ascension (hours) and declination (degrees), with apparent
visual magnitude. They were written from standard reference values, not from a downloaded
catalogue, so expect errors of a few tenths of a degree. Check with a planetarium app.
"""
import math
from datetime import datetime, timezone
from html import escape

STARS = [
    ("Sirius", 6.7525, -16.716, -1.46),
    ("Canopus", 6.3992, -52.695, -0.74),
    ("Arcturus", 14.2611, 19.182, -0.05),
    ("Alpha Centauri", 14.6600, -60.833, -0.27),
    ("Vega", 18.6156, 38.784, 0.03),
    ("Capella", 5.2781, 45.998, 0.08),
    ("Rigel", 5.2422, -8.202, 0.13),
    ("Procyon", 7.6550, 5.225, 0.34),
    ("Betelgeuse", 5.9194, 7.407, 0.50),
    ("Achernar", 1.6286, -57.237, 0.46),
    ("Hadar", 14.0636, -60.373, 0.61),
    ("Altair", 19.8464, 8.868, 0.77),
    ("Acrux", 12.4433, -63.099, 0.76),
    ("Aldebaran", 4.5986, 16.509, 0.85),
    ("Antares", 16.4900, -26.432, 1.06),
    ("Spica", 13.4199, -11.161, 0.98),
    ("Pollux", 7.7553, 28.026, 1.14),
    ("Fomalhaut", 22.9608, -29.622, 1.16),
    ("Deneb", 20.6906, 45.280, 1.25),
    ("Regulus", 10.1394, 11.967, 1.35),
    ("Castor", 7.5764, 31.888, 1.58),
    ("Bellatrix", 5.4189, 6.350, 1.64),
    ("Polaris", 2.5303, 89.264, 1.98),
    ("Alnilam", 5.6036, -1.202, 1.69),
    ("Alnitak", 5.6794, -1.943, 1.77),
    ("Mintaka", 5.5333, -0.299, 2.23),
    ("Mirzam", 6.3783, -17.956, 1.98),
    ("Adhara", 6.9770, -28.972, 1.50),
    ("Shaula", 17.5600, -37.104, 1.63),
    ("Mimosa", 12.7953, -59.689, 1.25),
    ("Gacrux", 12.5194, -57.113, 1.59),
    ("Alphard", 9.4597, -8.659, 1.98),
    ("Dubhe", 11.0622, 61.751, 1.79),
    ("Merak", 11.0306, 56.383, 2.37),
    ("Phecda", 11.8972, 53.695, 2.44),
    ("Alioth", 12.9006, 55.960, 1.77),
    ("Mizar", 13.3989, 54.925, 2.27),
    ("Alkaid", 13.7922, 49.313, 1.86),
    ("Hamal", 2.1194, 23.463, 2.00),
    ("Diphda", 0.7264, -17.987, 2.04),
    ("Algol", 3.1361, 40.956, 2.12),
    ("Mirfak", 3.4053, 49.861, 1.80),
    ("Elnath", 5.4383, 28.608, 1.65),
    ("Rasalhague", 17.5822, 12.560, 2.08),
    ("Kochab", 14.8450, 74.156, 2.08),
    ("Sadr", 20.3703, 40.257, 2.20),
    ("Albireo", 19.5119, 27.960, 3.08),
    ("Eltanin", 17.9433, 51.489, 2.23),
    ("Atria", 16.8111, -69.028, 1.92),
    ("Sabik", 17.1730, -15.725, 2.43),
    ("Kaus Australis", 18.4028, -34.385, 1.79),
    ("Nunki", 18.9210, -26.297, 2.02),
    ("Enif", 21.7364, 9.875, 2.39),
    ("Markab", 23.0794, 15.205, 2.49),
    ("Scheat", 23.0628, 28.083, 2.42),
    ("Algenib", 0.2206, 15.183, 2.83),
    ("Alpheratz", 0.1397, 29.091, 2.06),
    ("Schedar", 0.6750, 56.537, 2.23),
    ("Caph", 0.1528, 59.152, 2.27),
    ("Naos", 8.0647, -40.003, 2.25),
    ("Suhail", 9.1331, -43.433, 2.21),
    ("Miaplacidus", 9.2200, -69.717, 1.68),
    ("Avior", 8.3753, -59.509, 1.86),
    ("Sargas", 17.6220, -42.998, 1.87),
    ("Menkent", 14.1110, -36.370, 2.06),
    ("Unukalhai", 15.7378, 6.426, 2.63),
    ("Vindemiatrix", 13.0360, 10.959, 2.83),
    ("Denebola", 11.8178, 14.572, 2.14),
    ("Zosma", 11.2350, 20.524, 2.56),
    ("Ankaa", 0.4381, -42.306, 2.39),
    ("Alphecca", 15.5780, 26.715, 2.23),
    ("Mirach", 1.1622, 35.621, 2.06),
    ("Almach", 2.0650, 42.330, 2.10),
    ("Alnair", 22.1370, -46.961, 1.74),
    ("Peacock", 20.4275, -56.735, 1.94),
    ("Dschubba", 16.0056, -22.622, 2.29),
]

def _precess(ra_h, dec_d, when):
    """Move a J2000 position to the date, using the standard precession rates."""
    t = when.year + when.timetuple().tm_yday / 365.25 - 2000.0
    ra = math.radians(ra_h * 15.0)
    dec = math.radians(dec_d)
    dra_deg = (3.075 + 1.336 * math.sin(ra) * math.tan(dec)) * t / 3600.0
    ddec_deg = 1.336 * math.cos(ra) * t / 3600.0
    return ra_h + dra_deg / 15.0, dec_d + ddec_deg

def star_altaz(ra_h, dec_d, lat, lon, when):
    """Altitude and azimuth in degrees (azimuth measured from north through east)."""
    ra_h, dec_d = _precess(ra_h, dec_d, when)
    d = when.timestamp() / 86400.0 + 2440587.5 - 2451545.0
    lst = math.radians((280.46061837 + 360.98564736629 * d + lon) % 360)
    H = lst - math.radians(ra_h * 15.0)
    dec = math.radians(dec_d)
    latr = math.radians(lat)
    sin_alt = math.sin(dec) * math.sin(latr) + math.cos(dec) * math.cos(latr) * math.cos(H)
    alt = math.degrees(math.asin(max(-1.0, min(1.0, sin_alt))))
    az_from_south = math.degrees(math.atan2(math.sin(H), math.cos(H) * math.sin(latr) - math.tan(dec) * math.cos(latr)))
    return alt, (az_from_south + 180) % 360

def sky_svg(lat, lon, when, size=440):
    """Star chart: the whole sky above the horizon, looking straight up. North is up, east is left."""
    c = size / 2
    R = size / 2 - 22
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" aria-label="Star chart of the sky above this place">',
        f'<rect width="{size}" height="{size}" fill="#0A0D12"/>',
        f'<circle cx="{c}" cy="{c}" r="{R}" fill="#0F1620" stroke="#2A313C" stroke-width="2"/>',
        f'<circle cx="{c}" cy="{c}" r="{R / 3:.1f}" fill="none" stroke="#1C2330"/>',
        f'<circle cx="{c}" cy="{c}" r="{2 * R / 3:.1f}" fill="none" stroke="#1C2330"/>',
    ]
    for label, az in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
        rad = math.radians(az)
        x = c - (R + 12) * math.sin(rad)
        y = c - (R + 12) * math.cos(rad) + 4
        parts.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="#8C929C" font-family="sans-serif" font-size="13" text-anchor="middle">{label}</text>')
    for name, ra, dec, mag in STARS:
        alt, az = star_altaz(ra, dec, lat, lon, when)
        if alt < 0:
            continue
        r = R * (90 - alt) / 90
        x = c - r * math.sin(math.radians(az))
        y = c - r * math.cos(math.radians(az))
        radius = max(1.0, 3.2 - 0.45 * mag)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" fill="#E9E6DC"/>')
        if mag < 1.7 and alt >= 10:
            parts.append(f'<text x="{x + 6:.1f}" y="{y - 5:.1f}" fill="#8C929C" font-family="sans-serif" font-size="11">{escape(name)}</text>')
    parts.append(f'<text x="14" y="{size - 12}" fill="#8C929C" font-family="sans-serif" font-size="11">{when.strftime("%Y-%m-%d %H:%M")} UTC</text>')
    parts.append("</svg>")
    return "".join(parts)
