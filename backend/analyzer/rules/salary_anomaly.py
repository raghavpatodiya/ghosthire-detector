import re
from typing import Dict
from analyzer.parsing.schema import JDContext


def unrealistic_salary_rule(jd_context: JDContext) -> Dict:
    """
    Detects unrealistic / suspicious salary claims using structured JDContext.
    Prefers structured fields > textual regex.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    # =====================
    # Structured Salary Data
    # =====================
    salary = getattr(jd_context, "salary", None)
    salary_amount = None
    currency = None
    frequency = "month"

    if salary:
        currency = salary.currency or None
        frequency = (salary.frequency or "month").lower()
        if salary.amount_max:
            salary_amount = salary.amount_max
        elif salary.amount_min:
            salary_amount = salary.amount_min

    # Normalize salary to MONTHLY baseline if possible
    def normalize_to_monthly(amount, freq):
        if not amount:
            return None
        if "year" in freq:
            return amount / 12
        if "hour" in freq:
            return amount * 160   # rough monthly work hours assumption
        return amount

    monthly_salary = normalize_to_monthly(salary_amount, frequency) if salary_amount else None

    # =====================
    # Fallback: Regex salary detection
    # =====================
    if not monthly_salary:
        salary_pattern = r"(₹|\$)\s?([\d,]{4,})"
        m = re.search(salary_pattern, text)
        if m:
            currency = m.group(1)
            try:
                monthly_salary = float(m.group(2).replace(",", ""))
            except:
                monthly_salary = None

    # If still nothing → no decision
    if not monthly_salary:
        return {"score": 0.0, "reason": None}

    # =====================
    # Experience Signals
    # =====================
    structured_exp = None
    if hasattr(jd_context.job, "years_experience"):
        structured_exp = jd_context.job.years_experience

    positive_exp_patterns = [
        r"\b\d+\+?\s*(years|yrs)\b",
        r"\bminimum\s+\d+\s*(years|yrs)\b",
        r"\brequires?\s+\d+\s*(years|yrs)\b",
    ]

    negative_exp_patterns = [
        r"\bno experience\b",
        r"\bno experience required\b",
        r"\bfreshers?\b",
        r"\banyone can apply\b",
    ]

    has_negative = any(re.search(p, text) for p in negative_exp_patterns)

    has_positive = (
        (structured_exp and structured_exp >= 2)
        or any(re.search(p, text) for p in positive_exp_patterns)
    )

    # =====================
    # Thresholds
    # =====================
    HIGH_RISK_THRESHOLD = 70000   # INR monthly rough reference
    HIGH_RISK_USD = 3000          # USD monthly rough reference

    is_high_salary = False

    if currency == "₹":
        is_high_salary = monthly_salary and monthly_salary >= HIGH_RISK_THRESHOLD
    elif currency == "$":
        is_high_salary = monthly_salary and monthly_salary >= HIGH_RISK_USD
    else:
        is_high_salary = monthly_salary and monthly_salary > 60000   # fallback heuristic

    # =====================
    # Decision Logic
    # =====================
    if is_high_salary and has_negative:
        return {
            "score": 0.9,
            "reason": "Very high salary claimed despite explicitly no/zero experience requirement"
        }

    if is_high_salary and not has_positive:
        return {
            "score": 0.65,
            "reason": "High salary offered with no credible experience requirement"
        }

    return {"score": 0.0, "reason": None}