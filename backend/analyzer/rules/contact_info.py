import re
from typing import Dict


def poor_contact_info_rule(text: str) -> Dict:
    text = text.lower()

    if re.search(r"\b[a-z0-9._%+-]+@gmail\.com\b", text):
        return {
            "score": 0.8,
            "reason": "Generic email contact used instead of company domain"
        }

    return {"score": 0.0, "reason": None}