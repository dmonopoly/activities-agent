from typing import Any

from pydantic import BaseModel


class Activity(BaseModel):
    """Model for an activity/date idea"""

    name: str
    location: str
    description: str | None = None
    price: str | None = None
    date: str | None = None
    url: str | None = None
    image_url: str | None = None
    category: str | None = None

    gmaps_place_id: str | None = None
    gmaps_rating: float | None = None  # Scale: 1.0-5.0
    gmaps_price_level: int | None = (
        None  # Scale: 0-4 (0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive)
    )
    gmaps_opening_hours: Any | None = None  # Can be dict or string with hours info
    gmaps_review_summary: str | None = None

    # Generic fields (not Google Maps-specific)
    coordinates: dict[str, float] | None = None  # Dict with "lat" and "lng" keys
    weather_info: dict[str, Any] | None = None  # Weather data from weather API
