FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=3000
# Default timeout for OpenAI API calls (can be overridden)
ENV CONCIRCLE_OPENAI_TIMEOUT=180

COPY server/ ./server/
COPY web/ ./web/

# Create data directory for submissions storage with write permissions
RUN mkdir -p /app/data && chmod 777 /app/data

EXPOSE 3000

CMD ["python", "-m", "server.server"]


