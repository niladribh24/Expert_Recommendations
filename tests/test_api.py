"""
Tests for the Agriculture Expert Recommendation System API.
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services import WeatherService, AdvisoryService, SMSService


@pytest.fixture
def client():
    """Create test client for Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health endpoint returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "api_key_configured" in data


class TestWeatherEndpoint:
    """Tests for weather endpoint."""
    
    def test_weather_missing_location(self, client):
        """Test that missing location returns error."""
        response = client.get("/api/weather")
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "location" in data["error"].lower()


class TestAdvisoryEndpoint:
    """Tests for advisory endpoint."""
    
    def test_advisory_missing_location(self, client):
        """Test that missing location returns error."""
        response = client.get("/api/advisory")
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False


class TestAdvisoryService:
    """Tests for advisory logic."""
    
    def test_no_irrigation_on_rain(self):
        """Test that rainfall above threshold returns no irrigation advisory."""
        service = AdvisoryService()
        weather_data = {
            "success": True,
            "temperature": 30,
            "rainfall": 10,  # Above 5mm threshold
            "humidity": 80,
            "city": "TestCity"
        }
        result = service.generate_advisory(weather_data)
        assert result["advisory_type"] == "no_irrigation"
    
    def test_early_irrigation_on_high_temp(self):
        """Test that high temperature returns early irrigation advisory."""
        service = AdvisoryService()
        weather_data = {
            "success": True,
            "temperature": 40,  # Above 38°C threshold
            "rainfall": 0,
            "humidity": 30,
            "city": "TestCity"
        }
        result = service.generate_advisory(weather_data)
        assert result["advisory_type"] == "early_irrigation"
    
    def test_normal_irrigation(self):
        """Test normal conditions return normal irrigation advisory."""
        service = AdvisoryService()
        weather_data = {
            "success": True,
            "temperature": 32,  # Normal temp
            "rainfall": 0,
            "humidity": 50,
            "city": "TestCity"
        }
        result = service.generate_advisory(weather_data)
        assert result["advisory_type"] == "normal"


class TestSMSService:
    """Tests for SMS service."""
    
    def test_send_sms_valid_phone(self):
        """Test sending SMS with valid phone number."""
        service = SMSService()
        result = service.send_sms("9876543210", "Test message")
        assert result["success"] is True
        assert result["status"] == "delivered"
        assert "message_id" in result
    
    def test_send_sms_invalid_phone(self):
        """Test sending SMS with invalid phone number."""
        service = SMSService()
        result = service.send_sms("12345", "Test message")
        assert result["success"] is False
    
    def test_message_history(self):
        """Test that sent messages appear in history."""
        service = SMSService()
        service.send_sms("9876543210", "Test message")
        history = service.get_message_history()
        assert len(history) >= 1
        assert history[0]["message"] == "Test message"


class TestSMSEndpoint:
    """Tests for SMS API endpoints."""
    
    def test_sms_send_missing_phone(self, client):
        """Test that missing phone returns error."""
        response = client.post("/api/sms/send", json={"location": "Nagpur"})
        assert response.status_code == 400
        data = response.get_json()
        assert "phone" in data["error"].lower()
    
    def test_sms_send_missing_location(self, client):
        """Test that missing location returns error."""
        response = client.post("/api/sms/send", json={"phone": "9876543210"})
        assert response.status_code == 400
        data = response.get_json()
        assert "location" in data["error"].lower()
    
    def test_sms_history(self, client):
        """Test SMS history endpoint."""
        response = client.get("/api/sms/history")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "messages" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
