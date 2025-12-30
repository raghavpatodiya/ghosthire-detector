from typing import Dict
import re
from analyzer.parsing.schema import JDContext


def over_promising_language_rule(jd_context: JDContext) -> Dict:
    """
    Detects unrealistic / over‑promising guarantees in job descriptions.
    Fully aligned to JDContext pipeline with safer thresholds.

    Enhancements:
    - Stronger scam‑tier detection
    - Medium exaggeration tier
    - Reduced false positives
    - Uses context awareness (if JD looks structured/professional → less chance to flag)
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "")
    lower = text.lower()

    if not text.strip():
        return {"score": 0.0, "reason": None}

    # -------------------------
    # Strong scam / impossible guarantees
    # -------------------------
    strong_scams = [
        "guaranteed job",
        "100% job guarantee",
        "assured placement",
        "job assured",
        "placement guaranteed",
        "offer letter guaranteed",
        "salary guaranteed",
        "fixed job after training",
        "job without interview",
        "selection without interview",
        "instant selection",
        "same day joining guaranteed",
    ]

    for s in strong_scams:
        if s in lower:
            return {
                "score": 0.9,
                "reason": "Unrealistic guaranteed hiring / placement promises detected"
            }

    # -------------------------
    # Medium level exaggeration
    # -------------------------
    medium_promises = [
        "earn unlimited",
        "no effort required",
        "effortless income",
        "easy money",
        "earn while you sleep",
        "work only few hours and earn",
        "guaranteed selection",
        "instant approval",
        "quick approval",
        "job sure shot",
    ]

    med_hits = [t for t in medium_promises if t in lower]

    # -------------------------
    # Tone / formatting reinforcement
    # -------------------------
    excessive_exclamations = len(re.findall(r"[!?]{2,}", text))
    shouting_caps = len(re.findall(r"\b[A-Z]{4,}\b", text))

    # -------------------------
    # Professional JD tolerance
    # -------------------------
    seems_structured = (
        (jd_context.responsibilities and len(jd_context.responsibilities) >= 2)
        or (jd_context.requirements and len(jd_context.requirements) >= 2)
    )

    # -------------------------
    # Scoring logic
    # -------------------------
    if len(med_hits) >= 2:
        # escalate if formatting is aggressive
        if excessive_exclamations >= 3 or shouting_caps >= 4:
            return {
                "score": 0.8,
                "reason": "Highly exaggerated earning or instant hiring claims with aggressive tone"
            }

        return {
            "score": 0.7,
            "reason": "Multiple exaggerated earning / instant selection claims detected"
        }

    if len(med_hits) == 1:
        if not seems_structured:
            return {
                "score": 0.55,
                "reason": "Suspicious over‑promising hiring / earning claim in unstructured JD"
            }

        return {
            "score": 0.45,
            "reason": "Suspicious exaggerated promise found"
        }

    return {"score": 0.0, "reason": None}