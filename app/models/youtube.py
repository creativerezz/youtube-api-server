import re
from typing import Optional, List
from urllib.parse import urlparse, parse_qs
from pydantic import BaseModel, Field, model_validator


class YouTubeRequest(BaseModel):
    """Model for YouTube API requests."""

    video: str = Field(
        ...,
        description="YouTube video URL or video ID",
        json_schema_extra={
            "examples": ["dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://youtu.be/dQw4w9WgXcQ"]
        }
    )
    languages: Optional[List[str]] = Field(
        default=None,
        description="Language codes for captions (e.g., ['en', 'es'])",
        json_schema_extra={"examples": [["en"], ["en", "es"]]}
    )
    use_webshare: bool = Field(
        default=False,
        description="Use Webshare rotating proxy for the request"
    )
    proxy: Optional[str] = Field(
        default=None,
        description="Custom HTTP/HTTPS proxy URL (ignored if use_webshare is true)",
        json_schema_extra={"examples": ["http://user:pass@proxy.example.com:8080"]}
    )

    # Resolved video ID (set by validator)
    video_id: Optional[str] = Field(default=None, exclude=True)

    @model_validator(mode='after')
    def parse_video_id(self) -> 'YouTubeRequest':
        """Extract video ID from URL or use directly if already an ID."""
        video = self.video.strip()
        video_id = None

        # Check if it's a URL
        if video.startswith(('http://', 'https://', 'www.')):
            parsed = urlparse(video if '://' in video else f'https://{video}')
            hostname = parsed.hostname or ''

            if hostname == 'youtu.be':
                # https://youtu.be/VIDEO_ID
                video_id = parsed.path.lstrip('/')
            elif hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
                if parsed.path == '/watch':
                    # https://youtube.com/watch?v=VIDEO_ID
                    query_params = parse_qs(parsed.query)
                    video_id = query_params.get('v', [None])[0]
                elif parsed.path.startswith('/embed/'):
                    # https://youtube.com/embed/VIDEO_ID
                    video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else None
                elif parsed.path.startswith('/v/'):
                    # https://youtube.com/v/VIDEO_ID
                    video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else None
                elif parsed.path.startswith('/shorts/'):
                    # https://youtube.com/shorts/VIDEO_ID
                    video_id = parsed.path.split('/')[2] if len(parsed.path.split('/')) > 2 else None
        else:
            # Assume it's a video ID (11 characters, alphanumeric with - and _)
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video):
                video_id = video

        self.video_id = video_id
        return self

    @property
    def url(self) -> str:
        """Return full YouTube URL for the video."""
        if self.video_id:
            return f"https://www.youtube.com/watch?v={self.video_id}"
        return self.video

class VideoData(BaseModel):
    """YouTube video metadata from oEmbed API."""

    title: Optional[str] = Field(default=None, description="Video title")
    author_name: Optional[str] = Field(default=None, description="Channel name")
    author_url: Optional[str] = Field(default=None, description="Channel URL")
    type: Optional[str] = Field(default=None, description="Media type (video)")
    height: Optional[int] = Field(default=None, description="Embed height")
    width: Optional[int] = Field(default=None, description="Embed width")
    version: Optional[str] = Field(default=None, description="oEmbed version")
    provider_name: Optional[str] = Field(default=None, description="Provider (YouTube)")
    provider_url: Optional[str] = Field(default=None, description="Provider URL")
    thumbnail_url: Optional[str] = Field(default=None, description="Video thumbnail URL")


class TimestampEntry(BaseModel):
    """A single timestamped caption entry."""

    time: str = Field(description="Timestamp in M:SS format")
    text: str = Field(description="Caption text at this timestamp")
