#!/bin/sh
# Inject the Google Maps key into index.html at container start.
# If GOOGLE_MAPS_API_KEY is not set, the page keeps its empty key and falls back
# to the free Open-Meteo geocoder. Runs automatically via nginx:alpine's
# /docker-entrypoint.d hook, before nginx starts.
set -e

INDEX=/usr/share/nginx/html/index.html

if [ -n "${GOOGLE_MAPS_API_KEY:-}" ]; then
  sed -i "s|const GOOGLE_MAPS_API_KEY = \"\";|const GOOGLE_MAPS_API_KEY = \"${GOOGLE_MAPS_API_KEY}\";|" "$INDEX"
  echo "inject-key: Google Maps key injected."
else
  echo "inject-key: no GOOGLE_MAPS_API_KEY set — using the free geocoder fallback."
fi
