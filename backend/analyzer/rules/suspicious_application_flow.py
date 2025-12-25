from typing import Dict
import re
from analyzer.parsing.schema import JDContext
def suspicious_application_flow_rule(jd_context: JDContext) -> Dict:
    """
    Flags suspicious or unsafe application flows.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    suspicious_indicators = [
        "pay to apply",
        "application fee",
        "processing fee",
        "registration fee",
        "security deposit",
        "training fee",
        "refundable fee",
        "non refundable",
        "pay before interview",
        "pay before joining",

        "apply via whatsapp",
        "contact on whatsapp",
        "send resume on whatsapp",

        "telegram",
        "dm us",

        "fill google form",
        "forms.gle",
        "google form application",

        "directly message",
        "contact hr directly",
        "text us",

        "send documents before interview",
        "submit id proof",
        "share aadhaar",
        "share pan card",
    ]

    hit_terms = []
    for term in suspicious_indicators:
        if term in text:
            hit_terms.append(term)

    # High risk — payment / document demands
    payment_terms = [
        "application fee", "processing fee",
        "registration fee", "security deposit",
        "training fee", "refundable fee"
    ]
    payment_hits = [t for t in hit_terms if t in payment_terms]

    if len(payment_hits) > 0:
        return {
            "score": 0.9,
            "reason": "Application requires payment or financial commitment"
        }

    # Medium Risk — non-standard apply channels
    medium_terms = [
        "whatsapp", "telegram", "dm",
        "google form", "forms.gle"
    ]
    medium_hits = [t for t in hit_terms if any(m in t for m in medium_terms)]

    if len(medium_hits) >= 2:
        return {
            "score": 0.7,
            "reason": "Multiple suspicious non-standard application channels detected"
        }

    if len(medium_hits) == 1:
        return {
            "score": 0.5,
            "reason": "Suspicious application channel detected"
        }

    return {"score": 0.0, "reason": None}