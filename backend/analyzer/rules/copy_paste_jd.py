from typing import Dict
import re
from analyzer.parsing.schema import JDContext

def copy_paste_jd_rule(jd_context: JDContext) -> Dict:
    """
    Detects signs that the JD is copy‑pasted, templated,
    or borrowed from unrelated sources.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "")
    lower = text.lower()

    # ----------------- Strong plagiarism indicators -----------------
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
            "reason": "Job description shows strong signs of copied or redistributed content"
        }

    # ----------------- Repeated Content Detection -----------------
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    repeated_count = 0

    seen = {}
    for line in lines:
        norm = line.lower()
        seen[norm] = seen.get(norm, 0) + 1

    repeated_lines = [l for l, c in seen.items() if c >= 3]

    if len(repeated_lines) >= 3:
        return {
            "score": 0.8,
            "reason": "Job description repeats identical content unusually often"
        }

    if len(repeated_lines) == 2:
        return {
            "score": 0.6,
            "reason": "Job description contains duplicated sections suggesting copy-paste"
        }

    # ----------------- Multiple Company Identity Signals -----------------
    possible_company_mentions = re.findall(r"\b[A-Z][A-Za-z]{2,}\b", text)
    unique_tokens = set(possible_company_mentions)

    if len(unique_tokens) >= 4 and not jd_context.company.name:
        return {
            "score": 0.55,
            "reason": "Multiple unrelated brand/company names detected, suggesting reused JD content"
        }

    # ----------------- Template / Generic Boilerplate -----------------
    template_phrases = [
        "we are one of the leading",
        "we are among the top companies",
        "renowned organization",
        "prestigious company",
        "world class organization",
        "industry leading company",
        "number one company",
    ]

    if sum(1 for p in template_phrases if p in lower) >= 2:
        return {
            "score": 0.45,
            "reason": "Job description appears to use generic boilerplate template language"
        }

    return {"score": 0.0, "reason": None}