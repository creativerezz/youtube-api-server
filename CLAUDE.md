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
├── models/
│   ├── youtube.py       # Pydantic models (YouTubeRequest, VideoData)
│   ├── edge.py          # Edge API models
│   └── storage.py       # Storage API models
├── routes/
│   ├── youtube.py       # YouTube API endpoints (/youtube/*)
│   ├── edge.py          # Edge API passthrough endpoints (/edge/*)
│   └── storage.py       # Storage API passthrough endpoints (/storage/*)
└── utils/
    ├── youtube_tools.py # YouTubeTools class with static methods
    ├── webshare.py      # WebshareClient singleton for proxy management
    ├── redis_cache.py   # RedisCacheClient for transcript caching
    ├── edge_api.py      # EdgeAPIClient for Edge API integration
    └── storage_api.py   # StorageAPIClient for Storage API integration
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
- `REDIS_URL` - Redis connection URL for caching (optional)
- `WEBSHARE_API_TOKEN` - Webshare API token for proxy list fetching (optional)
- `WEBSHARE_PROXY_USERNAME` - Webshare proxy authentication username (optional)
- `WEBSHARE_PROXY_PASSWORD` - Webshare proxy authentication password (optional)
- `EDGE_API_URL` - YouTube Edge API base URL (optional)
- `EDGE_API_KEY` - YouTube Edge API authentication key (optional)
- `STORAGE_API_URL` - Transcript Storage API base URL (optional)
- `STORAGE_API_KEY` - Transcript Storage API authentication key (optional)

## Webshare Proxy Integration

The app supports Webshare rotating proxies via `app/utils/webshare.py`:
- `WebshareClient` fetches and caches proxy list from Webshare API
- Set `use_webshare: true` in request body to use a random Webshare proxy
- Proxies are fetched on-demand and cached in memory
- Falls back to manual `proxy` field if `use_webshare` is false
- Captions/timestamps endpoints automatically use Webshare if configured (no flag needed)

## External API Integration

### Three-Tier Architecture

This server integrates with two optional Cloudflare Workers APIs for improved performance and reliability:

1. **YouTube Edge API** (`youtube-edge-api.automatehub.workers.dev`)
   - Edge-cached metadata and captions via Cloudflare KV storage
   - Fast global distribution with low latency
   - Automatic fallback if unconfigured or unavailable
   - Passthrough endpoints: `/edge/metadata`, `/edge/captions`, `/edge/cache/stats`, `/edge/cache/clear`

2. **Transcript Storage API** (`youtube-transcript-storage.automatehub.workers.dev`)
   - D1-backed persistent transcript storage
   - Full CRUD operations (fetch, list, get, delete)
   - Usage tracking (fetch_count, last_accessed timestamps)
   - Passthrough endpoints: `/storage/fetch`, `/storage/transcripts`, `/storage/transcripts/{id}`

### Cache Hierarchy

For `/youtube/video-captions` endpoint, the system uses a multi-tier fallback strategy:

1. **Redis Cache** - Fastest (in-memory, 7-day TTL)
2. **Edge API** - Edge KV cache (Cloudflare global network)
3. **Storage API** - Persistent D1 database
4. **Direct YouTube** - Original source (with Webshare proxy support if needed)

For `/youtube/video-data` endpoint:
1. **Edge API** - Edge KV cache
2. **Direct YouTube** - oEmbed API

### Integration Patterns

All external API clients follow the same pattern:
- **Singleton instances**: `edge_api_client`, `storage_api_client`
- **is_configured property**: Check if credentials are set before use
- **Graceful degradation**: Return `None` on errors, don't crash
- **Connection failure tracking**: Skip subsequent requests after auth failures
- **Logging**: `logger.info()` for successes, `logger.warning()` for errors

### Passthrough Endpoints

Direct access to external APIs without fallback logic:

**Edge API** (`/edge/*`):
- `GET /edge/metadata?video={id}` - Get metadata from Edge API
- `GET /edge/captions?video={id}&languages={langs}` - Get captions from Edge API
- `GET /edge/cache/stats` - Get Edge API cache statistics
- `DELETE /edge/cache/clear?video={id}` - Clear Edge API cache for video

**Storage API** (`/storage/*`):
- `POST /storage/fetch` - Fetch and store transcript (body: `{video, languages?, force?}`)
- `GET /storage/transcripts?page={n}&limit={m}` - List stored transcripts
- `GET /storage/transcripts/{video_id}` - Get single transcript
- `DELETE /storage/transcripts/{video_id}` - Delete transcript

All passthrough endpoints return HTTP 503 if the respective API is not configured.

## AI Prompts

The `/prompts` directory contains reusable LLM/AI system prompts for Claude and other AI tools:
- See `prompts/README.md` for usage guidelines and best practices
- Prompts help maintain consistency in AI-assisted development tasks
- Organized by domain (YouTube extraction, API design, testing, deployment)
- Reference these prompts for common project patterns and workflows
