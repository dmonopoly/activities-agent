"""User preferences tool - MCP-style tool for managing user preferences"""
from typing import Dict, Any, Optional
import json
import os
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Simple file-based storage (can be upgraded to DB later)
PREFERENCES_FILE = "user_preferences.json"


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
        "budget_max": None,
        "date_preferences": None
    })
    return user_prefs


def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update user preferences
    
    Args:
        user_id: The user's unique identifier
        preferences: Dictionary of preferences to update
        
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
            "budget_max": None,
            "date_preferences": None
        }
    
    # Update only provided fields
    for key, value in preferences.items():
        if key != "user_id" and value is not None:
            prefs[user_id][key] = value
    
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
                    },
                    "date_preferences": {
                        "type": "string",
                        "description": "Preferred time (e.g., 'weekend', 'evening', 'anytime')"
                    }
                },
                "required": ["user_id"]
            }
        }
    }
]
