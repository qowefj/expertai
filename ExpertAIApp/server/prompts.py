MAX_INSIGHT_CHARS = 2000

SYSTEM_BASE = "You are a precise expert assistant. Follow the instructions exactly."

def expert_insight_prompt(responses_text: str) -> str:
    return "\n".join(
        [
            "Task: Create an expert summary by merging and summarizing the expert responses below.",
            "",
            "Rules:",
            "- Summarize the expert responses and highlight the most important points.",
            "- You may rephrase for clarity and consolidate duplicates.",
            f"- The output must be <= {MAX_INSIGHT_CHARS} characters.",
            "- Answer in English.",
            "",
            "Expert responses:",
            responses_text.strip(),
        ]
    ).strip()


def ai_insight_prompt(questions_text: str) -> str:
    return "\n".join(
        [
            "Task: Answer the following questions as an expert. The output should be a single combined insight for all questions.",
            "",
            "Rules:",
            "- Answer the questions with professional expertise and precision.",
            "- Do NOT reference expert responses (none are provided).",
            f"- The output must be <= {MAX_INSIGHT_CHARS} characters.",
            "- Answer in English.",
            "",
            "Questions:",
            questions_text.strip(),
        ]
    ).strip()


def merge_final_prompt(expert_insight: str, ai_insight: str) -> str:
    return "\n".join(
        [
            "Task: Create a final insight by merging and refining the AI insight with the expert insight.",
            "",
            "Rules:",
            "- Keep it discussion-ready and concise.",
            "- When there is tension, prefer alignment with the expert insight.",
            f"- The output must be <= {MAX_INSIGHT_CHARS} characters.",
            "- Answer in English.",
            "",
            "Expert insight:",
            expert_insight.strip(),
            "",
            "AI insight:",
            ai_insight.strip(),
        ]
    ).strip()


def multi_expert_summary_prompt(all_responses_text: str, expert_count: int) -> str:
    return "\n".join(
        [
            f"Task: Create a comprehensive summary of the responses from {expert_count} experts.",
            "",
            "Rules:",
            "- Summarize the responses of all experts and identify common themes.",
            "- Highlight both agreements and differing perspectives.",
            "- Identify the most important trends and challenges mentioned by multiple experts.",
            "- You may rephrase for clarity and consolidate duplicates.",
            f"- The output must be <= {MAX_INSIGHT_CHARS} characters.",
            "- Answer in English.",
            "",
            "Expert responses:",
            all_responses_text.strip(),
        ]
    ).strip()


def comparison_insight_prompt(expert_insight: str, ai_insight: str) -> str:
    return "\n".join(
        [
            "Task: Compare the expert insight with the AI insight and highlight the key differences.",
            "",
            "Rules:",
            "- Identify and explain the main differences between both insights.",
            "- Highlight where experts place different emphasis than the AI.",
            "- Mention points that appear in only one of the two insights.",
            "- Structure the analysis clearly (e.g. agreements, differences, expert-only, AI-only).",
            f"- The output must be <= {MAX_INSIGHT_CHARS} characters.",
            "- Answer in English.",
            "",
            "Expert insight:",
            expert_insight.strip(),
            "",
            "AI insight:",
            ai_insight.strip(),
        ]
    ).strip()
