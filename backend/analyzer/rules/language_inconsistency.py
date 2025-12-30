from typing import Dict
import re
from analyzer.parsing.schema import JDContext


def language_inconsistency_rule(jd_context: JDContext) -> Dict:
    """
    Detects suspicious or inconsistent language usage in JD.
    Now aligned to JDContext pipeline, safer thresholds, reduced false positives.

    Key improvements:
    - Allows legitimate bilingual posts if structured & professional
    - Stronger detection of scammy Hinglish spam tone
    - Formatting inconsistency detection tuned
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "")
    lower = text.lower()

    if not text.strip():
        return {"score": 0.0, "reason": None}

    # ---------------- Mixed / Suspicious Hinglish Detection ----------------
    hindi_like_terms = [
        "apply karein", "turant", "yahan", "naukri",
        "aap", "hum", "karega", "milegi", "paise",
        "sampark", "bharti", "rojgar", "avsar"
    ]

    hindi_hits = [t for t in hindi_like_terms if t in lower]

    english_detected = bool(re.search(r"[a-z]{3,}", lower))
    mixed_language = english_detected and len(hindi_hits) > 0

    # ---------------- Legit bilingual tolerance ----------------
    # If company seems proper + JD structured decently → don't punish mildly
    seems_professional = False

    if jd_context.company and jd_context.company.name:
        seems_professional = True

    has_structure = (
        (jd_context.responsibilities and len(jd_context.responsibilities) >= 2)
        or (jd_context.requirements and len(jd_context.requirements) >= 2)
    )

    # ---------------- Formatting inconsistency ----------------
    excessive_caps = len(re.findall(r"\b[A-Z]{4,}\b", text))
    random_punctuation = len(re.findall(r"[!?]{2,}", text))

    # ---------------- Strong Scam Tone ----------------
    if mixed_language and (excessive_caps >= 4 or random_punctuation >= 4):
        return {
            "score": 0.85,
            "reason": "Job uses mixed-language with aggressive formatting, common in scam posts"
        }

    # ---------------- Medium Suspicion ----------------
    if mixed_language and not seems_professional:
        return {
            "score": 0.6,
            "reason": "Job post uses informal mixed-language tone, lacks professionalism"
        }

    # ---------------- Mild Formatting Issues ----------------
    if excessive_caps >= 7 or random_punctuation >= 6:
        return {
            "score": 0.6,
            "reason": "Job description shows excessive random capitalization or punctuation"
        }

    if excessive_caps >= 4:
        return {
            "score": 0.4,
            "reason": "Unusual capitalization pattern detected in job post"
        }

    return {"score": 0.0, "reason": None}