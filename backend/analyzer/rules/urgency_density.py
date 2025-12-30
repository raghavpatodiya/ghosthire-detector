from typing import Dict
from analyzer.parsing.schema import JDContext
import re


def urgency_density_rule(jd_context: JDContext) -> Dict:
    """
    Detects urgency pressure intensity in the JD.
    Uses structured JDContext first, falls back to raw text.
    Now safer, fewer false positives.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    # If parsing confidence is extremely weak, avoid over-flagging
    if getattr(jd_context, "confidence_score", 0) < 0.35:
        return {"score": 0.0, "reason": None}

    # Prefer structured title + raw text as fallback
    text_sources = [
        getattr(jd_context.job, "title", "") or "",
        jd_context.raw_text or "",
    ]
    text = " ".join(text_sources).lower()

    # =========================
    # Strong scam urgency phrases
    # =========================
    strong_phrases = [
        r"\bjoin immediately\b",
        r"\bimmediate join(?:ing)?\b",
        r"\bapply now\b",
        r"\bjoin now\b",
        r"\bno interview\b",
        r"\binstant selection\b",
        r"\bselected instantly\b",
        r"\bguaranteed selection\b",
        r"\blimited slots\b",
        r"\bact fast\b",
        r"\bapply asap\b",
    ]

    # =========================
    # Normal urgency (mild)
    # =========================
    mild_phrases = [
        r"\burgent\b",
        r"\burgently\b",
        r"\basap\b",
        r"\bimmediately\b",
        r"\bfast hiring\b",
        r"\bquick hiring\b",
    ]

    strong_hits = 0
    mild_hits = 0

    for p in strong_phrases:
        strong_hits += len(re.findall(p, text))

    for p in mild_phrases:
        mild_hits += len(re.findall(p, text))

    total_hits = strong_hits + mild_hits

    # =========================
    # Risk Ladder
    # =========================

    # Extremely strong urgency repeated
    if strong_hits >= 3 or total_hits >= 6:
        return {
            "score": 0.9,
            "reason": "Extreme urgency pressure with repeated guaranteed / instant joining signals",
        }

    # Strong urgency repeated multiple times
    if strong_hits >= 2 or total_hits >= 4:
        return {
            "score": 0.7,
            "reason": "Multiple aggressive urgency phrases detected",
        }

    # Noticeable urgency pressure
    if strong_hits == 1 and total_hits >= 3:
        return {
            "score": 0.6,
            "reason": "Urgency-driven hiring language repeated several times",
        }

    # Some urgency present but not extreme
    if total_hits == 2:
        return {
            "score": 0.45,
            "reason": "Repeated urgency tone found in job post",
        }

    if total_hits == 1:
        return {
            "score": 0.25,
            "reason": "Some urgency pressure detected in the job description",
        }

    return {"score": 0.0, "reason": None}