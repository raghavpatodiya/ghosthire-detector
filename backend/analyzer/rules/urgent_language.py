import re
from typing import Dict
from analyzer.parsing.schema import JDContext


def urgent_language_rule(jd_context: JDContext) -> Dict:
    """
    Detects urgency / pressure-based hiring language.
    JDContext-first, safer thresholds, fewer false positives.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    # Avoid aggressive flagging when parsing confidence is weak
    if getattr(jd_context, "confidence_score", 0) < 0.35:
        return {"score": 0.0, "reason": None}

    text_sources = [
        jd_context.job.title or "",
        jd_context.raw_text or ""
    ]

    text = " ".join(text_sources)
    lower = text.lower()

    # =========================
    # Strong urgency / pressure
    # =========================
    strong_urgency_patterns = [
        r"\bjoin immediately\b",
        r"\bimmediate join(?:ing)?\b",
        r"\bapply now\b",
        r"\bjoin now\b",
        r"\bno interview\b",
        r"\binstant selection\b",
        r"\bselected instantly\b",
        r"\bguaranteed selection\b",
        r"\blimited slots\b",
        r"\bonly few positions\b",
        r"\bapply asap\b",
    ]

    # =========================
    # Mild urgency
    # =========================
    mild_urgency_patterns = [
        r"\burgent hiring\b",
        r"\burgent requirement\b",
        r"\burgently hiring\b",
        r"\burgent vacancy\b",
        r"\basap\b",
        r"\bimmediately\b",
        r"\bfast hiring\b",
        r"\bquick hiring\b",
    ]

    strong_hits = sum(len(re.findall(p, lower)) for p in strong_urgency_patterns)
    mild_hits = sum(len(re.findall(p, lower)) for p in mild_urgency_patterns)
    total_hits = strong_hits + mild_hits

    # =========================
    # Risk ladder
    # =========================
    if strong_hits >= 3 or total_hits >= 6:
        return {
            "score": 0.9,
            "reason": "Extreme urgency pressure and instant selection style language detected"
        }

    if strong_hits >= 2 or total_hits >= 4:
        return {
            "score": 0.75,
            "reason": "Multiple aggressive urgency signals indicating pressure-based hiring"
        }

    if strong_hits == 1 and total_hits >= 3:
        return {
            "score": 0.6,
            "reason": "Strong urgency tone repeated multiple times in job post"
        }

    if total_hits == 2:
        return {
            "score": 0.45,
            "reason": "Repeated urgency-based hiring language detected"
        }

    if total_hits == 1:
        return {
            "score": 0.25,
            "reason": "Urgency-driven hiring tone detected"
        }

    return {"score": 0.0, "reason": None}