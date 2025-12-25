from typing import Dict
from analyzer.parsing.schema import JDContext
import re

def missing_company_identity_rule(jd_context: JDContext) -> Dict:
    """
    Detects missing or suspiciously anonymous company identity.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    raw_text = (jd_context.raw_text or "").lower()

    # ------- Structured Signals -------
    company_name = (jd_context.company.name or "").strip()

    # ------- Direct strong red flags -------
    anonymous_phrases = [
        "confidential company",
        "company name not disclosed",
        "hiring for client",
        "client confidential",
        "third party hiring",
        "recruiting on behalf of",
        "agency hiring"
    ]

    if any(p in raw_text for p in anonymous_phrases):
        return {
            "score": 0.85,
            "reason": "Company identity intentionally hidden or anonymized"
        }

    # ------- No visible identity at all -------
    # check if no structured name and no likely company word signals in text
    has_company_keywords = any(
        k in raw_text
        for k in ["pvt ltd", "private limited", "inc", "llc", "corporation", "corp"]
    )

    has_brand_like_capital_word = bool(re.search(r"\b[A-Z][A-Za-z]{2,}\b", jd_context.raw_text or ""))

    if not company_name and not has_company_keywords and not has_brand_like_capital_word:
        return {
            "score": 0.7,
            "reason": "Job post does not reveal any identifiable company name"
        }

    # ------- Weak identity (fallback) -------
    if not company_name:
        return {
            "score": 0.45,
            "reason": "Company name missing or unclear"
        }

    return {"score": 0.0, "reason": None}