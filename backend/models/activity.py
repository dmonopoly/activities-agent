from pydantic import BaseModel
from typing import Optional
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

