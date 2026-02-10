# Troubleshooting 504 Gateway Timeout Errors

## What Causes 504 Errors?

A 504 Gateway Timeout occurs when:
1. **OpenAI API is slow** - The LLM takes > 60s to respond (most common)
2. **Network issues** - Slow connection to OpenAI
3. **Resource constraints** - Docker container out of memory/CPU
4. **Reverse proxy timeout** - Nginx/proxy times out before Python completes

---

## Quick Diagnostics

### 1. Check Docker Logs
```bash
# Real-time logs
docker logs -f <container_name>

# Last 200 lines
docker logs --tail 200 <container_name>

# Filter errors only
docker logs <container_name> 2>&1 | grep -E "ERROR|error|timeout|504"

# Check timing logs
docker logs <container_name> | grep -E "completed in|failed after"
```

### 2. Check Container Resources
```bash
# Check CPU/Memory usage
docker stats <container_name>

# Check if container is being OOM killed
docker inspect <container_name> | grep -A 10 OOMKilled
```

### 3. Check OpenAI API Status
```bash
# Test API connectivity
curl -i https://api.openai.com/v1/models \
  -H "Authorization: Bearer $CONCIRCLE_OPENAI_API_KEY"
```

---

## Solutions

### Solution 1: Increase Timeouts (Recommended)

The app now supports configurable timeouts via environment variables.

**In your `docker-compose.yml` or Docker run command:**

```yaml
services:
  app:
    environment:
      # Increase OpenAI API timeout (default: 120 seconds)
      - CONCIRCLE_OPENAI_TIMEOUT=180
      
      # If using Nginx/proxy
      - PROXY_READ_TIMEOUT=200
```

**Or with docker run:**
```bash
docker run -e CONCIRCLE_OPENAI_TIMEOUT=180 ...
```

### Solution 2: Increase Nginx/Proxy Timeouts

If you're using Nginx as a reverse proxy:

```nginx
location /api/ {
    proxy_pass http://app:3000;
    proxy_read_timeout 200s;  # Increase from default 60s
    proxy_connect_timeout 200s;
    proxy_send_timeout 200s;
}
```

For Apache:
```apache
ProxyTimeout 200
```

### Solution 3: Use Streaming Responses (Future Enhancement)

For very long operations, consider implementing streaming responses or webhooks.

### Solution 4: Optimize LLM Calls

**Current behavior:** The `/api/admin/summarize` endpoint makes 2 parallel LLM calls.

**If still timing out:**
- Reduce `max_tokens` in prompts
- Use faster models (e.g., `gpt-3.5-turbo` instead of `gpt-4`)
- Split into sequential calls instead of parallel

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `CONCIRCLE_OPENAI_TIMEOUT` | 120 | Timeout in seconds for OpenAI API calls |
| `CONCIRCLE_OPENAI_MODEL` | - | Model to use (e.g., `gpt-4o-mini`) |
| `CONCIRCLE_OPENAI_BASE_URL` | - | OpenAI API base URL |
| `CONCIRCLE_OPENAI_API_KEY` | - | Your OpenAI API key |
| `CONCIRCLE_SSL_VERIFY` | 1 | Set to `0` or `false` to disable SSL verification |
| `ADMIN_SECRET_KEY` | admin123 | Admin password for `/admin.html` |
| `HOST` | 0.0.0.0 | Server bind address |
| `PORT` | 3000 | Server port |

---

## Log Analysis

### Understanding the Logs

With the new logging, you'll see:

```log
2026-01-28 10:00:00 [INFO] server.server: Starting summarize request with 5 submissions
2026-01-28 10:00:01 [INFO] server.llm: Starting LLM request to https://api.openai.com/v1/chat/completions (timeout: 120s, model: gpt-4o-mini)
2026-01-28 10:00:45 [INFO] server.llm: LLM request completed in 44.23s
2026-01-28 10:01:30 [INFO] server.server: Summarize completed in 90.45s
```

**If you see a timeout:**
```log
2026-01-28 10:02:00 [ERROR] server.llm: LLM request error after 120.00s: TimeoutError: ...
2026-01-28 10:02:00 [ERROR] server.server: Summarize failed after 120.10s: RuntimeError: LLM request failed
```

### Common Patterns

1. **Slow OpenAI responses (> 60s)**
   - Solution: Increase `CONCIRCLE_OPENAI_TIMEOUT`
   - Or switch to faster model

2. **Proxy timeout before app timeout**
   - Log shows: "completed in 90s" but user sees 504
   - Solution: Increase proxy timeout > app timeout

3. **Memory issues**
   - Log shows: Process killed or OOM
   - Solution: Increase Docker memory limit

---

## Production Checklist

- [ ] Set `CONCIRCLE_OPENAI_TIMEOUT` to at least 180 seconds
- [ ] Configure reverse proxy timeouts > 200 seconds
- [ ] Monitor logs with `docker logs -f`
- [ ] Set up log aggregation (ELK, Datadog, etc.)
- [ ] Configure Docker resource limits (memory, CPU)
- [ ] Set up health checks
- [ ] Consider using a faster OpenAI model for production
- [ ] Test with realistic data volumes before going live

---

## Testing Timeout Fixes

1. **Start the container with new timeout:**
   ```bash
   docker run -e CONCIRCLE_OPENAI_TIMEOUT=180 <image>
   ```

2. **Submit test data and trigger summarize**

3. **Monitor logs:**
   ```bash
   docker logs -f <container> | grep -E "Starting|completed|failed"
   ```

4. **Expected output:**
   ```
   [INFO] Starting summarize request
   [INFO] LLM request completed in XX.XXs
   [INFO] Summarize completed in XX.XXs
   ```

---

## Need More Help?

1. Check logs with timing information
2. Test OpenAI API directly with curl
3. Check Docker container resources with `docker stats`
4. Verify network connectivity to OpenAI
5. Review nginx/proxy logs if using one

If issues persist, the problem may be:
- OpenAI API rate limiting
- Network firewall blocking long-running connections
- OpenAI service degradation (check status.openai.com)
