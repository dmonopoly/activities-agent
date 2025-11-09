"""API routes for FastAPI backend"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from agents.orchestrator import AgentOrchestrator
    from agents.tools.preferences import get_user_preferences, update_user_preferences
    from agents.tools.scraper import scrape_activities
except ImportError:
    # Handle import errors gracefully
    import importlib.util
    from pathlib import Path
    
    def load_module(module_path, module_name):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    orchestrator_path = backend_dir / "agents" / "orchestrator.py"
    prefs_path = backend_dir / "agents" / "tools" / "preferences.py"
    scraper_path = backend_dir / "agents" / "tools" / "scraper.py"
    
    orchestrator_module = load_module(orchestrator_path, "orchestrator")
    prefs_module = load_module(prefs_path, "preferences")
    scraper_module = load_module(scraper_path, "scraper")
    
    AgentOrchestrator = orchestrator_module.AgentOrchestrator
    get_user_preferences = prefs_module.get_user_preferences
    update_user_preferences = prefs_module.update_user_preferences
    scrape_activities = scraper_module.scrape_activities

router = APIRouter()

# Store agent instances per user (in production, use proper session management)
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
    user_id = chat_message.user_id or "default"
    
    # Get or create agent for user
    if user_id not in agents:
        agents[user_id] = AgentOrchestrator(user_id=user_id)
    
    agent = agents[user_id]
    
    try:
        result = agent.process_message(chat_message.message)
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
        updated = update_user_preferences(user_id, prefs_dict)
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
