"""Fetch forecasts for every place from GitHub's network, then push them to the site."""
import json, os, time, urllib.request, urllib.error

BASE = "https://vemmsunj.onrender.com/api/cron"
SECRET = os.environ["CRON_SECRET"]
H = {"Authorization": "Bearer " + SECRET, "Content-Type": "application/json"}
WX = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
      "&hourly=cloud_cover,visibility,relative_humidity_2m,precipitation_probability"
      "&forecast_days=2&timezone=UTC")

def get_places():
    req = urllib.request.Request(BASE + "/wx-places", headers=H)
    return json.loads(urllib.request.urlopen(req, timeout=120).read())

def fetch_all(places):
    url = WX.format(lat=",".join(str(p["lat"]) for p in places),
                    lon=",".join(str(p["lon"]) for p in places))
    for attempt in range(1, 6):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=60).read())
        except urllib.error.HTTPError as e:
            print("attempt", attempt, "HTTP", e.code, flush=True)
            if e.code != 429:
                raise
        time.sleep(90)
    raise SystemExit("Open-Meteo still rate-limited after 5 attempts")

places = get_places()
data = fetch_all(places)
items = data if isinstance(data, list) else [data]
body = {str(p["id"]): it for p, it in zip(places, items)
        if isinstance(it, dict) and "hourly" in it}
req = urllib.request.Request(BASE + "/wx-push", data=json.dumps(body).encode(),
                             headers=H, method="POST")
print("pushed", urllib.request.urlopen(req, timeout=120).read().decode())
