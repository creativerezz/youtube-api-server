from typing import Optional, List
from pydantic import BaseModel, Field


class StorageFetchRequest(BaseModel):
    """Request for POST /transcripts/fetch"""

    video: str = Field(
        ...,
        description="YouTube video ID or URL",
        json_schema_extra={"examples": ["dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"]}
    )
    languages: Optional[List[str]] = Field(
        default=None,
        description="Language codes for captions",
        json_schema_extra={"examples": [["en"], ["en", "es"]]}
    )
    force: bool = Field(
        default=False,
        description="Force fetch from upstream even if exists in database"
    )


class StorageFetchResponse(BaseModel):
    """Response from POST /transcripts/fetch"""

    video_id: str = Field(description="YouTube video ID")
    transcript: str = Field(description="Full transcript text")
    source: str = Field(description="Source of data: 'database' or 'upstream'")
    languages: Optional[List[str]] = Field(default=None, description="Language codes used")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    last_accessed: Optional[str] = Field(default=None, description="Last accessed timestamp")


class StorageTranscript(BaseModel):
    """Single transcript from Storage API"""

    video_id: str = Field(description="YouTube video ID")
    transcript: str = Field(description="Full transcript text")
    languages: Optional[List[str]] = Field(default=None, description="Language codes")
    fetch_count: int = Field(description="Number of times fetched")
    created_at: str = Field(description="Creation timestamp (ISO 8601)")
    last_accessed: str = Field(description="Last accessed timestamp (ISO 8601)")


class StorageTranscriptList(BaseModel):
    """Response from GET /transcripts (paginated)"""

    transcripts: List[StorageTranscript] = Field(description="Array of transcript objects")
    total: int = Field(description="Total number of transcripts")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
