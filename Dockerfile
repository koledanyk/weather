# Small Node server for the lovepup+ weather demo.
# Serves index.html and a tiny history API backed by Cloudflare D1.
# No backend framework, no dependencies - just Node's built-in http + fetch.
#
# Secrets and config come from Coolify environment variables:
#   GOOGLE_MAPS_API_KEY   - injected into the page at startup (optional)
#   CF_ACCOUNT_ID         - Cloudflare account id (for D1)
#   D1_DATABASE_ID        - the weather-history D1 database id
#   CF_API_TOKEN          - Cloudflare API token with D1 edit (server-only)
# If the D1 vars are missing, history falls back to the browser's localStorage.
FROM node:20-alpine

WORKDIR /app
COPY index.html server.js ./

EXPOSE 80
CMD ["node", "server.js"]
