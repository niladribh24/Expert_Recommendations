"""
Agriculture Expert Recommendation System - Flask Backend

A weather-based advisory system for Indian farmers that provides:
- Weather-based irrigation advisories
- Seasonal crop recommendations (Kharif, Rabi, Zaid)
- Weekly market price alerts
- Simulated SMS delivery

All advisories are generated using rule-based logic.
"""
from flask import Flask, request, jsonify
from services import WeatherService, AdvisoryService, SMSService, SeasonalService, MarketService
from config import Config


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize all services
weather_service = WeatherService()
advisory_service = AdvisoryService()
sms_service = SMSService()
seasonal_service = SeasonalService()
market_service = MarketService()


# ============================================
# Health Check Endpoint
# ============================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        "status": "healthy",
        "service": "Agriculture Expert Recommendation System",
        "version": "2.0.0",
        "api_key_configured": bool(Config.OPENWEATHER_API_KEY),
        "endpoints": [
            "/weather-advisory",
            "/seasonal-advisory",
            "/price-advisory",
            "/send-sms"
        ]
    })


# ============================================
# Weather Advisory Endpoint
# ============================================

@app.route("/weather-advisory", methods=["GET"])
def weather_advisory():
    """
    Get weather-based irrigation advisory.
    
    Query Parameters:
        location: City name or 6-digit Indian pincode (required)
        lang: Language preference ('en' or 'hi'), default: 'en'
        send_sms: Phone number to send SMS (optional)
        
    Example:
        GET /weather-advisory?location=Nagpur&lang=hi
        GET /weather-advisory?location=440001&send_sms=9876543210
    """
    location = request.args.get("location", "").strip()
    language = request.args.get("lang", "en").lower()
    send_sms_to = request.args.get("send_sms", "").strip()
    
    # Validate location
    if not location:
        return jsonify({
            "success": False,
            "error": "Missing required parameter: location. Provide a city name or pincode."
        }), 400
    
    if language not in ["en", "hi"]:
        language = "en"
    
    # Get weather data
    weather_data = weather_service.get_weather(location)
    
    if not weather_data.get("success"):
        return jsonify(weather_data), 400
    
    # Generate advisory using rule-based logic
    advisory = advisory_service.generate_advisory(weather_data)
    
    # Build response
    response = {
        "success": True,
        "location": location,
        "city": weather_data.get("city"),
        "weather": {
            "temperature": weather_data.get("temperature"),
            "feels_like": weather_data.get("feels_like"),
            "humidity": weather_data.get("humidity"),
            "rainfall": weather_data.get("rainfall"),
            "wind_speed": weather_data.get("wind_speed"),
            "description": weather_data.get("description")
        },
        "advisory": {
            "type": advisory.get("advisory_type"),
            "message": advisory.get(f"message_{language}"),
            "language": language,
            "thresholds": advisory.get("conditions", {})
        }
    }
    
    # If SMS requested, send it via dummy gateway
    if send_sms_to:
        message = advisory.get(f"message_{language}")
        sms_result = sms_service.send_sms(send_sms_to, message, language)
        response["sms_status"] = sms_result
    
    return jsonify(response)


# ============================================
# Seasonal Crop Advisory Endpoint
# ============================================

@app.route("/seasonal-advisory", methods=["GET"])
def seasonal_advisory():
    """
    Get seasonal crop recommendation advisory.
    
    Determines current agricultural season (Kharif/Rabi/Zaid) and
    recommends suitable crops for planting.
    
    Query Parameters:
        month: Month number 1-12 (optional, defaults to current month)
        lang: Language preference ('en' or 'hi'), default: 'en'
        send_sms: Phone number to send SMS (optional)
        
    Example:
        GET /seasonal-advisory
        GET /seasonal-advisory?month=7&lang=hi
    """
    month_str = request.args.get("month", "").strip()
    language = request.args.get("lang", "en").lower()
    send_sms_to = request.args.get("send_sms", "").strip()
    
    # Parse month if provided
    month = None
    if month_str:
        try:
            month = int(month_str)
            if not 1 <= month <= 12:
                return jsonify({
                    "success": False,
                    "error": "Month must be between 1 and 12."
                }), 400
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Month must be a number between 1 and 12."
            }), 400
    
    if language not in ["en", "hi"]:
        language = "en"
    
    # Get seasonal advisory
    advisory = seasonal_service.get_seasonal_advisory(month=month, lang=language)
    
    if not advisory.get("success"):
        return jsonify(advisory), 400
    
    response = {
        "success": True,
        "current_month": advisory.get("month"),
        "season": advisory.get("season"),
        "season_name": advisory.get("season_name"),
        "planting_period": advisory.get("planting_period"),
        "harvesting_period": advisory.get("harvesting_period"),
        "recommended_crops": advisory.get("recommended_crops"),
        "message": advisory.get("message"),
        "language": language
    }
    
    # If SMS requested, send it via dummy gateway
    if send_sms_to:
        sms_result = sms_service.send_sms(send_sms_to, advisory.get("message"), language)
        response["sms_status"] = sms_result
    
    return jsonify(response)


# ============================================
# Market Price Advisory Endpoint
# ============================================

@app.route("/price-advisory", methods=["GET"])
def price_advisory():
    """
    Get weekly market price advisory.
    
    Compares current vs previous week prices and provides trend analysis.
    Includes MSP (Minimum Support Price) comparisons.
    
    Query Parameters:
        crops: Comma-separated crop names to filter (optional)
        lang: Language preference ('en' or 'hi'), default: 'en'
        send_sms: Phone number to send SMS (optional)
        
    Example:
        GET /price-advisory
        GET /price-advisory?crops=Rice,Wheat&lang=hi
    """
    crops_str = request.args.get("crops", "").strip()
    language = request.args.get("lang", "en").lower()
    send_sms_to = request.args.get("send_sms", "").strip()
    
    # Parse crops list if provided
    crops = None
    if crops_str:
        crops = [c.strip() for c in crops_str.split(",") if c.strip()]
    
    if language not in ["en", "hi"]:
        language = "en"
    
    # Get market advisory
    advisory = market_service.get_price_advisory(crops=crops, lang=language)
    
    if not advisory.get("success"):
        return jsonify(advisory), 400
    
    response = {
        "success": True,
        "last_updated": advisory.get("last_updated"),
        "total_crops": advisory.get("total_crops"),
        "top_gainers": advisory.get("top_gainers"),
        "top_losers": advisory.get("top_losers"),
        "all_prices": advisory.get("all_prices"),
        "message": advisory.get("message"),
        "language": language
    }
    
    # If SMS requested, send it via dummy gateway
    if send_sms_to:
        sms_result = sms_service.send_sms(send_sms_to, advisory.get("message"), language)
        response["sms_status"] = sms_result
    
    return jsonify(response)


# ============================================
# Dummy SMS Gateway Endpoint
# ============================================

@app.route("/send-sms", methods=["POST"])
def send_sms():
    """
    Dummy SMS gateway endpoint.
    
    Simulates sending SMS messages. Does NOT send real SMS.
    All messages are logged and stored in memory for demonstration.
    
    Request Body (JSON):
        phone: Recipient phone number (Indian format: +91XXXXXXXXXX or 10 digits)
        message: Message content to send
        
    Example:
        POST /send-sms
        Content-Type: application/json
        
        {
            "phone": "+919876543210",
            "message": "Your advisory message here"
        }
        
    Response:
        {
            "status": "SENT",
            "delivery": "SIMULATED",
            "message_id": "uuid",
            "timestamp": "ISO format"
        }
    """
    data = request.get_json() or {}
    
    phone = data.get("phone", "").strip()
    message = data.get("message", "").strip()
    
    # Validate required fields
    if not phone:
        return jsonify({
            "success": False,
            "error": "Missing required field: phone"
        }), 400
    
    if not message:
        return jsonify({
            "success": False,
            "error": "Missing required field: message"
        }), 400
    
    # Send via dummy SMS service
    result = sms_service.send_sms(phone, message)
    
    if result.get("success"):
        return jsonify({
            "status": "SENT",
            "delivery": "SIMULATED",
            "message_id": result.get("message_id"),
            "phone": result.get("phone_number"),
            "timestamp": result.get("timestamp"),
            "note": "This is a dummy SMS. No real message was sent."
        })
    else:
        return jsonify({
            "status": "FAILED",
            "error": result.get("error")
        }), 400


# ============================================
# SMS History Endpoints (for demonstration)
# ============================================

@app.route("/api/sms/history", methods=["GET"])
def get_sms_history():
    """Get history of sent SMS messages (for demonstration)."""
    limit = request.args.get("limit", 50, type=int)
    phone = request.args.get("phone", "").strip()
    
    if phone:
        messages = sms_service.get_messages_by_phone(phone)
    else:
        messages = sms_service.get_message_history(limit)
    
    return jsonify({
        "success": True,
        "count": len(messages),
        "messages": messages
    })


# ============================================
# Legacy Endpoints (backward compatibility)
# ============================================

@app.route("/api/weather", methods=["GET"])
def get_weather():
    """Get current weather for a location (legacy endpoint)."""
    location = request.args.get("location", "").strip()
    
    if not location:
        return jsonify({
            "success": False,
            "error": "Missing required parameter: location."
        }), 400
    
    weather_data = weather_service.get_weather(location)
    return jsonify(weather_data) if weather_data.get("success") else (jsonify(weather_data), 400)


@app.route("/api/advisory", methods=["GET"])
def get_advisory():
    """Get weather advisory (legacy endpoint - redirects to /weather-advisory)."""
    return weather_advisory()


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found.",
        "available_endpoints": [
            "GET /weather-advisory?location=<city_or_pincode>&lang=<en|hi>",
            "GET /seasonal-advisory?month=<1-12>&lang=<en|hi>",
            "GET /price-advisory?crops=<comma_separated>&lang=<en|hi>",
            "POST /send-sms (body: {phone, message})"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error. Please try again later."
    }), 500


# ============================================
# Run Application
# ============================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌾 Agriculture Expert Recommendation System v2.0")
    print("="*60)
    print(f"Server running on: http://localhost:{Config.PORT}")
    print(f"Debug mode: {'ON' if Config.DEBUG else 'OFF'}")
    print(f"OpenWeather API: {'Configured ✓' if Config.OPENWEATHER_API_KEY else 'NOT CONFIGURED ✗'}")
    print("-"*60)
    print("Available Endpoints:")
    print("  GET  /weather-advisory   - Weather-based irrigation advice")
    print("  GET  /seasonal-advisory  - Seasonal crop recommendations")
    print("  GET  /price-advisory     - Weekly market price trends")
    print("  POST /send-sms           - Dummy SMS gateway")
    print("="*60 + "\n")
    
    if not Config.OPENWEATHER_API_KEY:
        print("⚠️  WARNING: OpenWeather API key not set!")
        print("   Set OPENWEATHER_API_KEY in your .env file\n")
    
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG
    )
