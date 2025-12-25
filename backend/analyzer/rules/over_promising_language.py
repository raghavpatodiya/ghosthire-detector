from typing import Dict
import re
from analyzer.parsing.schema import JDContext

def over_promising_language_rule(jd_context: JDContext) -> Dict:
    """
    Detects unrealistic / over‑promising guarantees in job descriptions.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    strong_scams = [
        "guaranteed job",
        "100% job guarantee",
        "assured placement",
        "job assured",
        "placement guaranteed",
        "offer letter guaranteed",
        "salary guaranteed",
        "fixed job after training",
    ]

    medium_promises = [
        "earn unlimited",
        "no effort required",
        "work only few hours and earn",
        "earn while you sleep",
        "instant approval",
        "instant joining",
        "guaranteed selection",
    ]

    hits = [t for t in strong_scams if t in text]
    if hits:
        return {
            "score": 0.9,
            "reason": "Unrealistic guaranteed job/placement claims detected"
        }

    med_hits = [t for t in medium_promises if t in text]
    if len(med_hits) >= 2:
        return {
            "score": 0.7,
            "reason": "Multiple exaggerated earning or instant selection claims"
        }

    if len(med_hits) == 1:
        return {
            "score": 0.5,
            "reason": "Suspicious exaggerated promise found"
        }

    return {"score": 0.0, "reason": None}