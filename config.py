"""
Configuration management for the Agriculture Expert Recommendation System.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenWeather API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    # Flask
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", 5000))
    
    # Advisory Thresholds
    RAINFALL_THRESHOLD_MM = 5.0  # Skip irrigation if rainfall exceeds this
    HIGH_TEMP_THRESHOLD_C = 38.0  # Advise early irrigation above this temperature
    
    # SMS Configuration (dummy)
    SMS_SENDER_ID = "AGRI-EXPERT"
