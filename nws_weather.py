#!/usr/bin/env python3
"""
nws_weather.py - Fetch current weather from the US National Weather Service.

lovepup+ home-screen weather row. US-only (NWS covers 50 states + territories).
Free, no API key, public-domain data. Requires a User-Agent identifying the app.

Usage:
    python nws_weather.py                 # default: New York City
    python nws_weather.py 34.05 -118.24   # any US lat lon (Los Angeles)
    python nws_weather.py --json          # raw JSON for the backend

Two-step NWS flow:
    1. GET /points/{lat},{lon}  -> returns the forecast grid for that point
    2. GET the gridpoint hourly forecast -> current temp + conditions

The grid for a coordinate never changes, so a real backend should cache step 1
per location forever and cache step 2 for ~15-30 min. This script does neither -
it's a demo to get data instantly.
"""

import sys
import json
import urllib.request
import urllib.error

# NWS requires a User-Agent that identifies your app (email or domain).
# Without it you get HTTP 403. Change this to your real contact before shipping.
USER_AGENT = "lovepup-plus-weather/0.1 (koledanyk@gmail.com)"

TIMEOUT = 10  # seconds


def _get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def walk_phrase(temp_f, humidity_pct):
    """Derive the lovepup+ 'walk weather' line from raw data.

    Generic (no breed logic), gentle, non-medical - comfort talk, not diagnosis.
    NWS gives numbers, we give the friendly phrase; Ginger/backend owns this.
    High humidity bumps one band warmer (vet heat-index rule:
    temp F + humidity % >= 150 = ease off outdoor exercise).
    """
    if temp_f is None:
        return "Weather unavailable"

    band = temp_f
    if temp_f >= 70 and humidity_pct is not None and (temp_f + humidity_pct) >= 150:
        band = temp_f + 6

    if band >= 90:
        return "Real hot right now - maybe wait for a cooler hour, grass over pavement."
    if band >= 85:
        return "Toasty out. Keep it short, shady, and bring water."
    if band >= 73:
        return "Warm one - bring water and take the shady side."
    if temp_f >= 50:
        return "Good walk weather. Enjoy it!"
    if temp_f >= 35:
        return "Cool and fresh - nice for a brisk stroll."
    if temp_f >= 21:
        return "Chilly today. A shorter walk, and keep your pup snug."
    return "Cold out - make sure your pup stays cozy, and keep it quick."


def walk_phrase_short(temp_f, humidity_pct):
    """Compact one-line version for the home-screen row: "Good walk weather - Bring water".
    Temp is shown separately in the UI. Same bands as walk_phrase, terser copy.
    """
    if temp_f is None:
        return "-"
    band = temp_f
    if temp_f >= 70 and humidity_pct is not None and (temp_f + humidity_pct) >= 150:
        band = temp_f + 6
    if band >= 90:
        return "Too warm - wait for a cooler hour"
    if band >= 85:
        verdict = "Hot"
    elif band >= 73:
        verdict = "Warm"
    elif temp_f >= 50:
        verdict = "Good walk weather"
    elif temp_f >= 35:
        verdict = "Cool - nice for a stroll"
    elif temp_f >= 21:
        verdict = "Chilly - keep it short"
    else:
        verdict = "Cold - keep pup cozy"
    tags = [verdict]
    if temp_f >= 72:
        tags.append("Bring water")
    return " - ".join(tags)


def get_weather(lat, lon):
    # Step 1: resolve the coordinate to an NWS grid + forecast URLs
    point = _get(f"https://api.weather.gov/points/{lat},{lon}")
    props = point["properties"]
    hourly_url = props["forecastHourly"]
    loc = props.get("relativeLocation", {}).get("properties", {})
    place = f'{loc.get("city", "?")}, {loc.get("state", "?")}'

    # Step 2: current conditions = first period of the hourly forecast
    hourly = _get(hourly_url)
    now = hourly["properties"]["periods"][0]

    temp_f = now["temperature"] if now["temperatureUnit"] == "F" else round(now["temperature"] * 9 / 5 + 32)
    short = now["shortForecast"]
    wind_mph = None
    try:
        wind_mph = int(str(now.get("windSpeed", "")).split()[0])
    except (ValueError, IndexError):
        pass
    precip_pct = (now.get("probabilityOfPrecipitation") or {}).get("value") or 0
    humidity_pct = (now.get("relativeHumidity") or {}).get("value")

    return {
        "place": place,
        "lat": lat,
        "lon": lon,
        "temp_f": temp_f,
        "short_forecast": short,
        "wind_mph": wind_mph,
        "precip_pct": precip_pct,
        "humidity_pct": humidity_pct,
        "phrase": walk_phrase(temp_f, humidity_pct),
        "short_phrase": walk_phrase_short(temp_f, humidity_pct),
    }


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv

    lat, lon = ("40.7128", "-74.0060")  # default: NYC
    if len(args) >= 2:
        lat, lon = args[0], args[1]

    try:
        data = get_weather(lat, lon)
    except urllib.error.HTTPError as e:
        # 404 usually = coordinate outside NWS coverage (not US)
        hint = " (coordinate is likely outside the US - NWS is US-only)" if e.code == 404 else ""
        print(f"NWS error: HTTP {e.code}{hint}", file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"Network/NWS unavailable: {e}", file=sys.stderr)
        sys.exit(1)

    if as_json:
        print(json.dumps(data, indent=2))
    else:
        print(data["place"])
        print(f"HOME ROW:  {data['temp_f']} F - {data['short_phrase']}")
        print(f"CARD:      {data['phrase']}")
        print(f"({data['short_forecast']}, humidity {data['humidity_pct']}%, "
              f"wind {data['wind_mph']} mph, precip {data['precip_pct']}%)")


if __name__ == "__main__":
    main()
