from datetime import date, timedelta

import httpx

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def get_forecast(city: str, start_date: str, end_date: str) -> dict:
    # Open-Meteo forecasts only ~16 days ahead
    last_day = (date.today() + timedelta(days=15)).isoformat()
    if start_date > last_day:
        return {"error": f"No forecast available yet: forecasts only go up to {last_day}."}

    try:
        # 1. City -> coordinates
        geo = httpx.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10).json()
        if not geo.get("results"):
            return {"error": f"Destination '{city}' not found."}
        place = geo["results"][0]

        # 2. Coordinates + dates -> daily forecast
        r = httpx.get(FORECAST_URL, params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "daily": "temperature_2m_max,temperature_2m_min,"
                     "precipitation_sum,precipitation_probability_max",
            "timezone": "auto",
            "start_date": start_date,
            "end_date": min(end_date, last_day),
        }, timeout=10)
        r.raise_for_status()
        daily = r.json()["daily"]
    except Exception as e:
        return {"error": f"Weather service unavailable: {e}"}

    return {"location": f"{place['name']}, {place.get('country', '')}", "daily": daily}
