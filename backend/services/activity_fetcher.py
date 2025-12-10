"""Activity Fetcher Service: Intelligently fetches activities between locations"""
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from agents.tools.google_maps import (
    get_transit_stops_between,
    search_places_near_location
)
from agents.tools.preferences import get_user_preferences


# Map interests to Google Maps place types (easier to cache)
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


def _budget_to_price_level(budget_min: Optional[float], budget_max: Optional[float]) -> Optional[int]:
    """
    Map budget range to Google Maps price level (0-4).
    
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
        "date": activity.get("date", ""),  # Opening hours
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
    
    If two locations are provided, finds transit stops between them and
    queries activities near each stop. If only one location, queries
    activities near that location.
    
    Args:
        location_a: First location (required)
        location_b: Second location (optional)
        user_id: User ID for fetching preferences
        
    Returns:
        Dictionary with:
        - activities: List of activities in sheets-compatible format
        - query_locations: List of locations that were queried
        - location_a: The resolved first location
        - location_b: The second location (or None)
        - error: Error message if any
    """
    prefs = get_user_preferences(user_id)
    
    interests = prefs.get("interests", [])
    budget_min = prefs.get("budget_min")
    budget_max = prefs.get("budget_max")
    
    # Convert preferences to Google Maps parameters
    place_types = _interests_to_place_types(interests)
    price_level = _budget_to_price_level(budget_min, budget_max)
    
    query_locations = []
    
    if location_b:
        transit_result = get_transit_stops_between(location_a, location_b)
        
        if transit_result.get("error"):
            query_locations = [
                {"name": location_a, "lat": None, "lng": None},
                {"name": location_b, "lat": None, "lng": None}
            ]
        else:
            stops = transit_result.get("stops", [])
            if stops:
                query_locations = stops
            else:
                query_locations = [
                    {"name": location_a, "lat": None, "lng": None},
                    {"name": location_b, "lat": None, "lng": None}
                ]
    else:
        query_locations = [{"name": location_a, "lat": None, "lng": None}]
    
    # Fetch activities near each query location
    all_activities = []
    seen_place_ids = set()  # Deduplicate by place ID
    
    for loc in query_locations:
        # Use coordinates if available, otherwise use name
        if loc.get("lat") and loc.get("lng"):
            search_location = f"{loc['lat']},{loc['lng']}"
        else:
            search_location = loc.get("name", location_a)
        
        result = search_places_near_location(
            location=search_location,
            place_types=place_types,
            price_level=price_level,
            min_rating=4.0,
            radius=0.5,  # 0.5 mile radius around each stop
            user_interests=interests
        )
        
        if result.get("error"):
            continue
        
        for activity in result.get("activities", []):
            place_id = activity.get("gmaps_place_id")
            if place_id and place_id not in seen_place_ids:
                seen_place_ids.add(place_id)
                all_activities.append(activity)
    
    # Sort by rating
    all_activities.sort(key=lambda x: x.get("gmaps_rating", 0) or 0, reverse=True)
    
    # Format for sheets compatibility
    formatted_activities = [_format_activity_for_sheets(a) for a in all_activities]
    
    return {
        "activities": formatted_activities,
        "query_locations": [
            {"name": loc.get("name"), "type": loc.get("type", "location")}
            for loc in query_locations
        ],
        "location_a": location_a,
        "location_b": location_b,
        "preferences_used": {
            "interests": interests,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "place_types": place_types,
            "price_level": price_level
        },
        "total_count": len(formatted_activities)
    }

