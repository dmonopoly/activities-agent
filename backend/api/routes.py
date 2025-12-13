"""API routes for FastAPI backend"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Absolute imports work because main.py runs from backend/ directory
# Python automatically adds the current directory to sys.path
from agents.orchestrator import AgentOrchestrator
from agents.tools.preferences import get_user_preferences, update_user_preferences
from agents.tools.scraper import scrape_activities

router = APIRouter()

# Store agent instances per user (TODO: in production, use proper session management)
agents: Dict[str, AgentOrchestrator] = {}


class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    tool_results: List[Dict[str, Any]] = []


class PreferencesUpdate(BaseModel):
    location: Optional[str] = None
    interests: Optional[List[str]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    date_preferences: Optional[str] = None


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
            response=result["response"],
            tool_results=result.get("tool_results", [])
        )
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
    query: Optional[str] = "date ideas",
    location: Optional[str] = None,
    user_id: Optional[str] = "default"
):
    """Get activities (can be used by gallery view)"""
    try:
        # Get user preferences to enhance search
        prefs = get_user_preferences(user_id)
        
        # Use location from preferences if not provided
        search_location = location or prefs.get("location")
        
        # Build filters from preferences
        filters = {}
        if prefs.get("budget_max"):
            filters["max_price"] = prefs["budget_max"]
        
        activities = scrape_activities(query, search_location, filters if filters else None)
        return {"activities": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
