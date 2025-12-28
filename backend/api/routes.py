"""API routes for FastAPI backend"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from agents.orchestrator import AgentOrchestrator
from agents.tools.preferences import get_user_preferences, update_user_preferences, get_all_user_ids
from agents.tools.scraper import scrape_activities
from services.activity_fetcher import fetch_activities

router = APIRouter()

# Store agent instances per user (TODO: in production, use proper session management)
agents: Dict[str, AgentOrchestrator] = {}


class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    tool_results: List[Dict[str, Any]] = []
    skipped_tools_message: Optional[str] = None


class PreferencesUpdate(BaseModel):
    location: Optional[str] = None
    interests: Optional[List[str]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None


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
            skipped_tools_message=result.get("skipped_tools_message")
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
    location_a: Optional[str] = None,
    location_b: Optional[str] = None,
    user_id: Optional[str] = "default"
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
                detail="location_a is required (or set a default location in user preferences)"
            )
        
        result = fetch_activities(
            location_a=search_location_a,
            location_b=location_b,
            user_id=user_id
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
