"""Pydantic models for chat history"""
from pydantic import BaseModel
from typing import List, Optional


class ChatHistoryMessage(BaseModel):
    """A single message in a chat history"""
    role: str
    content: str


class ChatHistoryEntry(BaseModel):
    """A complete chat history entry with messages"""
    id: str
    title: str
    messages: List[ChatHistoryMessage]
    created_at: str
    updated_at: str


class ChatHistoryListItem(BaseModel):
    """A chat history item for list views (without full messages)"""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ChatHistorySave(BaseModel):
    """Request model for saving a chat history"""
    id: Optional[str] = None
    messages: List[ChatHistoryMessage]

