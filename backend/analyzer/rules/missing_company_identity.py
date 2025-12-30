from typing import Dict
from analyzer.parsing.schema import JDContext
import re


def missing_company_identity_rule(jd_context: JDContext) -> Dict:
    """
    Detects missing or suspiciously anonymous company identity.
    Strongly aligned with JDContext pipeline.
    Safer thresholds, fewer false positives, clearer reasoning.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    raw_text = (jd_context.raw_text or "")
    lower = raw_text.lower()

    # ---------------- Structured Signal ----------------
    company_name = (jd_context.company.name or "").strip()

    # If parser extracted a confident company name → safe
    if company_name and len(company_name) >= 3:
        return {"score": 0.0, "reason": None}

    # ---------------- Strong Explicit Anonymity ----------------
    explicit_anonymous = [
        "confidential company",
        "company name not disclosed",
        "client confidential",
        "confidential employer",
        "hidden company",
        "undisclosed company",
        "name withheld"
    ]

    if any(p in lower for p in explicit_anonymous):
        return {
            "score": 0.9,
            "reason": "Company identity intentionally hidden or undisclosed"
        }

    # ---------------- Agency / Third Party Hiring ----------------
    third_party_markers = [
        "hiring for client",
        "recruiting for client",
        "recruiting on behalf of",
        "third party hiring",
        "staffing partner",
        "placement agency"
    ]

    if any(p in lower for p in third_party_markers):
        # If it's clearly stated agency hiring but identity truly unknown
        return {
            "score": 0.55,
            "reason": "Job appears to be posted by third-party recruiter without disclosing employer"
        }

    # ---------------- Heuristic Company Presence ----------------
    # Corporate keyword presence
    corporate_keywords = [
        "pvt ltd",
        "private limited",
        "inc",
        "llc",
        "corp",
        "corporation",
        "ltd"
    ]

    has_corporate_keyword = any(k in lower for k in corporate_keywords)

    # Capitalized probable brand tokens
    capital_words = re.findall(r"\b[A-Z][A-Za-z]{2,}\b", raw_text)
    has_brand_candidate = len(capital_words) >= 2

    # ---------------- Strong Missing Identity Condition ----------------
    if not company_name and not has_corporate_keyword and not has_brand_candidate:
        return {
            "score": 0.7,
            "reason": "Job post does not reveal any identifiable company name"
        }

    # ---------------- Weak Identity Case ----------------
    if not company_name:
        return {
            "score": 0.4,
            "reason": "Company identity unclear or weakly indicated"
        }

    return {"score": 0.0, "reason": None}