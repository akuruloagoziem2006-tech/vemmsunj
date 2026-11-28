# VEMMSUNJ

VEMMSUNJ is a sky-watching map for observatories, satellite passes, and sightings. It lists observatories and dark-sky viewing spots, shows when satellites and planets are visible from each place, and lets people log what they saw. When a sighting includes a place and time, the app checks which satellites were sunlit and above the horizon, and Gemini picks the most likely match from that list.

## Features

**Home**
- A hero with three starting points: explore places, open the map, and log a sighting.
- A three-step guide: pick a place, check tonight's passes, log what you saw.
- An Astronomy feed with two columns: Image of the Day (NASA) and Astronomy Picture of the Day (NASA APOD). Each column shows the four newest pictures, and each card links to NASA's page.
- A header slideshow of the newest Image of the Day and Astronomy Picture of the Day.
- "Find my nearest place" finds the closest observatory to your location, and a list lets you choose any place.
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
- **Pass simulation:** plays a satellite pass across the sky, at real time or faster. Each satellite is drawn as an icon that turns to face its direction of travel. Where a freely licensed photo exists, it replaces the icon, with its credit shown under the diagram.

**Map**
- A full-width map with pins. Each popup lists the next passes and links to the place page. On phones the map is tall.
- A key above the map: a blue dot for places and a red dot for satellites.
- Satellites drawn as small models with solar panels. Each one turns to face its direction of travel.

**Globe**
- A rotating Earth with ocean, land, desert, ice, and cloud, drawn in the app's own style, always shown as a complete circle.
- About 240 satellites from the stations, visual, and weather groups, grouped by source and filterable by name or NORAD number. Each button shows the NORAD number.
- Satellite positions are calculated in the browser from each satellite's orbit data (TLE), so motion is correct at any speed.
- Each satellite's orbit is drawn as a loop. Tap a name to track it, and the camera follows.
- Countries under each satellite's path are shaded red. Tracking a satellite brightens its countries and lists them.
- Track any satellite by its NORAD catalogue number, such as 25544 for the ISS.
- Speed buttons switch between real time and 60 times faster.
- A Voyager 1 and Voyager 2 panel above the globe shows each probe's distance from Earth, its light-travel time, its direction, and its rate of change. The probes are too far to draw.

**Tracker**
- Tonight's passes above a chosen place, and a table of live satellite positions.
- A world map of the tracked satellites that you can pan and zoom. Tap a satellite to highlight its row. The axis labels show degrees.
- **See the orbit on the Globe** opens the globe with that satellite selected and its orbit shown.

**Planet orbits**
- The planets on their real orbits, using NASA DE421 positions, at real time or faster. Orbit distances use a log scale, and a True scale view is available.
- Moon systems from the JPL SPICE satellite kernels. Tap a planet, or use its moons button, to open its moon panel. The panel shows each moon's name, real orbital period, and count, and it can be zoomed and panned.
- A deep-space background. Planet and moon colours are drawn to suggest each body's real appearance.

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
- The bot posts NASA's Earth image of the day from the EPIC camera, with credit to NASA, and NASA's Image of the Day and Astronomy Picture of the Day.
- Astronomy Picture of the Day entries are taken from NASA's APOD feed. Each card shows the photographer's credit where NASA gives one, and links to NASA's page for rights.
- Three example sightings by the VEMMSUNJ account are labelled "Example."

**Layout and appearance**
- One dark theme, with a row of planets under the header.
- Responsive from phones to big screens. Text columns widen on large monitors, and the visual pages (map, globe, aurora, compass, planet orbits) run edge to edge.
- Installable as an app. Offline support keeps the public pages you've opened recently, so they still load without a signal. Sightings, My log, and sign-in are not saved offline.
- Friendly error pages, and plain error messages.

## How the calculations work

**Satellites.** The app downloads orbit data (TLEs) from CelesTrak for the stations, visual, and weather groups, and for any satellite tracked by catalogue number. It checks whether the sun is more than 6 degrees below the horizon at the place, then keeps only satellites that are sunlit and above 10 degrees. Passes are computed on GitHub's runners every three hours from the stations, visual and weather groups, and stored. The place page reads the stored list. Time travel up to 7 days ahead reads a stored 7-day list. The 24-hour list is capped at 100. Globe positions are calculated in the browser from the stored TLEs.

**Identification.** Gemini chooses the best match from the list of satellites above only. It never names a satellite outside the list. The app doesn't calculate brightness, so the AI is told not to describe how bright a satellite is.

**Planets.** Positions come from NASA's DE421 planetary ephemeris, which is public domain. It's downloaded once and stored in the database. If it isn't stored yet, the app falls back to a simplified calculation, accurate to about a degree, and the page says so.

**Moons.** A weekly GitHub job reads the JPL satellite SPICE kernels and computes each moon's orbit from its state at a fixed epoch (2000-01-01). The results are stored in `data/moons.json` and served at `/api/moons`. Moons NAIF has no name for appear as "NAIF" followed by their ID. Moons without an orbit are listed by name only.

**Voyager.** An hourly GitHub job asks JPL Horizons for each probe's position, and stores the latest value and a rolling history of 168 points. Rates of change come from that history.

**Moon phases and eclipses.** Moon phases use a simplified lunar model, accurate to a few degrees. Eclipse dates are approximate, within about an hour, and can miss an eclipse or list one that doesn't happen. Check a published eclipse table before planning.

**Sky chart and star compass.** The chart uses the Yale Bright Star Catalogue (BSC5, public domain), bundled with the app, to magnitude 6.5. The sky list shows stars to magnitude 5. Positions are precessed to the date and are accurate to about a quarter of a degree.

**Compass sensors.** The compass uses the device's orientation sensors when they report direction. Without a magnetic compass, it uses the accelerometer for tilt only, and direction is set by aligning to a known object.

**Aurora.** The forecast is NOAA's OVATION model, cached for 15 minutes. The map is fitted to the world, so no area beyond the mapped limits shows.

**Satellite photos.** A weekly GitHub job searches Wikimedia Commons for a set of satellites and keeps only files whose licence allows reuse (public domain, CC0, or CC BY / CC BY-SA). Each photo is stored with its artist and licence, and the pass simulation shows the credit beneath the diagram. Satellites without an accepted photo keep the drawn icon.

**Automated jobs.** Scheduled work runs on GitHub Actions, which calls the app's protected endpoints. GitHub can delay or skip scheduled runs, so the job schedule is a target, not a guarantee. See the table below.

## Scheduled jobs

| Workflow | Schedule (UTC) | What it updates |
| --- | --- | --- |
| precompute-pages.yml | Hourly, at :10 | Stored planets, sky, tonight, observation and home data for each place |
| compute-passes.yml | Every 3 hours | Stored pass predictions for each place (24 hours and 7 days) |
| passes.yml | Every 6 hours | Pass summaries posted by the bot |
| precompute-globe.yml | Every 15 minutes | Globe satellite snapshot (TLEs for about 240 satellites) |
| ingest-data.yml | Every 30 minutes | Ingests stored data for the app |
| weather-forecasts.yml | Every 2 hours | Forecast data for each place |
| voyager.yml | Hourly, at :40 | Voyager 1 and 2 positions and history |
| daily-images.yml | 06:30 and 18:30 | NASA APOD and Image of the Day, EPIC Earth image |
| moons-data.yml | Weekly, Sunday 04:15 | Moon data from JPL SPICE kernels (`data/moons.json`) |
| sat-photos.yml | Weekly, Monday 05:30 | Satellite photos from Wikimedia Commons (`data/sat_photos.json`) |
| backup.yml | Daily | Encrypted database export, kept for 30 days (needs `BACKUP_PASSPHRASE`) |

The moons and photo jobs fail closed: if a result falls short of its check, the previous file stays live.

## Run it locally

Requires Python 3.13 and a Postgres database, such as one from Neon.

    pip install flask requests skyfield sgp4 jplephem numpy pg8000 waitress spiceypy

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
| NASA_API_KEY | NASA API key for the APOD and related checks. Without it, the shared demo key is used, which is rate-limited. |
| SECRET_KEY | Signs session cookies. Use a long random value. |
| CRON_SECRET | Bearer token for the scheduled jobs and the one-time data setup routes |
| SENTRY_DSN | Optional. Error monitoring with Sentry. |
| ADMIN_USERNAMES | Comma-separated usernames with admin access. |
| HTTPS | Set to 0 only for local testing. Leave unset in production. |
| TRUST_PROXY | Set to 1 behind a reverse proxy, such as Render |
| PRECOMPUTED_ONLY | Set to 1 in production so web requests read stored results and never calculate |
| STARLINK | Set to 1 to include the Starlink group. Very slow, so it's off by default. |

## Deploy on Render

The app runs as a Python web service on Render (Frankfurt). Connect the GitHub repository, set the environment variables above, and use this start command:

    waitress-serve --host=0.0.0.0 --port=$PORT --threads=8 app:app

Each push to the main branch deploys automatically. Health is checked at `/healthz`.

## Known limits

- The free Render instance sleeps when idle and has had several short outages. Slow first loads and occasional 502 errors are expected on the free plan.
- GitHub has delayed or skipped several scheduled runs. Stored results can be older than their stated times, and the pages show the time they were calculated.
- Passes are computed every three hours and stored. A place with no stored result shows no passes until the next run.
- Moon orbits cover only the moons with a SPICE kernel. Counts are checked against published totals, which are in the build script and may be out of date, since Jupiter and Saturn already list more moons than those totals. Moons without a name show as NAIF IDs.
- The moon data comes from JPL kernels. Orbits are computed at one epoch, so moons with poorly known orbits may drift from their true positions.
- Satellite photos come only from Wikimedia Commons and only for a short list of satellites. Other satellites keep the drawn icon.
- Starlink is off, because the full group makes the calculation too slow for a request.
- Time travel is limited to 7 days ahead, since predictions from current orbit data get less reliable further out.
- The bot posts at most once a day per place, and skips places where the sun is up.
- Bot charts are schematic. They show peak altitude and timing, not a real view of the sky.
- The sky chart and compass show stars from the bundled Yale catalogue to magnitude 6.5, not the full catalogue.
- Compass direction on phones without a magnetic compass must be set by tapping a known object, and it needs realigning after turning.
- The compass with a magnetic sensor is not yet tested on a phone that has one.
- Several browser features were checked on the server but not yet confirmed on every phone and browser. These include the moon panel zoom, the Voyager list, the orbit link from the tracker, and the Map height on phones.
- Globe and Map country borders are coarse, and small countries may be missed.
- Eclipse dates are approximate.
- Sighting explanations depend on Gemini's free-tier quota. When it runs out, explanations show an error until it resets.
- There is no email verification. Accounts created before recovery codes existed have no code, so the site owner resets their password with `reset_password.py`.
- Identification uses orbit data only. It can't confirm a satellite from a photo.

## Credits

- Satellite orbit data: CelesTrak.
- Planetary positions and moon orbits: NASA JPL DE421 and SPICE satellite kernels, public domain.
- Voyager distances: NASA JPL Horizons.
- Earth images, Image of the Day, and Astronomy Picture of the Day: NASA, public domain unless the picture's credit names another rights holder. Each card links to NASA's page.
- Satellite photos: Wikimedia Commons, each file under its own licence (public domain, CC0 or CC BY / CC BY-SA), with the artist credited on the page.
- Aurora forecast: NOAA Space Weather Prediction Center, OVATION model, public domain.
- Space weather: planetary Kp index from NOAA Space Weather Prediction Center, public domain.
- Country borders: Natural Earth, public domain.
- Sky conditions: weather forecast data from Open-Meteo, licensed under CC BY 4.0.
- Map tiles and data: OpenStreetMap contributors. Maps use Leaflet.
- Globe rendering: Three.js (MIT licence), loaded from cdnjs. Satellite positions use satellite.js (MIT licence), loaded from jsDelivr.
- Fonts: Fraunces and Atkinson Hyperlegible, from Google Fonts.
- Star data: Yale Bright Star Catalogue, public domain.

## Status

This is an early version, and it has not yet been tested with real users. The code is released under the MIT License. See the LICENSE file. Third-party data and images keep their own terms, as listed under Credits.
