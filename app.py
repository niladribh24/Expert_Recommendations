from flask import Flask, request, jsonify
from services import WeatherService, AdvisoryService, SMSService, SeasonalService, MarketService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

weather_service = WeatherService()
advisory_service = AdvisoryService()
sms_service = SMSService()
seasonal_service = SeasonalService()
market_service = MarketService()


@app.route("/api/health", methods=["GET"])
def health_check():
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


@app.route("/weather-advisory", methods=["GET"])
def weather_advisory():
    location = request.args.get("location", "").strip()
    language = request.args.get("lang", "en").lower()
    send_sms_to = request.args.get("send_sms", "").strip()
    
    if not location:
        return jsonify({
            "success": False,
            "error": "Missing required parameter: location. Provide a city name or pincode."
        }), 400
    
    if language not in ["en", "hi"]:
        language = "en"
    
    weather_data = weather_service.get_weather(location)
    
    if not weather_data.get("success"):
        return jsonify(weather_data), 400
    
    advisory = advisory_service.generate_advisory(weather_data)
    
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
    
    if send_sms_to:
        message = advisory.get(f"message_{language}")
        sms_result = sms_service.send_sms(send_sms_to, message, language)
        response["sms_status"] = sms_result
    
    return jsonify(response)


@app.route("/seasonal-advisory", methods=["GET"])
def seasonal_advisory():
    month_str = request.args.get("month", "").strip()
    language = request.args.get("lang", "en").lower()
    send_sms_to = request.args.get("send_sms", "").strip()
    
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
    
    if send_sms_to:
        sms_result = sms_service.send_sms(send_sms_to, advisory.get("message"), language)
        response["sms_status"] = sms_result
    
    return jsonify(response)


@app.route("/price-advisory", methods=["GET"])
def price_advisory():
    crops_str = request.args.get("crops", "").strip()
    language = request.args.get("lang", "en").lower()
    send_sms_to = request.args.get("send_sms", "").strip()
    
    crops = None
    if crops_str:
        crops = [c.strip() for c in crops_str.split(",") if c.strip()]
    
    if language not in ["en", "hi"]:
        language = "en"
    
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
    
    if send_sms_to:
        sms_result = sms_service.send_sms(send_sms_to, advisory.get("message"), language)
        response["sms_status"] = sms_result
    
    return jsonify(response)


@app.route("/send-sms", methods=["POST"])
def send_sms():
    data = request.get_json() or {}
    
    phone = data.get("phone", "").strip()
    message = data.get("message", "").strip()
    
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


@app.route("/api/sms/history", methods=["GET"])
def get_sms_history():
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


@app.route("/api/weather", methods=["GET"])
def get_weather():
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
    return weather_advisory()


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
