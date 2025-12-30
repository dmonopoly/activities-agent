"""Web scraping tool - MCP-style tool for scraping activity websites"""

import re
from typing import Any


def scrape_activities(
    query: str,
    location_a: str | None = None,
    location_b: str | None = None,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Scrape activities from the web based on query and location(s)

    Args:
        query: Search query for activities
        location_a: Primary location to search in (city, neighborhood, etc.)
        location_b: Optional second location (for finding activities between two locations)
        filters: Optional filters (category, price_range, etc.)

    Returns:
        List of activity dictionaries with fields: name, location, description, price,
        opening_hours, url, category
    """
    # For demo purposes, we'll scrape from a few common sources
    # In production, you'd want to use proper APIs or more sophisticated scraping

    # Build search terms from locations
    location_parts = [loc for loc in [location_a, location_b] if loc]
    if location_parts:
        _search_terms = f"{query} {' '.join(location_parts)}"  # Reserved for future use
        primary_location = location_a or location_b
    else:
        _search_terms = query  # Reserved for future use  # noqa: F841
        primary_location = "NYC"

    # Mock data for now - in production, implement actual scraping
    # This demonstrates the tool structure
    sample_activities = [
        {
            "name": "[Stub] Sunset Yoga in the Park",
            "location": primary_location,
            "description": "Join us for a relaxing yoga session as the sun sets",
            "price": "$25",
            "opening_hours": "This Saturday, 6:00 PM",
            "url": "https://example.com/yoga",
            "category": "Wellness",
        },
        {
            "name": "[Stub] Art Gallery Opening",
            "location": primary_location,
            "description": "New contemporary art exhibition with wine and cheese",
            "price": "Free",
            "opening_hours": "Friday, 7:00 PM",
            "url": "https://example.com/gallery",
            "category": "Arts",
        },
        {
            "name": "[Stub] Cooking Class: Italian Cuisine",
            "location": primary_location,
            "description": "Learn to make fresh pasta and authentic Italian dishes",
            "price": "$75",
            "opening_hours": "Next Sunday, 2:00 PM",
            "url": "https://example.com/cooking",
            "category": "Food & Drink",
        },
        {
            "name": "[Stub] Live Jazz Night",
            "location": primary_location,
            "description": "Intimate jazz performance with local musicians",
            "price": "$30",
            "opening_hours": "Saturday, 8:00 PM",
            "url": "https://example.com/jazz",
            "category": "Music",
        },
        {
            "name": "[Stub] Hiking Trail: Mountain View",
            "location": primary_location,
            "description": "Moderate 3-mile hike with scenic overlooks",
            "price": "Free",
            "opening_hours": "Any day, sunrise to sunset",
            "url": "https://example.com/hiking",
            "category": "Outdoor",
        },
    ]

    # Apply filters if provided
    if filters:
        if "category" in filters:
            sample_activities = [
                a
                for a in sample_activities
                if a.get("category", "").lower() == filters["category"].lower()
            ]
        if "max_price" in filters:
            # Simple price filtering (would need more sophisticated parsing in production)
            max_price = filters["max_price"]
            filtered = []
            for a in sample_activities:
                price_str = a.get("price", "$999")
                price_num = re.search(r"\d+", price_str)
                if price_num and int(price_num.group()) <= max_price:
                    filtered.append(a)
            sample_activities = filtered

    return sample_activities


# Tool definition for LLM function calling
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "scrape_activities",
        "description": "Search and scrape activities from the web based on query and location(s). Can search near one location or between two locations.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for activities (e.g., 'date ideas', 'nature', 'unique coffee shops')",
                },
                "location_a": {
                    "type": "string",
                    "description": "Primary location to search in (city, neighborhood, etc.)",
                },
                "location_b": {
                    "type": "string",
                    "description": "Optional second location - if provided, searches for activities between location_a and location_b",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Activity category (e.g., 'outdoor', 'arts', 'food', 'music')",
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price in dollars",
                        },
                    },
                },
            },
            "required": ["query"],
        },
    },
}
