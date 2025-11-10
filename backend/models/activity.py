from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class Activity(BaseModel):
    """Model for an activity/date idea"""
    name: str
    location: str
    description: Optional[str] = None
    price: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    
    gmaps_place_id: Optional[str] = None
    gmaps_rating: Optional[float] = None  # Scale: 1.0-5.0
    gmaps_price_level: Optional[int] = None  # Scale: 0-4 (0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive)
    gmaps_opening_hours: Optional[Any] = None  # Can be dict or string with hours info
    gmaps_review_summary: Optional[str] = None
    
    # Generic fields (not Google Maps-specific)
    coordinates: Optional[Dict[str, float]] = None  # Dict with "lat" and "lng" keys
    weather_info: Optional[Dict[str, Any]] = None  # Weather data from weather API

