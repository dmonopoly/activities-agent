"""
Datetime utilities for consistent timestamp formatting across the codebase.

Format: ISO 8601 with UTC timezone using 'Z' suffix.
Example: "2024-01-15T14:30:00.123456Z"

This format is:
- Standard ISO 8601 compliant
- Explicitly UTC (Z = Zulu time)
- Parseable by JavaScript's Date constructor: new Date("2024-01-15T14:30:00.123456Z")
- Sortable as strings (lexicographic order = chronological order)
"""

from datetime import datetime, timezone


def datetime_to_iso(dt: datetime | None = None) -> str:
    """
    Convert a datetime object to an ISO 8601 UTC string for storage.
    
    Args:
        dt: A datetime object. If None, uses current UTC time.
            If naive (no timezone), assumes UTC.
            If timezone-aware, converts to UTC.
    
    Returns:
        ISO 8601 formatted string with 'Z' suffix, e.g. "2024-01-15T14:30:00.123456Z"
    
    Example:
        >>> datetime_to_iso()  # Current UTC time
        '2024-01-15T14:30:00.123456Z'
        >>> datetime_to_iso(datetime(2024, 1, 15, 14, 30))
        '2024-01-15T14:30:00Z'
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    elif dt.tzinfo is None:
        # Naive datetime - assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        # Convert to UTC
        dt = dt.astimezone(timezone.utc)
    
    return dt.isoformat().replace('+00:00', 'Z')


def iso_to_datetime(iso_string: str) -> datetime:
    """
    Parse an ISO 8601 UTC string back to a timezone-aware datetime object.
    
    Args:
        iso_string: ISO 8601 formatted string, e.g. "2024-01-15T14:30:00.123456Z"
                   Supports both 'Z' suffix and '+00:00' offset notation.
    
    Returns:
        A timezone-aware datetime object in UTC.
    
    Example:
        >>> iso_to_datetime("2024-01-15T14:30:00.123456Z")
        datetime.datetime(2024, 1, 15, 14, 30, 0, 123456, tzinfo=datetime.timezone.utc)
    
    Note:
        In the frontend (TypeScript), parsing is done natively with:
        new Date("2024-01-15T14:30:00.123456Z")
        
        See frontend/app/history/page.tsx:formatDate() for display formatting.
    """
    # Handle 'Z' suffix by replacing with +00:00 for fromisoformat
    normalized = iso_string.replace('Z', '+00:00')
    return datetime.fromisoformat(normalized)


def utc_now_iso() -> str:
    """
    Get the current UTC time as an ISO 8601 string.
    
    Convenience wrapper for datetime_to_iso() with no arguments.
    
    Returns:
        Current UTC time as ISO 8601 string, e.g. "2024-01-15T14:30:00.123456Z"
    """
    return datetime_to_iso()

