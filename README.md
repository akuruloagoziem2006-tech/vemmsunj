# VEMMSUNJ

VEMMSUNJ is a sky-watching map for observatories, satellite passes, and sightings. It lists observatories and dark-sky viewing spots, shows when satellites pass over each place, and lets people log what they saw. When a sighting includes a place and time, the app checks which satellites were sunlit and above the horizon, and Gemini picks the most likely match from that list.

## Features

- **Places:** observatories and dark-sky spots, with an add form.
- **Place pages:** a 24-hour strip showing each satellite pass above 10 degrees, with the next pass highlighted.
- **Map:** Leaflet pins. Each popup lists the next passes and links to the place page.
- **Sightings:** a logbook-style feed. Each entry has an optional place and time, and the AI explanation appears under a red rule.
- **Recent sightings:** the Places page ends with the five latest posts, so new visitors see activity right away.
- **Daily bot:** VEMMSUNJ_BOT posts once a day for each place that has passes in the next 24 hours. Each post includes a schematic chart. Every bot post is labeled "Automated."
- **Example posts:** three sightings by the VEMMSUNJ account are labeled "Example" so the feed isn't empty.
- **Accounts:** sign up, log in, follow people, and like sightings. Passwords are stored as salted hashes. Failed logins are rate-limited by username and by IP address.
- **Reserved names:** usernames starting with VEMMSUNJ are reserved for the app's own accounts.
- **Dark theme:** the app uses one dark theme, since it's mostly used outdoors at night. A row of planets runs under the header.

## How identification works

1. The app downloads orbit data (TLEs) from CelesTrak for the stations, visual, and weather groups.
2. It checks whether the sun is more than 6 degrees below the horizon at the place, so the sky is dark enough to see satellites.
3. It keeps only satellites that are sunlit and above 10 degrees at that moment.
4. Gemini chooses the best match from that list only. It never names a satellite outside the list.

The app doesn't calculate brightness, so the AI is told not to describe how bright a satellite is.

## How the daily bot works

Vercel calls `/api/cron/daily` once a day at 03:00 UTC. The bot does the following for each place:

1. Skips the place if the sun is still up there, or if it already posted there today.
2. Takes the next three passes in the next 24 hours from the same orbit data the place pages use.
3. Posts a summary with the satellite names, times in UTC, and peak altitudes.
4. Adds a schematic chart. The arcs show peak altitude and are not a real view of the sky.

The endpoint requires a bearer token set in `CRON_SECRET`, so only Vercel or someone with the secret can trigger it.

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
| CRON_SECRET | Bearer token that protects the daily bot endpoint |
| HTTPS | Set to 0 only for local testing. Leave unset in production. |
| TRUST_PROXY | Set to 1 behind a reverse proxy, such as Vercel |
| STARLINK | Set to 1 to include the Starlink group. Very slow, so it's off by default. |

## Deploy on Vercel

The app runs as a Flask app on Vercel. Connect the GitHub repository in the Vercel project settings, set the environment variables above, and each push to the main branch deploys automatically. The daily schedule is defined in `vercel.json`.

## Known limits

- Passes are cached for an hour and limited to the next 100. The first calculation for a place can take close to a minute.
- Starlink is off, because the full group makes the calculation too slow for a serverless request.
- The bot posts at most once a day per place, and skips places where the sun is up.
- Bot charts are schematic. They show peak altitude and timing, not a real view of the sky.
- Sighting explanations depend on Gemini's free-tier quota. When it runs out, explanations show an error until it resets.
- There is no email verification and no password reset yet.
- Identification uses orbit data only. It can't confirm a satellite from a photo.

## Status

This is an early version. No license has been chosen yet.
