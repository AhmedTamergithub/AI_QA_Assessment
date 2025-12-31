import requests
from datetime import datetime

def fetch_weather(city: str, unit: str = "celsius") -> dict:
    """
    Fetch current weather for ANY city using Open-Meteo.
    """
     
    # Step 1: Geocoding (city -> lat/lon)
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": city,
        "count": 1
    }

    geo_response = requests.get(geo_url, params=geo_params)
    geo_response.raise_for_status()
    geo_data = geo_response.json()

    if "results" not in geo_data or len(geo_data["results"]) == 0:
        raise ValueError(f"City '{city}' not found")

    location = geo_data["results"][0]
    latitude = location["latitude"]
    longitude = location["longitude"]
    resolved_name = f"{location['name']}, {location.get('country', '')}"

    # Step 2: Weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    }

    weather_response = requests.get(weather_url, params=weather_params)
    weather_response.raise_for_status()
    weather_data = weather_response.json()
  
    current = weather_data["current_weather"]

    return {
        "weather": {
            "city": resolved_name,
            "temperature": current["temperature"],
            "wind_speed": current["windspeed"],
            "weather_code": current["weathercode"],
            "unit": unit
        },
        "api_metadata": {
            "provider": "Open-Meteo",
            "geocoding_endpoint": geo_url,
            "weather_endpoint": weather_url,
            "timestamp": datetime.utcnow().isoformat()
        }
    }



def fetch_exchange_rate(base: str, target: str) -> dict:
    """
    Fetch latest exchange rate for a currency pair.
    """

    url = "https://api.frankfurter.app/latest"
    params = {
        "from": base.upper(),
        "to": target.upper()
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return {
        "exchange_rate": {
            "base": base.upper(),
            "target": target.upper(),
            "rate": data["rates"][target.upper()]
        },
        "api_metadata": {
            "provider": "Frankfurter",
            "endpoint": url,
            "params": params,
            "date": data["date"],
            "timestamp": datetime.utcnow().isoformat()
        }
    }

