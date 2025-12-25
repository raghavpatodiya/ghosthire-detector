import re
from typing import Dict
from analyzer.parsing.schema import JDContext


def urgent_language_rule(jd_context: JDContext) -> Dict:
    """
    Detects urgency / pressure-based hiring language using parsed JD data.
    This rule now expects JDContext only.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    # Collect relevant text sources
    text_blocks = [
        jd_context.job.title or "",
        jd_context.raw_text or ""
    ]

    text = " ".join(text_blocks).lower()

    patterns = [
        r"immediate join",
        r"urgent hiring",
        r"limited slots",
        r"join immediately",
        r"only few positions",
        r"apply immediately",
        r"urgent requirement",
        r"urgent vacancy"
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return {
                "score": 0.7,
                "reason": "Urgent call-to-action language detected"
            }

    return {"score": 0.0, "reason": None}