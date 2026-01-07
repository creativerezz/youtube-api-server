import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Application settings

    Reads settings from environment variables or .env file
    """
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "YouTube Tools API"

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS settings - add specific origins in production
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Webshare Proxy settings
    WEBSHARE_API_TOKEN: Optional[str] = os.getenv("WEBSHARE_API_TOKEN")
    WEBSHARE_PROXY_USERNAME: Optional[str] = os.getenv("WEBSHARE_PROXY_USERNAME")
    WEBSHARE_PROXY_PASSWORD: Optional[str] = os.getenv("WEBSHARE_PROXY_PASSWORD")

    # Redis settings
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # YouTube Edge API settings (optional)
    EDGE_API_URL: Optional[str] = os.getenv("EDGE_API_URL")
    EDGE_API_KEY: Optional[str] = os.getenv("EDGE_API_KEY")

    # Transcript Storage API settings (optional)
    STORAGE_API_URL: Optional[str] = os.getenv("STORAGE_API_URL")
    STORAGE_API_KEY: Optional[str] = os.getenv("STORAGE_API_KEY")

# Create settings instance
settings = Settings()