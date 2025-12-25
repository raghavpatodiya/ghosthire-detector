from typing import Dict
from analyzer.parsing.schema import JDContext
def generic_job_title_rule(jd_context: JDContext) -> Dict:
    """
    Flags vague / non-specific job titles which are common in scam postings.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    title = (jd_context.job.title or "").lower()
    raw = (jd_context.raw_text or "").lower()

    if not title:
        return {
            "score": 0.5,
            "reason": "Job post does not specify a clear job title"
        }

    # Very generic scammy job titles
    strong_generic = [
        "work from home job",
        "easy job",
        "simple job",
        "no skill job",
        "anyone can apply",
        "home based job",
        "online typing job",
        "form filling job",
        "sms sending job",
        "data entry job",
        "back office job",
        "online job",
        "domestic job",
        "part time earning"
    ]

    # Weak generic naming
    weak_generic = [
        "multiple openings",
        "hiring for various roles",
        "multiple positions available",
        "staff required",
        "hiring staff",
        "required urgently",
        "fantastic opportunity",
        "great opportunity"
    ]

    # Strong hits
    for g in strong_generic:
        if g in title or g in raw:
            return {
                "score": 0.85,
                "reason": "Job title appears overly generic and commonly used in scam postings"
            }

    # Weak hits
    for g in weak_generic:
        if g in title or g in raw:
            return {
                "score": 0.55,
                "reason": "Job title is vague and not role-specific"
            }

    # Title must contain some profession / function
    meaningful_keywords = [
        "engineer", "developer", "designer", "analyst", "manager", "consultant",
        "specialist", "scientist", "architect", "administrator", "executive",
        "sales", "marketing", "support", "technician"
    ]

    if not any(k in title for k in meaningful_keywords):
        return {
            "score": 0.45,
            "reason": "Job title lacks clear professional role or function"
        }

    return {"score": 0.0, "reason": None}