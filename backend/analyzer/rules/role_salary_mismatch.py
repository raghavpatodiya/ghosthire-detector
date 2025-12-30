from typing import Dict, Optional
import re
from analyzer.parsing.schema import JDContext


def role_salary_mismatch_rule(jd_context: JDContext) -> Dict:
    """
    Detects mismatch between role seniority and salary signals.
    Works ONLY with JDContext now and prefers structured fields.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    # If parsing confidence is extremely weak, avoid over‑flagging
    if getattr(jd_context, "confidence_score", 0) < 0.35:
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()
    title = (jd_context.job.title or "").lower()

    # ---------- Seniority Detection ----------
    inferred_level = "unknown"

    # Prefer structured seniority if parser supports it
    if hasattr(jd_context.job, "seniority_level") and jd_context.job.seniority_level:
        inferred_level = jd_context.job.seniority_level.lower()
    else:
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
            "head": "high",
        }

        for keyword, level in seniority_levels.items():
            if keyword in title:
                inferred_level = level
                break

    # ---------- Salary Extraction ----------
    salary_obj = getattr(jd_context, "salary", None)

    salary_amount = None
    salary_currency = None
    salary_frequency = "month"

    if salary_obj:
        salary_currency = getattr(salary_obj, "currency", None)
        salary_frequency = getattr(salary_obj, "frequency", "month") or "month"

        if getattr(salary_obj, "amount_max", None):
            salary_amount = salary_obj.amount_max
        elif getattr(salary_obj, "amount_min", None):
            salary_amount = salary_obj.amount_min

    # fallback regex if structured not available
    if not salary_amount:
        match = re.search(r"(₹|\$)\s?([\d,]+)", text)
        if match:
            salary_currency = match.group(1)
            salary_amount = float(match.group(2).replace(",", ""))
            salary_frequency = "month"

    if not salary_amount:
        return {"score": 0.0, "reason": None}

    # ---------- Normalize Salary to Monthly ----------
    def normalize_monthly(amount: float, freq: Optional[str]) -> float:
        if not freq:
            return amount
        freq = freq.lower()
        if "year" in freq:
            return amount / 12
        if "month" in freq:
            return amount
        if "week" in freq:
            return amount * 4
        if "day" in freq:
            return amount * 22
        if "hour" in freq:
            return amount * 160
        return amount

    monthly_salary = normalize_monthly(salary_amount, salary_frequency)

    # ---------- Thresholds ----------
    # baseline assumptions
    high_threshold = 70000
    medium_threshold = 40000

    if salary_currency == "$":
        # USD approximate thresholds
        high_threshold = 8000
        medium_threshold = 5000

    is_high_salary = monthly_salary >= high_threshold
    is_medium_salary = monthly_salary >= medium_threshold

    # ---------- Experience Signals ----------
    structured_exp = getattr(jd_context.job, "years_experience", None)

    negative_exp_phrases = [
        "no experience required",
        "no experience",
        "fresher",
        "freshers",
        "anyone can apply",
    ]

    has_negative_experience = (
        (structured_exp is not None and structured_exp <= 0)
        or any(p in text for p in negative_exp_phrases)
    )

    # ---------- Decision Logic ----------
    if inferred_level == "low" and is_high_salary:
        return {
            "score": 0.9,
            "reason": "Entry‑level role claims unusually high salary for role level",
        }

    if inferred_level == "low" and is_medium_salary:
        return {
            "score": 0.65,
            "reason": "Entry‑level role shows suspiciously inflated salary range",
        }

    if inferred_level == "mid" and is_high_salary and has_negative_experience:
        return {
            "score": 0.75,
            "reason": "High salary advertised despite no real experience requirement",
        }

    return {"score": 0.0, "reason": None}