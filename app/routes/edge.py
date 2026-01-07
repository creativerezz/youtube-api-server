import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.edge import EdgeCacheStats, EdgeCacheClearResponse
from app.models.youtube import VideoData
from app.utils.edge_api import edge_api_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/edge",
    tags=["Edge API"],
    responses={
        503: {
            "description": "Edge API not configured or unavailable",
            "content": {
                "application/json": {
                    "example": {"detail": "Edge API not configured. Set EDGE_API_URL and EDGE_API_KEY."}
                }
            }
        }
    }
)


def _ensure_edge_configured():
    """Raise HTTP 503 if Edge API is not configured."""
    if not edge_api_client.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Edge API not configured. Set EDGE_API_URL and EDGE_API_KEY."
        )


@router.get(
    "/metadata",
    response_model=VideoData,
    summary="Get Video Metadata via Edge API",
    description="Fetch video metadata using Edge API with KV caching. Direct passthrough to Edge API.",
)
async def get_edge_metadata(
    video: str = Query(..., description="YouTube video ID (11 characters)")
):
    """Passthrough to Edge API GET /youtube/metadata"""
    _ensure_edge_configured()

    data = edge_api_client.get_metadata(video)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch metadata from Edge API")

    return VideoData(**data)


@router.get(
    "/captions",
    response_model=str,
    summary="Get Video Captions via Edge API",
    description="Fetch video captions using Edge API with KV caching. Direct passthrough to Edge API.",
)
async def get_edge_captions(
    video: str = Query(..., description="YouTube video ID (11 characters)"),
    languages: Optional[str] = Query(None, description="Comma-separated language codes (e.g., 'en,es')")
):
    """Passthrough to Edge API GET /youtube/captions"""
    _ensure_edge_configured()

    lang_list = languages.split(",") if languages else None
    captions = edge_api_client.get_captions(video, lang_list)
    if captions is None:
        raise HTTPException(status_code=500, detail="Failed to fetch captions from Edge API")

    return captions


@router.get(
    "/cache/stats",
    response_model=EdgeCacheStats,
    summary="Get Edge API Cache Statistics",
    description="Get cache statistics from Edge API including enabled status, backend type, and TTL.",
)
async def get_cache_stats():
    """Passthrough to Edge API GET /youtube/cache/stats"""
    _ensure_edge_configured()

    stats = edge_api_client.get_cache_stats()
    if stats is None:
        raise HTTPException(status_code=500, detail="Failed to fetch cache stats from Edge API")

    return EdgeCacheStats(**stats)


@router.delete(
    "/cache/clear",
    response_model=EdgeCacheClearResponse,
    summary="Clear Edge API Cache for Video",
    description="Clear cached data for a specific video in Edge API KV storage.",
)
async def clear_edge_cache(
    video: str = Query(..., description="YouTube video ID (11 characters)")
):
    """Passthrough to Edge API DELETE /youtube/cache/clear"""
    _ensure_edge_configured()

    success = edge_api_client.clear_cache(video)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear cache in Edge API")

    return EdgeCacheClearResponse(success=True, message=f"Cache cleared for video {video}")
