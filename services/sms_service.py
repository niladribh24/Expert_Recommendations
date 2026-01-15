"""
SMS Service - Dummy SMS sender for demonstration purposes.
"""
import uuid
from datetime import datetime
from typing import List, Optional


class SMSService:
    """
    Dummy SMS service that simulates sending SMS messages.
    Messages are stored in memory and can be retrieved for demonstration.
    """
    
    def __init__(self):
        # In-memory storage for sent messages
        self._sent_messages: List[dict] = []
    
    def send_sms(self, phone_number: str, message: str, language: str = "en") -> dict:
        """
        Simulate sending an SMS message.
        
        Args:
            phone_number: Recipient phone number (10 digits)
            message: Message content
            language: Message language (en/hi)
            
        Returns:
            dict with delivery status and message details
        """
        # Validate phone number
        validation_result = self._validate_phone_number(phone_number)
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"]
            }
        
        # Validate message
        if not message or len(message.strip()) == 0:
            return {
                "success": False,
                "error": "Message content cannot be empty."
            }
        
        # Generate message record
        message_record = {
            "message_id": str(uuid.uuid4()),
            "phone_number": self._normalize_phone(phone_number),
            "message": message,
            "language": language,
            "status": "delivered",  # Simulated delivery
            "timestamp": datetime.now().isoformat(),
            "sender_id": "AGRI-EXPERT"
        }
        
        # Store in memory
        self._sent_messages.append(message_record)
        
        # Log to console for demonstration
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
        """
        Get history of sent messages.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of message records, most recent first
        """
        return list(reversed(self._sent_messages[-limit:]))
    
    def get_message_by_id(self, message_id: str) -> Optional[dict]:
        """
        Get a specific message by its ID.
        
        Args:
            message_id: UUID of the message
            
        Returns:
            Message record or None if not found
        """
        for msg in self._sent_messages:
            if msg["message_id"] == message_id:
                return msg
        return None
    
    def get_messages_by_phone(self, phone_number: str) -> List[dict]:
        """
        Get all messages sent to a specific phone number.
        
        Args:
            phone_number: Phone number to search for
            
        Returns:
            List of message records
        """
        normalized_phone = self._normalize_phone(phone_number)
        return [
            msg for msg in self._sent_messages
            if msg["phone_number"] == normalized_phone
        ]
    
    def clear_history(self) -> dict:
        """Clear all message history (for testing purposes)."""
        count = len(self._sent_messages)
        self._sent_messages.clear()
        return {
            "success": True,
            "cleared_count": count
        }
    
    def _validate_phone_number(self, phone: str) -> dict:
        """Validate Indian phone number format."""
        # Remove spaces and common prefixes
        cleaned = phone.replace(" ", "").replace("-", "")
        
        # Remove country code if present
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0"):
            cleaned = cleaned[1:]
        
        # Check if it's a valid 10-digit Indian mobile number
        if not cleaned.isdigit():
            return {"valid": False, "error": "Phone number must contain only digits."}
        
        if len(cleaned) != 10:
            return {"valid": False, "error": "Phone number must be 10 digits."}
        
        # Indian mobile numbers start with 6, 7, 8, or 9
        if cleaned[0] not in "6789":
            return {"valid": False, "error": "Invalid Indian mobile number format."}
        
        return {"valid": True}
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to standard format."""
        cleaned = phone.replace(" ", "").replace("-", "")
        
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0"):
            cleaned = cleaned[1:]
        
        return f"+91{cleaned}"
