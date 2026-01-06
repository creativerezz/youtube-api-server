# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI server for extracting YouTube video data (metadata, captions, timestamps) using YouTube's oEmbed API and youtube-transcript-api.

## Commands

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server (with hot reload)
python -m app.main

# Run tests
pytest

# Run a single test file
pytest tests/test_youtube_endpoints.py

# Run a specific test
pytest tests/test_youtube_endpoints.py::test_function_name
```

### Docker
```bash
docker-compose up -d      # Start container
docker-compose down       # Stop container
docker-compose logs -f    # View logs
```

## Architecture

```
app/
├── main.py              # FastAPI app initialization, CORS, routers
├── core/config.py       # Settings class (reads from .env)
├── models/youtube.py    # Pydantic models (YouTubeRequest, VideoData)
├── routes/youtube.py    # API endpoints under /youtube prefix
└── utils/
    ├── youtube_tools.py # YouTubeTools class with static methods
    └── webshare.py      # WebshareClient singleton for proxy management
```

### Request Flow
1. Routes receive `YouTubeRequest` (url, optional languages[], optional proxy, use_webshare)
2. Routes resolve proxy via `_get_proxy()` (Webshare > manual proxy > none)
3. Routes call static methods on `YouTubeTools` class
4. `YouTubeTools` extracts video ID, fetches data via oEmbed or youtube-transcript-api
5. Captions/timestamps endpoints auto-retry with Webshare proxy on IP block errors

### Key Patterns
- All YouTube operations are static methods in `YouTubeTools` class
- Proxy support is per-request via request body, not environment variables (`session.trust_env = False`)
- Captions/timestamps use `YouTubeTranscriptApi` with `GenericProxyConfig`
- Metadata uses YouTube oEmbed API via requests
- Routes layer handles IP block detection and auto-retry logic (`_retry_with_proxy`)
- Captions/timestamps auto-enable Webshare proxy if configured (more likely to be blocked)

## API Endpoints

- `POST /youtube/video-data` - Get video metadata (title, author, thumbnail)
- `POST /youtube/video-captions` - Get video transcript as concatenated text
- `POST /youtube/video-timestamps` - Get timestamped caption entries

## Environment Variables

- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `WEBSHARE_API_TOKEN` - Webshare API token for proxy list fetching
- `WEBSHARE_PROXY_USERNAME` - Webshare proxy authentication username
- `WEBSHARE_PROXY_PASSWORD` - Webshare proxy authentication password

## Webshare Proxy Integration

The app supports Webshare rotating proxies via `app/utils/webshare.py`:
- `WebshareClient` fetches and caches proxy list from Webshare API
- Set `use_webshare: true` in request body to use a random Webshare proxy
- Proxies are fetched on-demand and cached in memory
- Falls back to manual `proxy` field if `use_webshare` is false
- Captions/timestamps endpoints automatically use Webshare if configured (no flag needed)
