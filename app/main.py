import logging
import os

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.youtube import router as youtube_router
from app.routes.edge import router as edge_router
from app.routes.storage import router as storage_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## YouTube Data Extraction API

Extract video metadata, captions, and timestamps from YouTube videos with multi-tier caching.

### Features
- **Video Metadata**: Title, author, thumbnail via oEmbed API
- **Captions**: Full transcript text
- **Timestamps**: Captions with time markers
- **Edge Caching**: Optional edge-cached responses via Edge API (Cloudflare KV)
- **Persistent Storage**: Optional transcript storage via Storage API (D1 database)
- **Multi-tier Fallback**: Redis → Edge API → Storage API → Direct YouTube

### Input Formats
All endpoints accept either:
- **Video ID**: `dQw4w9WgXcQ`
- **Full URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Short URL**: `https://youtu.be/dQw4w9WgXcQ`
- **Shorts URL**: `https://youtube.com/shorts/VIDEO_ID`

### External APIs (Optional)
Configure via environment variables to enable:
- **Edge API**: Set `EDGE_API_URL` and `EDGE_API_KEY` for edge caching
- **Storage API**: Set `STORAGE_API_URL` and `STORAGE_API_KEY` for persistent storage

See `/edge/*` and `/storage/*` endpoints for direct API access.
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "tryItOutEnabled": True,
        "defaultModelsExpandDepth": 1,
        "docExpansion": "list",
        "filter": True,
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(youtube_router)
app.include_router(edge_router)
app.include_router(storage_router)

@app.get("/", tags=["root"])
async def root():
    """Root endpoint that provides API information"""
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

def start():
    """Function to start the server"""
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    # Disable reload in production (Railway sets RAILWAY_ENVIRONMENT)
    # Only enable reload if explicitly requested via ENABLE_RELOAD env var
    enable_reload = os.getenv("ENABLE_RELOAD", "false").lower() == "true"
    is_production = os.getenv("RAILWAY_ENVIRONMENT") == "production"
    reload = enable_reload and not is_production
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=reload)

if __name__ == "__main__":
    start()