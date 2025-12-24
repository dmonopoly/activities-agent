"""User preferences tool - MCP-style tool for managing user preferences"""
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

# Simple file-based storage (TODO: upgrade to DB later)
# Store preferences file in backend directory
backend_dir = Path(__file__).parent.parent.parent
DATA_DIR = backend_dir / "data"
PREFERENCES_FILE = DATA_DIR / "user_preferences.json"


def _load_preferences() -> Dict[str, Dict[str, Any]]:
    """Load preferences from file"""
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_preferences(prefs: Dict[str, Dict[str, Any]]):
    """Save preferences to file"""
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)


def get_all_user_ids() -> list:
    """
    Get all user IDs from the preferences file
    
    Returns:
        List of user IDs
    """
    prefs = _load_preferences()
    return list(prefs.keys())


def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get user preferences
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Dictionary containing user preferences
    """
    prefs = _load_preferences()
    user_prefs = prefs.get(user_id, {
        "user_id": user_id,
        "location": None,
        "interests": [],
        "budget_min": None,
        "budget_max": None
    })
    return user_prefs


def update_user_preferences(
    user_id: str,
    location: Optional[str] = None,
    interests: Optional[list] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None
) -> Dict[str, Any]:
    """
    Update user preferences
    
    Args:
        user_id: The user's unique identifier
        location: Preferred location (city, neighborhood, etc.)
        interests: List of interests (e.g., ['outdoor', 'art', 'music'])
        budget_min: Minimum budget in dollars
        budget_max: Maximum budget in dollars
        
    Returns:
        Updated user preferences
    """
    prefs = _load_preferences()
    if user_id not in prefs:
        prefs[user_id] = {
            "user_id": user_id,
            "location": None,
            "interests": [],
            "budget_min": None,
            "budget_max": None
        }
    
    # Update only provided (non-None) fields
    if location is not None:
        prefs[user_id]["location"] = location
    if interests is not None:
        prefs[user_id]["interests"] = interests
    if budget_min is not None:
        prefs[user_id]["budget_min"] = budget_min
    if budget_max is not None:
        prefs[user_id]["budget_max"] = budget_max
    
    _save_preferences(prefs)
    return prefs[user_id]


# Tool definitions for LLM function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_user_preferences",
            "description": "Get user preferences including location, interests, budget, and date preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's unique identifier"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_user_preferences",
            "description": "Update user preferences. Only provide fields that should be updated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's unique identifier"
                    },
                    "location": {
                        "type": "string",
                        "description": "Preferred location (city, neighborhood, etc.)"
                    },
                    "interests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of interests (e.g., ['outdoor', 'art', 'music'])"
                    },
                    "budget_min": {
                        "type": "number",
                        "description": "Minimum budget in dollars"
                    },
                    "budget_max": {
                        "type": "number",
                        "description": "Maximum budget in dollars"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
]
