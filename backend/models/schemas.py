from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Activity(BaseModel):
    name: str
    location: str
    date: Optional[str] = None
    description: Optional[str] = None
    price: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


class UserPreferences(BaseModel):
    user_id: str
    location: Optional[str] = None
    interests: List[str] = []
    budget: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_history: List[ChatMessage] = []
