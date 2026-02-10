# Quick Fix for 504 Gateway Timeout

## Immediate Solutions

### 1. Increase App Timeout (Easiest)

Add to your docker-compose.yml or docker run command:

```yaml
environment:
  - CONCIRCLE_OPENAI_TIMEOUT=240  # 4 minutes instead of default 3
```

Or with docker run:
```bash
docker run -e CONCIRCLE_OPENAI_TIMEOUT=240 ...
```

### 2. Increase Nginx/Proxy Timeout

If using Nginx, add to your location block:

```nginx
location /api/ {
    proxy_read_timeout 250s;
    proxy_connect_timeout 250s;
    proxy_send_timeout 250s;
}
```

### 3. Check the Logs

```bash
# See what's timing out
docker logs <container> | grep -E "timeout|504|failed after"

# Real-time monitoring
docker logs -f <container>
```

## What to Look For in Logs

**Good (working):**
```
[INFO] Starting summarize request
[INFO] LLM request completed in 45.23s
[INFO] Summarize completed in 90.45s
```

**Bad (timing out):**
```
[ERROR] LLM request error after 120.00s: TimeoutError
[ERROR] Summarize failed after 120.10s
```

## Quick Test

1. Restart with new timeout:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. Try the summarize feature again

3. Check logs:
   ```bash
   docker-compose logs -f app
   ```

## Still Timing Out?

1. **Use faster model:**
   ```yaml
   - CONCIRCLE_OPENAI_MODEL=gpt-3.5-turbo  # Instead of gpt-4
   ```

2. **Check OpenAI status:** https://status.openai.com

3. **Test API directly:**
   ```bash
   curl -X POST https://api.openai.com/v1/chat/completions \
     -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'
   ```

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
