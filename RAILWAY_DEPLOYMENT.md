# Railway Deployment Guide

## Environment Variables

Configure the following environment variables in your Railway project settings:

### Required Variables

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Optional: Redis Caching

```bash
# Redis URL (Railway can provision this automatically)
REDIS_URL=redis://default:password@host:port
```

### Optional: Webshare Proxy

```bash
# For rotating residential/datacenter proxies
WEBSHARE_API_TOKEN=your_webshare_api_token_here
WEBSHARE_PROXY_USERNAME=your_webshare_username
WEBSHARE_PROXY_PASSWORD=your_webshare_password
```

### Optional: Edge API (Cloudflare Workers)

```bash
# YouTube Edge API for edge-cached metadata and captions
EDGE_API_URL=https://youtube-edge-api.automatehub.workers.dev
EDGE_API_KEY=your_edge_api_key_here
```

### Optional: Storage API (Cloudflare D1)

```bash
# Transcript Storage API for persistent D1 storage
STORAGE_API_URL=https://youtube-transcript-storage.automatehub.workers.dev
STORAGE_API_KEY=your_storage_api_key_here
```

## Quick Setup via Railway CLI

If you have the Railway CLI installed, you can set all variables at once:

```bash
# Required
railway variables set HOST=0.0.0.0
railway variables set PORT=8000
railway variables set LOG_LEVEL=INFO

# Optional: Edge API
railway variables set EDGE_API_URL=https://youtube-edge-api.automatehub.workers.dev
railway variables set EDGE_API_KEY=your_edge_api_key

# Optional: Storage API
railway variables set STORAGE_API_URL=https://youtube-transcript-storage.automatehub.workers.dev
railway variables set STORAGE_API_KEY=your_storage_api_key

# Optional: Webshare Proxy
railway variables set WEBSHARE_API_TOKEN=your_token
railway variables set WEBSHARE_PROXY_USERNAME=your_username
railway variables set WEBSHARE_PROXY_PASSWORD=your_password

# Optional: Redis (or provision via Railway dashboard)
railway variables set REDIS_URL=redis://...
```

## Performance Tiers

### Minimal Setup (No external APIs)
- Direct YouTube API calls only
- No caching beyond request-level
- Suitable for low-volume usage

### Standard Setup (Redis only)
```bash
REDIS_URL=redis://...
```
- In-memory caching with 7-day TTL
- Significantly reduces YouTube API calls
- Recommended for moderate usage

### Enhanced Setup (Redis + Edge API)
```bash
REDIS_URL=redis://...
EDGE_API_URL=https://youtube-edge-api.automatehub.workers.dev
EDGE_API_KEY=your_key
```
- Multi-tier caching: Redis → Edge KV
- Fast global edge responses
- Recommended for high-volume usage

### Full Setup (All services)
```bash
REDIS_URL=redis://...
EDGE_API_URL=https://youtube-edge-api.automatehub.workers.dev
EDGE_API_KEY=your_key
STORAGE_API_URL=https://youtube-transcript-storage.automatehub.workers.dev
STORAGE_API_KEY=your_key
WEBSHARE_API_TOKEN=your_token
WEBSHARE_PROXY_USERNAME=your_username
WEBSHARE_PROXY_PASSWORD=your_password
```
- Maximum performance and reliability
- Multi-tier fallback: Redis → Edge → Storage → Direct
- Proxy support for IP block avoidance
- Recommended for production usage

## Cache Hierarchy

With all services enabled:

1. **Redis** - Fastest (in-memory, 7-day TTL)
2. **Edge API** - Edge KV cache (Cloudflare global network)
3. **Storage API** - Persistent D1 database
4. **Direct YouTube** - Original source (with optional proxy)

## Verification

After deploying, verify the API is working:

```bash
# Check health
curl https://your-app.railway.app/health

# Test video metadata
curl -X POST https://your-app.railway.app/youtube/video-data \
  -H "Content-Type: application/json" \
  -d '{"video": "dQw4w9WgXcQ"}'

# Test captions
curl -X POST https://your-app.railway.app/youtube/video-captions \
  -H "Content-Type: application/json" \
  -d '{"video": "dQw4w9WgXcQ"}'
```

## Monitoring

Check logs for integration status:

```bash
railway logs
```

Look for:
- `Served metadata from Edge API` - Edge API is working
- `Served captions from Storage API` - Storage API is working
- `IP block detected, retrying with Webshare proxy` - Proxy fallback is working

## Troubleshooting

### Edge API not working
- Verify `EDGE_API_URL` and `EDGE_API_KEY` are set correctly
- Check logs for authentication errors
- Test Edge API directly: `curl https://youtube-edge-api.automatehub.workers.dev/youtube/metadata?video=dQw4w9WgXcQ -H "X-API-Key: your_key"`

### Storage API not working
- Verify `STORAGE_API_URL` and `STORAGE_API_KEY` are set correctly
- Check logs for authentication errors
- Test Storage API directly: `curl https://youtube-transcript-storage.automatehub.workers.dev/transcripts -H "X-API-Key: your_key"`

### Webshare proxy not working
- Verify all three Webshare variables are set
- Check if proxies are available in your Webshare account
- Review logs for proxy-related errors

## Railway Project Link

Project dashboard: https://railway.com/project/17f6e323-9de2-4540-9255-60e4200e804a
