# VEMMSUNJ

VEMMSUNJ is a web app for sky-watchers. It lists observatories and dark-sky viewing spots on a map, shows when satellites pass over each place, and lets people post sightings. Gemini helps identify a sighting by matching the time and place against satellite orbit data.

## Features

- **Places:** observatories and dark-sky spots, with an add form.
- **Map:** Leaflet pins with the next passes in each popup.
- **Place pages:** a 24-hour strip showing each satellite pass above 10 degrees.
- **Sightings:** a feed of posts with an optional place and time. If both are given, the app checks which satellites were sunlit and above the horizon, and Gemini picks the most likely match from that list.
- **Accounts:** sign up, log in, follow people, and like sightings. Passwords are stored as salted hashes, and failed logins are rate-limited by username and IP address.
- **Light and dark themes**, with a switch in the header.

## How the identification works

1. The app downloads orbit data (TLEs) from CelesTrak for the stations, visual, and weather groups.
2. It checks whether the sun is more than 6 degrees below the horizon at the place, so the sky is dark enough to see satellites.
3. It keeps only satellites that are sunlit and above 10 degrees at that moment.
4. Gemini chooses the best match from that list only. It never names a satellite outside the list.

The app doesn't calculate brightness, so the AI is told not to describe how bright a satellite is.

## Run it locally

Requires Python 3.13 and a Postgres database, such as one from Neon.

    pip install flask requests skyfield sgp4 jplephem numpy pg8000 waitress

Set the environment variables, then start the app:

    export DATABASE_URL="postgresql://user:password@host/dbname"
    export GEMINI_API_KEY="your-key"
    HTTPS=0 python app.py

Open http://127.0.0.1:5000. Use HTTPS=0 only for local testing, since the session cookie is secure by default.

## Environment variables

| Name | Purpose |
| --- | --- |
| DATABASE_URL | Postgres connection string |
| GEMINI_API_KEY | Gemini API key for sighting explanations |
| SECRET_KEY | Signs session cookies. Generate a long random value. |
| HTTPS | Set to 0 only for local testing. Leave unset in production. |
| TRUST_PROXY | Set to 1 behind a reverse proxy, such as Vercel |
| STARLINK | Set to 1 to include the Starlink group. Very slow, so it's off by default. |

## Deploy on Vercel

The app runs as a Flask app on Vercel. Connect the GitHub repository in the Vercel project settings, set the environment variables above, and each push to the main branch deploys automatically.

## Known limits

- Passes are cached for an hour and limited to the next 100. The first calculation for a place can take close to a minute.
- Starlink is off, because the full group makes the calculation too slow for a serverless request.
- Sighting explanations depend on Gemini's free-tier quota. When it runs out, explanations show an error until it resets.
- There is no email verification and no password reset yet.
- Identification uses orbit data only. It can't confirm a satellite from a photo.

## Status

This is an early version. No license has been chosen yet.
