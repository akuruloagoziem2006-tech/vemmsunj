# VEMMSUNJ

VEMMSUNJ is a sky-watching map for observatories, satellite passes, and sightings. It lists observatories and dark-sky viewing spots, shows when satellites and planets are visible from each place, and lets people log what they saw. When a sighting includes a place and time, the app checks which satellites were sunlit and above the horizon, and Gemini picks the most likely match from that list.

## Features

**Places and maps**
- Observatories and dark-sky spots, with an add form and a Near me sort that orders places by distance from the visitor's phone. Location stays in the browser.
- A map with pins. Each popup lists the next passes and links to the place page.
- A recent sightings section at the bottom of the Places page.

**Place pages**
- **Tonight's best:** the Moon phase, the dark hours in the next 24 hours, and the three highest satellite passes, ranked by peak altitude.
- **Time travel:** choose a time up to 7 days ahead to see passes from that moment.
- **Next 24 hours:** a strip showing each satellite pass above 10 degrees.
- **Planets:** the seven planets with their altitude and compass direction, each with a drawn illustration.
- **Next possible eclipse:** the next candidate eclipse and whether it's visible from that place.
- **Sky chart:** a star chart of the sky above the place, with north at the top. See below for the star data.
- **Sky conditions:** cloud cover, visibility, humidity, and rain chance for the next six hours.
- **Pass reminders:** a browser notification two minutes before each pass in the next 24 hours. Reminders are scheduled while the page is open.

**Globe**
- A rotating Earth with ocean, land, desert, ice, and cloud, drawn in the app's own style.
- Satellites from the stations group as small models with solar panels. The ISS is larger, with its truss.
- Each satellite's orbit is drawn as a loop. Tap a name to track it, and the camera follows.
- Countries under each satellite's path are shaded red. Tracking a satellite brightens its countries and lists them.
- Speed buttons switch between real time and 60 times faster.

**Sightings and accounts**
- A logbook-style feed of posts with an optional place and time. If both are given, the AI explanation appears under a red rule.
- Sign up, log in, follow people, and like sightings. Passwords are stored as salted hashes. Failed logins are rate-limited by username and by IP address.
- Password recovery uses a one-time recovery code, shown at sign-up. Entering it sets a new password and issues a new code.
- **My log:** a private list for each account. Entries never appear in the public feed.
- Usernames starting with VEMMSUNJ are reserved for the app's own accounts.

**Calendar**
- Moon phases for the next 60 days.
- Approximate meteor shower peaks for the next 60 days.
- Possible eclipses for the next 12 months.
- Space weather: the current planetary Kp index from NOAA, with a plain-language level.

**Aurora**
- A map of NOAA's OVATION aurora forecast, drawn as a green overlay. Brighter means a higher chance.
- Open a place from its page to see the forecast chance at that location.

**Automated posts**
- **VEMMSUNJ_BOT** posts once a day for each place that has passes in the next 24 hours, with a schematic chart. It skips places where the sun is still up. Every bot post is labelled "Automated."
- The bot also posts one Earth image a day from NASA's EPIC camera, with credit to NASA. NASA images are public domain.
- Three example sightings by the VEMMSUNJ account are labelled "Example."

**Appearance and use**
- One dark theme, with a row of planets under the header.
- A red-light mode, switched from the header. It stays on in this browser until turned off.
- Installable as an app, and offline support keeps the public pages you've opened recently, so they still load without a signal. Sightings, My log, and sign-in are not saved offline.
- Friendly error pages, and plain error messages.

## How the calculations work

**Satellites.** The app downloads orbit data (TLEs) from CelesTrak for the stations, visual, and weather groups. It checks whether the sun is more than 6 degrees below the horizon at the place, then keeps only satellites that are sunlit and above 10 degrees. Passes are calculated for the next 24 hours, or from the chosen time, and cached for an hour. Results are limited to the first 100.

**Identification.** Gemini chooses the best match from the list of satellites above only. It never names a satellite outside the list. The app doesn't calculate brightness, so the AI is told not to describe how bright a satellite is.

**Planets.** Positions come from NASA's DE421 planetary ephemeris, which is public domain. It's downloaded once and stored in the database. If it isn't stored yet, the app falls back to a simplified calculation, accurate to about a degree, and the page says so.

**Moon phases and eclipses.** Moon phases use a simplified lunar model, accurate to a few degrees. Eclipse dates are approximate, within about an hour, and can miss an eclipse or list one that doesn't happen. Check a published eclipse table before planning.

**Sky chart stars.** The chart uses 85 bright stars, with positions and magnitudes typed from standard reference values. They may contain small errors of a few tenths of a degree. The app can also load the full Yale Bright Star Catalogue (BSC5), which is public domain. The download from CDS fails from both the phone and the hosting server, because of a certificate problem on CDS's side, so the app keeps the bright stars. The loader stays in place for a later download.

**Globe countries.** Country borders come from Natural Earth's 110-metre data, which is public domain. It is coarse, so small countries may be missed. The browser loads it from GitHub when the Globe page opens.

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
| CRON_SECRET | Bearer token for the daily bot and the one-time planet data setup |
| HTTPS | Set to 0 only for local testing. Leave unset in production. |
| TRUST_PROXY | Set to 1 behind a reverse proxy, such as Vercel |
| STARLINK | Set to 1 to include the Starlink group. Very slow, so it's off by default. |

## Deploy on Vercel

The app runs as a Flask app on Vercel. Connect the GitHub repository in the Vercel project settings, set the environment variables above, and each push to the main branch deploys automatically. The daily schedule is defined in `vercel.json`.

After the first deploy, load the planetary data once:

    curl -H "Authorization: Bearer $CRON_SECRET" https://your-site/api/cron/ephemeris

## Known limits

- Passes are cached for an hour and limited to the first 100. The first calculation for a place can take close to a minute.
- Starlink is off, because the full group makes the calculation too slow for a serverless request.
- Time travel is limited to 7 days ahead, since predictions from current orbit data get less reliable further out.
- The bot posts at most once a day per place, and skips places where the sun is up.
- Bot charts are schematic. They show peak altitude and timing, not a real view of the sky.
- The sky chart shows 85 bright stars. The full catalogue can't currently be downloaded.
- Globe country borders are coarse, and small countries may be missed.
- The Globe needs an internet connection for Three.js and the country borders.
- Eclipse dates are approximate.
- Sighting explanations depend on Gemini's free-tier quota. When it runs out, explanations show an error until it resets.
- There is no email verification. Accounts created before recovery codes existed have no code, so the site owner resets their password with `reset_password.py`.
- Identification uses orbit data only. It can't confirm a satellite from a photo.

## Credits

- Satellite orbit data: CelesTrak.
- Planetary positions: NASA JPL DE421.
- Earth images: NASA EPIC, public domain.
- Map tiles and data: OpenStreetMap contributors. Maps use Leaflet.
- Fonts: Fraunces and Atkinson Hyperlegible, from Google Fonts.
- Globe rendering: Three.js (MIT licence), loaded from cdnjs.
- Country borders: Natural Earth, public domain.
- Star data: Yale Bright Star Catalogue, public domain (not yet loaded).
- Sky conditions: weather forecast data from Open-Meteo, licensed under CC BY 4.0.
- Space weather: planetary Kp index from NOAA Space Weather Prediction Center, public domain.
- Aurora forecast: NOAA Space Weather Prediction Center, OVATION model, public domain.

## Status

This is an early version. The code is released under the MIT License. See the LICENSE file. Third-party data and images keep their own terms, as listed under Credits.
