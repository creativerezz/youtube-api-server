import logging
import random
from typing import Optional, List
from dataclasses import dataclass

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class WebshareProxy:
    """Represents a Webshare proxy."""
    proxy_address: Optional[str]
    port: int
    username: str
    password: str
    country_code: str

    # Gateway address for backbone/residential proxies
    BACKBONE_GATEWAY = "p.webshare.io"

    def to_url(self) -> str:
        """Return proxy URL in http://user:pass@host:port format."""
        # Use backbone gateway if proxy_address is null (residential proxies)
        host = self.proxy_address or self.BACKBONE_GATEWAY
        return f"http://{self.username}:{self.password}@{host}:{self.port}"


class WebshareClient:
    """Client for fetching proxies from Webshare API."""

    API_BASE = "https://proxy.webshare.io/api/v2"

    def __init__(self):
        self.api_token = settings.WEBSHARE_API_TOKEN
        self.username = settings.WEBSHARE_PROXY_USERNAME
        self.password = settings.WEBSHARE_PROXY_PASSWORD
        self._proxy_cache: List[WebshareProxy] = []

    @property
    def is_configured(self) -> bool:
        """Check if Webshare credentials are configured."""
        return all([self.api_token, self.username, self.password])

    def _get_headers(self) -> dict:
        """Get authorization headers."""
        return {"Authorization": f"Token {self.api_token}"}

    def fetch_proxies(self, page_size: int = 100) -> List[WebshareProxy]:
        """Fetch proxy list from Webshare API."""
        if not self.is_configured:
            logger.warning("Webshare credentials not configured")
            return []

        try:
            # Use backbone mode for residential proxies
            response = requests.get(
                f"{self.API_BASE}/proxy/list/",
                headers=self._get_headers(),
                params={"page_size": page_size, "mode": "backbone"},
            )
            response.raise_for_status()
            data = response.json()

            proxies = []
            for proxy_data in data.get("results", []):
                # Accept proxies that are valid, or if valid field is not present, accept all
                if proxy_data.get("valid", True):
                    proxy = WebshareProxy(
                        proxy_address=proxy_data["proxy_address"],
                        port=proxy_data["port"],
                        username=proxy_data.get("username", self.username),
                        password=proxy_data.get("password", self.password),
                        country_code=proxy_data.get("country_code", ""),
                    )
                    proxies.append(proxy)

            self._proxy_cache = proxies
            logger.info(f"Fetched {len(proxies)} valid proxies from Webshare")
            return proxies

        except requests.HTTPError as e:
            # Log the actual error response for debugging
            error_detail = ""
            try:
                error_detail = f" - {e.response.text}"
            except:
                pass
            logger.error(f"Failed to fetch Webshare proxies: {e}{error_detail}")
            return []
        except requests.RequestException as e:
            logger.error(f"Failed to fetch Webshare proxies: {e}")
            return []

    def get_random_proxy(self) -> Optional[WebshareProxy]:
        """Get a random proxy from the cache, fetching if empty."""
        if not self._proxy_cache:
            self.fetch_proxies()

        if self._proxy_cache:
            return random.choice(self._proxy_cache)
        return None

    def get_proxy_url(self) -> Optional[str]:
        """Get a random proxy URL string."""
        proxy = self.get_random_proxy()
        return proxy.to_url() if proxy else None


# Singleton instance
webshare_client = WebshareClient()
