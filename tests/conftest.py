"""
Pytest configuration and shared fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_videos():
    """Fixture providing test video URLs."""
    return [
        "https://www.youtube.com/watch?v=4v4PJoxm8Bc",
        "https://www.youtube.com/watch?v=zN-rElTzR_4",
        "https://www.youtube.com/watch?v=6ivM8DwXB7Q",
        "https://www.youtube.com/watch?v=PLKrSVuT-Dg",
        "https://www.youtube.com/watch?v=_uvwh9x_MQ0",
    ]
