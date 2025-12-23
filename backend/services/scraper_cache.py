"""
Cache management for scraped activities.

The cache stores activities in a JSON file with the following structure:
{
    "last_updated": "2025-12-23T10:00:00Z",  # ISO timestamp
    "activities": [...]  # List of activity dicts
}

Activity Dict Fields (see scraper_sites.py for full documentation):
    name, location, description, price, date, url, source, category
"""
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# Cache file location (relative to backend directory)
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE_FILE = os.path.join(CACHE_DIR, "activities_cache.json")


def _ensure_cache_dir():
    """Ensure the cache directory exists."""
    os.makedirs(CACHE_DIR, exist_ok=True)


def load_cache() -> Dict[str, Any]:
    """
    Load activities cache from JSON file.
    
    Returns:
        Dict with 'last_updated' (str or None) and 'activities' (list)
    """
    _ensure_cache_dir()
    
    if not os.path.exists(CACHE_FILE):
        return {"last_updated": None, "activities": []}
    
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[CACHE] Error loading cache: {e}")
        return {"last_updated": None, "activities": []}


def save_cache(activities: List[Dict[str, Any]]) -> bool:
    """
    Save activities to cache file.
    
    Args:
        activities: List of activity dicts
        
    Returns:
        True if save successful, False otherwise
    """
    _ensure_cache_dir()
    
    cache_data = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "activities": activities
    }
    
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        print(f"[CACHE] Saved {len(activities)} activities to cache")
        return True
    except IOError as e:
        print(f"[CACHE] Error saving cache: {e}")
        return False


def get_cached_activities(
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Query cached activities with optional filtering.
    
    Args:
        query: Search query to match against name/description/category
        filters: Optional filters dict with keys:
            - category (str): Filter by category
            - max_price (int): Maximum price in dollars
            - source (str): Filter by source site
            
    Returns:
        List of matching activity dicts
    """
    cache = load_cache()
    activities = cache.get("activities", [])
    
    if not activities:
        return []
    
    results = activities
    
    if query:
        query_lower = query.lower()
        results = [
            a for a in results
            if query_lower in a.get("name", "").lower()
            or query_lower in a.get("description", "").lower()
            or query_lower in a.get("category", "").lower()
        ]
    
    if filters:
        if "category" in filters and filters["category"]:
            cat_lower = filters["category"].lower()
            results = [
                a for a in results
                if cat_lower in a.get("category", "").lower()
            ]
        
        if "max_price" in filters and filters["max_price"] is not None:
            max_price = filters["max_price"]
            filtered = []
            for a in results:
                price_str = a.get("price", "")
                if not price_str or price_str.lower() == "free":
                    filtered.append(a)
                else:
                    price_match = re.search(r'\d+', price_str)
                    if price_match and int(price_match.group()) <= max_price:
                        filtered.append(a)
            results = filtered
        
        if "source" in filters and filters["source"]:
            source_lower = filters["source"].lower()
            results = [
                a for a in results
                if source_lower in a.get("source", "").lower()
            ]
    
    return results


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.
    
    Returns:
        Dict with:
            - last_updated (str or None): ISO timestamp of last update
            - total_activities (int): Total cached activities
            - by_source (dict): Count breakdown by source site
    """
    cache = load_cache()
    activities = cache.get("activities", [])
    
    sources = {}
    for a in activities:
        source = a.get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1
    
    return {
        "last_updated": cache.get("last_updated"),
        "total_activities": len(activities),
        "by_source": sources
    }

