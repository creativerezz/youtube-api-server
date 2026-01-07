import json
import logging
from typing import Optional, List

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache client for YouTube transcript data."""

    # Cache TTL: 7 days (transcripts rarely change)
    DEFAULT_TTL = 60 * 60 * 24 * 7  # 604800 seconds

    # Key prefixes
    PREFIX_CAPTIONS = "yt:captions:"
    PREFIX_TIMESTAMPS = "yt:timestamps:"

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._connection_failed = False

    @property
    def is_configured(self) -> bool:
        """Check if Redis URL is configured."""
        return bool(settings.REDIS_URL)

    def _get_client(self) -> Optional[redis.Redis]:
        """Get or create Redis client with lazy initialization."""
        if self._connection_failed:
            return None

        if self._client is None and self.is_configured:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                # Test connection
                self._client.ping()
                logger.info("Redis connection established")
            except redis.RedisError as e:
                logger.warning(f"Redis connection failed: {e}")
                self._connection_failed = True
                self._client = None

        return self._client

    def _make_key(self, prefix: str, video_id: str, languages: Optional[List[str]]) -> str:
        """Generate cache key from video_id and languages.

        Key format: {prefix}{video_id}:{languages}
        Example: yt:captions:dQw4w9WgXcQ:en
                 yt:captions:dQw4w9WgXcQ:_auto_
                 yt:captions:dQw4w9WgXcQ:en_es
        """
        if languages:
            # Sort for consistent keys regardless of input order
            lang_part = "_".join(sorted(languages))
        else:
            lang_part = "_auto_"

        return f"{prefix}{video_id}:{lang_part}"

    def get_captions(self, video_id: str, languages: Optional[List[str]]) -> Optional[str]:
        """Get cached captions for a video."""
        client = self._get_client()
        if not client:
            return None

        key = self._make_key(self.PREFIX_CAPTIONS, video_id, languages)
        try:
            cached = client.get(key)
            if cached:
                logger.debug(f"Cache hit for captions: {video_id}")
                return cached
            logger.debug(f"Cache miss for captions: {video_id}")
        except redis.RedisError as e:
            logger.warning(f"Redis get failed: {e}")

        return None

    def set_captions(self, video_id: str, languages: Optional[List[str]], captions: str) -> bool:
        """Cache captions for a video."""
        client = self._get_client()
        if not client:
            return False

        key = self._make_key(self.PREFIX_CAPTIONS, video_id, languages)
        try:
            client.setex(key, self.DEFAULT_TTL, captions)
            logger.debug(f"Cached captions for: {video_id}")
            return True
        except redis.RedisError as e:
            logger.warning(f"Redis set failed: {e}")

        return False

    def get_timestamps(self, video_id: str, languages: Optional[List[str]]) -> Optional[List[str]]:
        """Get cached timestamps for a video."""
        client = self._get_client()
        if not client:
            return None

        key = self._make_key(self.PREFIX_TIMESTAMPS, video_id, languages)
        try:
            cached = client.get(key)
            if cached:
                logger.debug(f"Cache hit for timestamps: {video_id}")
                return json.loads(cached)
            logger.debug(f"Cache miss for timestamps: {video_id}")
        except redis.RedisError as e:
            logger.warning(f"Redis get failed: {e}")
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid cached timestamps JSON: {e}")

        return None

    def set_timestamps(self, video_id: str, languages: Optional[List[str]], timestamps: List[str]) -> bool:
        """Cache timestamps for a video."""
        client = self._get_client()
        if not client:
            return False

        key = self._make_key(self.PREFIX_TIMESTAMPS, video_id, languages)
        try:
            client.setex(key, self.DEFAULT_TTL, json.dumps(timestamps))
            logger.debug(f"Cached timestamps for: {video_id}")
            return True
        except redis.RedisError as e:
            logger.warning(f"Redis set failed: {e}")

        return False


# Singleton instance
redis_cache = RedisCache()
