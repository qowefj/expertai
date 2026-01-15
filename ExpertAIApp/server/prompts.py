MAX_INSIGHT_CHARS = 2000

SYSTEM_BASE = "Du bist ein präziser Experten-Assistent. Befolge die Anweisungen genau."

INDUSTRY_CONTEXT = (
    "Industrieunternehmen versuchen zunehmend, neben dem klassischen Produktverkauf "
    "von Maschinen, Anlagen oder Komponenten bzw. dem Ersatzteilgeschäft durch "
    "verrechenbare Services neue, margenstarke Umsatzströme zu generieren. "
    "Diese Services beruhen zu einem großen Teil auf digitalen Plattformen, "
    "digitaler Infrastruktur und IoT."
)


def expert_insight_prompt(responses_text: str) -> str:
    return "\n".join(
        [
            "Aufgabe: Erstelle eine Experten-Zusammenfassung durch Zusammenführen und Zusammenfassen der untenstehenden Expertenantworten.",
            "",
            "Kontext:",
            INDUSTRY_CONTEXT,
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
            "Kontext:",
            INDUSTRY_CONTEXT,
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
            "Kontext:",
            INDUSTRY_CONTEXT,
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


def compress_prompt(text: str) -> str:
    return "\n".join(
        [
            f"Aufgabe: Kürze den untenstehenden Text auf <= {MAX_INSIGHT_CHARS} Zeichen, während die Kernpunkte erhalten bleiben.",
            "Regeln:",
            "- Bewahre die Bedeutung.",
            "- Entferne zuerst Redundanzen.",
            "- Gib NUR den gekürzten Text aus.",
            "- Antworte auf Deutsch.",
            "",
            "Text:",
            text.strip(),
        ]
    ).strip()


def multi_expert_summary_prompt(all_responses_text: str, expert_count: int) -> str:
    return "\n".join(
        [
            f"Aufgabe: Erstelle eine umfassende Zusammenfassung der Antworten von {expert_count} Experten.",
            "",
            "Kontext:",
            INDUSTRY_CONTEXT,
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
