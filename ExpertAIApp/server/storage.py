"""
Storage module for expert submissions.
Stores submissions as JSON file on disk.
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import TypedDict

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SUBMISSIONS_FILE = DATA_DIR / "submissions.json"

MAX_SUBMISSIONS = 25

# Thread lock for file operations
_lock = threading.Lock()


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
        
        # Check if we've reached the limit
        if len(submissions) >= MAX_SUBMISSIONS:
            return {
                "success": False,
                "error": "Maximum number of submissions reached",
                "message": f"Es wurden bereits {MAX_SUBMISSIONS} Antworten eingereicht."
            }
        
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
