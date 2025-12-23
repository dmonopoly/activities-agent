"""Main FastAPI application"""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
# This ensures env vars are available when modules are imported
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from services.scraper_scheduler import (
    start_scraper_scheduler,
    stop_scraper_scheduler,
    get_scheduler_status
)

# Check if scraper scheduler should be enabled
ENABLE_SCRAPER_SCHEDULER = os.getenv("ENABLE_SCRAPER_SCHEDULER", "true").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.
    
    Handles startup and shutdown events:
    - Startup: Start the background scraper scheduler
    - Shutdown: Stop the scheduler gracefully
    """
    # Startup
    if ENABLE_SCRAPER_SCHEDULER:
        print("[MAIN] Starting scraper scheduler...")
        start_scraper_scheduler()
    else:
        print("[MAIN] Scraper scheduler disabled (ENABLE_SCRAPER_SCHEDULER=false)")
    
    yield  # App runs here
    
    # Shutdown
    if ENABLE_SCRAPER_SCHEDULER:
        print("[MAIN] Stopping scraper scheduler...")
        stop_scraper_scheduler()


app = FastAPI(
    title="Activities Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    return {"message": "Activities Agent API", "status": "running"}


@app.get("/health")
async def health():
    scheduler_status = get_scheduler_status()
    return {
        "status": "healthy",
        "scraper_scheduler": scheduler_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
