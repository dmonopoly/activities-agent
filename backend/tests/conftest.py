"""Pytest configuration and shared test setup"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables first (before any imports that need them)
# This ensures env vars are available when modules like orchestrator.py are imported
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend directory to path for imports
# Note: This is acceptable for tests as they may be run from different directories
# In production code, we use relative imports instead
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
