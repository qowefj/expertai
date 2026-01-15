import json
import os
import posixpath
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from server.questions import QUESTIONS
from server.generate import (
    generate_ai_insight,
    generate_expert_insight,
    generate_multi_expert_summary,
    merge_final_insight,
)
from server.storage import (
    save_submission,
    get_all_submissions,
    get_submission_count,
    clear_submissions,
    MAX_SUBMISSIONS,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT_DIR / "web"

# Admin secret key from environment (default for development)
ADMIN_SECRET_KEY = os.environ.get("ADMIN_SECRET_KEY", "admin123")


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
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/questions":
            return _json_response(self, 200, {"questions": QUESTIONS})
        
        # API: Get submission count (public)
        if parsed.path == "/api/submissions/count":
            count = get_submission_count()
            return _json_response(self, 200, {
                "count": count,
                "max": MAX_SUBMISSIONS,
                "isFull": count >= MAX_SUBMISSIONS
            })
        
        # Admin API: Get all submissions
        if parsed.path == "/api/admin/submissions":
            if not _check_admin_key(parsed):
                return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
            
            submissions = get_all_submissions()
            return _json_response(self, 200, {
                "submissions": submissions,
                "count": len(submissions),
                "max": MAX_SUBMISSIONS
            })
        
        # Admin API: Clear all submissions
        if parsed.path == "/api/admin/clear":
            if not _check_admin_key(parsed):
                return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
            
            clear_submissions()
            return _json_response(self, 200, {"success": True, "message": "All submissions cleared"})

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

    def do_POST(self):
        parsed = urlparse(self.path)
        body = _read_json(self)
        if body is None:
            return _json_response(self, 400, {"error": "Invalid JSON body"})

        # User submission endpoint
        if parsed.path == "/api/submit":
            name = (body.get("name") or "").strip()
            text_responses = body.get("textResponses") or {}
            
            if not name:
                return _json_response(self, 400, {"error": "Name is required", "message": "Bitte geben Sie Ihren Namen ein."})
            
            # Validate responses
            per_question_errors: dict[str, str] = {}
            sanitized: dict[str, str] = {}
            
            for q in QUESTIONS:
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
            if result["success"]:
                return _json_response(self, 200, result)
            else:
                return _json_response(self, 400, result)

        # Admin: Summarize all submissions
        if parsed.path == "/api/admin/summarize":
            if not _check_admin_key(parsed):
                return _json_response(self, 401, {"error": "Unauthorized", "message": "Invalid admin key"})
            
            submissions = get_all_submissions()
            if not submissions:
                return _json_response(self, 400, {"error": "No submissions", "message": "Es gibt noch keine Einreichungen zum Zusammenfassen."})
            
            try:
                # Run both LLM calls in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_expert = executor.submit(generate_multi_expert_summary, QUESTIONS, submissions)
                    future_ai = executor.submit(generate_ai_insight, QUESTIONS)
                    
                    expert = future_expert.result()
                    ai = future_ai.result()
                
                return _json_response(self, 200, {"expertInsight": expert, "aiInsight": ai})
            except Exception as e:
                return _json_response(self, 500, {"error": "LLM generation failed", "message": str(e)})

        if parsed.path == "/api/insights/generate":
            text_responses = body.get("textResponses") or {}
            per_question_errors: dict[str, str] = {}
            sanitized: dict[str, str] = {}

            for q in QUESTIONS:
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

            try:
                # Run both LLM calls in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_expert = executor.submit(generate_expert_insight, QUESTIONS, sanitized)
                    future_ai = executor.submit(generate_ai_insight, QUESTIONS)
                    
                    expert = future_expert.result()
                    ai = future_ai.result()
                
                return _json_response(self, 200, {"expertInsight": expert, "aiInsight": ai})
            except Exception as e:
                return _json_response(self, 500, {"error": "LLM generation failed", "message": str(e)})

        if parsed.path == "/api/insights/merge":
            expert = (body.get("expertInsight") or "").strip()
            ai = (body.get("aiInsight") or "").strip()

            if not expert or not ai:
                return _json_response(
                    self, 400, {"error": "expertInsight and aiInsight are required"}
                )

            try:
                final = merge_final_insight(expert, ai)
                return _json_response(self, 200, {"finalInsight": final})
            except Exception as e:
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
                final = merge_final_insight(expert, ai)
                return _json_response(self, 200, {"finalInsight": final})
            except Exception as e:
                return _json_response(self, 500, {"error": "LLM merge failed", "message": str(e)})

        return _json_response(self, 404, {"error": "Not Found"})

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
