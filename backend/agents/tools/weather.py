"""Weather tool - MCP-style tool for getting weather information"""
from typing import Dict, Any, Optional
import requests
import os
from datetime import datetime


def get_weather_for_location(location: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get weather information for a location
    
    Args:
        location: Location (address, city, or coordinates as "lat,lng")
        date: Optional date for weather forecast (format: "YYYY-MM-DD"). Default: current weather
        
    Returns:
        Dictionary with weather data (temperature, conditions, precipitation, etc.)
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    if not api_key:
        return {
            "error": "OPENWEATHER_API_KEY not set. Please set it in your .env file.",
            "location": location
        }
    
    try:
        # Check if location is coordinates (lat,lng format)
        if "," in location and len(location.split(",")) == 2:
            try:
                lat, lng = map(float, location.split(","))
                lat_param = lat
                lng_param = lng
            except ValueError:
                # Not valid coordinates, treat as city name
                lat_param = None
                lng_param = None
                city_param = location
        else:
            lat_param = None
            lng_param = None
            city_param = location
        
        if lat_param is not None and lng_param is not None:
            # Use coordinates
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": lat_param,
                "lon": lng_param,
                "appid": api_key,
                "units": "imperial"  # Use Fahrenheit
            }
        else:
            # Use city name
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city_param,
                "appid": api_key,
                "units": "imperial"
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        weather_info = {
            "location": data.get("name", location),
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "condition": data.get("weather", [{}])[0].get("main", "").lower() if data.get("weather") else None,
            "description": data.get("weather", [{}])[0].get("description", "") if data.get("weather") else None,
            "humidity": data.get("main", {}).get("humidity"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "precipitation": data.get("rain", {}).get("1h", 0) if data.get("rain") else 0,
            "clouds": data.get("clouds", {}).get("all", 0),
            "timestamp": datetime.now().isoformat(),
            "date": date or datetime.now().strftime("%Y-%m-%d")
        }
        
        condition = weather_info.get("condition", "")
        temp = weather_info.get("temperature")
        if temp and condition:
            if condition in ["clear", "clouds"] and 60 <= temp <= 85:
                weather_info["outdoor_suitable"] = True
                weather_info["outdoor_recommendation"] = "Great weather for outdoor activities!"
            elif condition in ["rain", "drizzle", "thunderstorm"]:
                weather_info["outdoor_suitable"] = False
                weather_info["outdoor_recommendation"] = "Rainy weather - consider indoor activities"
            elif temp < 50:
                weather_info["outdoor_suitable"] = False
                weather_info["outdoor_recommendation"] = "Cold weather - dress warmly or choose indoor activities"
            elif temp > 90:
                weather_info["outdoor_suitable"] = False
                weather_info["outdoor_recommendation"] = "Hot weather - stay hydrated or choose indoor activities"
            else:
                weather_info["outdoor_suitable"] = True
                weather_info["outdoor_recommendation"] = "Weather is okay for outdoor activities"
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Failed to fetch weather data: {str(e)}",
            "location": location
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "location": location
        }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_weather_for_location",
        "description": "Get current weather information for a location. Useful for determining if outdoor activities are suitable.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location (address, city name, or coordinates as 'lat,lng')"
                },
                "date": {
                    "type": "string",
                    "description": "Optional date for weather forecast (format: 'YYYY-MM-DD'). Default: current weather"
                }
            },
            "required": ["location"]
        }
    }
}

