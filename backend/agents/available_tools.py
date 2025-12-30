"""
Tool availability and filtering for the orchestrator.

This module controls which tools the orchestrator can execute,
allowing certain tools to be denylisted (e.g., for testing, cost control,
or feature flags).
"""

from typing import Any

ALLOWLISTED_TOOLS: set[str] = {
    # User preferences
    "get_user_preferences",
    "update_user_preferences",
    # Weather
    # 'get_weather_for_location',
    # Web Scraping
    # 'scrape_activities',
    # Google Sheets
    "save_to_sheets",
    # Google Maps
    # 'search_places_for_dates',
}

TOOL_DISPLAY_NAMES: dict[str, str] = {
    "search_places_for_dates": "Google Maps",
    "get_weather_for_location": "Weather",
    "scrape_activities": "Web Scraper",
    "save_to_sheets": "Google Sheets",
    "get_user_preferences": "Preferences",
    "update_user_preferences": "Preferences",
}


def filter_to_available_tools(
    tool_calls: list[Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Filter tool calls to only include available (non-denylisted) tools.

    Converts OpenAI ChatCompletionMessageToolCall objects to dicts suitable
    for storing in conversation history.

    Args:
        tool_calls: List of ChatCompletionMessageToolCall objects from the LLM response

    Returns:
        Tuple of:
        - List of tool call dicts with keys: id, type, function (only allowlisted tools)
        - List of display names for skipped tools (deduplicated)
    """
    filtered = []
    skipped_display_names: list[str] = []

    for tc in tool_calls:
        tool_name = tc.function.name

        if tool_name not in ALLOWLISTED_TOOLS:
            display_name = TOOL_DISPLAY_NAMES.get(tool_name, tool_name)
            if display_name not in skipped_display_names:
                skipped_display_names.append(display_name)
            print(
                f"[TOOLS] ⛔ Skipping tool not on allowlist: {tool_name} ({display_name})"
            )
            continue

        # Convert to dict format for conversation history
        # This format matches OpenAI's tool_call structure for API compatibility
        filtered.append(
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
        )

    return filtered, skipped_display_names
