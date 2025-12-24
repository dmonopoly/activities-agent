"""Chat history service for managing persistent chat storage"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from models.chat_history import (
    ChatHistoryMessage,
    ChatHistoryEntry,
    ChatHistoryListItem,
)


CHAT_HISTORY_FILE = Path(__file__).parent.parent / "data" / "chat_history.json"


def _read_chat_histories() -> Dict[str, Any]:
    """Read chat histories from JSON file"""
    if not CHAT_HISTORY_FILE.exists():
        return {"histories": {}}
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"histories": {}}


def _write_chat_histories(data: Dict[str, Any]) -> None:
    """Write chat histories to JSON file"""
    CHAT_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def list_all_histories() -> List[ChatHistoryListItem]:
    """List all chat histories (without full messages).
    
    Returns:
        List of ChatHistoryListItem sorted by updated_at descending (most recent first).
    """
    data = _read_chat_histories()
    histories = data.get("histories", {})
    
    items = []
    for _history_id, history in histories.items():
        items.append(ChatHistoryListItem(
            id=history["id"],
            title=history.get("title", "Untitled"),
            created_at=history.get("created_at", ""),
            updated_at=history.get("updated_at", ""),
            message_count=len(history.get("messages", []))
        ))
    
    # Sort by updated_at descending (most recent first)
    items.sort(key=lambda x: x.updated_at, reverse=True)
    return items


def get_history_by_id(history_id: str) -> Optional[ChatHistoryEntry]:
    """Get a specific chat history with full messages.
    
    Args:
        history_id: The unique identifier of the chat history
        
    Returns:
        ChatHistoryEntry or None if not found
    """
    data = _read_chat_histories()
    histories = data.get("histories", {})
    
    if history_id not in histories:
        return None
    
    history = histories[history_id]
    return ChatHistoryEntry(
        id=history["id"],
        title=history.get("title", "Untitled"),
        messages=[ChatHistoryMessage(**m) for m in history.get("messages", [])],
        created_at=history.get("created_at", ""),
        updated_at=history.get("updated_at", "")
    )


def save_history(history_id: Optional[str], messages: List[ChatHistoryMessage]) -> ChatHistoryEntry:
    """Save or update a chat history.
    
    Args:
        history_id: Existing history ID to update, or None to create new
        messages: List of ChatHistoryMessage objects
        
    Returns:
        The saved ChatHistoryEntry
    """
    data = _read_chat_histories()
    histories = data.get("histories", {})
    
    now = datetime.utcnow().isoformat() + "Z"
    final_history_id = history_id or str(uuid.uuid4())
    
    # Convert messages to dicts for storage
    messages_dicts = [m.dict() for m in messages]
    
    # Generate title from first user message
    title = "New Chat"
    for msg in messages:
        if msg.role == "user":
            title = msg.content[:50] + ("..." if len(msg.content) > 50 else "")
            break
    
    if final_history_id in histories:
        # Update existing
        histories[final_history_id]["messages"] = messages_dicts
        histories[final_history_id]["updated_at"] = now
        histories[final_history_id]["title"] = title
    else:
        # Create new
        histories[final_history_id] = {
            "id": final_history_id,
            "title": title,
            "messages": messages_dicts,
            "created_at": now,
            "updated_at": now
        }
    
    data["histories"] = histories
    _write_chat_histories(data)
    
    history = histories[final_history_id]
    return ChatHistoryEntry(
        id=history["id"],
        title=history["title"],
        messages=[ChatHistoryMessage(**m) for m in history["messages"]],
        created_at=history["created_at"],
        updated_at=history["updated_at"]
    )


def delete_history(history_id: str) -> bool:
    """Delete a specific chat history.
    
    Args:
        history_id: The unique identifier of the chat history to delete
        
    Returns:
        True if deleted successfully, False if not found
    """
    data = _read_chat_histories()
    histories = data.get("histories", {})
    
    if history_id not in histories:
        return False
    
    del histories[history_id]
    data["histories"] = histories
    _write_chat_histories(data)
    
    return True


def clear_all_histories() -> None:
    """Clear all chat histories."""
    _write_chat_histories({"histories": {}})

