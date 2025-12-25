from typing import Dict
import re
from analyzer.parsing.schema import JDContext

def language_inconsistency_rule(jd_context: JDContext) -> Dict:
    """
    Detects suspicious or inconsistent language usage in JD.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "")
    lower = text.lower()

    # ---------------- Mixed Language Detection ----------------
    # Simple heuristic: detect Hindi/Hinglish + English together
    hindi_like_terms = [
        "apply karein", "turant", "yahan", "naukri",
        "aap", "hum", "karega", "milegi", "paise"
    ]

    hindi_hits = [t for t in hindi_like_terms if t in lower]
    english_detected = bool(re.search(r"[a-z]{3,}", lower))

    mixed_language = english_detected and len(hindi_hits) > 0

    # ---------------- Excessive Formatting Shifts ---------------
    # Suspicious if post randomly shifts tone or capitalization style
    excessive_caps = len(re.findall(r"\b[A-Z]{4,}\b", text))
    random_punctuation = len(re.findall(r"[!?]{2,}", text))

    # ---------------- Heuristic Scoring ----------------
    if mixed_language and (excessive_caps >= 5 or random_punctuation >= 4):
        return {
            "score": 0.8,
            "reason": "Job description shows inconsistent or mixed-language writing style"
        }

    if mixed_language:
        return {
            "score": 0.6,
            "reason": "Job post uses mixed languages in a suspicious manner"
        }

    if excessive_caps >= 7 or random_punctuation >= 6:
        return {
            "score": 0.6,
            "reason": "Job description contains aggressive and inconsistent formatting"
        }

    if excessive_caps >= 4:
        return {
            "score": 0.4,
            "reason": "Unusual excessive capitalization detected"
        }

    return {"score": 0.0, "reason": None}