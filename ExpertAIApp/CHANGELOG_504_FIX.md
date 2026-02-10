# Changelog: 504 Timeout Fix & Logging Improvements

## Summary
Added comprehensive logging, increased default timeout, and created troubleshooting documentation to help diagnose and fix 504 Gateway Timeout errors in production Docker environments.

## Changes Made

### 1. Added Logging Infrastructure
**New file:** `server/logutil.py`
- Centralized logging configuration
- Outputs to stdout for Docker log collection
- Standardized log format with timestamps and levels

### 2. Enhanced `server/llm.py`
- ✅ Added detailed timing logs for all LLM API calls
- ✅ Increased default timeout from 60s to 120s
- ✅ Added configurable timeout via `CONCIRCLE_OPENAI_TIMEOUT` environment variable
- ✅ Log request start, completion time, and errors
- ✅ Better error messages with timing information

**Key changes:**
- Import `time` and `logger`
- `_post_json()` now logs timing and uses configurable timeout
- Logs: "Starting LLM request", "completed in X.XXs", "failed after X.XXs"

### 3. Enhanced `server/server.py`
- ✅ Added timing logs for `/api/admin/summarize` endpoint
- ✅ Added timing logs for `/api/admin/compare` endpoint
- ✅ Import `time` and `logger`
- ✅ Log request start, completion, and failures with timing

**Log examples:**
```
[INFO] Starting summarize request with 5 submissions
[INFO] Summarize completed in 90.45s
[ERROR] Comparison failed after 125.30s: TimeoutError: ...
```

### 4. Updated Dockerfile
- ✅ Set default `CONCIRCLE_OPENAI_TIMEOUT=180` (3 minutes)
- Can be overridden at runtime

### 5. Documentation

**New files:**
- `TROUBLESHOOTING.md` - Comprehensive troubleshooting guide
- `QUICK_FIX_504.md` - Quick reference for immediate fixes
- `docker-compose.yml` - Example with proper timeout configuration
- `nginx.conf.example` - Nginx configuration with increased timeouts
- `CHANGELOG_504_FIX.md` - This file

**Updated files:**
- `README.md` - Added `CONCIRCLE_OPENAI_TIMEOUT` env var and link to troubleshooting

## Environment Variables

### New Variable
| Variable | Default | Description |
|----------|---------|-------------|
| `CONCIRCLE_OPENAI_TIMEOUT` | 180 | Timeout in seconds for OpenAI API calls |

### How to Use

**Docker run:**
```bash
docker run -e CONCIRCLE_OPENAI_TIMEOUT=240 ...
```

**docker-compose.yml:**
```yaml
environment:
  - CONCIRCLE_OPENAI_TIMEOUT=240
```

**Local development:**
```bash
export CONCIRCLE_OPENAI_TIMEOUT=240
python3 -m server.server
```

## Troubleshooting 504 Errors

### Quick Diagnostic Commands

```bash
# Check logs for timing
docker logs <container> | grep -E "completed in|failed after"

# Real-time monitoring
docker logs -f <container>

# Check container resources
docker stats <container>
```

### Common Solutions

1. **Increase timeout** (recommended):
   - Set `CONCIRCLE_OPENAI_TIMEOUT=240` or higher

2. **Increase proxy timeout** (if using Nginx/Apache):
   - Nginx: `proxy_read_timeout 250s;`
   - Apache: `ProxyTimeout 250`

3. **Use faster model**:
   - Switch from `gpt-4` to `gpt-3.5-turbo` or `gpt-4o-mini`

4. **Check OpenAI status**:
   - Visit https://status.openai.com

## Deployment Steps

### 1. Rebuild Docker Image
```bash
docker build -t expert-ai-app .
```

### 2. Update docker-compose.yml (if using)
```yaml
services:
  app:
    environment:
      - CONCIRCLE_OPENAI_TIMEOUT=180  # Or higher if needed
```

### 3. Restart Container
```bash
docker-compose down
docker-compose up -d
```

### 4. Monitor Logs
```bash
docker-compose logs -f app | grep -E "INFO|ERROR"
```

### 5. Test Summarize Feature
- Submit test data
- Click "Summarize expert answers"
- Check logs for timing information

## Expected Log Output

**Successful request:**
```
2026-01-28 10:00:00 [INFO] server.server: Starting summarize request with 5 submissions
2026-01-28 10:00:01 [INFO] server.llm: Starting LLM request to https://api.openai.com/v1/chat/completions (timeout: 180s, model: gpt-4o-mini)
2026-01-28 10:00:45 [INFO] server.llm: LLM request completed in 44.23s
2026-01-28 10:01:30 [INFO] server.llm: Starting LLM request to https://api.openai.com/v1/chat/completions (timeout: 180s, model: gpt-4o-mini)
2026-01-28 10:02:15 [INFO] server.llm: LLM request completed in 45.12s
2026-01-28 10:02:15 [INFO] server.server: Summarize completed in 135.67s
```

**Failed request (timeout):**
```
2026-01-28 10:00:00 [INFO] server.server: Starting summarize request with 10 submissions
2026-01-28 10:00:01 [INFO] server.llm: Starting LLM request (timeout: 120s, model: gpt-4)
2026-01-28 10:02:01 [ERROR] server.llm: LLM request error after 120.00s: TimeoutError
2026-01-28 10:02:01 [ERROR] server.server: Summarize failed after 120.10s: RuntimeError: LLM request failed
```

## Testing

### Local Test
1. Set environment variable:
   ```bash
   export CONCIRCLE_OPENAI_TIMEOUT=240
   ```

2. Start server:
   ```bash
   python3 -m server.server
   ```

3. Watch logs in terminal

### Docker Test
1. Build and run:
   ```bash
   docker build -t expert-ai-app .
   docker run -e CONCIRCLE_OPENAI_TIMEOUT=240 -p 3000:3000 expert-ai-app
   ```

2. Check logs:
   ```bash
   docker logs -f <container_id>
   ```

## Rollback

If issues occur, revert to previous version:
```bash
git checkout <previous_commit>
docker build -t expert-ai-app .
docker-compose up -d
```

## Support

For issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [QUICK_FIX_504.md](QUICK_FIX_504.md)
3. Examine Docker logs with timing info
4. Verify OpenAI API status

## Files Modified

- ✅ `server/llm.py` - Added logging and configurable timeout
- ✅ `server/server.py` - Added request timing logs
- ✅ `Dockerfile` - Set default timeout
- ✅ `README.md` - Added timeout env var documentation

## Files Created

- ✅ `server/logutil.py` - Logging utilities
- ✅ `TROUBLESHOOTING.md` - Detailed troubleshooting guide
- ✅ `QUICK_FIX_504.md` - Quick reference
- ✅ `docker-compose.yml` - Example configuration
- ✅ `nginx.conf.example` - Nginx configuration example
- ✅ `CHANGELOG_504_FIX.md` - This changelog
