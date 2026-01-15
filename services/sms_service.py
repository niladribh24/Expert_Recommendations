import uuid
from datetime import datetime
from typing import List, Optional


class SMSService:
    
    def __init__(self):
        self._sent_messages: List[dict] = []
    
    def send_sms(self, phone_number: str, message: str, language: str = "en") -> dict:
        validation_result = self._validate_phone_number(phone_number)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"]
            }
        
        if not message or len(message.strip()) == 0:
            return {
                "success": False,
                "error": "Message content cannot be empty."
            }
        
        message_record = {
            "message_id": str(uuid.uuid4()),
            "phone_number": self._normalize_phone(phone_number),
            "message": message,
            "language": language,
            "status": "delivered",
            "timestamp": datetime.now().isoformat(),
            "sender_id": "AGRI-EXPERT"
        }
        
        self._sent_messages.append(message_record)
        
        print(f"\n{'='*50}")
        print(f"📱 [DUMMY SMS SENT]")
        print(f"To: {message_record['phone_number']}")
        print(f"Message ID: {message_record['message_id']}")
        print(f"Time: {message_record['timestamp']}")
        print(f"Content:\n{message}")
        print(f"{'='*50}\n")
        
        return {
            "success": True,
            "message_id": message_record["message_id"],
            "phone_number": message_record["phone_number"],
            "status": message_record["status"],
            "timestamp": message_record["timestamp"],
            "note": "This is a dummy SMS. No real message was sent."
        }
    
    def get_message_history(self, limit: int = 50) -> List[dict]:
        return list(reversed(self._sent_messages[-limit:]))
    
    def get_message_by_id(self, message_id: str) -> Optional[dict]:
        for msg in self._sent_messages:
            if msg["message_id"] == message_id:
                return msg
        return None
    
    def get_messages_by_phone(self, phone_number: str) -> List[dict]:
        normalized_phone = self._normalize_phone(phone_number)
        return [
            msg for msg in self._sent_messages
            if msg["phone_number"] == normalized_phone
        ]
    
    def clear_history(self) -> dict:
        count = len(self._sent_messages)
        self._sent_messages.clear()
        return {
            "success": True,
            "cleared_count": count
        }
    
    def _validate_phone_number(self, phone: str) -> dict:
        cleaned = phone.replace(" ", "").replace("-", "")
        
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0"):
            cleaned = cleaned[1:]
        
        if not cleaned.isdigit():
            return {"valid": False, "error": "Phone number must contain only digits."}
        
        if len(cleaned) != 10:
            return {"valid": False, "error": "Phone number must be 10 digits."}
        
        if cleaned[0] not in "6789":
            return {"valid": False, "error": "Invalid Indian mobile number format."}
        
        return {"valid": True}
    
    def _normalize_phone(self, phone: str) -> str:
        cleaned = phone.replace(" ", "").replace("-", "")
        
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0"):
            cleaned = cleaned[1:]
        
        return f"+91{cleaned}"
