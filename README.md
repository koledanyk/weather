# weather

Weather for the lovepup+ home-screen row, using the US National Weather Service (NWS) API. US-only, free, no API key.

Two pieces:

- `index.html` — standalone browser page. Pick a US city, get live temperature, humidity, wind, precipitation, conditions, last-updated time, and a friendly "walk weather" line. Open it directly, no server needed.
- `nws_weather.py` — command-line version of the same logic. Prints the home-screen row plus a longer card line, or raw JSON for a backend.

## Run the page

Open `index.html` in a browser.

## Run the script

```
python nws_weather.py                 # New York City (default)
python nws_weather.py 34.05 -118.24   # any US lat/lon (Los Angeles)
python nws_weather.py 41.88 -87.63 --json   # raw JSON
```

## How it works

NWS uses a two-step flow: `GET /points/{lat},{lon}` returns a forecast grid for that coordinate, then a second request to the returned hourly-forecast URL gives current conditions. The grid never changes for a coordinate, so a real backend should cache it permanently and cache the forecast for ~15–30 minutes.

NWS requires a `User-Agent` header identifying the app or it returns HTTP 403. The script sets one explicitly; the browser page relies on the browser's own User-Agent (JavaScript cannot set that header).

## Walk-weather logic

The "walk weather" line is derived on our side from temperature and humidity — it is not from NWS. It is intentionally generic (no breed logic), gentle, and non-medical: comfort suggestions, not diagnosis. High humidity nudges the phrasing one band warmer, following the common vet rule that temperature (°F) + humidity (%) at or above 150 means easing off outdoor exercise.

| Temp (°F) | Short line |
|-----------|------------|
| ≤ 20 | Cold · keep pup cozy |
| 21–34 | Chilly · keep it short |
| 35–49 | Cool · nice for a stroll |
| 50–71 | Good walk weather |
| 72 | Good walk weather · Bring water |
| 73–84 | Warm · Bring water |
| 85–89 | Hot · Bring water |
| ≥ 90 (or heat index) | Too warm · wait for a cooler hour |

## Notes

NWS covers only the US and its territories. Coordinates outside the US return HTTP 404. NWS is a public-domain government service with no uptime guarantee, so any integration should degrade gracefully (hide the row or show the last cached value) when it is unavailable.
