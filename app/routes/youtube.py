from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.youtube import YouTubeRequest
from app.utils.youtube_tools import YouTubeTools
from app.utils.webshare import webshare_client

router = APIRouter(
    prefix="/youtube",
    tags=["youtube"],
    responses={404: {"description": "Not found"}},
)


def _get_proxy(request: YouTubeRequest) -> Optional[str]:
    """Resolve proxy URL from request, using Webshare if requested."""
    if request.use_webshare:
        if not webshare_client.is_configured:
            raise HTTPException(status_code=500, detail="Webshare proxy not configured")
        proxy_url = webshare_client.get_proxy_url()
        if not proxy_url:
            raise HTTPException(status_code=503, detail="No Webshare proxies available")
        return proxy_url
    return request.proxy


@router.post("/video-data")
async def get_video_data(request: YouTubeRequest):
    """Endpoint to get video metadata"""
    proxy = _get_proxy(request)
    return YouTubeTools.get_video_data(request.url, proxy)


@router.post("/video-captions")
async def get_video_captions(request: YouTubeRequest):
    """Endpoint to get video captions"""
    proxy = _get_proxy(request)
    return YouTubeTools.get_video_captions(request.url, request.languages, proxy)


@router.post("/video-timestamps")
async def get_video_timestamps(request: YouTubeRequest):
    """Endpoint to get video timestamps"""
    proxy = _get_proxy(request)
    return YouTubeTools.get_video_timestamps(request.url, request.languages, proxy)
