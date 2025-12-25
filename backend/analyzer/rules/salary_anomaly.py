import re
from typing import Dict
from analyzer.parsing.schema import JDContext


def unrealistic_salary_rule(jd_context: JDContext) -> Dict:
    """
    Detects unrealistic / suspicious salary claims.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    # --- Structured salary signal (preferred if available) ---
    salary_text_sources = [
        jd_context.compensation.salary_text or "",
        jd_context.compensation.additional_notes or "",
        text
    ]
    combined_salary_text = " ".join(salary_text_sources)

    salary_pattern = r"(₹|\$)\s?[\d,]{3,}"
    salary_match = re.search(salary_pattern, combined_salary_text)

    # --- Experience signals ---
    # Prefer structured fields if parser supports them
    structured_experience_years = jd_context.job.years_experience if hasattr(jd_context.job, "years_experience") else None

    positive_experience_patterns = [
        r"\b\d+\+?\s*(years|yrs)\b",
        r"\bminimum\s+\d+\s*(years|yrs)\b",
        r"\brequires?\s+\d+\s*(years|yrs)\b",
    ]

    negative_experience_patterns = [
        r"\bno experience\b",
        r"\bno experience required\b",
        r"\bfreshers?\b",
        r"\banyone can apply\b",
    ]

    has_positive_experience = (
        (structured_experience_years and structured_experience_years >= 2)
        or any(re.search(p, text) for p in positive_experience_patterns)
    )

    has_negative_experience = any(
        re.search(p, text) for p in negative_experience_patterns
    )

    # --- Decision Logic ---
    if not salary_match:
        return {"score": 0.0, "reason": None}

    # Strong red flag: high salary + explicitly no experience
    if has_negative_experience:
        return {
            "score": 0.85,
            "reason": "High salary offered despite explicitly no experience requirement"
        }

    # Medium flag: salary exists but no credible experience requirement
    if not has_positive_experience:
        return {
            "score": 0.6,
            "reason": "High salary with no clear experience requirement"
        }

    return {"score": 0.0, "reason": None}