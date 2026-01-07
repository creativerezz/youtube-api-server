import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Body, Path

from app.models.storage import (
    StorageFetchRequest,
    StorageFetchResponse,
    StorageTranscript,
    StorageTranscriptList
)
from app.utils.storage_api import storage_api_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/storage",
    tags=["Storage API"],
    responses={
        503: {
            "description": "Storage API not configured or unavailable",
            "content": {
                "application/json": {
                    "example": {"detail": "Storage API not configured. Set STORAGE_API_URL and STORAGE_API_KEY."}
                }
            }
        }
    }
)


def _ensure_storage_configured():
    """Raise HTTP 503 if Storage API is not configured."""
    if not storage_api_client.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Storage API not configured. Set STORAGE_API_URL and STORAGE_API_KEY."
        )


@router.post(
    "/fetch",
    response_model=StorageFetchResponse,
    summary="Fetch and Store Transcript",
    description="Fetch transcript from Storage API database or upstream YouTube. Stores in D1 for persistence.",
)
async def fetch_transcript(
    request: Annotated[StorageFetchRequest, Body(
        openapi_examples={
            "basic": {
                "summary": "Basic fetch",
                "value": {"video": "dQw4w9WgXcQ"}
            },
            "with_languages": {
                "summary": "With language codes",
                "value": {"video": "dQw4w9WgXcQ", "languages": ["en", "es"]}
            },
            "force_upstream": {
                "summary": "Force upstream fetch",
                "description": "Force fetch from YouTube even if exists in database",
                "value": {"video": "dQw4w9WgXcQ", "force": True}
            }
        }
    )]
):
    """Passthrough to Storage API POST /transcripts/fetch"""
    _ensure_storage_configured()

    result = storage_api_client.fetch_transcript(
        request.video,
        request.languages,
        request.force
    )
    if not result:
        raise HTTPException(status_code=500, detail="Failed to fetch transcript from Storage API")

    return StorageFetchResponse(**result)


@router.get(
    "/transcripts",
    response_model=StorageTranscriptList,
    summary="List All Stored Transcripts",
    description="Get paginated list of all transcripts stored in D1 database.",
)
async def list_transcripts(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)")
):
    """Passthrough to Storage API GET /transcripts"""
    _ensure_storage_configured()

    result = storage_api_client.get_transcripts(page, limit)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to fetch transcripts from Storage API")

    return StorageTranscriptList(**result)


@router.get(
    "/transcripts/{video_id}",
    response_model=StorageTranscript,
    summary="Get Single Transcript",
    description="Get transcript for a specific video from Storage API. Updates last_accessed and increments fetch_count.",
)
async def get_transcript(
    video_id: str = Path(..., description="YouTube video ID (11 characters)")
):
    """Passthrough to Storage API GET /transcripts/{videoId}"""
    _ensure_storage_configured()

    result = storage_api_client.get_transcript(video_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Transcript not found for video {video_id}")

    return StorageTranscript(**result)


@router.delete(
    "/transcripts/{video_id}",
    summary="Delete Transcript",
    description="Delete transcript for a specific video from D1 database storage.",
)
async def delete_transcript(
    video_id: str = Path(..., description="YouTube video ID (11 characters)")
):
    """Passthrough to Storage API DELETE /transcripts/{videoId}"""
    _ensure_storage_configured()

    success = storage_api_client.delete_transcript(video_id)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to delete transcript for video {video_id}")

    return {"success": True, "message": f"Transcript deleted for video {video_id}"}
