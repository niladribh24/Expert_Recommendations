"""
Market Price Advisory Service - Provides weekly crop price trends
and comparisons with MSP (Minimum Support Price).
"""
import json
import os
from datetime import datetime
from typing import Optional, List


class MarketService:
    """
    Service for market price advisories.
    
    Uses simulated Agmarknet-style data to provide:
    - Current week prices
    - Week-over-week price changes
    - MSP (Minimum Support Price) comparisons
    """
    
    def __init__(self):
        self.price_data = self._load_price_data()
    
    def _load_price_data(self) -> dict:
        """Load market price data from JSON file."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "market_prices.json"
        )
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"prices": {}}
    
    def get_all_prices(self) -> dict:
        """Get all crop prices with trends."""
        prices = self.price_data.get("prices", {})
        result = []
        
        for crop_name, data in prices.items():
            current = data.get("current_week", 0)
            previous = data.get("previous_week", 0)
            msp = data.get("msp")
            
            # Calculate week-over-week change
            change = current - previous
            change_pct = (change / previous * 100) if previous > 0 else 0
            
            # Determine trend
            if change > 0:
                trend = "up"
            elif change < 0:
                trend = "down"
            else:
                trend = "stable"
            
            result.append({
                "crop": crop_name,
                "crop_hi": data.get("name_hi", crop_name),
                "unit": data.get("unit", "quintal"),
                "current_price": current,
                "previous_price": previous,
                "change": change,
                "change_percent": round(change_pct, 2),
                "trend": trend,
                "msp": msp,
                "above_msp": current >= msp if msp else None
            })
        
        return {
            "success": True,
            "last_updated": self.price_data.get("last_updated"),
            "market": self.price_data.get("market"),
            "prices": result
        }
    
    def get_price_advisory(
        self,
        crops: Optional[List[str]] = None,
        lang: str = "en"
    ) -> dict:
        """
        Generate weekly market price advisory.
        
        Args:
            crops: List of crop names to include. If None, includes top movers.
            lang: Language preference ('en' or 'hi')
            
        Returns:
            dict with price trends and advisory message
        """
        all_prices = self.get_all_prices()
        
        if not all_prices.get("success"):
            return {
                "success": False,
                "error": "Price data not available."
            }
        
        price_list = all_prices.get("prices", [])
        
        # Filter by requested crops if specified
        if crops:
            crops_lower = [c.lower() for c in crops]
            price_list = [
                p for p in price_list
                if p["crop"].lower() in crops_lower
            ]
        
        # Identify top gainers and losers
        sorted_by_change = sorted(price_list, key=lambda x: x["change_percent"], reverse=True)
        top_gainers = [p for p in sorted_by_change if p["change_percent"] > 0][:3]
        top_losers = [p for p in sorted_by_change if p["change_percent"] < 0][-3:]
        
        # Generate advisory message
        message = self._generate_message(
            prices=price_list,
            gainers=top_gainers,
            losers=top_losers,
            lang=lang
        )
        
        return {
            "success": True,
            "last_updated": all_prices.get("last_updated"),
            "total_crops": len(price_list),
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "all_prices": price_list,
            "message": message
        }
    
    def _generate_message(
        self,
        prices: list,
        gainers: list,
        losers: list,
        lang: str
    ) -> str:
        """Generate farmer-friendly market advisory message."""
        
        if lang == "hi":
            message = "📊 साप्ताहिक बाजार भाव सलाह\n\n"
            
            if gainers:
                message += "📈 बढ़ती कीमतें:\n"
                for g in gainers:
                    message += f"  • {g['crop_hi']}: ₹{g['current_price']}/{g['unit']} (+{g['change_percent']}%)\n"
            
            if losers:
                message += "\n📉 गिरती कीमतें:\n"
                for l in losers:
                    message += f"  • {l['crop_hi']}: ₹{l['current_price']}/{l['unit']} ({l['change_percent']}%)\n"
            
            # MSP advice
            below_msp = [p for p in prices if p.get("above_msp") is False]
            if below_msp:
                message += "\n⚠️ MSP से नीचे: "
                message += ", ".join([p['crop_hi'] for p in below_msp])
                message += "\n💡 सरकारी खरीद केंद्रों पर बेचने पर विचार करें।"
            
            message += "\n\n✅ सुझाव: बाजार के रुझान देखकर ही बेचें।"
            
        else:
            message = "📊 Weekly Market Price Advisory\n\n"
            
            if gainers:
                message += "📈 Prices Rising:\n"
                for g in gainers:
                    message += f"  • {g['crop']}: ₹{g['current_price']}/{g['unit']} (+{g['change_percent']}%)\n"
            
            if losers:
                message += "\n📉 Prices Falling:\n"
                for l in losers:
                    message += f"  • {l['crop']}: ₹{l['current_price']}/{l['unit']} ({l['change_percent']}%)\n"
            
            # MSP advice
            below_msp = [p for p in prices if p.get("above_msp") is False]
            if below_msp:
                message += "\n⚠️ Below MSP: "
                message += ", ".join([p['crop'] for p in below_msp])
                message += "\n💡 Consider selling at government procurement centers."
            
            message += "\n\n✅ Tip: Monitor market trends before selling your produce."
        
        return message
