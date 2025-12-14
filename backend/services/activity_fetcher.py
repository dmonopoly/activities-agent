"""Activity Fetcher Service: Fetches activities using shared google_maps tool with user preferences"""
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agents.tools.google_maps import search_places_for_dates
from agents.tools.preferences import get_user_preferences


# Map interests to Google Maps place types
INTEREST_TO_PLACE_TYPES = {
    "outdoor": ["park", "hiking_area", "campground"],
    "art": ["art_gallery", "museum"],
    "music": ["night_club", "bar"],
    "food": ["restaurant", "bakery"],
    "coffee": ["cafe"],
    "unique coffee shops": ["cafe"],
    "romantic": ["restaurant", "spa"],
    "shopping": ["shopping_mall", "clothing_store"],
    "entertainment": ["movie_theater", "amusement_park", "bowling_alley"],
    "nature": ["park", "zoo", "aquarium"],
    "walks": ["park", "tourist_attraction"],
    "beautiful views": ["tourist_attraction", "park"],
    "views": ["tourist_attraction", "park"],
}

# Default place types if no interests specified
DEFAULT_PLACE_TYPES = ["cafe", "restaurant", "park", "tourist_attraction"]


def _budget_to_price_level(budget_max: Optional[float]) -> Optional[int]:
    """
    Map budget to Google Maps price level (0-4).
    
    Price levels:
    - 0: Free
    - 1: Inexpensive (~$10-15)
    - 2: Moderate (~$15-30)
    - 3: Expensive (~$30-60)
    - 4: Very Expensive ($60+)
    """
    if budget_max is None:
        return None
    
    if budget_max <= 0:
        return 0
    elif budget_max <= 15:
        return 1
    elif budget_max <= 30:
        return 2
    elif budget_max <= 60:
        return 3
    else:
        return 4


def _interests_to_place_types(interests: Optional[List[str]]) -> List[str]:
    """Convert user interests to Google Maps place types."""
    if not interests:
        return DEFAULT_PLACE_TYPES
    
    place_types = set()
    for interest in interests:
        interest_lower = interest.lower()
        if interest_lower in INTEREST_TO_PLACE_TYPES:
            place_types.update(INTEREST_TO_PLACE_TYPES[interest_lower])
        else:
            # Try using the interest directly as a place type
            place_types.add(interest_lower.replace(" ", "_"))
    
    return list(place_types) if place_types else DEFAULT_PLACE_TYPES


def _format_activity_for_sheets(activity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format an activity to be compatible with Google Sheets export.
    
    Ensures the activity has the required fields:
    name, location, description, price, date, category, url
    """
    return {
        "name": activity.get("name", ""),
        "location": activity.get("location", ""),
        "description": activity.get("description", ""),
        "price": activity.get("price", ""),
        "opening_hours": activity.get("opening_hours", ""),
        "category": activity.get("category", ""),
        "url": activity.get("url", ""),
        # Additional metadata (won't break sheets but useful for UI)
        "gmaps_rating": activity.get("gmaps_rating"),
        "near_stop": activity.get("near_stop"),
        "coordinates": activity.get("coordinates"),
    }


def fetch_activities(
    location_a: str,
    location_b: Optional[str],
    user_id: str
) -> Dict[str, Any]:
    """
    Fetch activities based on one or two locations and user preferences.
    
    This is a thin wrapper around search_places_for_dates that:
    1. Loads user preferences automatically
    2. Converts preferences to search parameters
    3. Formats results for sheets compatibility
    
    The underlying search_places_for_dates intelligently chooses:
    - Transit stops approach for cities with public transit (NYC, SF, etc.)
    - Midpoint approach for car-centric areas
    
    Args:
        location_a: First location (required)
        location_b: Second location (optional)
        user_id: User ID for fetching preferences
        
    Returns:
        Dictionary with activities and metadata
    """
    prefs = get_user_preferences(user_id)
    
    interests = prefs.get("interests", [])
    budget_max = prefs.get("budget_max")
    
    # Convert preferences to Google Maps parameters
    place_types = _interests_to_place_types(interests)
    price_level = _budget_to_price_level(budget_max)
    
    # Use the unified search function (handles transit vs midpoint internally)
    result = search_places_for_dates(
        location1=location_a,
        location2=location_b,
        place_types=place_types,
        price_level=price_level,
        min_rating=4.0,
        radius=0.5,
        user_interests=interests
    )
    
    if result.get("error"):
        return {
            "activities": [],
            "error": result["error"],
            "location_a": location_a,
            "location_b": location_b
        }
    
    # Format for sheets compatibility
    formatted_activities = [_format_activity_for_sheets(a) for a in result.get("activities", [])]
    
    return {
        "activities": formatted_activities,
        "search_mode": result.get("search_mode"),
        "query_locations": result.get("search_points", []),
        "location_a": location_a,
        "location_b": location_b,
        "preferences_used": {
            "interests": interests,
            "budget_max": budget_max,
            "place_types": place_types,
            "price_level": price_level
        },
        "total_count": len(formatted_activities)
    }

