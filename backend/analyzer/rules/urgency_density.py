from typing import Dict
from analyzer.parsing.schema import JDContext
import re

def urgency_density_rule(jd_context: JDContext) -> Dict:
    """
    Measures how aggressively urgent the JD is by checking repeated urgency phrases.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text_sources = [
        jd_context.job.title or "",
        jd_context.raw_text or ""
    ]

    text = " ".join(text_sources).lower()

    urgency_terms = [
        "urgent", "immediately", "immediate join",
        "join now", "apply now", "asap",
        "limited slots", "hurry"
    ]

    count = 0
    for term in urgency_terms:
        count += len(re.findall(term, text))

    if count >= 4:
        return {
            "score": 0.8,
            "reason": "High urgency pressure detected repeatedly"
        }

    if count == 3:
        return {
            "score": 0.6,
            "reason": "Multiple urgency triggers found"
        }

    if count == 2:
        return {
            "score": 0.5,
            "reason": "Several urgency phrases present"
        }

    if count == 1:
        return {
            "score": 0.3,
            "reason": "Some urgency pressure detected"
        }

    return {"score": 0.0, "reason": None}