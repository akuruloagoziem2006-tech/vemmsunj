# VEMMSUNJ

VEMMSUNJ is a sky-watching map for observatories, satellite passes, and sightings. It lists observatories and dark-sky viewing spots, shows when satellites and planets are visible from each place, and lets people log what they saw. When a sighting includes a place and time, the app checks which satellites were sunlit and above the horizon, and Gemini picks the most likely match from that list.

## Features

**Home**
- A hero with three starting points: explore places, open the map, and log a sighting.
- A three-step guide: pick a place, check tonight's passes, log what you saw.
- The three most recent sightings.

**Navigation**
- The top bar links to Places, Map, Sightings, and Log in.
- Tapping **VEMMSUNJ** opens a menu with every page, Red light, and Log in or My log.
- Red light mode switches the whole site to red tones for dark-adapted eyes. It stays on in that browser until turned off.

**Places**
- Observatories and dark-sky spots, shown as a grid of cards: three across on wide screens, two on tablets and sideways phones, and one on narrow phones.
- A **Near me** sort that orders places by distance from the visitor's phone. Location stays in the browser.
- An add form for new places.
- Recent sightings at the bottom of the page.

**Place pages**
- **Tonight's best:** the Moon phase, the dark hours in the next 24 hours, and the three highest satellite passes, ranked by peak altitude.
- **Time travel:** choose a time up to 7 days ahead to see passes from that moment.
- **Sky conditions:** cloud cover, visibility, humidity, and rain chance for the next six hours, in a table.
- **Pass reminders:** a browser notification two minutes before each pass in the next 24 hours. Reminders are scheduled while the page is open.
- **Next 24 hours:** a strip showing each satellite pass above 10 degrees, and a table of the passes.
- **Planets:** the seven planets with their altitude and compass direction, each with a drawn illustration.
- **Next possible eclipse:** the next candidate eclipse and whether it's visible from that place.
- **Sky chart:** a star chart of the sky above the place, with north at the top.
- **Star compass:** a live view of the sky in front of the phone. See below.

**Map**
- A full-width map with pins. Each popup lists the next passes and links to the place page.
- A key above the map: a blue dot for places and a red dot for satellites.
- Satellites drawn as small models with solar panels. Each one turns to face its direction of travel.

**Globe**
- A rotating Earth with ocean, land, desert, ice, and cloud, drawn in the app's own style, always shown as a complete circle.
- Satellites from the stations group as small models with solar panels. The ISS is larger, with its truss.
- Each satellite's orbit is drawn as a loop. Tap a name to track it, and the camera follows.
- Countries under each satellite's path are shaded red. Tracking a satellite brightens its countries and lists them.
- Track any satellite by its NORAD catalogue number, such as 25544 for the ISS.
- Speed buttons switch between real time and 60 times faster.

**Aurora**
- NOAA's OVATION aurora forecast, drawn as a green overlay on a square map of the world, with country borders and names.
- The current Kp reading, with a plain-language level and a colour key.
- The forecast chance at a chosen place.

**Star compass**
- Stars, planets, the Moon, and satellites above the horizon, drawn across a sky view that runs edge to edge.
- Phones with a magnetic compass can turn to find objects. Phones without one sense tilt only: the horizon and each object's height work, and you line up direction by tapping **I am pointing at this** on an object you can see.
- A North correction slider for fine alignment.

**Calendar**
- Moon phases for the next 60 days, in a table.
- Approximate meteor shower peaks for the next 60 days, in a table.
- Possible eclipses for the next 12 months, in a table.
- The current planetary Kp index from NOAA, with a plain-language level.

**Sightings and accounts**
- A logbook-style feed. Each entry has an optional place and time, and the AI explanation appears under a red rule.
- **Log a sighting** opens the posting form on demand, so the feed comes first.
- Likes and follows happen in the background. The page doesn't reload or move, and the button and like count update in place.
- Sign up, log in, and follow people. Passwords are stored as salted hashes. Failed logins are rate-limited by username and by IP address.
- Recovery codes: each new account gets a one-time code at sign-up. Entering it on the Reset password page sets a new password and issues a new code.
- **My log:** a private list for each account. Entries never appear in the public feed.
- Usernames starting with VEMMSUNJ are reserved for the app's own accounts.

**Automated posts**
- **VEMMSUNJ_BOT** posts once a day for each place that has passes in the next 24 hours, with a schematic chart. It skips places where the sun is still up. Every bot post is labelled "Automated."
- The bot also posts one Earth image a day from NASA's EPIC camera, with credit to NASA. NASA images are public domain.
- Three example sightings by the VEMMSUNJ account are labelled "Example."

**Layout and appearance**
- One dark theme, with a row of planets under the header.
- Responsive from phones to big screens. Text columns widen on large monitors, and the visual pages (map, globe, aurora, compass) run edge to edge.
- Installable as an app. Offline support keeps the public pages you've opened recently, so they still load without a signal. Sightings, My log, and sign-in are not saved offline.
- Friendly error pages, and plain error messages.

## How the calculations work

**Satellites.** The app downloads orbit data (TLEs) from CelesTrak for the stations, visual, and weather groups, and for any satellite tracked by catalogue number. It checks whether the sun is more than 6 degrees below the horizon at the place, then keeps only satellites that are sunlit and above 10 degrees. Passes are calculated for the next 24 hours, or from the chosen time, and cached for an hour. Results are limited to the first 100.

**Identification.** Gemini chooses the best match from the list of satellites above only. It never names a satellite outside the list. The app doesn't calculate brightness, so the AI is told not to describe how bright a satellite is.

**Planets.** Positions come from NASA's DE421 planetary ephemeris, which is public domain. It's downloaded once and stored in the database. If it isn't stored yet, the app falls back to a simplified calculation, accurate to about a degree, and the page says so.

**Moon phases and eclipses.** Moon phases use a simplified lunar model, accurate to a few degrees. Eclipse dates are approximate, within about an hour, and can miss an eclipse or list one that doesn't happen. Check a published eclipse table before planning.

**Sky chart and star compass.** The chart and the compass use 85 bright stars, with positions and magnitudes typed from standard reference values. They may contain small errors of a few tenths of a degree. The app can also load the full Yale Bright Star Catalogue (BSC5), which is public domain, but the download from CDS fails from both the phone and the hosting server because of a certificate problem on CDS's side.

**Compass sensors.** The compass uses the device's orientation sensors when they report direction. Without a magnetic compass, it uses the accelerometer for tilt only, and direction is set by aligning to a known object.

**Aurora.** The forecast is NOAA's OVATION model, cached for 15 minutes. The map is fitted to the world, so no area beyond the mapped limits shows.

**The daily bot.** Vercel calls `/api/cron/daily` once a day at 03:00 UTC. The endpoint requires a bearer token set in `CRON_SECRET`, so only Vercel or someone with the secret can trigger it.

## Run it locally

Requires Python 3.13 and a Postgres database, such as one from Neon.

    pip install flask requests skyfield sgp4 jplephem numpy pg8000 waitress

Set the environment variables, then start the app:

    export DATABASE_URL="postgresql://user:password@host/dbname"
    export GEMINI_API_KEY="your-key"
    export CRON_SECRET="a-long-random-value"
    HTTPS=0 python app.py

Open http://127.0.0.1:5000. Use HTTPS=0 only for local testing, since the session cookie is secure by default.

## Environment variables

| Name | Purpose |
| --- | --- |
| DATABASE_URL | Postgres connection string |
| GEMINI_API_KEY | Gemini API key for sighting explanations |
| SECRET_KEY | Signs session cookies. Use a long random value. |
| CRON_SECRET | Bearer token for the daily bot and the one-time data setup routes |
| HTTPS | Set to 0 only for local testing. Leave unset in production. |
| TRUST_PROXY | Set to 1 behind a reverse proxy, such as Vercel |
| STARLINK | Set to 1 to include the Starlink group. Very slow, so it's off by default. |

## Deploy on Vercel

The app runs as a Flask app on Vercel. Connect the GitHub repository in the Vercel project settings, set the environment variables above, and each push to the main branch deploys automatically. The daily schedule is defined in `vercel.json`.

After the first deploy, load the planetary data once:

    curl -H "Authorization: Bearer $CRON_SECRET" https://your-site/api/cron/ephemeris

## Known limits

- Passes are cached for an hour and limited to the first 100. The first calculation for a place can take close to a minute on a slow connection.
- Starlink is off, because the full group makes the calculation too slow for a serverless request.
- Time travel is limited to 7 days ahead, since predictions from current orbit data get less reliable further out.
- The bot posts at most once a day per place, and skips places where the sun is up.
- Bot charts are schematic. They show peak altitude and timing, not a real view of the sky.
- The sky chart and compass show 85 bright stars. The full catalogue can't currently be downloaded.
- Compass direction on phones without a magnetic compass must be set by tapping a known object, and it needs realigning after turning.
- The compass with a magnetic sensor is not yet tested on a phone that has one.
- Globe and Map country borders are coarse, and small countries may be missed.
- Eclipse dates are approximate.
- Sighting explanations depend on Gemini's free-tier quota. When it runs out, explanations show an error until it resets.
- There is no email verification. Accounts created before recovery codes existed have no code, so the site owner resets their password with `reset_password.py`.
- Identification uses orbit data only. It can't confirm a satellite from a photo.

## Credits

- Satellite orbit data: CelesTrak.
- Planetary positions: NASA JPL DE421.
- Earth images: NASA EPIC, public domain.
- Aurora forecast: NOAA Space Weather Prediction Center, OVATION model, public domain.
- Space weather: planetary Kp index from NOAA Space Weather Prediction Center, public domain.
- Country borders: Natural Earth, public domain.
- Sky conditions: weather forecast data from Open-Meteo, licensed under CC BY 4.0.
- Map tiles and data: OpenStreetMap contributors. Maps use Leaflet.
- Globe rendering: Three.js (MIT licence), loaded from cdnjs.
- Fonts: Fraunces and Atkinson Hyperlegible, from Google Fonts.
- Star data: Yale Bright Star Catalogue, public domain (not yet loaded).

## Status

This is an early version. The code is released under the MIT License. See the LICENSE file. Third-party data and images keep their own terms, as listed under Credits.
