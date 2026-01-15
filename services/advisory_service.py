from config import Config


class AdvisoryService:
    
    ADVISORIES = {
        "no_irrigation": {
            "en": "Do not irrigate today. Rainfall is expected or has occurred. Save water and let nature do the work!",
            "hi": "आज सिंचाई न करें। बारिश हो रही है या होने की संभावना है। पानी बचाएं!"
        },
        "early_irrigation": {
            "en": "High temperature alert! Irrigate early morning (before 8 AM) to reduce water loss from evaporation.",
            "hi": "तापमान अधिक है! सुबह जल्दी (8 बजे से पहले) सिंचाई करें ताकि पानी वाष्पीकरण से बर्बाद न हो।"
        },
        "normal": {
            "en": "Weather conditions are favorable. You may irrigate as per your normal schedule.",
            "hi": "मौसम अनुकूल है। आप अपने सामान्य समय पर सिंचाई कर सकते हैं।"
        }
    }
    
    def __init__(self):
        self.rainfall_threshold = Config.RAINFALL_THRESHOLD_MM
        self.high_temp_threshold = Config.HIGH_TEMP_THRESHOLD_C
    
    def generate_advisory(self, weather_data: dict) -> dict:
        if not weather_data.get("success"):
            return {
                "success": False,
                "error": weather_data.get("error", "Weather data not available")
            }
        
        temperature = weather_data.get("temperature", 0)
        rainfall = weather_data.get("rainfall", 0)
        humidity = weather_data.get("humidity", 0)
        
        advisory_type = self._determine_advisory_type(temperature, rainfall)
        
        message = self._generate_personalized_message(
            advisory_type=advisory_type,
            city=weather_data.get("city", "your area"),
            temperature=temperature,
            rainfall=rainfall,
            humidity=humidity
        )
        
        return {
            "success": True,
            "advisory_type": advisory_type,
            "message_en": message["en"],
            "message_hi": message["hi"],
            "conditions": {
                "temperature": temperature,
                "rainfall": rainfall,
                "humidity": humidity,
                "rainfall_threshold": self.rainfall_threshold,
                "temp_threshold": self.high_temp_threshold
            }
        }
    
    def _determine_advisory_type(self, temperature: float, rainfall: float) -> str:
        if rainfall > self.rainfall_threshold:
            return "no_irrigation"
        elif temperature > self.high_temp_threshold:
            return "early_irrigation"
        else:
            return "normal"
    
    def _generate_personalized_message(self, advisory_type: str, city: str, temperature: float, rainfall: float, humidity: float) -> dict:
        base_advisory = self.ADVISORIES.get(advisory_type, self.ADVISORIES["normal"])
        
        if advisory_type == "no_irrigation":
            message_en = (
                f"🌧️ Rain Alert for {city}!\n"
                f"Rainfall: {rainfall}mm | Temp: {temperature}°C | Humidity: {humidity}%\n\n"
                f"{base_advisory['en']}"
            )
            message_hi = (
                f"🌧️ {city} में बारिश की सूचना!\n"
                f"वर्षा: {rainfall}mm | तापमान: {temperature}°C | नमी: {humidity}%\n\n"
                f"{base_advisory['hi']}"
            )
        elif advisory_type == "early_irrigation":
            message_en = (
                f"🌡️ Heat Alert for {city}!\n"
                f"Temperature: {temperature}°C | Humidity: {humidity}%\n\n"
                f"{base_advisory['en']}"
            )
            message_hi = (
                f"🌡️ {city} में गर्मी की चेतावनी!\n"
                f"तापमान: {temperature}°C | नमी: {humidity}%\n\n"
                f"{base_advisory['hi']}"
            )
        else:
            message_en = (
                f"✅ Weather Update for {city}\n"
                f"Temp: {temperature}°C | Humidity: {humidity}%\n\n"
                f"{base_advisory['en']}"
            )
            message_hi = (
                f"✅ {city} का मौसम अपडेट\n"
                f"तापमान: {temperature}°C | नमी: {humidity}%\n\n"
                f"{base_advisory['hi']}"
            )
        
        return {"en": message_en, "hi": message_hi}
