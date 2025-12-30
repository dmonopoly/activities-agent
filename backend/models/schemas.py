
from pydantic import BaseModel


class Activity(BaseModel):
    name: str
    location: str
    date: str | None = None
    description: str | None = None
    price: str | None = None
    url: str | None = None
    image_url: str | None = None


class UserPreferences(BaseModel):
    user_id: str
    location: str | None = None
    interests: list[str] = []
    budget: str | None = None


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    user_id: str
    conversation_history: list[ChatMessage] = []
