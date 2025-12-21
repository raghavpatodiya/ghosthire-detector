import re
from typing import Dict


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
        if re.search(pattern, text):
            return {
                "score": 0.7,
                "reason": "Urgent call-to-action language detected"
            }

    return {"score": 0.0, "reason": None}