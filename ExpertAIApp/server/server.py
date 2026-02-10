import json
import os
import posixpath
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from server.generate import (
    generate_ai_insight,
    generate_comparison_insight,
    generate_expert_insight,
    generate_multi_expert_summary,
    merge_final_insight,
)
from server.logutil import get_logger
from server.storage import (
    clear_submissions,
    get_all_submissions,
    get_submission_count,
    load_questions,
    reset_questions,
    save_questions,
    save_submission,
)

logger = get_logger(__name__)


ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"

# Admin secret key from environment (default for development)
ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "admin123")

# Total timeout for LLM request handling (should be less than any reverse proxy timeout)
REQUEST_TIMEOUT = int(os.environ.get("CONCIRCLE_REQUEST_TIMEOUT", "150"))


def _json_response(handler: BaseHTTPRequestHandler, status: int, obj: dict):
    payload = json.dumps(obj).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


def _read_json(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length) if length else b"{}"
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def _safe_static_path(url_path: str) -> Path | None:
    # Map / -> index.html
    if url_path == "/" or url_path == "":
        url_path = "/index.html"

    # Normalize and prevent path traversal
    norm = posixpath.normpath(url_path)
    if norm.startswith("../") or "/../" in norm or norm == "..":
        return None
    if norm.startswith("/"):
        norm = norm[1:]

    candidate = (WEB_DIR / norm).resolve()
    try:
        candidate.relative_to(WEB_DIR.resolve())
    except Exception:
        return None
    return candidate


def _content_type(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".html"):
        return "text/html; charset=utf-8"
    if name.endswith(".css"):
        return "text/css; charset=utf-8"
    if name.endswith(".js"):
        return "application/javascript; charset=utf-8"
    if name.endswith(".json"):
        return "application/json; charset=utf-8"
    if name.endswith(".png"):
        return "image/png"
    if name.endswith(".jpg") or name.endswith(".jpeg"):
        return "image/jpeg"
    if name.endswith(".svg"):
        return "image/svg+xml"
    if name.endswith(".ico"):
        return "image/x-icon"
    return "application/octet-stream"


def _check_admin_key(parsed) -> bool:
    """Check if the admin key in query string is valid."""
    query_params = parse_qs(parsed.query)
    key = query_params.get("key", [""])[0]
    return key == ADMIN_SECRET_KEY


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
        
            if parsed.path == "/api/questions":
                questions = load_questions()
                return _json_response(self, 200, {"questions": questions})
        
            # API: Get submission count (public)
            if parsed.path == "/api/submissions/count":
                count = get_submission_count()
                return _json_response(self, 200, {"count": count})
        
            # Admin API: Get all submissions
            if parsed.path == "/api/admin/submissions":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
                
                submissions = get_all_submissions()
                return _json_response(self, 200, {
                    "submissions": submissions,
                    "count": len(submissions)
                })
        
            # Admin API: Clear all submissions
            if parsed.path == "/api/admin/clear":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
                
                clear_submissions()
                return _json_response(self, 200, {"success": True, "message": "All submissions cleared"})

            # Admin API: Get questions configuration
            if parsed.path == "/api/admin/questions":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
                
                questions = load_questions()
                return _json_response(self, 200, {"questions": questions})

            # serve static files
            file_path = _safe_static_path(parsed.path)
            if file_path is None or not file_path.exists() or not file_path.is_file():
                self.send_error(404, "Not Found")
                return

            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", _content_type(file_path))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            # Avoid empty responses if something goes wrong
            try:
                return _json_response(self, 500, {"error": "Server error", "message": str(e)})
            except Exception:
                return

    def do_POST(self):
        try:
            parsed = urlparse(self.path)
            body = _read_json(self)
            if body is None:
                return _json_response(self, 400, {"error": "Invalid JSON body"})

            # User submission endpoint
            if parsed.path == "/api/submit":
                name = (body.get("name") or "").strip()
                text_responses = body.get("textResponses") or {}
                if not isinstance(text_responses, dict):
                    text_responses = {}
            
                if not name:
                    return _json_response(self, 400, {"error": "Name is required", "message": "Bitte geben Sie Ihren Namen ein."})
            
                # Validate responses
                questions = load_questions()
                per_question_errors: dict[str, str] = {}
                sanitized: dict[str, str] = {}
            
                for q in questions:
                    qid = q["id"]
                    response = text_responses.get(qid, "")
                    if not isinstance(response, str):
                        response = ""
                    response = response.strip()
                    sanitized[qid] = response
                
                    if not response:
                        per_question_errors[qid] = "Bitte geben Sie eine Antwort ein."
            
                if per_question_errors:
                    return _json_response(
                        self, 400, {"error": "Validation failed", "perQuestionErrors": per_question_errors}
                    )
            
                # Save submission
                result = save_submission(name, sanitized)
                if bool(result.get("success")):
                    return _json_response(self, 200, result)
                return _json_response(self, 400, result)

            # Admin: Summarize all submissions
            if parsed.path == "/api/admin/summarize":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})

                submissions = get_all_submissions()
                if not submissions:
                    return _json_response(self, 400, {"error": "No submissions", "message": "Es gibt noch keine Einreichungen zum Zusammenfassen."})

                start_time = time.time()
                try:
                    logger.info("Starting summarize request with %d submissions (timeout %ds)", len(submissions), REQUEST_TIMEOUT)

                    questions = load_questions()
                    # Run both LLM calls in parallel
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        future_expert = executor.submit(generate_multi_expert_summary, questions, submissions)
                        future_ai = executor.submit(generate_ai_insight, questions)

                        expert = future_expert.result(timeout=REQUEST_TIMEOUT)
                        ai = future_ai.result(timeout=REQUEST_TIMEOUT)

                    elapsed = time.time() - start_time
                    logger.info("Summarize completed in %.2fs", elapsed)
                    return _json_response(self, 200, {"expertInsight": expert, "aiInsight": ai})
                except FuturesTimeoutError:
                    elapsed = time.time() - start_time
                    logger.error("Summarize timed out after %.2fs (limit %ds)", elapsed, REQUEST_TIMEOUT)
                    return _json_response(self, 504, {"error": "Request timeout", "message": f"LLM generation timed out after {int(elapsed)}s. Try again or increase CONCIRCLE_REQUEST_TIMEOUT."})
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error("Summarize failed after %.2fs: %s: %s", elapsed, type(e).__name__, e)
                    return _json_response(self, 500, {"error": "LLM generation failed", "message": str(e)})

            if parsed.path == "/api/insights/generate":
                text_responses = body.get("textResponses") or {}
                if not isinstance(text_responses, dict):
                    text_responses = {}
                questions = load_questions()
                per_question_errors: dict[str, str] = {}
                sanitized: dict[str, str] = {}

                for q in questions:
                    qid = q["id"]
                    response = text_responses.get(qid, "")
                    if not isinstance(response, str):
                        response = ""
                    response = response.strip()
                    sanitized[qid] = response

                    if not response:
                        per_question_errors[qid] = "Bitte geben Sie eine Antwort ein."

                if per_question_errors:
                    return _json_response(
                        self, 400, {"error": "Validation failed", "perQuestionErrors": per_question_errors}
                    )

                start_time = time.time()
                try:
                    logger.info("Starting insights/generate request (timeout %ds)", REQUEST_TIMEOUT)

                    # Run both LLM calls in parallel
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        future_expert = executor.submit(generate_expert_insight, questions, sanitized)
                        future_ai = executor.submit(generate_ai_insight, questions)

                        expert = future_expert.result(timeout=REQUEST_TIMEOUT)
                        ai = future_ai.result(timeout=REQUEST_TIMEOUT)

                    elapsed = time.time() - start_time
                    logger.info("insights/generate completed in %.2fs", elapsed)
                    return _json_response(self, 200, {"expertInsight": expert, "aiInsight": ai})
                except FuturesTimeoutError:
                    elapsed = time.time() - start_time
                    logger.error("insights/generate timed out after %.2fs (limit %ds)", elapsed, REQUEST_TIMEOUT)
                    return _json_response(self, 504, {"error": "Request timeout", "message": f"LLM generation timed out after {int(elapsed)}s. Try again or increase CONCIRCLE_REQUEST_TIMEOUT."})
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error("insights/generate failed after %.2fs: %s: %s", elapsed, type(e).__name__, e)
                    return _json_response(self, 500, {"error": "LLM generation failed", "message": str(e)})

            if parsed.path == "/api/insights/merge":
                expert = (body.get("expertInsight") or "").strip()
                ai = (body.get("aiInsight") or "").strip()

                if not expert or not ai:
                    return _json_response(
                        self, 400, {"error": "expertInsight and aiInsight are required"}
                    )

                try:
                    logger.info("Starting insights/merge request")
                    start_time = time.time()
                    final = merge_final_insight(expert, ai)
                    elapsed = time.time() - start_time
                    logger.info("insights/merge completed in %.2fs", elapsed)
                    return _json_response(self, 200, {"finalInsight": final})
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error("insights/merge failed after %.2fs: %s: %s", elapsed, type(e).__name__, e)
                    return _json_response(self, 500, {"error": "LLM merge failed", "message": str(e)})

            # Admin: Merge insights
            if parsed.path == "/api/admin/merge":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})

                expert = (body.get("expertInsight") or "").strip()
                ai = (body.get("aiInsight") or "").strip()

                if not expert or not ai:
                    return _json_response(
                        self, 400, {"error": "expertInsight and aiInsight are required"}
                    )

                try:
                    logger.info("Starting admin/merge request")
                    start_time = time.time()
                    final = merge_final_insight(expert, ai)
                    elapsed = time.time() - start_time
                    logger.info("admin/merge completed in %.2fs", elapsed)
                    return _json_response(self, 200, {"finalInsight": final})
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error("admin/merge failed after %.2fs: %s: %s", elapsed, type(e).__name__, e)
                    return _json_response(self, 500, {"error": "LLM merge failed", "message": str(e)})

            # Admin: Compare insights (highlight differences)
            if parsed.path == "/api/admin/compare":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
            
                expert = (body.get("expertInsight") or "").strip()
                ai = (body.get("aiInsight") or "").strip()

                if not expert or not ai:
                    return _json_response(
                        self, 400, {"error": "expertInsight and aiInsight are required"}
                    )

                try:
                    logger.info("Starting comparison request")
                    start_time = time.time()
                    
                    comparison = generate_comparison_insight(expert, ai)
                    
                    elapsed = time.time() - start_time
                    logger.info(f"Comparison completed in {elapsed:.2f}s")
                    return _json_response(self, 200, {"comparisonInsight": comparison})
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error(f"Comparison failed after {elapsed:.2f}s: {type(e).__name__}: {e}")
                    return _json_response(self, 500, {"error": "LLM comparison failed", "message": str(e)})

            # Admin: Save questions configuration
            if parsed.path == "/api/admin/questions":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
            
                questions = body.get("questions")
                if questions is None:
                    return _json_response(self, 400, {"error": "questions field is required"})
                
                result = save_questions(questions)
                if bool(result.get("success")):
                    return _json_response(self, 200, result)
                return _json_response(self, 400, result)

            # Admin: Reset questions to defaults
            if parsed.path == "/api/admin/questions/reset":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})

                result = reset_questions()
                return _json_response(self, 200, result)

            # Admin: Demo summarize (no storage access)
            if parsed.path == "/api/admin/demo/summarize":
                if not _check_admin_key(parsed):
                    return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})

                questions = body.get("questions")
                submissions = body.get("submissions")
                if not questions or not submissions:
                    return _json_response(self, 400, {"error": "questions and submissions are required"})

                start_time = time.time()
                try:
                    logger.info("Starting demo/summarize with %d submissions (timeout %ds)", len(submissions), REQUEST_TIMEOUT)

                    with ThreadPoolExecutor(max_workers=2) as executor:
                        future_expert = executor.submit(generate_multi_expert_summary, questions, submissions)
                        future_ai = executor.submit(generate_ai_insight, questions)

                        expert = future_expert.result(timeout=REQUEST_TIMEOUT)
                        ai = future_ai.result(timeout=REQUEST_TIMEOUT)

                    elapsed = time.time() - start_time
                    logger.info("Demo summarize completed in %.2fs", elapsed)
                    return _json_response(self, 200, {"expertInsight": expert, "aiInsight": ai})
                except FuturesTimeoutError:
                    elapsed = time.time() - start_time
                    logger.error("Demo summarize timed out after %.2fs (limit %ds)", elapsed, REQUEST_TIMEOUT)
                    return _json_response(self, 504, {"error": "Request timeout", "message": f"LLM generation timed out after {int(elapsed)}s. Try again or increase CONCIRCLE_REQUEST_TIMEOUT."})
                except Exception as e:
                    elapsed = time.time() - start_time
                    logger.error("Demo summarize failed after %.2fs: %s: %s", elapsed, type(e).__name__, e)
                    return _json_response(self, 500, {"error": "LLM generation failed", "message": str(e)})

            return _json_response(self, 404, {"error": "Not Found"})
        except Exception as e:
            # Ensure fetch() always gets a response body (no ERR_EMPTY_RESPONSE)
            try:
                return _json_response(self, 500, {"error": "Server error", "message": str(e)})
            except Exception:
                return

    def log_message(self, fmt, *args):
        # cleaner logs
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), fmt % args))


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "3000"))

    if not WEB_DIR.exists():
        raise RuntimeError(f"Missing web directory at {WEB_DIR}")

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Listening on http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
