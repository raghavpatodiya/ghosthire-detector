import re
from typing import Dict


def unrealistic_salary_rule(text: str) -> Dict:
    text = text.lower()

    salary_pattern = r"(₹|\$)\s?[\d,]{3,}"
    salary_match = re.search(salary_pattern, text)

    # experience signals
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

    has_positive_experience = any(
        re.search(p, text) for p in positive_experience_patterns
    )

    has_negative_experience = any(
        re.search(p, text) for p in negative_experience_patterns
    )

    # anomaly logic
    if salary_match and (has_negative_experience or not has_positive_experience):
        return {
            "score": 0.6,
            "reason": "High salary with no credible experience requirement"
        }

    return {"score": 0.0, "reason": None}