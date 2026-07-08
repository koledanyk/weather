# Deploy (Coolify)

This page is a client-side app: the script and all API calls (NWS, geocoder, Google Places) run in the visitor's browser. It ships as a static site — nginx serves one HTML file. There is no backend.

## Steps

1. Coolify: New Resource → Git → repo `github.com/koledanyk/weather`, branch `main`.
2. Build pack: Dockerfile (Coolify auto-detects the `Dockerfile` in the repo root).
3. Port: `80`.
4. Domain: `weather.looksfine.work` (Coolify issues the HTTPS certificate).
5. Environment variable (only needed for Google Places):
   - `GOOGLE_MAPS_API_KEY` = your key.
   - In Google Cloud, restrict the key to referrer `https://weather.looksfine.work/*` and to the Maps JavaScript API + Places API.
   - Leave it unset to run on the free Open-Meteo geocoder instead.
6. Deploy.

The key is injected into `index.html` at container start from the env var (see `inject-key.sh`), so it is never committed to this public repo.

## Notes

- NWS covers the US only. Coordinates outside the US return no weather.
- Weather auto-updates every 15 minutes, in the browser.
- Default city is Austin, Texas.
