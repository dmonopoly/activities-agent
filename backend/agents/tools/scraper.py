"""
Web scraping tool - MCP-style tool for searching cached activity data.

This module exposes only the tool interface (scrape_activities function and
TOOL_DEFINITION). The actual scraping and caching logic lives in services/.
"""
from typing import List, Dict, Any, Optional

from services.scraper_cache import get_cached_activities, get_cache_stats


def scrape_activities(
    query: str,
    location_a: Optional[str] = None, 
    location_b: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Search for activities from the cached scraped data.
    
    This function reads from a local cache of scraped activities.
    The cache is updated periodically by a background scraper.
    
    Args:
        query: Search query for activities
        location_a: Primary location to search in (currently supports NYC area)
        location_b: Optional second location (for filtering)
        filters: Optional filters dict:
            - category (str): Filter by category
            - max_price (int): Maximum price in dollars
            - source (str): Filter by source site
        
    Returns:
        List of activity dicts with fields:
            name, location, description, price, date, url, source, category
    """
    activities = get_cached_activities(query=query, filters=filters)
    
    # If locations are specified, filter by them (basic text matching)
    if location_a or location_b:
        location_terms = []
        if location_a:
            location_terms.extend(location_a.lower().split())
        if location_b:
            location_terms.extend(location_b.lower().split())
        
        if location_terms:
            location_filtered = []
            for activity in activities:
                activity_location = activity.get("location", "").lower()
                activity_name = activity.get("name", "").lower()
                activity_desc = activity.get("description", "").lower()
                combined = f"{activity_location} {activity_name} {activity_desc}"
                
                # Include if any location term matches, or if it's a general NYC event
                if any(term in combined for term in location_terms) or "nyc" in combined or "new york" in combined:
                    location_filtered.append(activity)
            
            if location_filtered:
                activities = location_filtered
    
    # If cache is empty, return a helpful notice
    if not activities:
        cache_stats = get_cache_stats()
        if cache_stats["total_activities"] == 0:
            return [{
                "name": "No activities cached yet",
                "location": "NYC",
                "description": "The activity cache is empty. A background scraper will populate it shortly, or you can trigger a manual scrape via POST /api/scrape.",
                "price": "",
                "date": "",
                "url": "",
                "source": "system",
                "category": "Notice"
            }]
        else:
            return [{
                "name": f"No activities found matching '{query}'",
                "location": "NYC",
                "description": f"Try a different search term. There are {cache_stats['total_activities']} activities in the cache.",
                "price": "",
                "date": "",
                "url": "",
                "source": "system",
                "category": "Notice"
            }]
    
    return activities


# Tool definition for LLM function calling
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "scrape_activities",
        "description": "Search for activities and events in NYC from cached scraped data (sources: theskint, timeout, eventbrite). Returns events matching the query and filters.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for activities (e.g., 'free comedy', 'outdoor events', 'live music', 'art gallery')"
                },
                "location_a": {
                    "type": "string",
                    "description": "Primary location/neighborhood (e.g., 'Brooklyn', 'Manhattan', 'East Village')"
                },
                "location_b": {
                    "type": "string",
                    "description": "Optional second location for finding activities in a broader area"
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Activity category (e.g., 'Music', 'Comedy', 'Arts', 'Food & Drink', 'Outdoor', 'Theater')"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price in dollars (events marked 'Free' are always included)"
                        },
                        "source": {
                            "type": "string",
                            "description": "Filter by source site: 'theskint', 'timeout', or 'eventbrite'"
                        }
                    }
                }
            },
            "required": ["query"]
        }
    }
}
