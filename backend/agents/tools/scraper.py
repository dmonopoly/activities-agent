"""Web scraping tool - MCP-style tool for scraping activity websites"""
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import re
import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))


def scrape_activities(query: str, location: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Scrape activities from the web based on query and location
    
    Args:
        query: Search query for activities (e.g., "date ideas", "fun activities")
        location: Location to search in (city, neighborhood, etc.)
        filters: Optional filters (category, price_range, etc.)
        
    Returns:
        List of activity dictionaries
    """
    activities = []
    
    # For demo purposes, we'll scrape from a few common sources
    # In production, you'd want to use proper APIs or more sophisticated scraping
    
    # Example: Scrape Eventbrite-style sites
    search_terms = f"{query} {location}" if location else query
    
    # Mock data for now - in production, implement actual scraping
    # This demonstrates the tool structure
    sample_activities = [
        {
            "name": "Sunset Yoga in the Park",
            "location": location or "Downtown",
            "description": "Join us for a relaxing yoga session as the sun sets",
            "price": "$25",
            "date": "This Saturday, 6:00 PM",
            "url": "https://example.com/yoga",
            "category": "Wellness"
        },
        {
            "name": "Art Gallery Opening",
            "location": location or "Arts District",
            "description": "New contemporary art exhibition with wine and cheese",
            "price": "Free",
            "date": "Friday, 7:00 PM",
            "url": "https://example.com/gallery",
            "category": "Arts"
        },
        {
            "name": "Cooking Class: Italian Cuisine",
            "location": location or "Culinary School",
            "description": "Learn to make fresh pasta and authentic Italian dishes",
            "price": "$75",
            "date": "Next Sunday, 2:00 PM",
            "url": "https://example.com/cooking",
            "category": "Food & Drink"
        },
        {
            "name": "Live Jazz Night",
            "location": location or "Jazz Club",
            "description": "Intimate jazz performance with local musicians",
            "price": "$30",
            "date": "Saturday, 8:00 PM",
            "url": "https://example.com/jazz",
            "category": "Music"
        },
        {
            "name": "Hiking Trail: Mountain View",
            "location": location or "Nature Reserve",
            "description": "Moderate 3-mile hike with scenic overlooks",
            "price": "Free",
            "date": "Any day, sunrise to sunset",
            "url": "https://example.com/hiking",
            "category": "Outdoor"
        }
    ]
    
    # Apply filters if provided
    if filters:
        if "category" in filters:
            sample_activities = [a for a in sample_activities if a.get("category", "").lower() == filters["category"].lower()]
        if "max_price" in filters:
            # Simple price filtering (would need more sophisticated parsing in production)
            max_price = filters["max_price"]
            filtered = []
            for a in sample_activities:
                price_str = a.get("price", "$999")
                price_num = re.search(r'\d+', price_str)
                if price_num and int(price_num.group()) <= max_price:
                    filtered.append(a)
            sample_activities = filtered
    
    return sample_activities


# Tool definition for LLM function calling
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "scrape_activities",
        "description": "Search and scrape activities/date ideas from the web based on query, location, and optional filters",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for activities (e.g., 'date ideas', 'fun activities', 'outdoor activities')"
                },
                "location": {
                    "type": "string",
                    "description": "Location to search in (city, neighborhood, etc.)"
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Activity category (e.g., 'outdoor', 'arts', 'food', 'music')"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price in dollars"
                        }
                    }
                }
            },
            "required": ["query"]
        }
    }
}
