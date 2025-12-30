

"""
Salary Detector

Purpose:
Extract reliable structured salary signals such as:
- Currency
- Min / Max salary
- Frequency (monthly / yearly / hourly / unspecified)
- Confidence estimation

We DO NOT flag fraud here.
We ONLY extract structured information.
"""

import re
from typing import Dict, Optional


# ----------- Currency Detection -----------
CURRENCY_SYMBOLS = {
    "₹": "INR",
    "$": "USD",
    "€": "EUR",
    "£": "GBP"
}

CURRENCY_WORDS = {
    "usd": "USD",
    "dollar": "USD",
    "inr": "INR",
    "rs": "INR",
    "rupees": "INR",
    "eur": "EUR",
    "euro": "EUR",
    "gbp": "GBP",
    "pound": "GBP"
}


# ----------- Frequency -----------
FREQUENCY_PATTERNS = {
    "month": [
        r"\bper\s*month\b",
        r"\bmonthly\b",
        r"/\s*month"
    ],
    "year": [
        r"\bper\s*year\b",
        r"\bannually\b",
        r"\byearly\b",
        r"/\s*year"
    ],
    "hour": [
        r"\bper\s*hour\b",
        r"\bhourly\b",
        r"/\s*hour"
    ]
}


# ----------- Salary Numeric Pattern -----------
SALARY_REGEX = re.compile(
    r"(₹|\$|€|£)?\s*([\d,]+)(?:\s*-\s*(₹|\$|€|£)?\s*([\d,]+))?",
    re.IGNORECASE
)


def detect_frequency(text: str) -> (Optional[str], float):
    lower = text.lower()

    for freq, patterns in FREQUENCY_PATTERNS.items():
        for p in patterns:
            if re.search(p, lower):
                return freq, 0.9

    return None, 0.0


def detect_currency(symbol: Optional[str], text: str) -> Optional[str]:
    if symbol and symbol in CURRENCY_SYMBOLS:
        return CURRENCY_SYMBOLS[symbol]

    lower = text.lower()

    for word, code in CURRENCY_WORDS.items():
        if word in lower:
            return code

    return None


def normalize_amount(val: str) -> float:
    return float(val.replace(",", ""))


def detect_salary(text: str) -> Dict:
    """
    Returns:
        {
            "raw_text": str or None,
            "currency": str or None,
            "amount_min": float or None,
            "amount_max": float or None,
            "frequency": str or None,
            "confidence": float
        }
    """

    if not text:
        return {
            "raw_text": None,
            "currency": None,
            "amount_min": None,
            "amount_max": None,
            "frequency": None,
            "confidence": 0.0
        }

    match = SALARY_REGEX.search(text)

    if not match:
        return {
            "raw_text": None,
            "currency": None,
            "amount_min": None,
            "amount_max": None,
            "frequency": None,
            "confidence": 0.0
        }

    symbol1 = match.group(1)
    amount1 = match.group(2)
    symbol2 = match.group(3)
    amount2 = match.group(4)

    currency = detect_currency(symbol1 or symbol2, text)

    try:
        min_val = normalize_amount(amount1)
        max_val = normalize_amount(amount2) if amount2 else min_val
    except:
        min_val, max_val = None, None

    frequency, freq_conf = detect_frequency(text)

    confidence = 0.0

    if currency:
        confidence += 0.3
    if min_val:
        confidence += 0.4
    if frequency:
        confidence += 0.3

    confidence = round(min(confidence, 1.0), 2)

    return {
        "raw_text": match.group(0),
        "currency": currency,
        "amount_min": min_val,
        "amount_max": max_val,
        "frequency": frequency,
        "confidence": confidence
    }

    # ------------------------------------
# Compatibility Wrapper
# ------------------------------------
def extract_salary_info(text: str):
    """
    Backward compatible wrapper.
    Older pipeline expects `extract_salary_info()`,
    but new detector uses `detect_salary()`.
    """
    return detect_salary(text)