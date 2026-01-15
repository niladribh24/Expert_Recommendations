import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", 5000))
    
    RAINFALL_THRESHOLD_MM = 5.0
    HIGH_TEMP_THRESHOLD_C = 38.0
    
    SMS_SENDER_ID = "AGRI-EXPERT"
