from typing import Dict
import re
from analyzer.parsing.schema import JDContext

def hiring_process_absence_rule(jd_context: JDContext) -> Dict:
    """
    Detects absence of credible hiring process or suspiciously shortcut recruitment.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    # -------- Strong scam indicators (very high risk) --------
    strong_indicators = [
        "no interview",
        "without interview",
        "direct joining",
        "instant joining",
        "same day joining",
        "same day selection",
        "guaranteed selection",
        "offer letter immediately",
        "instant offer",
        "no selection process"
    ]

    for ind in strong_indicators:
        if ind in text:
            return {
                "score": 0.9,
                "reason": "Job claims hiring without any interview or formal selection process"
            }

    # -------- Weak or vague hiring process phrases --------
    vague_indicators = [
        "simple selection process",
        "easy hiring process",
        "very easy selection",
        "minimal interview",
        "quick selection",
        "fastest hiring"
    ]

    vague_hits = [t for t in vague_indicators if t in text]

    if len(vague_hits) >= 2:
        return {
            "score": 0.6,
            "reason": "Suspiciously simplified hiring process with vague explanations"
        }

    if len(vague_hits) == 1:
        return {
            "score": 0.4,
            "reason": "Job description suggests unusually easy or unclear hiring process"
        }

    # -------- Absence heuristic (fallback) --------
    # If JD has responsibilities & salary but no mention of interview / hr / selection flow
    has_role_info = bool(jd_context.responsibilities or jd_context.requirements)
    mentions_interview = any(
        k in text for k in [
            "interview", "hr round", "technical round", "assessment",
            "screening", "shortlist", "selection process"
        ]
    )

    if has_role_info and not mentions_interview:
        return {
            "score": 0.35,
            "reason": "Job post does not describe any interview or selection process"
        }

    return {"score": 0.0, "reason": None}