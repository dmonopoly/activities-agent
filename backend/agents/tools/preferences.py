"""User preferences tool - MCP-style tool for managing user preferences.

Supports two storage backends:
- MongoDB (production): Used when MONGODB_URI is set
- JSON files (local/preview): Used when MONGODB_URI is not set
"""

from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path

from services.db import is_mongodb_enabled, get_user_preferences_collection


# JSON file storage path (used when MongoDB is not enabled)
backend_dir = Path(__file__).parent.parent.parent
DATA_DIR = backend_dir / "data"
PREFERENCES_FILE = DATA_DIR / "user_preferences.json"


# =============================================================================
# Public API (Auto-selects storage backend)
# =============================================================================

def get_all_user_ids() -> List[str]:
    """
    Get all user IDs from storage.
    
    Returns:
        List of user IDs
    """
    if is_mongodb_enabled():
        return _get_all_user_ids_mongo()
    return _get_all_user_ids_json()


def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """
    Get user preferences.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Dictionary containing user preferences
    """
    if is_mongodb_enabled():
        return _get_user_preferences_mongo(user_id)
    return _get_user_preferences_json(user_id)


def update_user_preferences(
    user_id: str,
    location: Optional[str] = None,
    interests: Optional[list] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None
) -> Dict[str, Any]:
    """
    Update user preferences.
    
    Args:
        user_id: The user's unique identifier
        location: Preferred location (city, neighborhood, etc.)
        interests: List of interests (e.g., ['outdoor', 'art', 'music'])
        budget_min: Minimum budget in dollars
        budget_max: Maximum budget in dollars
        
    Returns:
        Updated user preferences
    """
    if is_mongodb_enabled():
        return _update_user_preferences_mongo(user_id, location, interests, budget_min, budget_max)
    return _update_user_preferences_json(user_id, location, interests, budget_min, budget_max)


# -----------------------------------------------------------------------------
# get_all_user_ids
# -----------------------------------------------------------------------------

def _get_all_user_ids_json() -> List[str]:
    prefs = _load_preferences_json()
    return list(prefs.keys())


def _get_all_user_ids_mongo() -> List[str]:
    collection = get_user_preferences_collection()
    cursor = collection.find({}, {"user_id": 1})
    return [doc["user_id"] for doc in cursor if "user_id" in doc]


# -----------------------------------------------------------------------------
# get_user_preferences
# -----------------------------------------------------------------------------

def _get_user_preferences_json(user_id: str) -> Dict[str, Any]:
    prefs = _load_preferences_json()
    user_prefs = prefs.get(user_id, {
        "user_id": user_id,
        "location": None,
        "interests": [],
        "budget_min": None,
        "budget_max": None
    })
    return user_prefs


def _get_user_preferences_mongo(user_id: str) -> Dict[str, Any]:
    collection = get_user_preferences_collection()
    doc = collection.find_one({"user_id": user_id})
    
    if doc is None:
        return {
            "user_id": user_id,
            "location": None,
            "interests": [],
            "budget_min": None,
            "budget_max": None
        }
    
    # Remove MongoDB _id field
    doc.pop("_id", None)
    return doc


# -----------------------------------------------------------------------------
# update_user_preferences
# -----------------------------------------------------------------------------

def _update_user_preferences_json(
    user_id: str,
    location: Optional[str] = None,
    interests: Optional[list] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None
) -> Dict[str, Any]:
    prefs = _load_preferences_json()
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
    
    _save_preferences_json(prefs)
    return prefs[user_id]


def _update_user_preferences_mongo(
    user_id: str,
    location: Optional[str] = None,
    interests: Optional[list] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None
) -> Dict[str, Any]:
    collection = get_user_preferences_collection()
    
    # Build update document with only non-None fields
    update_fields = {}
    if location is not None:
        update_fields["location"] = location
    if interests is not None:
        update_fields["interests"] = interests
    if budget_min is not None:
        update_fields["budget_min"] = budget_min
    if budget_max is not None:
        update_fields["budget_max"] = budget_max
    
    # Upsert: update if exists, insert if not
    if update_fields:
        collection.update_one(
            {"user_id": user_id},
            {
                "$set": update_fields,
                "$setOnInsert": {
                    "user_id": user_id,
                    "location": location,
                    "interests": interests or [],
                    "budget_min": budget_min,
                    "budget_max": budget_max
                }
            },
            upsert=True
        )
    
    return _get_user_preferences_mongo(user_id)


def seed_preferences_from_json_if_empty() -> bool:
    """
    Seed MongoDB user preferences collection from JSON file if empty.
    
    Used during production startup to initialize the database with
    predefined user profiles.
    
    Returns:
        True if seeding was performed, False if collection already had data
    """
    if not is_mongodb_enabled():
        return False
    
    collection = get_user_preferences_collection()
    
    if collection.count_documents({}) > 0:
        print("[PREFERENCES] MongoDB collection already has data, skipping seed")
        return False
    
    if not os.path.exists(PREFERENCES_FILE):
        print("[PREFERENCES] No JSON file to seed from")
        return False
    
    prefs = _load_preferences_json()
    if not prefs:
        print("[PREFERENCES] JSON file is empty, nothing to seed")
        return False
    
    documents = []
    for user_id, user_prefs in prefs.items():
        doc = {**user_prefs, "user_id": user_id}
        documents.append(doc)
    
    collection.insert_many(documents)
    print(f"[PREFERENCES] Seeded {len(documents)} user preferences from JSON")
    return True


# -----------------------------------------------------------------------------
# Other private helpers (JSON file I/O)
# -----------------------------------------------------------------------------

def _load_preferences_json() -> Dict[str, Dict[str, Any]]:
    """Load preferences from JSON file"""
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_preferences_json(prefs: Dict[str, Dict[str, Any]]):
    """Save preferences to JSON file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)


# =============================================================================
# Tool Definitions (for LLM function calling)
# =============================================================================

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
