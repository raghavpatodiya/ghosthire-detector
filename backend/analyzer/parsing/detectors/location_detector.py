"""
Location Detector

Purpose:
Extract structured information about WHERE the job is based and HOW it is worked:
- City / Country / Generic region (if detectable)
- Remote / Hybrid / Onsite working model
- Confidence estimation

We DO NOT guess aggressively — better to return low confidence
than wrong structured data.
"""

import re
from typing import Dict, Optional


# ----------- Remote / Hybrid / Onsite Keywords -----------
REMOTE_PATTERNS = [
    r"\bremote\b",
    r"\bwork from home\b",
    r"\bwork\-from\-home\b",
    r"\banywhere\b",
    r"\bwork from anywhere\b",
]

HYBRID_PATTERNS = [
    r"\bhybrid\b",
    r"\bpartial remote\b",
    r"\b2-3 days office\b",
    r"\bsplit work model\b"
]

ONSITE_PATTERNS = [
    r"\bonsite\b",
    r"\bon-site\b",
    r"\boffice based\b",
    r"\bwork from office\b",
]


# ------------- Basic location heuristic -------------
CITY_COUNTRY_REGEX = r"\b([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)(,\s*[A-Z][a-zA-Z]+)?\b"


def detect_remote_mode(text: str) -> (Optional[str], float):
    lower = text.lower()

    for p in REMOTE_PATTERNS:
        if re.search(p, lower):
            return "remote", 0.9

    for p in HYBRID_PATTERNS:
        if re.search(p, lower):
            return "hybrid", 0.85

    for p in ONSITE_PATTERNS:
        if re.search(p, lower):
            return "onsite", 0.8

    return None, 0.0


def detect_location_name(text: str) -> (Optional[str], float):
    """
    Lightweight city/country extraction.
    Does NOT hardcode city lists yet — keeps generic + safe.
    """

    matches = re.findall(CITY_COUNTRY_REGEX, text)

    if not matches:
        return None, 0.0

    # Take first meaningful non-generic match
    for match in matches:
        candidate = " ".join([m for m in match if m]).strip()

        if not candidate:
            continue

        # Avoid matching normal English words falsely
        if len(candidate.split()) > 5:
            continue

        # Basic sanity check
        if candidate.lower() in ["responsibilities", "requirements", "benefits"]:
            continue

        return candidate, 0.75

    return None, 0.0


def detect_location(text: str) -> Dict:
    """
    Returns:
        {
            "location": str or None,
            "location_confidence": float,
            "remote_mode": str or None,
            "remote_confidence": float
        }
    """

    if not text:
        return {
            "location": None,
            "location_confidence": 0.0,
            "remote_mode": None,
            "remote_confidence": 0.0
        }

    remote_mode, remote_conf = detect_remote_mode(text)
    location_name, loc_conf = detect_location_name(text)

    # If remote AND a city exists, reduce certainty of city relevance
    if remote_mode == "remote" and location_name:
        loc_conf = min(loc_conf, 0.4)

    return {
        "location": location_name,
        "location_confidence": round(loc_conf, 2),
        "remote_mode": remote_mode,
        "remote_confidence": round(remote_conf, 2),
    }

# ===== Compatibility Wrapper for jd_parser =====
def extract_location(text: str) -> Dict:
    """
    Wrapper to maintain backward compatibility.
    jd_parser imports extract_location(), internally we use detect_location().
    """
    return detect_location(text)