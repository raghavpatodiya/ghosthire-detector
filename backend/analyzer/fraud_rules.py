"""
fraud_rules.py

Rule-based checks to detect suspicious job postings.
Each rule returns:
- score (0 to 1)
- reason (human-readable explanation)
"""

import re
from typing import List, Dict


def urgent_language_rule(text: str) -> Dict:
    text = text.lower()
    patterns = [
        r"immediate join",
        r"urgent hiring",
        r"limited slots",
        r"join immediately",
        r"only few positions",
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "score": 0.7,
                "reason": "Urgent call-to-action language detected"
            }

    return {"score": 0.0, "reason": None}


def unrealistic_salary_rule(text: str) -> Dict:
    """
    Flags very high salary claims without experience mention.
    """
    text = text.lower()
    salary_pattern = r"(₹|\$)\s?[\d,]{3,}"
    experience_keywords = ["experience", "years", "yrs"]

    salary_match = re.search(salary_pattern, text)
    mentions_experience = any(k in text.lower() for k in experience_keywords)

    if salary_match and not mentions_experience:
        return {
            "score": 0.6,
            "reason": "High salary mentioned without experience requirements"
        }

    return {"score": 0.0, "reason": None}


def poor_contact_info_rule(text: str) -> Dict:
    """
    Detects generic or suspicious contact info.
    """
    text = text.lower()
    if re.search(r"\b[a-z0-9._%+-]+@gmail\.com\b", text, re.IGNORECASE):
        return {
            "score": 0.8,
            "reason": "Generic email contact used instead of company domain"
        }

    return {"score": 0.0, "reason": None}


def run_all_rules(job_text: str) -> Dict:
    """
    Runs all fraud detection rules on a job post.
    """
    rules = [
        urgent_language_rule,
        unrealistic_salary_rule,
        poor_contact_info_rule,
    ]

    total_score = 0.0
    reasons: List[str] = []

    for rule in rules:
        result = rule(job_text)
        total_score += result["score"]
        if result["reason"]:
            reasons.append(result["reason"])

    return {
        "rule_score": round(min(total_score, 1.0), 2),
        "reasons": reasons
    }