"""
Database configuration module.

Provides MongoDB client access for production deployments.
If MONGODB_URI is not set, the application uses JSON file storage instead.

Environment Variables:
- MONGODB_URI: MongoDB connection string (if unset, uses JSON files)
- MONGODB_DATABASE: Database name (default: activities_agent)
- MONGODB_USER_PREFERENCES_COLLECTION: Collection for user preferences (default: user_preferences)
- MONGODB_CHAT_HISTORY_COLLECTION: Collection for chat history (default: chat_histories)
"""

import os
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

# Client singleton (lazily initialized on first use)
_client: Optional[MongoClient] = None


def is_mongodb_enabled() -> bool:
    """Check if MongoDB is configured via environment variables."""
    return bool(os.getenv("MONGODB_URI"))


def get_mongo_client() -> MongoClient:
    """
    Get the MongoDB client singleton.
    
    Returns:
        MongoClient instance
        
    Raises:
        ValueError: If MONGODB_URI is not set
    """
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        print(f"tmp delete [DEBUG] Connecting to MongoDB at {uri}")
        _client = MongoClient(uri)
    return _client


def get_database() -> Database:
    """
    Get the MongoDB database.
    
    Returns:
        Database instance for the configured database name
    """
    client = get_mongo_client()
    db_name = os.getenv("MONGODB_DATABASE", "activities_agent")
    return client[db_name]


def get_user_preferences_collection() -> Collection:
    """
    Get the user preferences collection.
    
    Returns:
        Collection instance for user preferences
    """
    db = get_database()
    collection_name = os.getenv("MONGODB_USER_PREFERENCES_COLLECTION", "user_preferences")
    return db[collection_name]


def get_chat_history_collection() -> Collection:
    """
    Get the chat history collection.
    
    Returns:
        Collection instance for chat histories
    """
    db = get_database()
    collection_name = os.getenv("MONGODB_CHAT_HISTORY_COLLECTION", "chat_histories")
    return db[collection_name]
