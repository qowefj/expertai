## AI Challenge Workshop (Plain HTML + Python)

Multi-user workshop web app where experts submit their answers. A moderator can then view all submissions and generate AI-powered summaries. Supports **German and English** with a language toggle.

### Features

**User Page (`/`):**
- Language toggle (DE/EN) and theme toggle (light/dark)
- Experts enter their name and answer questions
- Click "Submit" to save (no AI triggered at this point)
- Submissions stored persistently in JSON file
- No limit on number of submissions

**Admin Page (`/admin.html?key=YOUR_KEY`):**
- Protected by secret URL key
- View all submitted expert answers
- "Summarize expert answers" button to generate:
  - **Expert Summary** (from all expert submissions)
  - **AI Insight** (from questions only; single call)
  - **Final Insight** (merge of Expert + AI)
- All insights are constrained to **max 2000 characters**
- View all individual submissions at the bottom
- Clear all submissions option

### Environment variables

- `CONCIRCLE_OPENAI_BASE_URL` (e.g. `https://api.openai.com/v1`)
- `CONCIRCLE_OPENAI_API_KEY`
- `CONCIRCLE_OPENAI_MODEL` (e.g. `gpt-5.2`)
- `CONCIRCLE_OPENAI_TIMEOUT` - Timeout in seconds for OpenAI API calls (default: `180`)
- `ADMIN_SECRET_KEY` - Admin page access key (default: `admin123`)
- Optional: `CONCIRCLE_OPENAI_API_MODE=auto|responses|chat_completions`
- Optional (MVP-only): `CONCIRCLE_SSL_VERIFY=0` (disables TLS verification)

**Note:** If experiencing 504 Gateway Timeout errors, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Run locally (no npm)

```bash
export CONCIRCLE_OPENAI_BASE_URL="https://api.openai.com/v1"
export CONCIRCLE_OPENAI_API_KEY="..."
export CONCIRCLE_OPENAI_MODEL="gpt-5.2"
export CONCIRCLE_OPENAI_API_MODE="auto"
export ADMIN_SECRET_KEY="mysecretkey"

python3 -m server.server
```

- User page: `http://localhost:3000`
- Admin page: `http://localhost:3000/admin.html?key=mysecretkey`

### Docker

Build:

```bash
docker build -t expert-ai-app .
```

Run:

```bash
docker run -d -p 3200:3000 \
  -v /path/to/local/data:/app/data \
  -e CONCIRCLE_OPENAI_BASE_URL="https://api.openai.com/v1" \
  -e CONCIRCLE_OPENAI_API_KEY="your-api-key" \
  -e CONCIRCLE_OPENAI_MODEL="gpt-5-mini-2025-08-07" \
  -e CONCIRCLE_OPENAI_TIMEOUT="180" \
  -e ADMIN_SECRET_KEY="mysecretkey" \
  expert-ai-app
```

- User page: `http://<host>:3200/`
- Admin page: `http://<host>:3200/admin.html?key=mysecretkey`

**Important:** The `-v /path/to/local/data:/app/data` volume mount is **required** to persist submissions across container restarts. Replace `/path/to/local/data` with an actual directory on your host machine (e.g., `$(pwd)/data` or `/var/lib/expert-ai/data`).

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/questions` | GET | Get all questions |
| `/api/submissions/count` | GET | Get current submission count |
| `/api/submit` | POST | Submit expert answers |
| `/api/admin/submissions?key=KEY` | GET | Get all submissions (admin) |
| `/api/admin/summarize?key=KEY` | POST | Generate AI summary (admin) |
| `/api/admin/merge?key=KEY` | POST | Merge insights (admin) |
| `/api/admin/clear?key=KEY` | GET | Clear all submissions (admin) |
