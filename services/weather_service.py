"""
Weather Service - Fetches live weather data from OpenWeather API.
"""
import json
import os
import requests
from typing import Optional
from config import Config


class WeatherService:
    """Service for fetching weather data from OpenWeather API."""
    
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.OPENWEATHER_BASE_URL
        self.pincode_mapping = self._load_pincode_mapping()
    
    def _load_pincode_mapping(self) -> dict:
        """Load pincode to city mapping from JSON file."""
        mapping_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "pincode_mapping.json"
        )
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _resolve_location(self, location: str) -> str:
        """
        Resolve location input to a city name.
        Accepts either a city name or a pincode.
        """
        # Check if it's a pincode (6 digits)
        if location.isdigit() and len(location) == 6:
            city = self.pincode_mapping.get(location)
            if city:
                return city
            # If pincode not found, try using it directly
            return location
        return location
    
    def get_weather(self, location: str) -> dict:
        """
        Fetch weather data for a given city or pincode.
        
        Args:
            location: City name or 6-digit Indian pincode
            
        Returns:
            dict with weather data or error information
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "OpenWeather API key not configured. Set OPENWEATHER_API_KEY in .env file."
            }
        
        city = self._resolve_location(location)
        
        try:
            params = {
                "q": f"{city},IN",  # Restrict to India
                "appid": self.api_key,
                "units": "metric"  # Celsius
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_response(data, location)
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid OpenWeather API key."
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Location '{location}' not found. Please check the city name or pincode."
                }
            else:
                return {
                    "success": False,
                    "error": f"Weather API error: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Weather service timeout. Please try again."
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to fetch weather data: {str(e)}"
            }
    
    def _parse_weather_response(self, data: dict, original_location: str) -> dict:
        """Parse OpenWeather API response into our format."""
        # Extract rainfall (may not be present)
        rainfall = 0.0
        if "rain" in data:
            # rain.1h = rainfall in last 1 hour (mm)
            rainfall = data["rain"].get("1h", data["rain"].get("3h", 0.0))
        
        return {
            "success": True,
            "location": original_location,
            "city": data.get("name", "Unknown"),
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "humidity": data["main"]["humidity"],
            "rainfall": round(rainfall, 1),
            "description": data["weather"][0]["description"] if data.get("weather") else "Unknown",
            "wind_speed": round(data.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s to km/h
        }
