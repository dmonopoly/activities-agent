
from pydantic import BaseModel


class UserPreferences(BaseModel):
    """Model for user preferences"""

    user_id: str
    location: str | None = None
    interests: list[str] = []
    budget_min: float | None = None
    budget_max: float | None = None
