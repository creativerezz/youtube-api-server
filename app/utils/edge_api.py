import logging
from typing import Optional, List

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class EdgeAPIClient:
    """Client for YouTube Edge API with KV caching."""

    def __init__(self):
        self.api_url = settings.EDGE_API_URL
        self.api_key = settings.EDGE_API_KEY
        self._connection_failed = False

    @property
    def is_configured(self) -> bool:
        """Check if Edge API credentials are configured."""
        return bool(self.api_url and self.api_key)

    def _get_headers(self) -> dict:
        """Get authorization headers."""
        return {"X-API-Key": self.api_key}

    def get_metadata(self, video_id: str) -> Optional[dict]:
        """
        Get video metadata from Edge API.

        Args:
            video_id: YouTube video ID (11 characters)

        Returns:
            VideoData-compatible dict or None on error
        """
        if not self.is_configured or self._connection_failed:
            return None

        try:
            response = requests.get(
                f"{self.api_url}/youtube/metadata",
                headers=self._get_headers(),
                params={"video": video_id},
                timeout=5
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.warning(f"Edge API metadata request failed: {e}")
            if e.response.status_code in [401, 403]:
                self._connection_failed = True
            return None
        except requests.RequestException as e:
            logger.warning(f"Edge API metadata request failed: {e}")
            return None

    def get_captions(self, video_id: str, languages: Optional[List[str]] = None) -> Optional[str]:
        """
        Get video captions from Edge API.

        Args:
            video_id: YouTube video ID (11 characters)
            languages: List of language codes (e.g., ['en', 'es'])

        Returns:
            Concatenated caption text or None on error
        """
        if not self.is_configured or self._connection_failed:
            return None

        try:
            params = {"video": video_id}
            if languages:
                # Join languages with comma for query parameter
                params["languages"] = ",".join(languages)

            response = requests.get(
                f"{self.api_url}/youtube/captions",
                headers=self._get_headers(),
                params=params,
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            # Extract caption text from response
            # Assuming response format: {"captions": "text", ...}
            return data.get("captions") or data.get("transcript") or data.get("text")

        except requests.HTTPError as e:
            logger.warning(f"Edge API captions request failed: {e}")
            if e.response.status_code in [401, 403]:
                self._connection_failed = True
            return None
        except requests.RequestException as e:
            logger.warning(f"Edge API captions request failed: {e}")
            return None

    def get_cache_stats(self) -> Optional[dict]:
        """
        Get cache statistics from Edge API.

        Returns:
            Cache stats dict or None on error
        """
        if not self.is_configured or self._connection_failed:
            return None

        try:
            response = requests.get(
                f"{self.api_url}/youtube/cache/stats",
                headers=self._get_headers(),
                timeout=5
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.warning(f"Edge API cache stats request failed: {e}")
            if e.response.status_code in [401, 403]:
                self._connection_failed = True
            return None
        except requests.RequestException as e:
            logger.warning(f"Edge API cache stats request failed: {e}")
            return None

    def clear_cache(self, video_id: str) -> bool:
        """
        Clear cache for a specific video in Edge API.

        Args:
            video_id: YouTube video ID (11 characters)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured or self._connection_failed:
            return False

        try:
            response = requests.delete(
                f"{self.api_url}/youtube/cache/clear",
                headers=self._get_headers(),
                params={"video": video_id},
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Cleared Edge API cache for video {video_id}")
            return True

        except requests.HTTPError as e:
            logger.warning(f"Edge API cache clear request failed: {e}")
            if e.response.status_code in [401, 403]:
                self._connection_failed = True
            return False
        except requests.RequestException as e:
            logger.warning(f"Edge API cache clear request failed: {e}")
            return False


# Singleton instance
edge_api_client = EdgeAPIClient()
