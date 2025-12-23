"""
Tool availability and filtering for the orchestrator.

This module controls which tools the orchestrator can execute,
allowing certain tools to be denylisted (e.g., for testing, cost control, 
or feature flags).
"""

from typing import List, Dict, Any

ALLOWLISTED_TOOLS: set[str] = {
    # User preferences
    'get_user_preferences',
    'update_user_preferences',

    # Weather
    # 'get_weather_for_location',

    # Web Scraping
    'scrape_activities',

    # Google Sheets
    'save_to_sheets',

    # Google Maps
    # 'search_places_for_dates',
}


def filter_to_available_tools(
    tool_calls: List[Any]
) -> List[Dict[str, Any]]:
    """
    Filter tool calls to only include available (non-denylisted) tools.
    
    Converts OpenAI ChatCompletionMessageToolCall objects to dicts suitable
    for storing in conversation history.
    
    Args:
        tool_calls: List of ChatCompletionMessageToolCall objects from the LLM response
        
    Returns:
        List of tool call dicts with keys: id, type, function
        Only includes tools in ALLOWLISTED_TOOLS
    """
    filtered = []
    
    for tc in tool_calls:
        tool_name = tc.function.name
        
        if tool_name not in ALLOWLISTED_TOOLS:
            print(f"[TOOLS] ⛔ Skipping tool not on allowlist: {tool_name}")
            continue
        
        # Convert to dict format for conversation history
        # This format matches OpenAI's tool_call structure for API compatibility
        filtered.append({
            "id": tc.id,
            "type": tc.type,
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        })
    
    return filtered
