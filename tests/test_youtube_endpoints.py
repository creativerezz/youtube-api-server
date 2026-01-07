"""
Tests for YouTube API endpoints.
Tests multiple video URLs to ensure endpoints work correctly.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

# Test video URLs
TEST_VIDEOS = [
    "https://www.youtube.com/watch?v=4v4PJoxm8Bc",
    "https://www.youtube.com/watch?v=zN-rElTzR_4",
    "https://www.youtube.com/watch?v=6ivM8DwXB7Q",
    "https://www.youtube.com/watch?v=PLKrSVuT-Dg",
    "https://www.youtube.com/watch?v=_uvwh9x_MQ0",
]


class TestVideoData:
    """Tests for /youtube/video-data endpoint."""

    @pytest.mark.parametrize("url", TEST_VIDEOS)
    def test_get_video_data(self, client, url):
        """Test getting video metadata for each test video."""
        response = client.post(
            "/youtube/video-data",
            json={"video": url}
        )
        assert response.status_code == 200, f"Failed for URL: {url}"
        data = response.json()
        
        # Verify required fields
        assert "title" in data
        assert data["title"] is not None
        assert "author_name" in data
        assert "thumbnail_url" in data
        assert "type" in data
        assert data["type"] == "video"

    def test_get_video_data_invalid_url(self, client):
        """Test video-data endpoint with invalid URL."""
        response = client.post(
            "/youtube/video-data",
            json={"video": "https://invalid-url.com"}
        )
        assert response.status_code == 400

    def test_get_video_data_missing_url(self, client):
        """Test video-data endpoint with missing URL."""
        response = client.post(
            "/youtube/video-data",
            json={}
        )
        assert response.status_code == 422  # Validation error


class TestVideoCaptions:
    """Tests for /youtube/video-captions endpoint."""

    @pytest.mark.parametrize("url", TEST_VIDEOS)
    def test_get_video_captions(self, client, url):
        """Test getting video captions for each test video."""
        response = client.post(
            "/youtube/video-captions",
            json={"video": url}
        )
        # Note: May fail if IP is blocked, but should work with auto-proxy
        if response.status_code == 200:
            data = response.json()
            # Response should be a string (captions text)
            assert isinstance(data, str)
            assert len(data) > 0, "Captions should not be empty"
        else:
            # If blocked, check error message
            error_detail = response.json().get("detail", "")
            assert "blocked" in error_detail.lower() or "error" in error_detail.lower()

    @pytest.mark.parametrize("url", TEST_VIDEOS)
    def test_get_video_captions_with_languages(self, client, url):
        """Test getting video captions with specific language."""
        response = client.post(
            "/youtube/video-captions",
            json={"video": url, "languages": ["en"]}
        )
        # May succeed or fail depending on proxy/IP blocking
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, str)

    def test_get_video_captions_invalid_url(self, client):
        """Test video-captions endpoint with invalid URL."""
        response = client.post(
            "/youtube/video-captions",
            json={"video": "https://invalid-url.com"}
        )
        assert response.status_code == 400

    def test_get_video_captions_with_webshare_proxy(self, client):
        """Test video-captions with explicit Webshare proxy flag."""
        # Test with first video URL
        url = TEST_VIDEOS[0]
        response = client.post(
            "/youtube/video-captions",
            json={"video": url, "use_webshare": True}
        )
        # Should work if Webshare is configured, or return appropriate error
        assert response.status_code in [200, 500, 503]


class TestVideoTimestamps:
    """Tests for /youtube/video-timestamps endpoint."""

    @pytest.mark.parametrize("url", TEST_VIDEOS)
    def test_get_video_timestamps(self, client, url):
        """Test getting video timestamps for each test video."""
        response = client.post(
            "/youtube/video-timestamps",
            json={"video": url}
        )
        # May succeed or fail depending on proxy/IP blocking
        if response.status_code == 200:
            data = response.json()
            # Response should be a list of timestamp strings
            assert isinstance(data, list)
            if len(data) > 0:
                # Check format: "minutes:seconds - text"
                assert ":" in data[0] and "-" in data[0]

    @pytest.mark.parametrize("url", TEST_VIDEOS)
    def test_get_video_timestamps_with_languages(self, client, url):
        """Test getting video timestamps with specific language."""
        response = client.post(
            "/youtube/video-timestamps",
            json={"video": url, "languages": ["en"]}
        )
        # May succeed or fail depending on proxy/IP blocking
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_video_timestamps_invalid_url(self, client):
        """Test video-timestamps endpoint with invalid URL."""
        response = client.post(
            "/youtube/video-timestamps",
            json={"video": "https://invalid-url.com"}
        )
        assert response.status_code == 400


class TestRootEndpoints:
    """Tests for root endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestVideoIDExtraction:
    """Tests for video ID extraction from various URL formats."""

    def test_standard_youtube_url(self, client):
        """Test standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=4v4PJoxm8Bc"
        response = client.post(
            "/youtube/video-data",
            json={"video": url}
        )
        assert response.status_code == 200

    def test_youtube_short_url(self, client):
        """Test youtu.be short URL."""
        url = "https://youtu.be/4v4PJoxm8Bc"
        response = client.post(
            "/youtube/video-data",
            json={"video": url}
        )
        assert response.status_code == 200

    def test_youtube_embed_url(self, client):
        """Test YouTube embed URL."""
        url = "https://www.youtube.com/embed/4v4PJoxm8Bc"
        response = client.post(
            "/youtube/video-data",
            json={"video": url}
        )
        assert response.status_code == 200
