"""
Mock data for simulating API responses when APIs are disabled.

This module contains mock data structures that match the real API response formats,
allowing the application to be demoed without incurring API costs.

Each mock data section documents the expected structure based on the real API.
"""

import json
from typing import Dict, List, Any, Optional

from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function


def make_mock_completion(
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    content: Optional[str] = None
) -> ChatCompletion:
    """
    Build a real ChatCompletion object for mocking LLM responses.
    
    Args:
        tool_calls: List of {"name": str, "arguments": dict} for iteration 1
        content: Response text for final iteration (no tool calls)
    
    Returns:
        A real ChatCompletion object that matches the OpenAI API structure
    """
    # Build tool_calls list if provided
    message_tool_calls = None
    if tool_calls:
        message_tool_calls = [
            ChatCompletionMessageToolCall(
                id=f"call_mock_{i}",
                type="function",
                function=Function(
                    name=tc["name"],
                    arguments=json.dumps(tc.get("arguments", {}))
                )
            )
            for i, tc in enumerate(tool_calls)
        ]
    
    return ChatCompletion(
        id="mock-completion",
        choices=[
            Choice(
                index=0,
                message=ChatCompletionMessage(
                    role="assistant",
                    content=content,
                    tool_calls=message_tool_calls
                ),
                finish_reason="tool_calls" if tool_calls else "stop"
            )
        ],
        created=1234567890,
        model="mock-model",
        object="chat.completion"
    )

# =============================================================================
# WEATHER API MOCK DATA
# =============================================================================
# Structure matches OpenWeatherMap API response after processing in weather.py:
# {
#     "location": str,           # City name or requested location
#     "temperature": float,      # Temperature in Fahrenheit (imperial units)
#     "feels_like": float,       # "Feels like" temperature
#     "condition": str,          # Main condition (lowercased): "clear", "clouds", "rain", etc.
#     "description": str,        # Detailed description: "clear sky", "scattered clouds", etc.
#     "humidity": int,           # Humidity percentage (0-100)
#     "wind_speed": float,       # Wind speed in mph
#     "precipitation": float,    # Precipitation in mm (last 1h)
#     "clouds": int,             # Cloud coverage percentage (0-100)
#     "timestamp": str,          # ISO timestamp (added at runtime)
#     "date": str,               # Date in YYYY-MM-DD format (added at runtime)
#     "outdoor_suitable": bool,  # Whether weather is good for outdoor activities
#     "outdoor_recommendation": str  # Human-readable recommendation
# }

MOCK_WEATHER_RESPONSES: List[Dict[str, Any]] = [
    {
        "location": "San Francisco, CA",
        "temperature": 68,
        "feels_like": 65,
        "condition": "clear",
        "description": "clear sky",
        "humidity": 55,
        "wind_speed": 8.5,
        "precipitation": 0,
        "clouds": 10,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Great weather for outdoor activities!"
    },
    {
        "location": "Oakland, CA",
        "temperature": 72,
        "feels_like": 70,
        "condition": "clouds",
        "description": "scattered clouds",
        "humidity": 48,
        "wind_speed": 12.3,
        "precipitation": 0,
        "clouds": 40,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Weather is okay for outdoor activities"
    },
    {
        "location": "Berkeley, CA",
        "temperature": 58,
        "feels_like": 55,
        "condition": "drizzle",
        "description": "light drizzle",
        "humidity": 78,
        "wind_speed": 5.2,
        "precipitation": 0.5,
        "clouds": 85,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Rainy weather - consider indoor activities"
    },
    {
        "location": "Palo Alto, CA",
        "temperature": 75,
        "feels_like": 73,
        "condition": "clear",
        "description": "sunny",
        "humidity": 42,
        "wind_speed": 6.0,
        "precipitation": 0,
        "clouds": 5,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Great weather for outdoor activities!"
    },
    {
        "location": "San Jose, CA",
        "temperature": 82,
        "feels_like": 84,
        "condition": "clear",
        "description": "hot and sunny",
        "humidity": 35,
        "wind_speed": 4.5,
        "precipitation": 0,
        "clouds": 0,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Weather is okay for outdoor activities"
    },
    {
        "location": "Mountain View, CA",
        "temperature": 45,
        "feels_like": 40,
        "condition": "clouds",
        "description": "overcast clouds",
        "humidity": 68,
        "wind_speed": 15.0,
        "precipitation": 0,
        "clouds": 95,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Cold weather - dress warmly or choose indoor activities"
    }
]


# =============================================================================
# GOOGLE MAPS TRANSIT STOPS MOCK DATA
# =============================================================================
# Structure matches Google Maps Directions API transit_details after processing:
# {
#     "name": str,       # Station/stop name
#     "lat": float,      # Latitude
#     "lng": float,      # Longitude
#     "type": str,       # Vehicle type: "SUBWAY", "LIGHT_RAIL", "BUS", "TRAM", etc.
#     "line_name": str   # Line short name or name (e.g., "BART", "N Judah")
# }

MOCK_TRANSIT_STOPS: List[Dict[str, Any]] = [
    {"name": "16th St Mission", "lat": 37.7650, "lng": -122.4197, "type": "SUBWAY", "line_name": "BART"},
    {"name": "24th St Mission", "lat": 37.7522, "lng": -122.4181, "type": "SUBWAY", "line_name": "BART"},
    {"name": "Powell St", "lat": 37.7844, "lng": -122.4080, "type": "SUBWAY", "line_name": "BART"},
    {"name": "Montgomery St", "lat": 37.7894, "lng": -122.4013, "type": "SUBWAY", "line_name": "BART"},
    {"name": "Embarcadero", "lat": 37.7929, "lng": -122.3968, "type": "SUBWAY", "line_name": "BART"},
    {"name": "Church & Market", "lat": 37.7679, "lng": -122.4291, "type": "LIGHT_RAIL", "line_name": "Muni Metro"},
    {"name": "Castro St", "lat": 37.7625, "lng": -122.4351, "type": "LIGHT_RAIL", "line_name": "Muni Metro"},
    {"name": "Van Ness", "lat": 37.7752, "lng": -122.4192, "type": "SUBWAY", "line_name": "Muni Metro"},
    {"name": "Civic Center", "lat": 37.7796, "lng": -122.4139, "type": "SUBWAY", "line_name": "BART"},
    {"name": "Glen Park", "lat": 37.7329, "lng": -122.4332, "type": "SUBWAY", "line_name": "BART"},
]


# =============================================================================
# GOOGLE MAPS PLACES MOCK DATA
# =============================================================================
# Structure matches Google Maps Places API after processing in google_maps.py.
# Used by both search_places_near_location and search_places_for_dates.
#
# search_places_near_location returns:
# {
#     "name": str,                    # Place name
#     "location": str,                # Formatted address
#     "description": str,             # Review analysis summary
#     "price": str | None,            # Price string like "$$" or None for free
#     "date": str | None,             # Opening hours text (for near_location)
#     "url": str,                     # Google Maps URL
#     "category": str,                # Place type (title case)
#     "gmaps_place_id": str,          # Google Place ID
#     "gmaps_rating": float,          # Rating (1.0-5.0)
#     "gmaps_price_level": int,       # Price level (0-4)
#     "near_stop": str,               # The transit stop this place is near
#     "coordinates": {"lat": float, "lng": float}
# }
#
# search_places_for_dates additionally includes:
# {
#     "image_url": str | None,        # Photo URL (if available)
#     "gmaps_opening_hours": str | dict,  # Opening hours
#     "gmaps_review_summary": str,    # Review summary text
# }

MOCK_PLACES: List[Dict[str, Any]] = [
    {
        "name": "[Stub] Dolores Park",
        "location": "Dolores St & 19th St, San Francisco, CA 94114",
        "description": "Reviewers mention: local favorite, unique. Matches interests: outdoor",
        "price": None,
        "date": "Open 24 hours",
        "url": "https://maps.google.com/?cid=mock1",
        "image_url": None,
        "category": "Park",
        "gmaps_place_id": "ChIJmock_dolores_park",
        "gmaps_rating": 4.7,
        "gmaps_price_level": 0,
        "gmaps_opening_hours": "Open 24 hours",
        "gmaps_review_summary": "Reviewers mention: local favorite, unique. Matches interests: outdoor",
        "coordinates": {"lat": 37.7598, "lng": -122.4269}
    },
    {
        "name": "[Stub] Sightglass Coffee",
        "location": "270 7th St, San Francisco, CA 94103",
        "description": "Reviewers mention: unique, authentic. Matches interests: coffee",
        "price": "$$",
        "date": "Mon-Fri: 7AM-6PM; Sat-Sun: 8AM-6PM",
        "url": "https://maps.google.com/?cid=mock2",
        "image_url": None,
        "category": "Cafe",
        "gmaps_place_id": "ChIJmock_sightglass",
        "gmaps_rating": 4.5,
        "gmaps_price_level": 2,
        "gmaps_opening_hours": "Mon-Fri: 7AM-6PM; Sat-Sun: 8AM-6PM",
        "gmaps_review_summary": "Reviewers mention: unique, authentic. Matches interests: coffee",
        "coordinates": {"lat": 37.7771, "lng": -122.4074}
    },
    {
        "name": "[Stub] Tartine Bakery",
        "location": "600 Guerrero St, San Francisco, CA 94110",
        "description": "Reviewers mention: local favorite, authentic. Matches interests: food, coffee",
        "price": "$$",
        "date": "Mon-Sun: 7:30AM-7PM",
        "url": "https://maps.google.com/?cid=mock5",
        "image_url": None,
        "category": "Cafe",
        "gmaps_place_id": "ChIJmock_tartine",
        "gmaps_rating": 4.5,
        "gmaps_price_level": 2,
        "gmaps_opening_hours": "Mon-Sun: 7:30AM-7PM",
        "gmaps_review_summary": "Reviewers mention: local favorite, authentic. Matches interests: food, coffee",
        "coordinates": {"lat": 37.7614, "lng": -122.4241}
    },
    {
        "name": "[Stub] Lands End Trail",
        "location": "Lands End Trail, San Francisco, CA 94121",
        "description": "Reviewers mention: hidden gem, scenic. Matches interests: outdoor",
        "price": None,
        "date": "Sunrise to Sunset",
        "url": "https://maps.google.com/?cid=mock6",
        "image_url": None,
        "category": "Park",
        "gmaps_place_id": "ChIJmock_lands_end",
        "gmaps_rating": 4.8,
        "gmaps_price_level": 0,
        "gmaps_opening_hours": "Sunrise to Sunset",
        "gmaps_review_summary": "Reviewers mention: hidden gem, scenic. Matches interests: outdoor",
        "coordinates": {"lat": 37.7875, "lng": -122.5048}
    },
    {
        "name": "[Stub] Stern Grove",
        "location": "19th Ave & Sloat Blvd, San Francisco, CA 94132",
        "description": "Reviewers mention: local favorite, unique. Matches interests: outdoor, music",
        "price": None,
        "date": "Open 6AM-10PM daily",
        "url": "https://maps.google.com/?cid=mock8",
        "image_url": None,
        "category": "Park",
        "gmaps_place_id": "ChIJmock_stern_grove",
        "gmaps_rating": 4.7,
        "gmaps_price_level": 0,
        "gmaps_opening_hours": "Open 6AM-10PM daily",
        "gmaps_review_summary": "Reviewers mention: local favorite, unique. Matches interests: outdoor, music",
        "coordinates": {"lat": 37.7327, "lng": -122.4710}
    },
    {
        "name": "[Stub] California Academy of Sciences",
        "location": "55 Music Concourse Dr, San Francisco, CA 94118",
        "description": "Reviewers mention: one-of-a-kind, special, unique. Matches interests: art, outdoor",
        "price": "$$$",
        "date": "Mon-Sat: 9:30AM-5PM; Sun: 11AM-5PM",
        "url": "https://maps.google.com/?cid=mock12",
        "image_url": None,
        "category": "Tourist Attraction",
        "gmaps_place_id": "ChIJmock_cal_academy",
        "gmaps_rating": 4.6,
        "gmaps_price_level": 3,
        "gmaps_opening_hours": "Mon-Sat: 9:30AM-5PM; Sun: 11AM-5PM",
        "gmaps_review_summary": "Reviewers mention: one-of-a-kind, special, unique. Matches interests: art, outdoor",
        "coordinates": {"lat": 37.7699, "lng": -122.4661}
    }
]


# =============================================================================
# ORCHESTRATOR MOCK DATA
# =============================================================================
# Two lists with identical format:
# - "response": Final LLM response text
# - "tool_calls": What LLM requests on iteration 1 (name + arguments)
# - "tool_results": Expected results (for reference/testing)
#
# In mock mode:
# - Iteration 1: Return ChatCompletion with tool_calls → tools actually execute
# - Iteration 2: Return ChatCompletion with response content
# =============================================================================

# Responses where tools were called
MOCK_RESPONSES_WITH_TOOLS: List[Dict[str, Any]] = [
    {
        "response": "I found some great activities for you! There's a lovely hiking trail at Sunset Ridge Park, a pottery class downtown, and a new escape room that just opened. Would you like me to save these to a spreadsheet?",
        "tool_calls": [
            {"name": "get_user_preferences", "arguments": {"user_id": "default"}},
            {"name": "scrape_activities", "arguments": {"query": "fun activities", "location_a": "San Francisco"}}
        ],
        "tool_results": [
            {"tool": "get_user_preferences", "result": {"interests": ["hiking", "arts"], "location": "San Francisco"}},
            {"tool": "scrape_activities", "result": [
                {"name": "Sunset Ridge Park Trail", "type": "hiking", "rating": 4.5},
                {"name": "Clay & Create Pottery", "type": "arts", "rating": 4.8},
                {"name": "Puzzle Palace Escape Room", "type": "entertainment", "rating": 4.6}
            ]}
        ]
    },
    {
        "response": "The weather looks perfect for outdoor activities this weekend! It'll be sunny with highs around 72°F. I'd recommend checking out the farmers market or having a picnic at Golden Gate Park.",
        "tool_calls": [
            {"name": "get_weather_for_location", "arguments": {"location": "San Francisco, CA"}}
        ],
        "tool_results": [
            {"tool": "get_weather_for_location", "result": {
                "location": "San Francisco, CA",
                "temperature": 72,
                "condition": "clear",
                "humidity": 45,
                "outdoor_suitable": True,
                "outdoor_recommendation": "Great weather for outdoor activities!"
            }}
        ]
    },
    {
        "response": "I've found some wonderful date spots between your two locations! There's a cozy wine bar, an art gallery with a new exhibit, and a rooftop restaurant with amazing views.",
        "tool_calls": [
            {"name": "search_places_for_dates", "arguments": {
                "location1": "San Francisco, CA",
                "location2": "Oakland, CA",
                "place_types": ["cafe", "restaurant", "park"]
            }}
        ],
        "tool_results": [
            {"tool": "search_places_for_dates", "result": {
                "activities": [
                    {"name": "Vine & Dine Wine Bar", "gmaps_rating": 4.7, "category": "Restaurant"},
                    {"name": "Modern Perspectives Gallery", "gmaps_rating": 4.4, "category": "Tourist Attraction"},
                    {"name": "Skyline Bistro", "gmaps_rating": 4.9, "category": "Restaurant"}
                ],
                "search_mode": "transit_stops",
                "count": 3
            }}
        ]
    },
    {
        "response": "I've saved those activities to your spreadsheet! You can access it anytime to review your saved ideas.",
        "tool_calls": [
            {"name": "save_to_sheets", "arguments": {
                "activities": [{"name": "Test Activity", "location": "SF"}],
                "spreadsheet_id": "mock-sheet-id"
            }}
        ],
        "tool_results": [
            {"tool": "save_to_sheets", "result": {"success": True, "rows_added": 3, "sheet_url": "https://docs.google.com/spreadsheets/d/mock123"}}
        ]
    },
    {
        "response": "I've updated your preferences! I'll keep your love for outdoor activities and Italian food in mind for future recommendations.",
        "tool_calls": [
            {"name": "update_user_preferences", "arguments": {
                "user_id": "default",
                "preferences": {"interests": ["outdoor", "food"], "cuisine": "Italian"}
            }}
        ],
        "tool_results": [
            {"tool": "update_user_preferences", "result": {"updated": True, "preferences": {"interests": ["outdoor", "food"], "cuisine": "Italian"}}}
        ]
    },
    {
        "response": "Based on your preferences and the nice weather forecast, I recommend the outdoor concert series at the amphitheater this Saturday. It's supposed to be 68°F and clear skies!",
        "tool_calls": [
            {"name": "get_user_preferences", "arguments": {"user_id": "default"}},
            {"name": "get_weather_for_location", "arguments": {"location": "San Francisco, CA"}},
            {"name": "scrape_activities", "arguments": {"query": "outdoor concert", "location_a": "San Francisco"}}
        ],
        "tool_results": [
            {"tool": "get_user_preferences", "result": {"interests": ["music", "outdoor"]}},
            {"tool": "get_weather_for_location", "result": {
                "location": "San Francisco, CA",
                "temperature": 68,
                "condition": "clear",
                "outdoor_suitable": True
            }},
            {"tool": "scrape_activities", "result": [
                {"name": "Summer Concert Series", "type": "music", "date": "Saturday", "venue": "Riverside Amphitheater"}
            ]}
        ]
    }
]

# Responses where no tools were needed
MOCK_RESPONSES_NO_TOOLS: List[Dict[str, Any]] = [
    {
        "response": "Great question! I'd be happy to help you find some fun things to do. What kind of activities are you interested in? Are you looking for outdoor adventures, arts and culture, food experiences, or something else?",
        "tool_calls": [],
        "tool_results": []
    },
    {
        "response": "Sure! To give you the best recommendations, could you tell me a bit about what you're in the mood for? Something active, relaxing, or maybe a mix of both?",
        "tool_calls": [],
        "tool_results": []
    },
    {
        "response": "I can help with that! Are you planning something for just yourself, a date, or a group outing? That'll help me tailor my suggestions.",
        "tool_calls": [],
        "tool_results": []
    }
]

