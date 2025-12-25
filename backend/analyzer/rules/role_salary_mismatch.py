from typing import Dict
import re
from analyzer.parsing.schema import JDContext

def role_salary_mismatch_rule(jd_context: JDContext) -> Dict:
    """
    Detects mismatch between role seniority and salary signals.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    # -------- Determine Role Seniority --------
    title = (jd_context.job.title or "").lower()

    seniority_levels = {
        "intern": "low",
        "trainee": "low",
        "junior": "low",
        "associate": "low",
        "graduate": "low",

        "mid": "mid",
        "engineer": "mid",
        "developer": "mid",
        "analyst": "mid",

        "senior": "high",
        "lead": "high",
        "principal": "high",
        "architect": "high",
        "manager": "high",
        "head": "high"
    }

    inferred_level = "unknown"
    for keyword, level in seniority_levels.items():
        if keyword in title:
            inferred_level = level
            break

    # -------- Extract Salary (structured preferred) --------
    try:
        salary_amount = jd_context.salary.amount_max or jd_context.salary.amount_min
        salary_currency = jd_context.salary.currency
    except Exception:
        salary_amount = None
        salary_currency = None

    # fallback regex
    if not salary_amount:
        salary_pattern = r"(₹|\$)\s?([\d,]+)"
        match = re.search(salary_pattern, text)
        if match:
            salary_currency = match.group(1)
            salary_amount = float(match.group(2).replace(",", ""))

    if not salary_amount:
        return {"score": 0.0, "reason": None}

    # -------- Heuristic Thresholds --------
    high_threshold = 70000   # monthly
    medium_threshold = 40000

    is_high_salary = salary_amount >= high_threshold
    is_medium_salary = salary_amount >= medium_threshold

    # -------- Decision Logic --------
    if inferred_level == "low" and is_high_salary:
        return {
            "score": 0.85,
            "reason": "Entry-level role claims unusually high salary"
        }

    if inferred_level == "low" and is_medium_salary:
        return {
            "score": 0.6,
            "reason": "Entry-level role salary appears suspiciously inflated"
        }

    if inferred_level == "mid" and is_high_salary and "no experience" in text:
        return {
            "score": 0.75,
            "reason": "High salary offered despite no strong seniority requirement"
        }

    return {"score": 0.0, "reason": None}