from __future__ import annotations

from server.llm import complete
from server.prompts import (
    MAX_INSIGHT_CHARS,
    ai_insight_prompt,
    compress_prompt,
    expert_insight_prompt,
    merge_final_prompt,
    multi_expert_summary_prompt,
)


def _hard_trim(text: str) -> str:
    """Hard trim text to MAX_INSIGHT_CHARS, breaking at word boundary if possible."""
    t = (text or "").strip()
    if len(t) <= MAX_INSIGHT_CHARS:
        return t
    sliced = t[:MAX_INSIGHT_CHARS]
    last_space = sliced.rfind(" ")
    # Try to break at word boundary if we're at least 80% through
    min_length = int(MAX_INSIGHT_CHARS * 0.8)
    if last_space > min_length:
        return sliced[:last_space].strip()
    return sliced.strip()


def compress_to_limit(text: str) -> str:
    """Compress text to MAX_INSIGHT_CHARS limit."""
    t = (text or "").strip()
    if len(t) <= MAX_INSIGHT_CHARS:
        return t
    shortened = complete(compress_prompt(t))
    return _hard_trim(shortened)


def format_text_responses_for_prompt(questions: list[dict], text_responses: dict[str, str]) -> str:
    """Format free-text expert responses for the prompt."""
    parts: list[str] = []
    for q in questions:
        qid = q["id"]
        response = text_responses.get(qid, "").strip()

        parts.append(f"Frage: {q['text']}")
        parts.append("Expertenantwort:")
        if not response:
            parts.append("- (keine Antwort)")
        else:
            parts.append(response)
        parts.append("")
    return "\n".join(parts).strip()


def generate_expert_insight(questions: list[dict], text_responses: dict[str, str]) -> str:
    """Generate expert insight from free-text responses."""
    responses_text = format_text_responses_for_prompt(questions, text_responses)
    raw = complete(expert_insight_prompt(responses_text))
    return compress_to_limit(raw)


def generate_ai_insight(questions: list[dict]) -> str:
    """Generate AI insight from questions only (no expert context)."""
    questions_text = "\n".join([f"{i+1}) {q['text']}" for i, q in enumerate(questions)])
    raw = complete(ai_insight_prompt(questions_text))
    return compress_to_limit(raw)


def merge_final_insight(expert_insight: str, ai_insight: str) -> str:
    """Merge expert and AI insights into a final combined insight."""
    raw = complete(merge_final_prompt(expert_insight, ai_insight))
    return compress_to_limit(raw)


def format_all_submissions_for_prompt(questions: list[dict], submissions: list[dict]) -> str:
    """Format all expert submissions for the multi-expert summary prompt."""
    parts: list[str] = []
    
    for i, sub in enumerate(submissions, 1):
        parts.append(f"=== Experte {i}: {sub.get('name', 'Anonym')} ===")
        responses = sub.get("responses", {})
        
        for q in questions:
            qid = q["id"]
            response = responses.get(qid, "").strip()
            parts.append(f"Frage: {q['text']}")
            parts.append(f"Antwort: {response if response else '(keine Antwort)'}")
            parts.append("")
        
        parts.append("")
    
    return "\n".join(parts).strip()


def generate_multi_expert_summary(questions: list[dict], submissions: list[dict]) -> str:
    """Generate a summary from multiple expert submissions."""
    all_responses_text = format_all_submissions_for_prompt(questions, submissions)
    raw = complete(multi_expert_summary_prompt(all_responses_text, len(submissions)))
    return compress_to_limit(raw)
