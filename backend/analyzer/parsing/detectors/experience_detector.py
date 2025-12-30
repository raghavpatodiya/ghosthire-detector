"""
Experience Detector

Purpose:
Extract clear experience signals such as:
- "2+ years"
- "0-2 years"
- "at least 3 yrs"
- "minimum 5 years"
- "freshers"
- "no experience required"

Returns structured & confidence-scored output for JD parser.
"""

import re
from typing import Dict, Optional


FRESHER_PATTERNS = [
    r"\bfreshers?\b",
    r"\bno experience required\b",
    r"\bno prior experience\b",
    r"\bentry level\b"
]

POSITIVE_EXPERIENCE_PATTERNS = [
    r"\bminimum\s+(\d+)\s*(years|year|yrs|yr)\b",
    r"\bat\s+least\s+(\d+)\s*(years|year|yrs|yr)\b",
    r"\b(\d+)\+?\s*(years|year|yrs|yr)\b",
    r"\b(\d+)\s*-\s*(\d+)\s*(years|year|yrs|yr)\b",
]


def detect_experience(text: str) -> Dict:
    """
    Returns:
        {
          "years_min": Optional[int],
          "years_max": Optional[int],
          "inferred_label": str,
          "confidence": float
        }
    """

    if not text:
        return {
            "years_min": None,
            "years_max": None,
            "inferred_label": None,
            "confidence": 0.0
        }

    lower = text.lower()

    # -------- FRESHER DETECTION --------
    for p in FRESHER_PATTERNS:
        if re.search(p, lower, re.IGNORECASE):
            return {
                "years_min": 0,
                "years_max": 1,
                "inferred_label": "freshers",
                "confidence": 0.9
            }

    # -------- POSITIVE EXPERIENCE MATCH --------
    for p in POSITIVE_EXPERIENCE_PATTERNS:
        match = re.search(p, lower, re.IGNORECASE)
        if not match:
            continue

        groups = match.groups()

        # Case: Range match like 2-4 years
        if len(groups) == 3:
            try:
                years_min = int(groups[0])
                years_max = int(groups[1])
                return {
                    "years_min": years_min,
                    "years_max": years_max,
                    "inferred_label": f"{years_min}-{years_max} years",
                    "confidence": 0.9 if years_min >= 2 else 0.75
                }
            except:
                pass

        # Case: Single number match like "3 years", "2+ years"
        if len(groups) >= 1:
            try:
                yrs = int(groups[0])
                return {
                    "years_min": yrs,
                    "years_max": yrs + 1,
                    "inferred_label": f"{yrs}+ years",
                    "confidence": 0.85 if yrs >= 2 else 0.7
                }
            except:
                pass

    # -------- If nothing matches --------
    return {
        "years_min": None,
        "years_max": None,
        "inferred_label": None,
        "confidence": 0.0
    }

# ------------------------------------------------------------------
# Compatibility wrapper
# jd_parser expects `extract_experience`
# ------------------------------------------------------------------
def extract_experience(text: str):
    """
    Wrapper to maintain compatibility with parser import style.
    Internally uses detect_experience().
    """
    return detect_experience(text)