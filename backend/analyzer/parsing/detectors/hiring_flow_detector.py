"""
Hiring Flow Detector

Purpose:
Extract structured signals about hiring / recruitment process such as:
- Interview rounds
- HR screening
- Technical assessment
- Background verification
- Offer letter timing
- Suspicious "no interview / instant offer" claims

We do NOT judge fraud here.
We ONLY extract clean structured information so rules layer can decide.
"""

import re
from typing import Dict, List


HIRING_KEYWORDS = {
    "interview": [
        r"\binterview\b",
        r"\btechnical interview\b",
        r"\bhr interview\b",
        r"\btelephonic interview\b",
        r"\bvirtual interview\b",
        r"\bvideo interview\b"
    ],
    "screening": [
        r"\bscreening\b",
        r"\bshortlist(ed|ing)?\b",
        r"\bprofile review\b"
    ],
    "assessment": [
        r"\bassignment\b",
        r"\bassessment\b",
        r"\btest\b",
        r"\bcoding test\b",
        r"\baptitude test\b"
    ],
    "background_check": [
        r"\bbackground\b",
        r"\bverification\b",
        r"\bdocument verification\b"
    ],
    "offer_stage": [
        r"\boffer letter\b",
        r"\bselection letter\b",
        r"\bjoining letter\b"
    ]
}

SUSPICIOUS_NO_PROCESS_PATTERNS = [
    r"\bno interview\b",
    r"\bno interview required\b",
    r"\bno selection process\b",
    r"\bguaranteed selection\b",
    r"\binstant offer\b",
    r"\binstant joining\b"
]


def detect_hiring_flow(text: str) -> Dict:
    """
    Returns:
        {
            "steps": List[str],
            "mentions_interview": bool,
            "suspicious_fast_track": bool,
            "confidence": float
        }
    """

    if not text:
        return {
            "steps": [],
            "mentions_interview": False,
            "suspicious_fast_track": False,
            "confidence": 0.0
        }

    lower = text.lower()

    detected_steps: List[str] = []
    mentions_interview = False
    suspicious_fast_track = False

    # -------- Positive Hiring Steps --------
    for step_name, patterns in HIRING_KEYWORDS.items():
        for p in patterns:
            if re.search(p, lower):
                if step_name not in detected_steps:
                    detected_steps.append(step_name)

                if step_name == "interview":
                    mentions_interview = True

    # -------- Suspicious Fast Lane --------
    for p in SUSPICIOUS_NO_PROCESS_PATTERNS:
        if re.search(p, lower):
            suspicious_fast_track = True

    # -------- Confidence Heuristic --------
    confidence = 0.0

    if detected_steps:
        confidence += 0.6  # structured hiring process exists

    if mentions_interview:
        confidence += 0.2

    if suspicious_fast_track:
        confidence += 0.2

    confidence = round(min(confidence, 1.0), 2)

    return {
        "steps": detected_steps,
        "mentions_interview": mentions_interview,
        "suspicious_fast_track": suspicious_fast_track,
        "confidence": confidence
    }
# ------------------------------------
# Compatibility Wrapper
# ------------------------------------
def extract_hiring_flow(text: str):
    """
    Backward compatible wrapper so older pipeline code using
    `extract_hiring_flow()` continues to work.
    """
    return detect_hiring_flow(text)