from typing import Dict
import re
from analyzer.parsing.schema import JDContext


def copy_paste_jd_rule(jd_context: JDContext) -> Dict:
    """
    Detects signals that the JD is copy‑pasted, templated, or reused.
    Works ONLY with JDContext now.

    Improvements vs old version:
    - Uses structured company + role context if available
    - Safer repetition thresholds
    - Avoids falsely penalizing normal boilerplate HR language
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").strip()
    if not text:
        return {"score": 0.0, "reason": None}

    lower = text.lower()

    # ----------------- Strong plagiarism / redistribution hints -----------------
    strong_indicators = [
        "do not copy",
        "copyright",
        "all rights reserved",
        "this content is protected",
        "original posting",
        "plagiarized",
        "taken from",
        "source:",
    ]

    if any(p in lower for p in strong_indicators):
        return {
            "score": 0.9,
            "reason": "Job description explicitly indicates copied / redistributed content"
        }

    # ----------------- Repeated Content Detection -----------------
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Ignore very short boilerplate lines
    lines = [l for l in lines if len(l) > 25]

    seen = {}
    for line in lines:
        norm = re.sub(r"\s+", " ", line.lower())
        seen[norm] = seen.get(norm, 0) + 1

    repeated_lines = [l for l, c in seen.items() if c >= 3]

    if len(repeated_lines) >= 3:
        return {
            "score": 0.8,
            "reason": "Job description repeats large sections, suggesting reused content"
        }

    if len(repeated_lines) == 2:
        return {
            "score": 0.6,
            "reason": "Job description contains duplicated sections indicating possible copy-paste"
        }

    # ----------------- Multiple Company / Brand Confusion -----------------
    company_name = (jd_context.company.name or "").strip()
    company_name_lower = company_name.lower()

    # Tokens starting capital letter (potential brand names)
    tokens = re.findall(r"\b[A-Z][A-Za-z]{2,}\b", text)
    tokens = [t for t in tokens if t.lower() != company_name_lower]

    unique_tokens = set(tokens)

    # Only flag if there are *clearly unrelated* brand/company references
    if len(unique_tokens) >= 5 and not company_name:
        return {
            "score": 0.55,
            "reason": "Multiple unrelated company/brand names suggest reused JD from other sources"
        }

    # ----------------- Template / Boilerplate Style -----------------
    template_phrases = [
        "we are one of the leading",
        "renowned organization",
        "prestigious company",
        "world class organization",
        "industry leading company",
        "among the top companies",
        "number one company",
    ]

    boilerplate_hits = sum(1 for p in template_phrases if p in lower)

    if boilerplate_hits >= 3:
        return {
            "score": 0.45,
            "reason": "JD appears heavily templated with generic promotional language"
        }

    return {"score": 0.0, "reason": None}