# Static deploy for the lovepup+ weather page.
# The page is a client-side app: all logic and API calls run in the browser.
# nginx just serves index.html. No backend.
#
# The Google Maps key is injected at container start from the GOOGLE_MAPS_API_KEY
# env var (set in Coolify), so the key stays out of the public git repo.
FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html

# Runs before nginx starts (nginx:alpine executes /docker-entrypoint.d/*.sh).
COPY inject-key.sh /docker-entrypoint.d/40-inject-key.sh
RUN chmod +x /docker-entrypoint.d/40-inject-key.sh

EXPOSE 80
