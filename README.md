# 🌾 Agriculture Expert Recommendation System

A Flask-based advisory system for Indian farmers providing:
- **Weather-based irrigation advisories** (OpenWeather API)
- **Seasonal crop recommendations** (Kharif, Rabi, Zaid)
- **Weekly market price alerts** (Agmarknet-style data)
- **Simulated SMS delivery** (Dummy gateway)

> **Note**: This is an academic demonstration project. No real SMS messages are sent.

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /weather-advisory ──► WeatherService ──► OpenWeather API   │
│         │                    │                               │
│         ▼                    ▼                               │
│  /seasonal-advisory ──► SeasonalService ──► seasonal_crops  │
│         │                                     .json          │
│         ▼                                                    │
│  /price-advisory ──► MarketService ──► market_prices.json   │
│         │                                                    │
│         ▼                                                    │
│  /send-sms ──────────► SMSService (Dummy Gateway)           │
│                              │                               │
│                              ▼                               │
│                     [Console Log + Memory]                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your OpenWeather API key
# Get free key: https://openweathermap.org/api
```

### 3. Run the Server
```bash
python app.py
```

Server starts at: `http://localhost:5000`

---

## 📡 API Endpoints

### 1. Weather Advisory
Get weather-based irrigation advice using rule-based logic.

**Endpoint:** `GET /weather-advisory`

| Parameter | Required | Description |
|-----------|----------|-------------|
| location | Yes | City name or 6-digit pincode |
| lang | No | Language: `en` (default) or `hi` |
| send_sms | No | Phone number to send SMS |

**Example:**
```bash
curl "http://localhost:5000/weather-advisory?location=Nagpur&lang=hi"
```

**Decision Logic:**
| Condition | Advisory |
|-----------|----------|
| Rainfall > 5mm | Do not irrigate |
| Temperature > 38°C | Irrigate early morning |
| Otherwise | Normal irrigation |

---

### 2. Seasonal Crop Advisory
Get crop recommendations based on current agricultural season.

**Endpoint:** `GET /seasonal-advisory`

| Parameter | Required | Description |
|-----------|----------|-------------|
| month | No | Month 1-12 (default: current) |
| lang | No | Language: `en` or `hi` |
| send_sms | No | Phone number to send SMS |

**Example:**
```bash
curl "http://localhost:5000/seasonal-advisory?month=7&lang=hi"
```

**Seasons:**
| Season | Months | Key Crops |
|--------|--------|-----------|
| Kharif | Jun-Oct | Rice, Cotton, Soybean |
| Rabi | Nov-Mar | Wheat, Mustard, Gram |
| Zaid | Apr-May | Watermelon, Cucumber |

---

### 3. Market Price Advisory
Get weekly crop price trends with MSP comparison.

**Endpoint:** `GET /price-advisory`

| Parameter | Required | Description |
|-----------|----------|-------------|
| crops | No | Comma-separated crop names |
| lang | No | Language: `en` or `hi` |
| send_sms | No | Phone number to send SMS |

**Example:**
```bash
curl "http://localhost:5000/price-advisory?crops=Rice,Wheat"
```

---

### 4. Dummy SMS Gateway
Simulates sending SMS (no real messages sent).

**Endpoint:** `POST /send-sms`

**Request Body:**
```json
{
    "phone": "+919876543210",
    "message": "Your advisory message"
}
```

**Response:**
```json
{
    "status": "SENT",
    "delivery": "SIMULATED",
    "message_id": "uuid",
    "timestamp": "2026-01-15T21:00:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/send-sms \
  -H "Content-Type: application/json" \
  -d '{"phone": "9876543210", "message": "Test advisory"}'
```

---

## 📁 Project Structure

```
SpecRec/
├── app.py                      # Flask application (main entry)
├── config.py                   # Configuration & thresholds
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API key)
├── README.md                   # This documentation
├── services/
│   ├── weather_service.py      # OpenWeather API integration
│   ├── advisory_service.py     # Irrigation decision logic
│   ├── seasonal_service.py     # Crop season recommendations
│   ├── market_service.py       # Price trend analysis
│   └── sms_service.py          # Dummy SMS gateway
├── data/
│   ├── pincode_mapping.json    # Indian pincode → city
│   ├── seasonal_crops.json     # Season → crops knowledge base
│   └── market_prices.json      # Simulated market data
└── tests/
    └── test_api.py             # Unit tests
```

---

## 🧪 Testing

Run all tests:
```bash
python -m pytest tests/test_api.py -v
```

---

## ⚙️ Technical Details

| Component | Technology |
|-----------|------------|
| Language | Python 3.x |
| Framework | Flask |
| Weather API | OpenWeather (free tier) |
| Data Storage | JSON files |
| SMS | Simulated (in-memory) |

---

## 📌 Important Notes

- ❌ No real SMS providers (Twilio, MSG91, etc.)
- ❌ No ML models - rule-based logic only
- ✅ India-specific data and assumptions
- ✅ Bilingual support (English + Hindi)
- ✅ Works offline for seasonal/price advisories

---
