import json
import os
import re
import ssl
import time
import urllib.request
from urllib.parse import urlparse, urlunparse

from server.logutil import get_logger
from server.prompts import SYSTEM_BASE

logger = get_logger(__name__)


def _get_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing env var: {name}")
    return v


def _normalize_v1_base(base_url: str) -> str:
    raw = (base_url or "").strip()
    if not raw:
        raise RuntimeError("CONCIRCLE_OPENAI_BASE_URL is empty")

    # Accept full endpoints too
    if re.search(r"/v1/(chat/completions|responses)/?$", raw):
        raw = re.sub(r"/(chat/completions|responses)/?$", "", raw)

    u = urlparse(raw)
    path = (u.path or "").rstrip("/")
    if "/v1/models" in path:
        path = re.sub(r"/v1/models(/.*)?$", "/v1", path)
    elif "/v1" in path:
        path = re.sub(r"/v1(/.*)?$", "/v1", path)
    else:
        path = (path + "/v1").replace("//v1", "/v1")

    u2 = u._replace(path=path, params="", query="", fragment="")
    return urlunparse(u2).rstrip("/")


def _post_json(url: str, api_key: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    verify = (os.environ.get("CONCIRCLE_SSL_VERIFY") or "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    
    # Get timeout from env or use 120 seconds (increased from 60)
    timeout = int(os.environ.get("CONCIRCLE_OPENAI_TIMEOUT", "120"))
    
    ctx = ssl.create_default_context() if verify else ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    
    logger.info(f"Starting LLM request to {url} (timeout: {timeout}s, model: {payload.get('model', 'unknown')})")
    start_time = time.time()
    
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            elapsed = time.time() - start_time
            text = resp.read().decode("utf-8")
            logger.info(f"LLM request completed in {elapsed:.2f}s")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        text = e.read().decode("utf-8", errors="replace")
        logger.error(f"LLM request failed after {elapsed:.2f}s ({e.code}): {text or e.reason}")
        raise RuntimeError(f"LLM request failed ({e.code}): {text or e.reason}") from e
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"LLM request error after {elapsed:.2f}s: {type(e).__name__}: {e}")
        raise


def _should_prefer_responses(model: str) -> bool:
    return model.lower().startswith("gpt-5")


def _parse_responses_text(data: dict) -> str:
    if isinstance(data.get("output_text"), str) and data["output_text"].strip():
        return data["output_text"].strip()

    # fallback: output[0].content[].text
    out = data.get("output") or []
    if out and isinstance(out, list):
        first = out[0] if out else {}
        content = first.get("content") or []
        if isinstance(content, list):
            text = "".join((c.get("text") or "") for c in content if isinstance(c, dict))
            if text.strip():
                return text.strip()

    err = data.get("error") or {}
    if isinstance(err, dict) and err.get("message"):
        raise RuntimeError(str(err["message"]))
    raise RuntimeError("LLM response missing content")


def _parse_chat_text(data: dict) -> str:
    choices = data.get("choices") or []
    if choices and isinstance(choices, list):
        msg = (choices[0] or {}).get("message") or {}
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    err = data.get("error") or {}
    if isinstance(err, dict) and err.get("message"):
        raise RuntimeError(str(err["message"]))
    raise RuntimeError("LLM response missing content")


def complete(user: str, system: str | None = None) -> str:
    base_url = _get_env("CONCIRCLE_OPENAI_BASE_URL")
    api_key = _get_env("CONCIRCLE_OPENAI_API_KEY")
    model = _get_env("CONCIRCLE_OPENAI_MODEL")
    mode = (os.environ.get("CONCIRCLE_OPENAI_API_MODE") or "auto").strip().lower()

    v1 = _normalize_v1_base(base_url)
    sys_text = system or SYSTEM_BASE

    def try_chat() -> str:
        url = f"{v1}/chat/completions"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_text},
                {"role": "user", "content": user},
            ],
        }
        data = _post_json(url, api_key, payload)
        return _parse_chat_text(data)

    def try_responses() -> str:
        url = f"{v1}/responses"
        payload = {
            "model": model,
            "instructions": sys_text,
            "input": user,
        }
        data = _post_json(url, api_key, payload)
        return _parse_responses_text(data)

    prefer_responses = mode == "responses" or (mode == "auto" and _should_prefer_responses(model))
    if mode == "chat_completions":
        return try_chat()

    if prefer_responses:
        try:
            return try_responses()
        except Exception as e1:
            try:
                return try_chat()
            except Exception as e2:
                raise RuntimeError(f"{e1}\nFallback attempt failed: {e2}") from e2
    else:
        try:
            return try_chat()
        except Exception as e1:
            try:
                return try_responses()
            except Exception as e2:
                raise RuntimeError(f"{e1}\nFallback attempt failed: {e2}") from e2


