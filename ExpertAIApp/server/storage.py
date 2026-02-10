"""
Storage module for expert submissions and questions.
Stores data as JSON files on disk.
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from server.questions import DEFAULT_QUESTIONS

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"
QUESTIONS_FILE = DATA_DIR / "questions.json"

# Thread lock for file operations
_lock = threading.Lock()
_questions_lock = threading.Lock()


class Submission(TypedDict):
    id: str
    name: str
    responses: dict[str, str]
    timestamp: str


def _ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_submissions() -> list[Submission]:
    """Load submissions from file."""
    if not SUBMISSIONS_FILE.exists():
        return []
    try:
        with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("submissions", [])
    except (json.JSONDecodeError, IOError):
        return []


def _save_submissions(submissions: list[Submission]):
    """Save submissions to file."""
    _ensure_data_dir()
    with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"submissions": submissions}, f, ensure_ascii=False, indent=2)


def save_submission(name: str, responses: dict[str, str]) -> dict:
    """
    Save a user's submission.
    
    Args:
        name: The user's name
        responses: Dictionary of question_id -> response text
        
    Returns:
        dict with 'success' and 'message' or 'error'
    """
    with _lock:
        submissions = _load_submissions()
        
        # Check if this name already submitted
        for sub in submissions:
            if sub["name"].lower().strip() == name.lower().strip():
                return {
                    "success": False,
                    "error": "Duplicate submission",
                    "message": f"'{name}' hat bereits eine Antwort eingereicht."
                }
        
        # Create new submission
        submission: Submission = {
            "id": f"sub_{len(submissions) + 1}_{int(datetime.now().timestamp())}",
            "name": name.strip(),
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }
        
        submissions.append(submission)
        _save_submissions(submissions)
        
        return {
            "success": True,
            "message": "Antwort erfolgreich gespeichert.",
            "submission_count": len(submissions)
        }


def get_all_submissions() -> list[Submission]:
    """Get all stored submissions."""
    with _lock:
        return _load_submissions()


def get_submission_count() -> int:
    """Get the current number of submissions."""
    with _lock:
        return len(_load_submissions())


def clear_submissions():
    """Clear all submissions (for testing/reset)."""
    with _lock:
        _save_submissions([])


# ============ Questions Storage ============

def _load_questions_from_file() -> list[dict] | None:
    """Load questions from file, returns None if file doesn't exist."""
    if not QUESTIONS_FILE.exists():
        return None
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("questions", None)
    except (json.JSONDecodeError, IOError):
        return None


def _save_questions_to_file(questions: list[dict]):
    """Save questions to file."""
    _ensure_data_dir()
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump({"questions": questions}, f, ensure_ascii=False, indent=2)


def load_questions() -> list[dict]:
    """Load questions from file, fallback to defaults if not found."""
    with _questions_lock:
        questions = _load_questions_from_file()
        if questions is None:
            return DEFAULT_QUESTIONS
        return questions


def save_questions(questions: list[dict]) -> dict:
    """
    Save questions configuration.
    
    Args:
        questions: List of question dictionaries
        
    Returns:
        dict with 'success' and 'message'
    """
    with _questions_lock:
        # Validate questions structure
        if not isinstance(questions, list):
            return {
                "success": False,
                "error": "Invalid questions format",
                "message": "Fragen müssen als Liste übergeben werden."
            }
        
        # Ensure each question has required fields and generate IDs if missing
        validated = []
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                continue
            text = (q.get("text") or "").strip()
            if not text:
                continue
            validated.append({
                "id": q.get("id") or f"q{i + 1}",
                "type": q.get("type") or "text",
                "text": text
            })
        
        if not validated:
            return {
                "success": False,
                "error": "No valid questions",
                "message": "Mindestens eine gültige Frage ist erforderlich."
            }
        
        _save_questions_to_file(validated)
        return {
            "success": True,
            "message": f"{len(validated)} Fragen erfolgreich gespeichert.",
            "count": len(validated)
        }


def reset_questions() -> dict:
    """Reset questions to defaults."""
    with _questions_lock:
        _save_questions_to_file(DEFAULT_QUESTIONS)
        return {
            "success": True,
            "message": "Fragen auf Standardwerte zurückgesetzt.",
            "count": len(DEFAULT_QUESTIONS)
        }
