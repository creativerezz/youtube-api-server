import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException

from app.models.youtube import YouTubeRequest, VideoData
from app.utils.youtube_tools import YouTubeTools
from app.utils.webshare import webshare_client

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
    responses={
        400: {"description": "Invalid YouTube URL or video ID"},
        500: {"description": "Error fetching data from YouTube"},
    },
)


def _is_ip_block_error(error_message: str) -> bool:
    """Check if error message indicates an IP block from YouTube."""
    error_lower = error_message.lower()
    return any(keyword in error_lower for keyword in [
        "ip has been blocked",
        "ip belonging to a cloud provider",
        "blocked by youtube",
        "requestblocked",
        "ipblocked",
        "youtube is blocking requests"
    ])


def _get_proxy(request: YouTubeRequest, auto_use_webshare: bool = False) -> Optional[str]:
    """Resolve proxy URL from request, using Webshare if requested or auto-enabled.
    
    Args:
        request: The YouTube request object
        auto_use_webshare: If True, automatically use Webshare proxy if configured
    """
    # Explicit use_webshare flag takes precedence
    if request.use_webshare:
        if not webshare_client.is_configured:
            raise HTTPException(status_code=500, detail="Webshare proxy not configured")
        proxy_url = webshare_client.get_proxy_url()
        if not proxy_url:
            raise HTTPException(status_code=503, detail="No Webshare proxies available")
        return proxy_url
    
    # Auto-use Webshare if enabled and configured
    if auto_use_webshare and webshare_client.is_configured:
        proxy_url = webshare_client.get_proxy_url()
        if proxy_url:
            return proxy_url
    
    # Fall back to manual proxy if provided
    return request.proxy


def _retry_with_proxy(func, *args, initial_proxy: Optional[str] = None, **kwargs):
    """Execute a function and retry with Webshare proxy if IP block error occurs.
    
    Args:
        func: The function to execute
        *args: Positional arguments for the function
        initial_proxy: Initial proxy to use (may be None)
        **kwargs: Keyword arguments for the function (proxy should be in kwargs)
    """
    try:
        return func(*args, **kwargs)
    except HTTPException as e:
        # Check if it's an IP block error and we haven't tried with proxy yet
        if _is_ip_block_error(str(e.detail)) and not initial_proxy and webshare_client.is_configured:
            logger.info("IP block detected, retrying with Webshare proxy")
            proxy_url = webshare_client.get_proxy_url()
            if proxy_url:
                kwargs['proxy'] = proxy_url
                return func(*args, **kwargs)
        raise


@router.post(
    "/video-data",
    response_model=VideoData,
    summary="Get Video Metadata",
    description="Fetch video metadata (title, author, thumbnail) using YouTube's oEmbed API.",
)
async def get_video_data(request: YouTubeRequest) -> VideoData:
    """Get video metadata including title, author, and thumbnail URL."""
    if not request.video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL or video ID")
    proxy = _get_proxy(request)
    return YouTubeTools.get_video_data(request.url, proxy)


@router.post(
    "/video-captions",
    response_model=str,
    summary="Get Video Captions",
    description="Fetch the full transcript/captions as concatenated text. Automatically uses proxy if configured.",
)
async def get_video_captions(request: YouTubeRequest) -> str:
    """Get video transcript as a single text string."""
    if not request.video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL or video ID")
    proxy = _get_proxy(request, auto_use_webshare=True)
    return _retry_with_proxy(
        YouTubeTools.get_video_captions,
        request.url,
        request.languages,
        initial_proxy=proxy,
        proxy=proxy
    )


@router.post(
    "/video-timestamps",
    response_model=List[str],
    summary="Get Timestamped Captions",
    description="Fetch captions with timestamps in 'M:SS - text' format. Automatically uses proxy if configured.",
)
async def get_video_timestamps(request: YouTubeRequest) -> List[str]:
    """Get video captions with timestamps."""
    if not request.video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL or video ID")
    proxy = _get_proxy(request, auto_use_webshare=True)
    return _retry_with_proxy(
        YouTubeTools.get_video_timestamps,
        request.url,
        request.languages,
        initial_proxy=proxy,
        proxy=proxy
    )
