"""Main FastAPI application"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST, before any other imports
# This ensures env vars are available when modules are imported
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="Activities Agent API", version="1.0.0")

def require_preview_api_token(
    x_preview_token: str | None = Header(default=None, alias="X-Preview-Token"),
) -> None:
    """
    Preview-only protection for /api/* routes.

    Why: Vercel preview deployments often have dynamic URLs. Instead of trying to keep
    CORS + "Vercel Authentication" aligned across separately deployed frontends/backends,
    we allow the preview backend to be network-reachable but require a shared secret
    for any API request. The Next.js frontend calls the backend via a server-side proxy
    that injects this header, so the secret never reaches the browser.
    """
    if os.getenv("VERCEL_ENV") != "preview":
        return

    expected = os.getenv("PREVIEW_API_TOKEN", "")
    if not expected:
        # Fail closed if preview token is not configured.
        raise HTTPException(
            status_code=500,
            detail="PREVIEW_API_TOKEN is not configured on this preview deployment.",
        )

    if x_preview_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


PRODUCTION_URL = "https://activitiesagent.vercel.app"
# Starlette CORSMiddleware uses `fullmatch()` on this regex.
# This pattern allows any `https://*.vercel.app` origin (paths are not part of Origin).
VERCEL_PREVIEW_URL_REGEX = r"https://.*\.vercel\.app"

cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    PRODUCTION_URL,
]

extra_origins = os.getenv("CORS_ORIGINS", "")
if extra_origins:
    cors_origins.extend([origin.strip() for origin in extra_origins.split(",") if origin.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=VERCEL_PREVIEW_URL_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix="/api",
    tags=["api"],
    dependencies=[Depends(require_preview_api_token)],
)


@app.get("/")
async def root():
    return {"message": "Activities Agent API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
