# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ExpertAIApp is a full-stack AI Challenge Workshop application where experts submit answers to questions and a moderator generates AI-powered summaries comparing expert vs AI insights. Built with Python 3.12 backend (stdlib only, no framework) and vanilla JavaScript frontend (no dependencies).

## Running Locally

```bash
# Required environment variables
export CONCIRCLE_OPENAI_BASE_URL="https://api.openai.com/v1"
export CONCIRCLE_OPENAI_API_KEY="your-key"
export CONCIRCLE_OPENAI_MODEL="gpt-4o-mini"
export ADMIN_SECRET_KEY="your-admin-key"

# Start the server
python3 -m server.server

# Access points
# User page:  http://localhost:3000
# Admin page: http://localhost:3000/admin.html?key=<ADMIN_SECRET_KEY>
```

## Docker

```bash
docker build -t expert-ai-app .
docker-compose up -d
```

## Architecture

**Backend** (`server/`): Python stdlib HTTP server (`ThreadingHTTPServer`), no external dependencies.
- `server.py` — HTTP request handler, routes all API endpoints, serves static files from `web/`
- `llm.py` — OpenAI API client using `urllib`. Supports both `/chat/completions` and `/responses` endpoints with automatic fallback
- `generate.py` — LLM content generation functions (expert summaries, AI insights, merging, comparison). All generation functions call `llm.complete()`
- `prompts.py` — Prompt templates. Default language is German, industry context is manufacturing/services
- `storage.py` — JSON file persistence with thread-safe locks. Data lives in `data/submissions.json` and `data/questions.json`
- `questions.py` — Default question definitions (fallback when no `questions.json` exists)
- `logutil.py` — Centralized logging setup

**Frontend** (`web/`): Vanilla HTML/CSS/JS, no build step.
- `index.html` + `app.js` — Expert submission form
- `admin.html` + `admin.js` — Admin dashboard for viewing submissions and triggering AI generation
- `styles.css` — Shared styles with CSS variable-based light/dark theme

**Data** (`data/`): JSON files, auto-created at runtime. Thread-safe via `threading.Lock()`.

## Key Patterns

- **Zero external dependencies**: Backend uses only Python stdlib (`urllib`, `json`, `threading`, `http.server`). Frontend is vanilla JS.
- **Thread safety**: File I/O protected by `_lock` and `_questions_lock` in `storage.py`. LLM calls use `ThreadPoolExecutor` for parallel execution.
- **LLM dual-endpoint support**: `llm.py` auto-detects whether to use chat completions or responses API based on model name, with fallback on failure.
- **Admin auth**: Query parameter `?key=ADMIN_SECRET_KEY` on all `/api/admin/*` endpoints.
- **i18n**: Frontend supports German (default) and English via translation maps in JS. Language/theme persisted in localStorage.
- **2000-char limit**: All generated insights are constrained to 2000 characters via `compress_to_limit()`.

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `CONCIRCLE_OPENAI_BASE_URL` | Yes | — | OpenAI API base URL |
| `CONCIRCLE_OPENAI_API_KEY` | Yes | — | API key |
| `CONCIRCLE_OPENAI_MODEL` | Yes | — | Model name |
| `CONCIRCLE_OPENAI_TIMEOUT` | No | `120` | Per-LLM-call timeout in seconds |
| `CONCIRCLE_REQUEST_TIMEOUT` | No | `150` | Total request timeout for LLM endpoints (should be < proxy timeout) |
| `CONCIRCLE_OPENAI_API_MODE` | No | `auto` | `auto`, `responses`, or `chat_completions` |
| `CONCIRCLE_SSL_VERIFY` | No | `1` | Set `0` to disable SSL verification |
| `ADMIN_SECRET_KEY` | No | `admin123` | Admin authentication key |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `3000` | Server port |

## API Endpoints

Public: `GET /api/questions`, `GET /api/submissions/count`, `POST /api/submit`

Admin (require `?key=`): `GET /api/admin/submissions`, `POST /api/admin/summarize`, `POST /api/admin/merge`, `POST /api/admin/compare`, `GET /api/admin/clear`, `GET|POST /api/admin/questions`, `POST /api/admin/questions/reset`
