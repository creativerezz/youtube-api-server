"""
Tests for Edge API client.
Demonstrates testing patterns for external API clients.
"""
import pytest
from unittest.mock import patch, MagicMock
import requests

from app.utils.edge_api import edge_api_client


class TestEdgeAPIClient:
    """Tests for EdgeAPIClient"""

    def test_is_configured_returns_true_when_credentials_set(self):
        """Test is_configured property when credentials are set."""
        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "test-key-123"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            assert client.is_configured is True

    def test_is_configured_returns_false_when_credentials_missing(self):
        """Test is_configured property when credentials are missing."""
        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = None
            mock_settings.EDGE_API_KEY = None

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            assert client.is_configured is False

    @patch('app.utils.edge_api.requests.get')
    def test_get_metadata_success(self, mock_get):
        """Test successful metadata fetch."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test Video",
            "author_name": "Test Author",
            "thumbnail_url": "https://example.com/thumb.jpg",
            "type": "video"
        }
        mock_get.return_value = mock_response

        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "test-key"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.get_metadata("dQw4w9WgXcQ")

            assert result is not None
            assert result["title"] == "Test Video"
            assert result["author_name"] == "Test Author"
            mock_get.assert_called_once()

    @patch('app.utils.edge_api.requests.get')
    def test_get_metadata_http_error(self, mock_get):
        """Test metadata fetch with HTTP error."""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 500
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "test-key"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.get_metadata("dQw4w9WgXcQ")

            assert result is None

    @patch('app.utils.edge_api.requests.get')
    def test_get_metadata_auth_failure_sets_connection_failed(self, mock_get):
        """Test that authentication failures set connection_failed flag."""
        # Mock 401 error
        mock_response = MagicMock()
        mock_response.status_code = 401
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "invalid-key"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.get_metadata("dQw4w9WgXcQ")

            assert result is None
            assert client._connection_failed is True

    @patch('app.utils.edge_api.requests.get')
    def test_get_captions_success(self, mock_get):
        """Test successful captions fetch."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "captions": "Hello world. This is a test transcript."
        }
        mock_get.return_value = mock_response

        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "test-key"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.get_captions("dQw4w9WgXcQ", ["en"])

            assert result is not None
            assert "Hello world" in result
            mock_get.assert_called_once()

    @patch('app.utils.edge_api.requests.get')
    def test_get_captions_with_multiple_languages(self, mock_get):
        """Test captions fetch with multiple language codes."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"captions": "Test content"}
        mock_get.return_value = mock_response

        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "test-key"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.get_captions("dQw4w9WgXcQ", ["en", "es"])

            assert result is not None
            # Verify languages are joined with comma
            call_args = mock_get.call_args
            assert call_args[1]["params"]["languages"] == "en,es"

    def test_get_metadata_returns_none_when_not_configured(self):
        """Test that methods return None when client is not configured."""
        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = None
            mock_settings.EDGE_API_KEY = None

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.get_metadata("dQw4w9WgXcQ")

            assert result is None

    @patch('app.utils.edge_api.requests.delete')
    def test_clear_cache_success(self, mock_delete):
        """Test successful cache clear."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_delete.return_value = mock_response

        with patch('app.utils.edge_api.settings') as mock_settings:
            mock_settings.EDGE_API_URL = "https://edge-api.example.com"
            mock_settings.EDGE_API_KEY = "test-key"

            from app.utils.edge_api import EdgeAPIClient
            client = EdgeAPIClient()

            result = client.clear_cache("dQw4w9WgXcQ")

            assert result is True
            mock_delete.assert_called_once()
