from typing import Optional
from pydantic import BaseModel, Field


class EdgeCacheStats(BaseModel):
    """Response from GET /youtube/cache/stats"""

    enabled: bool = Field(description="Whether caching is enabled")
    backend: str = Field(description="Cache backend type (e.g., 'kv')")
    ttl_seconds: int = Field(description="Time-to-live for cached items in seconds")
    kv_namespace: Optional[str] = Field(default=None, description="KV namespace name")


class EdgeCacheClearResponse(BaseModel):
    """Response from DELETE /youtube/cache/clear"""

    success: bool = Field(description="Whether cache clear was successful")
    message: str = Field(description="Result message")
