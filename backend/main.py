"""Main FastAPI application"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
# This ensures env vars are available when modules are imported
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Activities Agent API", version="1.0.0")

# CORS configuration - allow local dev and production origins
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://activitiesagent.vercel.app",
]

# Add any additional origins from environment variable
extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    cors_origins.extend([origin.strip() for origin in extra_origins.split(",") if origin.strip()])

# Regex to match Vercel preview deployment URLs
# Matches: https://activities-agent-frontend-*.vercel.app
vercel_preview_regex = r"https://activities-agent-frontend.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=vercel_preview_regex,
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
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
