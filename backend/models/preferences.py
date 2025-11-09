from pydantic import BaseModel
from typing import Optional, List


class UserPreferences(BaseModel):
    """Model for user preferences"""
    user_id: str
    location: Optional[str] = None
    interests: List[str] = []
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    date_preferences: Optional[str] = None  # e.g., "weekend", "evening", "anytime"

