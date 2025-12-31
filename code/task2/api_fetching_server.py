import sys
import json
import requests
from datetime import datetime
# FastMCP Import
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("api-fetching-mcp-server")


@mcp.tool()
def fetch_weather(city: str, unit: str = "celsius") -> str:
    """
    Fetch current weather for ANY city using Open-Meteo.
    
    Args:
        city: Name of the city to fetch weather for
        unit: Temperature unit - 'celsius' or 'fahrenheit'
    
    Returns:
        JSON string containing weather data and API metadata
    """
    try:
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
            return json.dumps({"error": f"City '{city}' not found"})

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

        result = {
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
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error fetching weather: {str(e)}"})


@mcp.tool()
def fetch_exchange_rate(base: str, target: str) -> str:
    """
    Fetch latest exchange rate for a currency pair.
    
    Args:
        base: Base currency code (e.g., 'USD', 'EUR')
        target: Target currency code (e.g., 'GBP', 'JPY')
    
    Returns:
        JSON string containing exchange rate and API metadata
    """
    try:
        url = "https://api.frankfurter.app/latest"
        params = {
            "from": base.upper(),
            "to": target.upper()
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        result = {
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
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error fetching exchange rate: {str(e)}"})



if __name__ == "__main__":
    print("Launching FastMCP Server via stdio...", file=sys.stderr)
    mcp.run()
