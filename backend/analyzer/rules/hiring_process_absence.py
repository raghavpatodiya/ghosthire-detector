from typing import Dict
from analyzer.parsing.schema import JDContext


def hiring_process_absence_rule(jd_context: JDContext) -> Dict:
    """
    Detects absence of credible hiring process or suspiciously shortcut recruitment.
    Aligned to structured JDContext pipeline with graceful fallback to raw text.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    raw = (jd_context.raw_text or "").lower()

    # Prefer structured parsed signals if parser already extracted them
    # (we coded HiringProcessDetector earlier – this integrates with it safely)
    parsed_steps = None
    if hasattr(jd_context, "hiring_steps"):
        parsed_steps = (jd_context.hiring_steps or [])

    # ----------------------------
    # 1️⃣ Strong scam indicators
    # ----------------------------
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
        "no selection process",
        "no hr round",
        "no screening"
    ]

    for ind in strong_indicators:
        if ind in raw:
            return {
                "score": 0.9,
                "reason": "Job claims hiring/selection without any interview or formal evaluation"
            }

    # ----------------------------
    # 2️⃣ Vague shortcut language
    # ----------------------------
    vague_indicators = [
        "simple selection process",
        "easy hiring process",
        "very easy selection",
        "minimal interview",
        "quick selection",
        "fastest hiring",
        "hassle free hiring",
        "smooth selection"
    ]

    vague_hits = [v for v in vague_indicators if v in raw]

    if len(vague_hits) >= 2:
        return {
            "score": 0.6,
            "reason": "Hiring process described vaguely with unusually simplified claims"
        }

    if len(vague_hits) == 1:
        return {
            "score": 0.4,
            "reason": "Job suggests unusually easy hiring process without clarity"
        }

    # ----------------------------
    # 3️⃣ Structured absence heuristic
    # ----------------------------
    # If parser already found explicit hiring steps → then safe
    if parsed_steps and len(parsed_steps) >= 1:
        return {"score": 0.0, "reason": None}

    # ----------------------------
    # 4️⃣ Heuristic fallback
    # ----------------------------
    has_role_info = bool(jd_context.responsibilities or jd_context.requirements)

    mentions_interview = any(
        k in raw for k in [
            "interview",
            "technical round",
            "assessment",
            "screening",
            "shortlist",
            "selection process",
            "hr interview",
            "panel interview",
        ]
    )

    # If job has responsibilities + salary/role clarity but zero hiring mention
    if has_role_info and not mentions_interview:
        return {
            "score": 0.35,
            "reason": "Job post describes role but does not explain interview or selection steps"
        }

    return {"score": 0.0, "reason": None}