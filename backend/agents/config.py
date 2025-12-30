"""Configuration for paid API flags"""

import os


def _is_enabled(var: str) -> bool:
    return os.getenv(var, "false").lower() == "true"


# Global flag - enables all paid APIs
ENABLE_PAID_APIS_OVERRIDE_ALL = _is_enabled("ENABLE_PAID_APIS_OVERRIDE_ALL")

# Individual flags - each API can be toggled independently
ENABLE_OPENROUTER_API = ENABLE_PAID_APIS_OVERRIDE_ALL or _is_enabled(
    "ENABLE_OPENROUTER_API"
)
ENABLE_GOOGLE_MAPS_API = ENABLE_PAID_APIS_OVERRIDE_ALL or _is_enabled(
    "ENABLE_GOOGLE_MAPS_API"
)
ENABLE_WEATHER_API = ENABLE_PAID_APIS_OVERRIDE_ALL or _is_enabled("ENABLE_WEATHER_API")
