# Deploy (Coolify)

The page is a client-side app for the weather logic. A tiny Node server (`server.js`) serves it and keeps the reading history in Cloudflare D1, so history is central and survives reloads, redeploys, and different browsers. No framework, no dependencies (Node's built-in `http` + `fetch`).

## Steps

1. Coolify: the `weather` app already exists (repo `github.com/koledanyk/weather`, branch `main`, Dockerfile build, port `80`, domain `weather.looksfine.work`).
2. Set environment variables on the app:
   - `GOOGLE_MAPS_API_KEY` - Google Places key (optional; injected into the page at startup). Empty = free Open-Meteo geocoder.
   - `CF_ACCOUNT_ID` - your Cloudflare account id (dashboard sidebar, or the D1 page URL).
   - `D1_DATABASE_ID` - `0feaaf72-d590-4b0a-98b3-22c6d170e6b6` (the `lovepup-weather-history` database).
   - `CF_API_TOKEN` - a Cloudflare API token with **D1 Edit** permission. Server-only, never reaches the browser.
3. Redeploy.

If the three D1 vars are missing, the API returns empty and the page falls back to the browser's localStorage history, so nothing breaks before the token is set.

## API

- `GET /api/history` - returns the reading log (oldest first) from D1.
- `POST /api/log` - `{ t, text, place }`, inserts one reading.
- `GET /api/health` - `{ ok, d1 }` (whether D1 is configured).

## Database

D1 `lovepup-weather-history`, table `readings (id, ts, text, place, created_at)`. Created and indexed on `ts`.

## Notes

- NWS covers the US only. Coordinates outside the US show the "No weather nearby. On Pluto?" state.
- The demo polls every 5 minutes. Manual Refresh logs a reading immediately.
- The Google key is injected by `server.js` at startup (this replaces the old `inject-key.sh`, which is no longer used).
