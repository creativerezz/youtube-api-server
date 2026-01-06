import json
from typing import Optional, List
from urllib.parse import urlparse, parse_qs, urlencode

import requests
from fastapi import HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig

class YouTubeTools:
    @staticmethod
    def get_youtube_video_id(url: str) -> Optional[str]:
        """Function to get the video ID from a YouTube URL."""
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        if hostname == "youtu.be":
            return parsed_url.path[1:]
        if hostname in ("www.youtube.com", "youtube.com"):
            if parsed_url.path == "/watch":
                query_params = parse_qs(parsed_url.query)
                return query_params.get("v", [None])[0]
            if parsed_url.path.startswith("/embed/"):
                return parsed_url.path.split("/")[2]
            if parsed_url.path.startswith("/v/"):
                return parsed_url.path.split("/")[2]
        return None

    @staticmethod
    def get_video_data(url: str, proxy: Optional[str] = None) -> dict:
        """Function to get video data from a YouTube URL.

        Args:
            url: Link to the YouTube video.
            proxy: Optional HTTP/HTTPS proxy URL used for the request.
        """
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            params = {"format": "json", "url": f"https://www.youtube.com/watch?v={video_id}"}
            oembed_url = "https://www.youtube.com/oembed"
            proxies = {"http": proxy, "https": proxy} if proxy else {}
            session = requests.Session()
            session.trust_env = False  # ignore HTTP(S)_PROXY environment variables
            response = session.get(oembed_url, params=params, proxies=proxies)
            response.raise_for_status()
            video_data = response.json()
            clean_data = {
                "title": video_data.get("title"),
                "author_name": video_data.get("author_name"),
                "author_url": video_data.get("author_url"),
                "type": video_data.get("type"),
                "height": video_data.get("height"),
                "width": video_data.get("width"),
                "version": video_data.get("version"),
                "provider_name": video_data.get("provider_name"),
                "provider_url": video_data.get("provider_url"),
                "thumbnail_url": video_data.get("thumbnail_url"),
            }
            return clean_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting video data: {str(e)}")

    @staticmethod
    def get_video_captions(url: str, languages: Optional[List[str]] = None, proxy: Optional[str] = None) -> str:
        """Get captions from a YouTube video.

        Args:
            url: Link to the YouTube video.
            languages: Optional list of language codes to filter captions.
            proxy: Optional HTTP/HTTPS proxy URL used for the request.
        """
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            proxy_config = GenericProxyConfig(http_url=proxy, https_url=proxy) if proxy else None
            session = requests.Session()
            session.trust_env = False  # ignore HTTP(S)_PROXY environment variables
            api = YouTubeTranscriptApi(proxy_config=proxy_config, http_client=session)
            captions = api.fetch(video_id, languages=languages or ["en"])
            if captions:
                return " ".join(snippet.text for snippet in captions)
            return "No captions found for video"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting captions for video: {str(e)}")

    @staticmethod
    def get_video_timestamps(url: str, languages: Optional[List[str]] = None, proxy: Optional[str] = None) -> List[str]:
        """Generate timestamps for a YouTube video based on captions.

        Args:
            url: Link to the YouTube video.
            languages: Optional list of language codes to filter captions.
            proxy: Optional HTTP/HTTPS proxy URL used for the request.
        """
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            proxy_config = GenericProxyConfig(http_url=proxy, https_url=proxy) if proxy else None
            session = requests.Session()
            session.trust_env = False  # ignore HTTP(S)_PROXY environment variables
            api = YouTubeTranscriptApi(proxy_config=proxy_config, http_client=session)
            captions = api.fetch(video_id, languages=languages or ["en"])
            timestamps = []
            for snippet in captions:
                start = int(snippet.start)
                minutes, seconds = divmod(start, 60)
                timestamps.append(f"{minutes}:{seconds:02d} - {snippet.text}")
            return timestamps
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating timestamps: {str(e)}")
