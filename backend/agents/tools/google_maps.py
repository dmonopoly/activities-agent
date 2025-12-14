"""Google Maps Places tool - MCP-style tool for finding date activities using Google Maps"""
import googlemaps
import os
import random

from typing import List, Dict, Any, Optional, Tuple

from agents.config import ENABLE_GOOGLE_MAPS_API
from agents.mock_data import MOCK_TRANSIT_STOPS, MOCK_PLACES

try:
    from agents.tools.weather import get_weather_for_location
except ImportError:
    get_weather_for_location = None

NUM_METERS_PER_MILE = 1609.34

def _calculate_midpoint(lat1: float, lng1: float, lat2: float, lng2: float) -> Tuple[float, float]:
    """Calculate midpoint between two coordinates"""
    mid_lat = (lat1 + lat2) / 2
    mid_lng = (lng1 + lng2) / 2
    return (mid_lat, mid_lng)


def _geocode_location(gmaps_client: googlemaps.Client, location: str) -> Optional[Dict[str, Any]]:
    """Geocode a location string to coordinates"""
    try:
        geocode_result = gmaps_client.geocode(location)
        if geocode_result:
            location_data = geocode_result[0]
            geometry = location_data.get("geometry", {})
            location_coords = geometry.get("location", {})
            return {
                "lat": location_coords.get("lat"),
                "lng": location_coords.get("lng"),
                "formatted_address": location_data.get("formatted_address", location)
            }
        return None
    except Exception as e:
        print(f"Geocoding error for {location}: {e}")
        return None


def _analyze_reviews(reviews: List[Dict[str, Any]], user_interests: Optional[List[str]] = None) -> Dict[str, Any]:
    """Analyze reviews to extract insights and match with user interests"""
    if not reviews:
        return {
            "summary": "",
            "unique_indicators": [],
            "interest_matches": []
        }
    
    all_text = " ".join([r.get("text", "") for r in reviews]).lower()
    
    # Look for uniqueness indicators
    unique_keywords = ["hidden gem", "unique", "one-of-a-kind", "special", "unusual", "different", "authentic", "local favorite"]
    unique_indicators = [kw for kw in unique_keywords if kw in all_text]
    
    # Match with user interests if provided
    interest_matches = []
    if user_interests:
        for interest in user_interests:
            interest_lower = interest.lower()
            # Check if interest appears in review text
            if interest_lower in all_text:
                interest_matches.append(interest)
            # Also check for related keywords
            interest_keywords = {
                "outdoor": ["outdoor", "park", "hiking", "nature", "trail", "scenic"],
                "art": ["art", "gallery", "museum", "exhibition", "creative"],
                "music": ["music", "live", "performance", "concert", "jazz", "acoustic"],
                "food": ["food", "cuisine", "restaurant", "dining", "menu", "delicious"],
                "coffee": ["coffee", "cafe", "espresso", "latte", "brew"],
                "romantic": ["romantic", "intimate", "cozy", "date", "couple"]
            }
            if interest_lower in interest_keywords:
                for keyword in interest_keywords[interest_lower]:
                    if keyword in all_text:
                        interest_matches.append(interest)
                        break
    
    # Create summary
    summary_parts = []
    if unique_indicators:
        summary_parts.append(f"Reviewers mention: {', '.join(unique_indicators[:3])}")
    if interest_matches:
        summary_parts.append(f"Matches interests: {', '.join(set(interest_matches))}")
    
    return {
        "summary": ". ".join(summary_parts) if summary_parts else "No specific insights from reviews",
        "unique_indicators": unique_indicators,
        "interest_matches": list(set(interest_matches))
    }


def get_transit_stops_between(
    location_a: str,
    location_b: str
) -> Dict[str, Any]:
    """
    Get transit stops along the route between two locations.
    
    Uses Google Maps Directions API with transit mode to find stops
    (subway stations, bus stops, etc.) along the route.
    
    Args:
        location_a: First location (address or coordinates as "lat,lng")
        location_b: Second location (address or coordinates as "lat,lng")
        
    Returns:
        Dictionary with list of transit stops and metadata:
        {
            "stops": [{"name": str, "lat": float, "lng": float, "type": str}, ...],
            "location_a": str,
            "location_b": str,
            "error": str (optional)
        }
    """
    print(f"[GMAPS] get_transit_stops_between called: location_a={location_a}, location_b={location_b}")
    print(f"[GMAPS] ENABLE_GOOGLE_MAPS_API={ENABLE_GOOGLE_MAPS_API}")
    
    if not ENABLE_GOOGLE_MAPS_API:
        num_stops = random.randint(3, 6)
        mock_stops = random.sample(MOCK_TRANSIT_STOPS, min(num_stops, len(MOCK_TRANSIT_STOPS)))
        print(f"[GMAPS] ❌ API DISABLED - returning MOCK transit stops")
        print(f"[GMAPS] Mock response: {len(mock_stops)} stops - {[s['name'] for s in mock_stops]}")
        return {
            "stops": mock_stops,
            "location_a": location_a,
            "location_b": location_b,
            "stop_count": len(mock_stops)
        }
    
    print(f"[GMAPS] ✅ API ENABLED - calling Google Maps Directions API")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return {
            "error": "GOOGLE_MAPS_API_KEY not set. Please set it in your .env file.",
            "stops": []
        }
    
    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Get transit directions
        directions_result = gmaps.directions(
            origin=location_a,
            destination=location_b,
            mode="transit"
        )
        
        if not directions_result:
            return {
                "error": f"No transit route found between {location_a} and {location_b}",
                "stops": []
            }
        
        # Extract stops from the route
        stops = []
        seen_stops = set()  # Track unique stops by name
        
        route = directions_result[0]
        legs = route.get("legs", [])
        
        for leg in legs:
            steps = leg.get("steps", [])
            
            for step in steps:
                # Only process transit steps
                if step.get("travel_mode") != "TRANSIT":
                    continue
                
                transit_details = step.get("transit_details", {})
                
                # Get departure stop
                departure_stop = transit_details.get("departure_stop", {})
                if departure_stop:
                    stop_name = departure_stop.get("name", "")
                    if stop_name and stop_name not in seen_stops:
                        seen_stops.add(stop_name)
                        location = departure_stop.get("location", {})
                        line = transit_details.get("line", {})
                        vehicle = line.get("vehicle", {})
                        stops.append({
                            "name": stop_name,
                            "lat": location.get("lat"),
                            "lng": location.get("lng"),
                            "type": vehicle.get("type", "TRANSIT"),
                            "line_name": line.get("short_name") or line.get("name", "")
                        })
                
                # Get arrival stop
                arrival_stop = transit_details.get("arrival_stop", {})
                if arrival_stop:
                    stop_name = arrival_stop.get("name", "")
                    if stop_name and stop_name not in seen_stops:
                        seen_stops.add(stop_name)
                        location = arrival_stop.get("location", {})
                        line = transit_details.get("line", {})
                        vehicle = line.get("vehicle", {})
                        stops.append({
                            "name": stop_name,
                            "lat": location.get("lat"),
                            "lng": location.get("lng"),
                            "type": vehicle.get("type", "TRANSIT"),
                            "line_name": line.get("short_name") or line.get("name", "")
                        })
        
        return {
            "stops": stops,
            "location_a": location_a,
            "location_b": location_b,
            "stop_count": len(stops)
        }
        
    except Exception as e:
        return {
            "error": f"Error getting transit stops: {str(e)}",
            "stops": []
        }


def search_places_for_dates(
    location1: str,
    location2: Optional[str] = None,
    place_types: Optional[List[str]] = None,
    price_level: Optional[int] = None,
    min_rating: float = 4.0,
    radius: float = 0.5,
    check_weather: bool = False,
    user_interests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for date activities near one location or between two locations.
    
    Intelligently chooses search strategy:
    - For two locations: tries transit stops first (great for cities like NYC, SF, Chicago),
      falls back to midpoint if no transit available (car-centric areas)
    - For one location: searches near that location
    
    Args:
        location1: First location (address or coordinates as "lat,lng")
        location2: Second location (optional - if not provided, searches near location1)
        place_types: List of place types (e.g., ["cafe", "restaurant", "park", "tourist_attraction"])
        price_level: Max price level filter (0-4, where 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive)
        min_rating: Minimum rating threshold (default: 4.0, scale: 1.0-5.0)
        radius: Search radius in miles per search point (default: 0.5mi for transit stops, auto-expanded for midpoint)
        check_weather: Boolean to include weather info for outdoor activities
        user_interests: List of interests for review matching (e.g., ["outdoor", "art", "coffee"])
        
    Returns:
        Dictionary with list of activities and metadata including search_mode used
    """
    print(f"[GMAPS] search_places_for_dates called: location={location}, place_types={place_types}, radius={radius}mi")
    print(f"[GMAPS] ENABLE_GOOGLE_MAPS_API={ENABLE_GOOGLE_MAPS_API}")
    
    if not ENABLE_GOOGLE_MAPS_API:
        num_places = random.randint(3, 6)
        mock_activities = [p.copy() for p in random.sample(MOCK_PLACES, min(num_places, len(MOCK_PLACES)))]
        # Add near_stop field to match expected format
        for activity in mock_activities:
            activity["near_stop"] = location
        print(f"[GMAPS] ❌ API DISABLED - returning MOCK places")
        print(f"[GMAPS] Mock response: {len(mock_activities)} places - {[a['name'] for a in mock_activities]}")
        return {
            "activities": mock_activities,
            "search_location": location,
            "count": len(mock_activities)
        }
    
    print(f"[GMAPS] ✅ API ENABLED - calling Google Maps Places API")
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return {
            "error": "GOOGLE_MAPS_API_KEY not set. Please set it in your .env file.",
            "activities": []
        }
    
    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Default place types if not provided
        if not place_types:
            place_types = ["cafe", "restaurant", "park", "tourist_attraction"]
        
        # Determine search points based on locations provided
        search_points = []
        search_mode = "single_location"
        
        if location2:
            # Two locations: try transit-aware search first, fallback to midpoint
            transit_result = get_transit_stops_between(location1, location2)
            
            if transit_result.get("stops") and len(transit_result["stops"]) >= 2:
                # Transit available - use stops along the route
                search_mode = "transit_stops"
                search_points = [
                    {
                        "name": stop["name"],
                        "lat": stop["lat"],
                        "lng": stop["lng"],
                        "type": stop.get("type", "TRANSIT")
                    }
                    for stop in transit_result["stops"]
                ]
                effective_radius = radius  # Use smaller radius per stop. TODO: Do only 1 search for stops near each other.
            else:
                # No transit - fallback to midpoint (car-centric area)
                search_mode = "midpoint"
                loc1_data = _geocode_location(gmaps, location1)
                loc2_data = _geocode_location(gmaps, location2)
                
                if not loc1_data or not loc2_data:
                    return {
                        "error": f"Could not geocode locations. Location1: {location1}, Location2: {location2}",
                        "activities": []
                    }
                
                midpoint_lat, midpoint_lng = _calculate_midpoint(
                    loc1_data["lat"], loc1_data["lng"],
                    loc2_data["lat"], loc2_data["lng"]
                )
                search_points = [{
                    "name": "Midpoint",
                    "lat": midpoint_lat,
                    "lng": midpoint_lng,
                    "type": "midpoint"
                }]
                # Use larger radius for midpoint since it's a single search point
                effective_radius = max(radius * 4, 2.0)
        else:
            # Single location search
            loc_data = _geocode_location(gmaps, location1)
            if not loc_data:
                return {
                    "error": f"Could not geocode location: {location1}",
                    "activities": []
                }
            search_points = [{
                "name": loc_data["formatted_address"],
                "lat": loc_data["lat"],
                "lng": loc_data["lng"],
                "type": "origin"
            }]
            effective_radius = radius
        
        # Search for activities near each search point
        activities = []
        seen_place_ids = set()
        
        for search_point in search_points:
            search_lat = search_point["lat"]
            search_lng = search_point["lng"]
            
            for place_type in place_types:
                places_result = gmaps.places_nearby(
                    location=(search_lat, search_lng),
                    radius=int(effective_radius * NUM_METERS_PER_MILE),
                    type=place_type
                )
                
                # Fallback to text search if no results
                if not places_result.get("results"):
                    text_search = gmaps.places(
                        query=place_type,
                        location=(search_lat, search_lng),
                        radius=int(effective_radius * NUM_METERS_PER_MILE)
                    )
                    if text_search.get("results"):
                        places_result = text_search
                
                # Limit per type per location (more for midpoint since it's single point)
                limit = 10 if search_mode == "midpoint" else 5
                
                for place in places_result.get("results", [])[:limit]:
                    place_id = place.get("place_id")
                    
                    # Deduplicate across search points
                    if place_id in seen_place_ids:
                        continue
                    seen_place_ids.add(place_id)
                    
                    rating = place.get("rating")
                    price_level_place = place.get("price_level")
                    
                    if rating and rating < min_rating:
                        continue
                    
                    # Filter by max price level (not exact match)
                    if price_level is not None and price_level_place is not None:
                        if price_level_place > price_level:
                            continue
                    
                    try:
                        place_details = gmaps.place(
                            place_id=place_id,
                            fields=["name", "formatted_address", "rating", "price_level", 
                                   "opening_hours", "reviews", "geometry", "url", "types"]
                        )
                        
                        details = place_details.get("result", {})
                        reviews = details.get("reviews", [])
                        review_analysis = _analyze_reviews(reviews, user_interests)
                        
                        opening_hours = details.get("opening_hours", {})
                        hours_text = None
                        if opening_hours:
                            periods = opening_hours.get("weekday_text", [])
                            if periods:
                                hours_text = "; ".join(periods)
                        
                        geometry = details.get("geometry", {})
                        location_coords = geometry.get("location", {})
                        
                        activity = {
                            "name": details.get("name", place.get("name", "Unknown")),
                            "location": details.get("formatted_address", place.get("vicinity", "Unknown")),
                            "description": review_analysis.get("summary", ""),
                            "price": f"${'$' * (price_level_place or 0)}" if price_level_place is not None else None,
                            "opening_hours": hours_text,
                            "url": details.get("url"),
                            "category": place_type.replace("_", " ").title(),
                            "gmaps_place_id": place_id,
                            "gmaps_rating": rating,
                            "gmaps_price_level": price_level_place,
                            "near_stop": search_point["name"],
                            "coordinates": {
                                "lat": location_coords.get("lat"),
                                "lng": location_coords.get("lng")
                            } if location_coords else None
                        }
                        
                        # Add weather info if requested (useful for outdoor activities)
                        if check_weather and get_weather_for_location:
                            coords = activity.get("coordinates")
                            if coords:
                                weather_location = f"{coords['lat']},{coords['lng']}"
                                weather_info = get_weather_for_location(weather_location)
                                if "error" not in weather_info:
                                    activity["weather_info"] = weather_info
                        
                        activities.append(activity)
                        
                    except Exception as e:
                        print(f"Error getting details for place {place_id}: {e}")
                        continue
        
        activities.sort(key=lambda x: x.get("gmaps_rating", 0) or 0, reverse=True)
        
        result = {
            "activities": activities,
            "search_mode": search_mode,
            "search_points": [{"name": sp["name"], "type": sp["type"]} for sp in search_points],
            "location1": location1,
            "count": len(activities)
        }
        
        if location2:
            result["location2"] = location2
        
        return result
        
    except Exception as e:
        return {
            "error": f"Error searching places: {str(e)}",
            "activities": []
        }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_places_for_dates",
        "description": "Search for date activities near one location or between two locations using Google Maps. Intelligently chooses search strategy: for transit-friendly cities (NYC, SF, Chicago), searches along transit stops; for car-centric areas, searches around midpoint. Finds places like coffee shops, restaurants, parks, and attractions.",
        "parameters": {
            "type": "object",
            "properties": {
                "location1": {
                    "type": "string",
                    "description": "First/primary location (address or coordinates as 'lat,lng')"
                },
                "location2": {
                    "type": "string",
                    "description": "Second location (optional - if provided, searches between locations; if omitted, searches near location1)"
                },
                "place_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of place types to search for (e.g., ['cafe', 'restaurant', 'park', 'tourist_attraction'])"
                },
                "price_level": {
                    "type": "integer",
                    "description": "Maximum price level filter (0-4, where 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive)"
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum rating threshold (default: 4.0, scale: 1.0-5.0)"
                },
                "radius": {
                    "type": "number",
                    "description": "Search radius in miles per search point (default: 0.5mi, auto-expanded for car-centric areas)"
                },
                "check_weather": {
                    "type": "boolean",
                    "description": "Whether to include weather information for outdoor activities (default: false)"
                },
                "user_interests": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of user interests for matching against reviews (e.g., ['outdoor', 'art', 'coffee'])"
                }
            },
            "required": ["location1"]
        }
    }
}

