MAX_INSIGHT_CHARS = 2000

SYSTEM_BASE = "Du bist ein präziser Experten-Assistent. Befolge die Anweisungen genau."

def expert_insight_prompt(responses_text: str) -> str:
    return "\n".join(
        [
            "Aufgabe: Erstelle eine Experten-Zusammenfassung durch Zusammenführen und Zusammenfassen der untenstehenden Expertenantworten.",
            "",
            "Regeln:",
            "- Fasse die Antworten der Experten zusammen und hebe die wichtigsten Punkte hervor.",
            "- Du darfst für Klarheit umformulieren und Duplikate zusammenfassen.",
            f"- Die Ausgabe muss <= {MAX_INSIGHT_CHARS} Zeichen sein.",
            "- Antworte auf Deutsch.",
            "",
            "Expertenantworten:",
            responses_text.strip(),
        ]
    ).strip()


def ai_insight_prompt(questions_text: str) -> str:
    return "\n".join(
        [
            "Aufgabe: Beantworte die folgenden Fragen als Experte. Die Ausgabe sollte eine einzige kombinierte Einsicht für alle Fragen sein.",
            "",
            "Regeln:",
            "- Nutze dein Fachwissen, um Geschäftswert, Herausforderungen, Trends und umsetzbare Ideen vorzuschlagen.",
            "- Beziehe dich NICHT auf Expertenantworten (es werden keine bereitgestellt).",
            f"- Die Ausgabe muss <= {MAX_INSIGHT_CHARS} Zeichen sein.",
            "- Antworte auf Deutsch.",
            "",
            "Fragen:",
            questions_text.strip(),
        ]
    ).strip()


def merge_final_prompt(expert_insight: str, ai_insight: str) -> str:
    return "\n".join(
        [
            "Aufgabe: Erstelle eine finale Einsicht durch Zusammenführen und Verfeinern der KI-Einsicht mit der Experten-Einsicht.",
            "",
            "Regeln:",
            "- Halte es diskussionsbereit und prägnant.",
            "- Bevorzuge bei Spannungen die Ausrichtung an der Experten-Einsicht.",
            f"- Die Ausgabe muss <= {MAX_INSIGHT_CHARS} Zeichen sein.",
            "- Antworte auf Deutsch.",
            "",
            "Experten-Einsicht:",
            expert_insight.strip(),
            "",
            "KI-Einsicht:",
            ai_insight.strip(),
        ]
    ).strip()


def multi_expert_summary_prompt(all_responses_text: str, expert_count: int) -> str:
    return "\n".join(
        [
            f"Aufgabe: Erstelle eine umfassende Zusammenfassung der Antworten von {expert_count} Experten.",
            "",
            "Regeln:",
            "- Fasse die Antworten aller Experten zusammen und identifiziere gemeinsame Themen.",
            "- Hebe sowohl Übereinstimmungen als auch unterschiedliche Perspektiven hervor.",
            "- Identifiziere die wichtigsten Trends und Herausforderungen, die von mehreren Experten genannt wurden.",
            "- Du darfst für Klarheit umformulieren und Duplikate zusammenfassen.",
            f"- Die Ausgabe muss <= {MAX_INSIGHT_CHARS} Zeichen sein.",
            "- Antworte auf Deutsch.",
            "",
            "Expertenantworten:",
            all_responses_text.strip(),
        ]
    ).strip()


def comparison_insight_prompt(expert_insight: str, ai_insight: str) -> str:
    return "\n".join(
        [
            "Aufgabe: Vergleiche die Experten-Einsicht mit der KI-Einsicht und hebe die wichtigsten Unterschiede hervor.",
            "",
            "Regeln:",
            "- Identifiziere und erkläre die Hauptunterschiede zwischen beiden Einsichten.",
            "- Hebe hervor, wo die Experten andere Schwerpunkte setzen als die KI.",
            "- Erwähne Punkte, die nur in einer der beiden Einsichten vorkommen.",
            "- Strukturiere die Analyse klar (z.B. Übereinstimmungen, Unterschiede, Nur-Experten, Nur-KI).",
            f"- Die Ausgabe muss <= {MAX_INSIGHT_CHARS} Zeichen sein.",
            "- Antworte auf Deutsch.",
            "",
            "Experten-Einsicht:",
            expert_insight.strip(),
            "",
            "KI-Einsicht:",
            ai_insight.strip(),
        ]
    ).strip()
