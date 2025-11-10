"""Google Maps Places tool - MCP-style tool for finding date activities using Google Maps"""
import googlemaps
import os

from typing import List, Dict, Any, Optional, Tuple

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


def search_places_for_dates(
    location1: str,
    location2: str,
    place_types: Optional[List[str]] = None,
    price_level: Optional[int] = None,
    min_rating: float = 4.0,
    radius: float = 10.0,
    check_weather: bool = False,
    user_interests: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for date activities between two locations using Google Maps Places API
    
    Args:
        location1: First location (address or coordinates as "lat,lng")
        location2: Second location (address or coordinates as "lat,lng")
        place_types: List of place types (e.g., ["cafe", "restaurant", "park", "tourist_attraction"])
        price_level: Price level filter (0-4, where 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive)
        min_rating: Minimum rating threshold (default: 4.0, scale: 1.0-5.0)
        radius: Max distance from midpoint in miles (default: 10mi)
        check_weather: Boolean to include weather info
        user_interests: List of interests for review matching
        
    Returns:
        Dictionary with list of activities and metadata
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        return {
            "error": "GOOGLE_MAPS_API_KEY not set. Please set it in your .env file.",
            "activities": []
        }
    
    try:
        gmaps = googlemaps.Client(key=api_key)
        
        # Geocode both locations
        loc1_data = _geocode_location(gmaps, location1)
        loc2_data = _geocode_location(gmaps, location2)
        
        if not loc1_data or not loc2_data:
            return {
                "error": f"Could not geocode one or both locations. Location1: {location1}, Location2: {location2}",
                "activities": []
            }
        
        # Calculate midpoint
        midpoint_lat, midpoint_lng = _calculate_midpoint(
            loc1_data["lat"], loc1_data["lng"],
            loc2_data["lat"], loc2_data["lng"]
        )
        
        # Default place types if not provided
        if not place_types:
            place_types = ["cafe", "restaurant", "park", "tourist_attraction"]
        
        activities = []
        
        # Search for each place type
        for place_type in place_types:
            # Build search query
            query = place_type
            
            # Use Places API Text Search
            places_result = gmaps.places_nearby(
                location=(midpoint_lat, midpoint_lng),
                radius=int(radius * NUM_METERS_PER_MILE),
                type=place_type
            )
            
            # Also try text search as fallback
            if not places_result.get("results"):
                text_search = gmaps.places(
                    query=query,
                    location=(midpoint_lat, midpoint_lng),
                    radius=int(radius * NUM_METERS_PER_MILE)
                )
                if text_search.get("results"):
                    places_result = text_search
            
            # Process each place
            for place in places_result.get("results", [])[:10]:  # Limit to 10 per type
                place_id = place.get("place_id")
                rating = place.get("rating")
                price_level_place = place.get("price_level")
                
                if rating and rating < min_rating:
                    continue
                
                if price_level is not None and price_level_place is not None:
                    if price_level_place != price_level:
                        continue
                
                try:
                    place_details = gmaps.place(
                        place_id=place_id,
                        fields=["name", "formatted_address", "rating", "price_level", 
                               "opening_hours", "reviews", "photos", "geometry", "url", "types"]
                    )
                    
                    details = place_details.get("result", {})
                    
                    reviews = details.get("reviews", [])
                    review_analysis = _analyze_reviews(reviews, user_interests)
                    
                    opening_hours = details.get("opening_hours", {})
                    hours_text = None
                    if opening_hours:
                        periods = opening_hours.get("weekday_text", [])
                        if periods:
                            hours_text = "\n".join(periods)
                    
                    geometry = details.get("geometry", {})
                    location_coords = geometry.get("location", {})
                    
                    activity = {
                        "name": details.get("name", place.get("name", "Unknown")),
                        "location": details.get("formatted_address", place.get("vicinity", "Unknown")),
                        "description": review_analysis.get("summary", ""),
                        "price": f"${'$' * (price_level_place or 0)}" if price_level_place is not None else None,
                        "date": None,  # Not applicable for places
                        "url": details.get("url"),
                        "image_url": None,  # Could extract from photos if needed
                        "category": place_type.replace("_", " ").title(),
                        "gmaps_place_id": place_id,
                        "gmaps_rating": rating,
                        "gmaps_price_level": price_level_place,
                        "gmaps_opening_hours": hours_text or opening_hours,
                        "gmaps_review_summary": review_analysis.get("summary"),
                        "coordinates": {
                            "lat": location_coords.get("lat"),
                            "lng": location_coords.get("lng")
                        } if location_coords else None
                    }
                    
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
        
        return {
            "activities": activities,
            "midpoint": {
                "lat": midpoint_lat,
                "lng": midpoint_lng
            },
            "location1": loc1_data.get("formatted_address", location1),
            "location2": loc2_data.get("formatted_address", location2),
            "count": len(activities)
        }
        
    except Exception as e:
        return {
            "error": f"Error searching places: {str(e)}",
            "activities": []
        }


TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_places_for_dates",
        "description": "Search for date activities between two locations using Google Maps. Finds places like coffee shops, restaurants, parks, and attractions that are between the two locations, filtered by price, rating, and user interests.",
        "parameters": {
            "type": "object",
            "properties": {
                "location1": {
                    "type": "string",
                    "description": "First location (address or coordinates as 'lat,lng')"
                },
                "location2": {
                    "type": "string",
                    "description": "Second location (address or coordinates as 'lat,lng')"
                },
                "place_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of place types to search for (e.g., ['cafe', 'restaurant', 'park', 'tourist_attraction'])"
                },
                "price_level": {
                    "type": "integer",
                    "description": "Price level filter (0-4, where 0=Free, 1=Inexpensive, 2=Moderate, 3=Expensive, 4=Very Expensive)"
                },
                "min_rating": {
                    "type": "number",
                    "description": "Minimum rating threshold (default: 4.0, scale: 1.0-5.0)"
                },
                "radius": {
                    "type": "number",
                    "description": "Max distance from midpoint in miles (default: 10mi)"
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
            "required": ["location1", "location2"]
        }
    }
}

