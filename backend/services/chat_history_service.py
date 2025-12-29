"""Chat history service for managing persistent chat storage.

Supports two storage backends:
- MongoDB (production): Used when MONGODB_URI is set
- JSON files (local/preview): Used when MONGODB_URI is not set
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

from models.chat_history import (
    ChatHistoryMessage,
    ChatHistoryEntry,
    ChatHistoryListItem,
)
from utils.datetime_utils import utc_now_iso
from services.db import is_mongodb_enabled, get_chat_history_collection


# JSON file storage path (used when MongoDB is not enabled)
CHAT_HISTORY_FILE = Path(__file__).parent.parent / "data" / "chat_history.json"


# =============================================================================
# Public API (Auto-selects storage backend)
# =============================================================================

def list_all_histories() -> List[ChatHistoryListItem]:
    """List all chat histories (without full messages).
    
    Returns:
        List of ChatHistoryListItem sorted by updated_at descending (most recent first).
    """
    if is_mongodb_enabled():
        return _list_all_histories_mongo()
    return _list_all_histories_json()


def get_history_by_id(history_id: str) -> Optional[ChatHistoryEntry]:
    """Get a specific chat history with full messages.
    
    Args:
        history_id: The unique identifier of the chat history
        
    Returns:
        ChatHistoryEntry or None if not found
    """
    if is_mongodb_enabled():
        return _get_history_by_id_mongo(history_id)
    return _get_history_by_id_json(history_id)


def save_history(history_id: Optional[str], messages: List[ChatHistoryMessage]) -> ChatHistoryEntry:
    """Save or update a chat history.
    
    Args:
        history_id: Existing history ID to update, or None to create new
        messages: List of ChatHistoryMessage objects
        
    Returns:
        The saved ChatHistoryEntry
    """
    if is_mongodb_enabled():
        return _save_history_mongo(history_id, messages)
    return _save_history_json(history_id, messages)


def delete_history(history_id: str) -> bool:
    """Delete a specific chat history.
    
    Args:
        history_id: The unique identifier of the chat history to delete
        
    Returns:
        True if deleted successfully, False if not found
    """
    if is_mongodb_enabled():
        return _delete_history_mongo(history_id)
    return _delete_history_json(history_id)


def clear_all_histories() -> None:
    """Clear all chat histories."""
    if is_mongodb_enabled():
        _clear_all_histories_mongo()
    else:
        _clear_all_histories_json()


# -----------------------------------------------------------------------------
# list_all_histories
# -----------------------------------------------------------------------------

def _list_all_histories_json() -> List[ChatHistoryListItem]:
    data = _read_chat_histories_json()
    histories = data.get("histories", {})
    
    items = [_dict_to_list_item(h) for h in histories.values()]
    items.sort(key=lambda x: x.updated_at, reverse=True)
    return items


def _list_all_histories_mongo() -> List[ChatHistoryListItem]:
    collection = get_chat_history_collection()
    
    cursor = collection.find({}).sort("updated_at", -1)
    return [_dict_to_list_item(doc) for doc in cursor]


# -----------------------------------------------------------------------------
# get_history_by_id
# -----------------------------------------------------------------------------

def _get_history_by_id_json(history_id: str) -> Optional[ChatHistoryEntry]:
    data = _read_chat_histories_json()
    histories = data.get("histories", {})
    
    if history_id not in histories:
        return None
    
    return _dict_to_entry(histories[history_id])


def _get_history_by_id_mongo(history_id: str) -> Optional[ChatHistoryEntry]:
    collection = get_chat_history_collection()
    
    doc = collection.find_one({"id": history_id})
    if doc is None:
        return None
    
    return _dict_to_entry(doc)


# -----------------------------------------------------------------------------
# save_history
# -----------------------------------------------------------------------------

def _save_history_json(history_id: Optional[str], messages: List[ChatHistoryMessage]) -> ChatHistoryEntry:
    data = _read_chat_histories_json()
    histories = data.get("histories", {})
    
    now = utc_now_iso()
    final_id = history_id or str(uuid.uuid4())
    title = _generate_title(messages)
    messages_dicts = [m.model_dump() for m in messages]
    
    # Get existing created_at or use now
    created_at = histories.get(final_id, {}).get("created_at", now)
    
    histories[final_id] = _build_history_dict(
        history_id=final_id,
        title=title,
        messages=messages_dicts,
        created_at=created_at,
        updated_at=now
    )
    
    data["histories"] = histories
    _write_chat_histories_json(data)
    
    return _dict_to_entry(histories[final_id])


def _save_history_mongo(history_id: Optional[str], messages: List[ChatHistoryMessage]) -> ChatHistoryEntry:
    collection = get_chat_history_collection()
    
    now = utc_now_iso()
    final_id = history_id or str(uuid.uuid4())
    title = _generate_title(messages)
    messages_dicts = [m.model_dump() for m in messages]
    
    # Get existing created_at or use now
    existing = collection.find_one({"id": final_id})
    created_at = existing.get("created_at", now) if existing else now
    
    history_dict = _build_history_dict(
        history_id=final_id,
        title=title,
        messages=messages_dicts,
        created_at=created_at,
        updated_at=now
    )
    
    if existing:
        collection.update_one({"id": final_id}, {"$set": history_dict})
    else:
        collection.insert_one(history_dict)
    
    return _dict_to_entry(history_dict)


# -----------------------------------------------------------------------------
# delete_history
# -----------------------------------------------------------------------------

def _delete_history_json(history_id: str) -> bool:
    data = _read_chat_histories_json()
    histories = data.get("histories", {})
    
    if history_id not in histories:
        return False
    
    del histories[history_id]
    data["histories"] = histories
    _write_chat_histories_json(data)
    return True


def _delete_history_mongo(history_id: str) -> bool:
    collection = get_chat_history_collection()
    result = collection.delete_one({"id": history_id})
    return result.deleted_count > 0


# -----------------------------------------------------------------------------
# clear_all_histories
# -----------------------------------------------------------------------------

def _clear_all_histories_json() -> None:
    _write_chat_histories_json({"histories": {}})


def _clear_all_histories_mongo() -> None:
    collection = get_chat_history_collection()
    collection.delete_many({})

# -----------------------------------------------------------------------------
# Other private helpers
# -----------------------------------------------------------------------------

def _read_chat_histories_json() -> Dict[str, Any]:
    """Read chat histories from JSON file."""
    if not CHAT_HISTORY_FILE.exists():
        return {"histories": {}}
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"histories": {}}


def _write_chat_histories_json(data: Dict[str, Any]) -> None:
    """Write chat histories to JSON file."""
    CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _generate_title(messages: List[ChatHistoryMessage]) -> str:
    """Generate a title from the first user message."""
    for msg in messages:
        if msg.role == "user":
            content = msg.content[:50]
            return content + ("..." if len(msg.content) > 50 else "")
    return "New Chat"


def _dict_to_list_item(data: Dict[str, Any]) -> ChatHistoryListItem:
    """Convert a raw dict to ChatHistoryListItem."""
    return ChatHistoryListItem(
        id=data.get("id", ""),
        title=data.get("title", "Untitled"),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        message_count=len(data.get("messages", []))
    )


def _dict_to_entry(data: Dict[str, Any]) -> ChatHistoryEntry:
    """Convert a raw dict to ChatHistoryEntry."""
    return ChatHistoryEntry(
        id=data.get("id", ""),
        title=data.get("title", "Untitled"),
        messages=[ChatHistoryMessage(**m) for m in data.get("messages", [])],
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", "")
    )


def _build_history_dict(
    history_id: str,
    title: str,
    messages: List[Dict[str, Any]],
    created_at: str,
    updated_at: str
) -> Dict[str, Any]:
    """Build a history dict for storage."""
    return {
        "id": history_id,
        "title": title,
        "messages": messages,
        "created_at": created_at,
        "updated_at": updated_at
    }
