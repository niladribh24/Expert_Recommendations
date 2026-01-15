import json
import os
from datetime import datetime
from typing import Optional


class SeasonalService:
    
    def __init__(self):
        self.crop_data = self._load_crop_data()
    
    def _load_crop_data(self) -> dict:
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "seasonal_crops.json"
        )
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_current_season(self, month: Optional[int] = None) -> str:

        if month is None:
            month = datetime.now().month
        
        for season_key, season_data in self.crop_data.items():
            if month in season_data.get("months", []):
                return season_key
        
        return "rabi"
    
    def get_seasonal_advisory(self, month: Optional[int] = None, lang: str = "en") -> dict:

        if month is None:
            month = datetime.now().month
        
        if not 1 <= month <= 12:
            return {
                "success": False,
                "error": "Invalid month. Must be between 1 and 12."
            }
        
        season_key = self.get_current_season(month)
        season_data = self.crop_data.get(season_key, {})
        
        if not season_data:
            return {
                "success": False,
                "error": "Seasonal data not available."
            }
        
        season_name = season_data.get("name_hi" if lang == "hi" else "name", season_key)
        
        crops = season_data.get("crops", [])
        crop_list = []
        for crop in crops:
            crop_list.append({
                "name": crop.get("name_hi" if lang == "hi" else "name"),
                "water_requirement": crop.get("water_requirement")
            })
        
        message = self._generate_message(
            season_name=season_name,
            season_key=season_key,
            planting=season_data.get("planting_period", ""),
            harvesting=season_data.get("harvesting_period", ""),
            crops=crops,
            lang=lang
        )
        
        return {
            "success": True,
            "month": month,
            "season": season_key,
            "season_name": season_name,
            "planting_period": season_data.get("planting_period"),
            "harvesting_period": season_data.get("harvesting_period"),
            "recommended_crops": crop_list,
            "message": message
        }
    
    def _generate_message(self, season_name: str, season_key: str, planting: str, harvesting: str, crops: list, lang: str) -> str:
        crop_names = [c.get("name_hi" if lang == "hi" else "name") for c in crops[:5]]
        crop_str = ", ".join(crop_names)
        
        if lang == "hi":
            message = (
                f"🌾 वर्तमान मौसम: {season_name}\n"
                f"📅 बुवाई का समय: {planting}\n"
                f"🌻 कटाई का समय: {harvesting}\n\n"
                f"✅ अनुशंसित फसलें:\n{crop_str}\n\n"
                f"💡 सुझाव: अपने क्षेत्र की मिट्टी और पानी की उपलब्धता के अनुसार फसल चुनें।"
            )
        else:
            message = (
                f"🌾 Current Season: {season_name}\n"
                f"📅 Planting Period: {planting}\n"
                f"🌻 Harvesting Period: {harvesting}\n\n"
                f"✅ Recommended Crops:\n{crop_str}\n\n"
                f"💡 Tip: Choose crops based on your local soil type and water availability."
            )
        
        return message
