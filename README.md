# YouTube Summaries API

[![Tests](https://github.com/creativerezz/youtube-summaries-api/actions/workflows/tests.yml/badge.svg)](https://github.com/creativerezz/youtube-summaries-api/actions/workflows/tests.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A FastAPI-based server that provides convenient endpoints for extracting information from YouTube videos, including video metadata, captions, timestamped transcripts, summaries, and AI-powered features.

## Features

### Core Video Extraction
- Get video metadata (title, author, thumbnails, etc.)
- Extract video captions/transcripts with language fallback
- Generate timestamped transcripts
- List available transcript languages for videos
- Support for 20+ YouTube URL formats including Shorts, Live, Mobile, Music
- Support for direct video IDs (just pass `"dQw4w9WgXcQ"`)

### AI-Powered Features 🤖 (New!)
- **Generate structured notes** from video transcripts (summary, structured, or detailed)
- **Translate transcripts** to 50+ languages with AI
- **OpenRouter API proxy** - Direct access to 100+ AI models (default: free Xiaomi MiMo model)
- Perfect for building YouTube video translation tools with ElevenLabs voice dubbing
- Powered by OpenRouter (Claude 3.5 and 100+ other models available)

### Performance & Infrastructure
- **Redis caching layer** for 10-56x performance boost on video data
- Webshare proxy integration to avoid IP blocking
- Async processing with parallel execution
- Clean and RESTful API design
- Comprehensive error handling
- Cache management endpoints for monitoring and control
- Graceful degradation when optional features unavailable

## Quick Links

- 🚀 **[API Quick Reference](API_QUICK_REFERENCE.md)** - Fast copy-paste examples for frontend developers
- 🤖 **[AI Features Guide](AI_FEATURES.md)** - Video notes & translation with Claude AI (New!)
- 📘 **[Frontend Integration Guide](FRONTEND_INTEGRATION.md)** - Complete React, Vue, Next.js examples
- 🎯 **[Quick Start](QUICK_START.md)** - Get started in 2 minutes
- 📊 **[Redis Setup](REDIS_SETUP.md)** - Enable caching for 10-56x performance boost
- 📖 **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference with examples
- 🧪 **[Testing Guide](TESTING_GUIDE.md)** - Performance testing and quality assurance

## Quick Deploy to Railway

Deploy this API server to Railway in 2 minutes:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?template=https://github.com/creativerezz/youtube-summaries-api)

See [QUICK_START.md](QUICK_START.md) for detailed deployment instructions.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

1. Clone the repository:
```bash
git clone https://github.com/creativerezz/youtube-summaries-api.git
cd youtube-summaries-api
```

2. Install dependencies using uv (recommended):
```bash
uv sync
```

## Configuration

### Environment Variables

The server supports the following configuration options:

**Proxy Configuration (Optional):**
- `WEBSHARE_PROXY_USERNAME` - Your Webshare proxy username (optional)
- `WEBSHARE_PROXY_PASSWORD` - Your Webshare proxy password (optional)

**Redis Caching (Optional but Recommended):**
- `REDIS_URL` - Redis connection URL (e.g., `redis://localhost:6379`)
- `CACHE_TTL_SECONDS` - Cache expiration time in seconds (default: 3600)

**AI Features (Optional):**
- `OPENROUTER_API_KEY` - OpenRouter API key for /video-notes and /video-translate endpoints

**Server Configuration:**
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

You can set these in your environment or create a `.env` file in the project root. See [.env.example](.env.example) for a template.

### Redis Caching Setup

Redis caching dramatically improves performance by caching YouTube API responses. See the [Redis Setup Guide](REDIS_SETUP.md) for:
- Local development setup with Docker or native Redis
- Railway deployment with managed Redis
- Cache configuration and monitoring
- Performance optimization tips

### Check Environment Setup

Use the included environment checker:
```bash
python load_env.py
```

This will verify your environment configuration and show which variables are set.

## Running the Server

Start the server using:

```bash
uv run main.py
```

By default, the server runs on:
- Host: 0.0.0.0
- Port: 8000

You can customize these using environment variables:
```bash
export PORT=8080
export HOST=127.0.0.1
uv run main.py
```

## API Endpoints

### 1. Health Check
```http
GET /health
```

**Response:** Server status, proxy configuration, cache status, and system information.

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "proxy_status": "webshare_enabled",
  "cache_status": "redis_enabled",
  "cache_ttl_seconds": 3600,
  "parallel_processing": "enabled"
}
```

### 2. Cache Statistics
```http
GET /cache/stats
```

**Response:** Redis cache performance metrics.

```json
{
  "enabled": true,
  "status": "connected",
  "total_keys": 42,
  "ttl_seconds": 3600,
  "keyspace_hits": 156,
  "keyspace_misses": 42
}
```

### 3. Clear Cache
```http
POST /cache/clear
```

**Response:** Clears all cached data.

```json
{
  "success": true,
  "message": "Cache cleared successfully",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 4. Get Video Metadata (Cached)
```http
POST /video-data
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:** Video metadata including title, author, thumbnails, duration, etc.

### 5. List Available Transcript Languages (Cached)
```http
POST /video-transcript-languages
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:** List of available transcript languages with details about generated vs manual transcripts.

### 6. Get Video Captions (Cached)
```http
POST /video-captions
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "languages": ["en", "es"]  // Optional, supports fallback
}
```

**Response:** Complete transcript text of the video with automatic language fallback.

### 7. Get Video Timestamps (Cached)
```http
POST /video-timestamps
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "languages": ["en"]  // Optional, supports fallback
}
```

**Response:** List of timestamps with corresponding caption text and timing information.

### 8. OpenRouter API Proxy
```http
POST /openrouter-proxy
```

**Request Body:**
```json
{
    "prompt": "Your prompt here",
    "model": "xiaomi/mimo-v2-flash:free",  // Optional, defaults to xiaomi/mimo-v2-flash:free
    "max_tokens": 800  // Optional, defaults to 800
}
```

**Response:** Raw response from OpenRouter API including model output, usage statistics, and cost information.

**Example:**
```json
{
  "response": {
    "id": "gen-...",
    "model": "xiaomi/mimo-v2-flash:free",
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "Your AI-generated response here"
      }
    }],
    "usage": {
      "prompt_tokens": 43,
      "completion_tokens": 16,
      "total_tokens": 59,
      "cost": 0
    }
  }
}
```

**Features:**
- Direct proxy to OpenRouter's chat completions API
- Default free model: `xiaomi/mimo-v2-flash:free` (no cost)
- Support for custom model selection
- Rate limited to 30 requests/minute
- Requires `OPENROUTER_API_KEY` environment variable

## Example Usage

### Using curl

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Get video metadata
curl -X POST "http://localhost:8000/video-data" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# List available languages
curl -X POST "http://localhost:8000/video-transcript-languages" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Get video captions with language fallback
curl -X POST "http://localhost:8000/video-captions" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "languages": ["en", "es"]}'

# Get timestamped transcript
curl -X POST "http://localhost:8000/video-timestamps" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "languages": ["en"]}'

# Use OpenRouter proxy for AI requests
curl -X POST "http://localhost:8000/openrouter-proxy" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Explain quantum computing in simple terms"}'
```

### Using Python

```python
import requests

base_url = "http://localhost:8000"
video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get video metadata
response = requests.post(f"{base_url}/video-data",
                        json={"url": video_url})
metadata = response.json()

# Get captions
response = requests.post(f"{base_url}/video-captions",
                        json={"url": video_url, "languages": ["en"]})
captions = response.json()["captions"]

# Use OpenRouter proxy
response = requests.post(f"{base_url}/openrouter-proxy",
                        json={"prompt": "Summarize this video transcript",
                              "max_tokens": 500})
ai_response = response.json()["response"]["choices"][0]["message"]["content"]
```

## Testing

The project includes a comprehensive performance testing suite with detailed metrics:

```bash
# Run all performance tests
./run_tests.sh

# Run specific test suite
./run_tests.sh health    # Health & cache endpoints
./run_tests.sh video     # Video data endpoints
./run_tests.sh ai        # AI-powered endpoints
./run_tests.sh storage   # Storage endpoints
./run_tests.sh prompts   # Prompt management

# Skip optional tests
./run_tests.sh --skip-ai --skip-storage
```

**Test Coverage:**
- ✓ Performance metrics (response times, throughput, success rates)
- ✓ All 22 API endpoints
- ✓ Error handling and edge cases
- ✓ Cache effectiveness
- ✓ Complete workflow testing

**See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing documentation.**

### Legacy Test Script

The original endpoint test script is still available:
```bash
./test_endpoints.sh
```

## Error Handling

The API includes comprehensive error handling for:
- Invalid YouTube URLs (400 Bad Request)
- Missing or unavailable captions (500 Internal Server Error)
- Network errors and proxy issues
- Invalid language codes
- Malformed requests (422 Unprocessable Entity)
- Server connectivity issues

## Proxy Support

The server supports Webshare proxy integration to avoid YouTube's IP blocking:

1. Sign up for a [Webshare](https://www.webshare.io/) account
2. Set your credentials as environment variables:
   ```bash
   export WEBSHARE_PROXY_USERNAME="your_username"
   export WEBSHARE_PROXY_PASSWORD="your_password"
   ```
3. Restart the server - proxy will be automatically enabled

## Performance Features

- **Async Processing**: All transcript operations run asynchronously
- **Parallel Execution**: Blocking operations are executed in background threads
- **Language Fallback**: Automatic fallback to available languages
- **Proxy Rotation**: Webshare proxy integration for reliable access

## Dependencies

The project uses these main dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `youtube-transcript-api` - YouTube transcript extraction
- `pydantic` - Data validation
- `gunicorn` - Production WSGI server

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests (`./test_endpoints.sh`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Clone and install dependencies:
```bash
git clone https://github.com/creativerezz/youtube-summaries-api.git
cd youtube-summaries-api
uv sync
```

2. Check environment setup:
```bash
python load_env.py
```

3. Run the server:
```bash
python main.py
```

4. Run tests:
```bash
./test_endpoints.sh
```

Please make sure to test your changes with the provided test script before submitting.
