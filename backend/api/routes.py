"""API routes for FastAPI backend"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.orchestrator import AgentOrchestrator
from agents.tools.preferences import (
    get_all_user_ids,
    get_user_preferences,
    update_user_preferences,
)
from models.chat_history import (
    ChatHistoryEntry,
    ChatHistoryListItem,
    ChatHistorySave,
)
from services import chat_history_service
from services.activity_fetcher import fetch_activities

router = APIRouter()

# Store agent instances per user (TODO: in production, use proper session management)
agents: dict[str, AgentOrchestrator] = {}


class ChatMessage(BaseModel):
    message: str
    user_id: str | None = "default"


class ChatResponse(BaseModel):
    response: str
    tool_results: list[dict[str, Any]] = []
    skipped_tools_message: str | None = None


class PreferencesUpdate(BaseModel):
    location: str | None = None
    interests: list[str] | None = None
    budget_min: float | None = None
    budget_max: float | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Chat endpoint for agent interaction"""
    print(f"[DEBUG][/chat] Chat message: {chat_message}")
    user_id = chat_message.user_id or "default"

    if user_id not in agents:
        print(f"[DEBUG][/chat] Creating new agent for user: {user_id}")
        agents[user_id] = AgentOrchestrator(user_id=user_id)

    agent = agents[user_id]

    try:
        result = agent.process_message(chat_message.message)
        print(f"[DEBUG][/chat] Result: {result}")
        return ChatResponse(
            response=result.get("response") or "I couldn't generate a response.",
            tool_results=result.get("tool_results", []),
            skipped_tools_message=result.get("skipped_tools_message"),
        )
    except Exception as e:
        import traceback

        print(f"[ERROR][/chat] Exception: {type(e).__name__}: {e}")
        print(f"[ERROR][/chat] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def list_users():
    """List all user IDs from preferences file"""
    try:
        user_ids = get_all_user_ids()
        return {"users": user_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user preferences"""
    try:
        prefs = get_user_preferences(user_id)
        return prefs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences/{user_id}")
async def update_preferences(user_id: str, preferences: PreferencesUpdate):
    """Update user preferences"""
    try:
        prefs_dict = preferences.dict(exclude_unset=True)
        # Unpack dictionary as keyword arguments to match new function signature
        updated = update_user_preferences(user_id=user_id, **prefs_dict)
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activities")
async def get_activities(
    location_a: str | None = None,
    location_b: str | None = None,
    user_id: str | None = "default",
):
    """Get activities between two locations.

    Uses the activity_fetcher service to intelligently find activities:
    - If two locations provided, finds transit stops between them and queries nearby
    - If one location provided, queries activities near that location
    - Uses user preferences for interests, budget, etc.

    Args:
        location_a: First location (defaults to user preferences if not provided)
        location_b: Second location (optional)
        user_id: User ID for preferences lookup
    """
    try:
        # Use location from preferences if location_a not provided
        prefs = get_user_preferences(user_id)
        search_location_a = location_a or prefs.get("location")

        if not search_location_a:
            raise HTTPException(
                status_code=400,
                detail="location_a is required (or set a default location in user preferences)",
            )

        result = fetch_activities(
            location_a=search_location_a, location_b=location_b, user_id=user_id
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-history")
async def list_chat_histories() -> list[ChatHistoryListItem]:
    """List all chat histories (without full messages)"""
    try:
        return chat_history_service.list_all_histories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat-history/{history_id}")
async def get_chat_history(history_id: str) -> ChatHistoryEntry:
    """Get a specific chat history with full messages"""
    try:
        history = chat_history_service.get_history_by_id(history_id)

        if history is None:
            raise HTTPException(status_code=404, detail="Chat history not found")

        return history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat-history")
async def save_chat_history(history_save: ChatHistorySave) -> ChatHistoryEntry:
    """Save or update a chat history"""
    try:
        return chat_history_service.save_history(history_save.id, history_save.messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat-history/{history_id}")
async def delete_chat_history(history_id: str):
    """Delete a specific chat history"""
    try:
        deleted = chat_history_service.delete_history(history_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Chat history not found")

        return {"message": "Chat history deleted", "id": history_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat-history")
async def clear_all_chat_history():
    """Clear all chat histories"""
    try:
        chat_history_service.clear_all_histories()
        return {"message": "All chat histories cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
