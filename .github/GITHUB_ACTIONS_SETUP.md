# GitHub Actions Setup Guide

## Overview

The YouTube Summaries API uses GitHub Actions for continuous integration (CI). Tests run automatically on every push and pull request to ensure code quality.

## Workflows

### 1. Tests Workflow (`tests.yml`)

Runs comprehensive API tests with two configurations:

**Job 1: Full Tests (with Redis)**
- ✓ All 22 API endpoints
- ✓ Health & cache tests
- ✓ Video data & transcripts
- ✓ Storage tests (with Redis)
- ✓ Prompts management
- ✓ AI features (if API key configured)

**Job 2: Minimal Tests (without Redis)**
- ✓ Core API endpoints
- ✓ Video data & transcripts
- ✓ Prompts management
- ✗ Skips storage tests (require Redis)
- ✗ Skips AI tests (optional)

## Required Setup

### 1. No Additional Setup Required

The basic tests run automatically without any configuration:
- ✓ Health checks
- ✓ Video data extraction
- ✓ Transcript fetching
- ✓ Prompt management

### 2. Optional: Configure Secrets for Full Testing

To enable all features in CI, add these secrets to your GitHub repository:

#### Add Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

**For AI Features (Optional):**
- **Name:** `OPENROUTER_API_KEY`
- **Value:** Your OpenRouter API key
- **Purpose:** Enables AI-powered features (notes, translation)

**For Proxy Features (Optional):**
- **Name:** `WEBSHARE_PROXY_USERNAME`
- **Value:** Your Webshare proxy username
- **Purpose:** Enables proxy support for YouTube requests

- **Name:** `WEBSHARE_PROXY_PASSWORD`
- **Value:** Your Webshare proxy password
- **Purpose:** Enables proxy support for YouTube requests

#### Secrets Summary

| Secret | Required | Purpose |
|--------|----------|---------|
| `OPENROUTER_API_KEY` | No | AI features (notes, translation) |
| `WEBSHARE_PROXY_USERNAME` | No | Proxy support for YouTube |
| `WEBSHARE_PROXY_PASSWORD` | No | Proxy support for YouTube |

## What Gets Tested

### Automatic Tests (No Secrets Required)
- ✓ API health checks
- ✓ Video metadata fetching
- ✓ Transcript extraction
- ✓ Language detection
- ✓ Timestamped transcripts
- ✓ Prompt management (36 prompts)
- ✓ Cache management
- ✓ Error handling

### Optional Tests (Require Secrets)
- AI-powered notes generation (requires `OPENROUTER_API_KEY`)
- AI-powered translation (requires `OPENROUTER_API_KEY`)
- OpenRouter API proxy (requires `OPENROUTER_API_KEY`)

### With Redis (Automatic in CI)
- Transcript storage
- Cache statistics
- Storage workflow tests

## Viewing Test Results

### On GitHub

1. Go to your repository
2. Click the **Actions** tab
3. Click on any workflow run to see results
4. Expand jobs to see detailed test output

### Status Badge

The README includes a status badge that shows:
- ✓ Green: All tests passing
- ✗ Red: Tests failing
- ○ Yellow: Tests running

## Local Testing

To run the same tests locally:

```bash
# Full test suite (requires Redis)
./run_tests.sh

# Skip AI tests (no API key needed)
./run_tests.sh --skip-ai

# Skip storage tests (no Redis needed)
./run_tests.sh --skip-storage

# Minimal tests (no Redis, no AI)
./run_tests.sh --skip-ai --skip-storage
```

## Troubleshooting

### Tests Failing in CI but Passing Locally

1. **Check Redis connection**
   - CI uses Redis service container
   - Ensure tests don't depend on local Redis data

2. **Check environment variables**
   - CI uses secrets from GitHub
   - Verify secrets are set correctly

3. **Check Python version**
   - CI uses Python 3.12
   - Ensure compatibility with Python 3.12+

### Server Not Starting in CI

1. **Check server logs**
   - Workflow outputs server logs on failure
   - Look for port conflicts or dependency issues

2. **Check dependencies**
   - Ensure all dependencies in `pyproject.toml`
   - Run `uv sync` to verify locally

### Timeout Issues

If tests timeout:
1. Increase wait time in workflow (currently 60s)
2. Check for hanging processes
3. Verify network connectivity

## Workflow Customization

### Modify Test Timeout

Edit `.github/workflows/tests.yml`:

```yaml
- name: Wait for server to be ready
  run: |
    for i in {1..30}; do  # Change 30 to desired timeout in 2s intervals
      ...
    done
```

### Add Additional Test Jobs

```yaml
test-python-311:
  name: Test on Python 3.11
  runs-on: ubuntu-latest
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    # ... rest of steps
```

### Run on Different Branches

Edit the `on:` section:

```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Add your branches
  pull_request:
    branches: [ main ]
```

## Best Practices

1. **Keep Secrets Secure**
   - Never commit secrets to git
   - Use GitHub secrets for sensitive data
   - Rotate API keys regularly

2. **Test Before Pushing**
   - Run tests locally first
   - Use `./run_tests.sh` before pushing
   - Verify all tests pass

3. **Monitor CI Runs**
   - Check Actions tab after push
   - Fix failures promptly
   - Keep CI green

4. **Update Dependencies**
   - Keep `pyproject.toml` updated
   - Test with latest dependencies
   - Pin critical versions

## Support

- **Tests failing?** Check the Actions tab for detailed logs
- **Need help?** Open an issue on GitHub
- **Feature request?** Submit a pull request

## Related Documentation

- [Testing Guide](../../TESTING_GUIDE.md) - Local testing documentation
- [API Documentation](../../API_DOCUMENTATION.md) - API reference
- [README](../../README.md) - Project overview
