

"""
Employment Type Detector

Purpose:
Identify whether the job is:
- Full Time
- Part Time
- Contract
- Internship
- Temporary / Freelance

Returns a simple structured result used by jd_parser.py
"""

import re
from typing import Dict


EMPLOYMENT_PATTERNS = {
    "full-time": [
        r"\bfull[\s\-]?time\b",
        r"\bpermanent\b",
        r"\bregular employment\b"
    ],
    "part-time": [
        r"\bpart[\s\-]?time\b"
    ],
    "contract": [
        r"\bcontract\b",
        r"\bcontractual\b",
        r"\bfixed term\b",
        r"\b6 month contract\b",
        r"\b12 month contract\b"
    ],
    "internship": [
        r"\bintern(ship)?\b",
        r"\btrainee\b"
    ],
    "temporary": [
        r"\btemporary\b",
        r"\bfreelance\b",
        r"\bgig work\b"
    ]
}


def detect_employment_type(text: str) -> Dict:
    """
    Detects employment type confidence and classifies best type.
    Returns:
        {
            "employment_type": str or None,
            "confidence": float
        }
    """

    if not text:
        return {"employment_type": None, "confidence": 0.0}

    lower = text.lower()

    best_match = None
    best_confidence = 0.0

    for emp_type, patterns in EMPLOYMENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, lower, re.IGNORECASE):
                # Confidence heuristic:
                # direct explicit match → higher confidence
                confidence = 0.9 if "full-time" in emp_type or "contract" in emp_type else 0.75

                if confidence > best_confidence:
                    best_match = emp_type
                    best_confidence = confidence

    return {
        "employment_type": best_match,
        "confidence": round(best_confidence, 2)
    }

# ------------------------------------
# Compatibility Wrapper
# ------------------------------------
def extract_employment_type(text: str):
    """
    Backward compatible wrapper so older code using
    `extract_employment_type()` continues to work.
    """
    return detect_employment_type(text)