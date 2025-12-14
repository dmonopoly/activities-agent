"""Configuration for paid API flags"""
import os


def _is_enabled(var: str) -> bool:
    return os.getenv(var, "false").lower() == "true"


# Global flag - enables all paid APIs
ENABLE_PAID_APIS = _is_enabled("ENABLE_PAID_APIS")

# Individual flags - each API can be toggled independently
ENABLE_OPENAI_API = ENABLE_PAID_APIS or _is_enabled("ENABLE_OPENAI_API")
ENABLE_GOOGLE_MAPS_API = ENABLE_PAID_APIS or _is_enabled("ENABLE_GOOGLE_MAPS_API")
ENABLE_WEATHER_API = ENABLE_PAID_APIS or _is_enabled("ENABLE_WEATHER_API")
