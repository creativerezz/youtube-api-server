import logging
from typing import Optional, List

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageAPIClient:
    """Client for YouTube Transcript Storage API with D1 persistence."""

    def __init__(self):
        self.api_url = settings.STORAGE_API_URL
        self.api_key = settings.STORAGE_API_KEY
        self._connection_failed = False

    @property
    def is_configured(self) -> bool:
        """Check if Storage API credentials are configured."""
        return bool(self.api_url and self.api_key)

    def _get_headers(self) -> dict:
        """Get authorization headers."""
        return {"X-API-Key": self.api_key}

    def fetch_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None,
        force: bool = False
    ) -> Optional[dict]:
        """
        Fetch transcript from Storage API (database or upstream).

        Args:
            video_id: YouTube video ID (11 characters)
            languages: List of language codes (default: ['en'])
            force: Force fetch from upstream even if exists in database

        Returns:
            Dict with video_id, transcript, source, etc. or None on error
        """
        if not self.is_configured or self._connection_failed:
            return None

        try:
            payload = {"video": video_id, "force": force}
            if languages:
                payload["languages"] = languages

            response = requests.post(
                f"{self.api_url}/transcripts/fetch",
                headers=self._get_headers(),
                json=payload,
                timeout=10  # Longer timeout for potential upstream fetch
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.warning(f"Storage API fetch request failed: {e}")
            if e.response.status_code in [401, 403]:
                self._connection_failed = True
            return None
        except requests.RequestException as e:
            logger.warning(f"Storage API fetch request failed: {e}")
            return None

    def get_transcripts(self, page: int = 1, limit: int = 10) -> Optional[dict]:
        """
        Get paginated list of all stored transcripts.

        Args:
            page: Page number (1-indexed)
            limit: Items per page (1-100)

        Returns:
            Dict with transcripts array and pagination info, or None on error
        """
        if not self.is_configured or self._connection_failed:
            return None

        try:
            response = requests.get(
                f"{self.api_url}/transcripts",
                headers=self._get_headers(),
                params={"page": page, "limit": limit},
                timeout=5
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            logger.warning(f"Storage API list request failed: {e}")
            if e.response.status_code in [401, 403]:
                self._connection_failed = True
            return None
        except requests.RequestException as e:
            logger.warning(f"Storage API list request failed: {e}")
            return None

    def get_transcript(self, video_id: str) -> Optional[dict]:
        """
        Get single transcript by video ID.

        Note: This updates last_accessed and increments fetch_count.

        Args:
            video_id: YouTube video ID (11 characters)

        Returns:
            Transcript dict or None if not found/error
        """
        if not self.is_configured or self._connection_failed:
            return None

        try:
            response = requests.get(
                f"{self.api_url}/transcripts/{video_id}",
                headers=self._get_headers(),
                timeout=5
            )
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.debug(f"Transcript not found in Storage API for video {video_id}")
            elif e.response.status_code in [401, 403]:
                logger.warning(f"Storage API authentication failed: {e}")
                self._connection_failed = True
            else:
                logger.warning(f"Storage API get request failed: {e}")
            return None
        except requests.RequestException as e:
            logger.warning(f"Storage API get request failed: {e}")
            return None

    def delete_transcript(self, video_id: str) -> bool:
        """
        Delete transcript from storage.

        Args:
            video_id: YouTube video ID (11 characters)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured or self._connection_failed:
            return False

        try:
            response = requests.delete(
                f"{self.api_url}/transcripts/{video_id}",
                headers=self._get_headers(),
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Deleted transcript from Storage API for video {video_id}")
            return True

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.debug(f"Transcript not found for deletion: {video_id}")
            elif e.response.status_code in [401, 403]:
                logger.warning(f"Storage API authentication failed: {e}")
                self._connection_failed = True
            else:
                logger.warning(f"Storage API delete request failed: {e}")
            return False
        except requests.RequestException as e:
            logger.warning(f"Storage API delete request failed: {e}")
            return False


# Singleton instance
storage_api_client = StorageAPIClient()
