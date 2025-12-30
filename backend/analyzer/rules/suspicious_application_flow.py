from typing import Dict
import re
from analyzer.parsing.schema import JDContext
def suspicious_application_flow_rule(jd_context: JDContext) -> Dict:
    """
    Flags suspicious or unsafe application flows.
    Now prefers structured JDContext signals, falls back to raw text.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "").lower()

    # ==========================================================
    # STRUCTURED SIGNALS (preferred if parsing provided them)
    # ==========================================================
    hiring_steps = getattr(jd_context, "hiring_steps", None) or []
    application_channels = getattr(jd_context, "application_channels", None) or []
    requires_documents_before_interview = getattr(jd_context, "requires_documents_before_interview", False)

    structured_hits = []

    for step in hiring_steps:
        s = (step or "").lower()
        if any(x in s for x in ["fee", "deposit", "payment", "charge", "registration"]):
            structured_hits.append("fee_in_process")
        if any(x in s for x in ["whatsapp", "telegram", "dm", "google form"]):
            structured_hits.append("non_standard_channel")

    for c in application_channels:
        ch = (c or "").lower()
        if any(x in ch for x in ["whatsapp", "telegram", "google form", "dm"]):
            structured_hits.append("non_standard_channel")

    if requires_documents_before_interview:
        structured_hits.append("documents_before_interview")

    # HIGH RISK from structured
    if "fee_in_process" in structured_hits:
        return {
            "score": 0.9,
            "reason": "Application process includes monetary payment / fee requirement"
        }

    if "documents_before_interview" in structured_hits:
        return {
            "score": 0.8,
            "reason": "Applicant is asked to submit personal documents before interview"
        }

    if structured_hits.count("non_standard_channel") >= 2:
        return {
            "score": 0.7,
            "reason": "Multiple suspicious non-standard application channels detected"
        }

    if "non_standard_channel" in structured_hits:
        return {
            "score": 0.5,
            "reason": "Suspicious non-standard application channel detected"
        }

    # ==========================================================
    # TEXT-BASED BACKUP (legacy but safe)
    # ==========================================================
    suspicious_indicators = [
        # Money
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

        # Informal channels
        "apply via whatsapp",
        "contact on whatsapp",
        "send resume on whatsapp",
        "telegram",
        "dm us",
        "directly message",
        "contact hr directly",
        "text us",

        # Google forms
        "fill google form",
        "forms.gle",
        "google form application",

        # Documents
        "send documents before interview",
        "submit id proof",
        "share aadhaar",
        "share pan card",
    ]

    payment_terms = [
        "application fee", "processing fee",
        "registration fee", "security deposit",
        "training fee", "refundable fee",
        "pay to apply", "pay before"
    ]

    hit_terms = [t for t in suspicious_indicators if t in text]

    # High risk — payment / document demands
    if any(t in text for t in payment_terms):
        return {
            "score": 0.9,
            "reason": "Application requires payment or financial commitment"
        }

    if any(x in text for x in ["aadhaar", "pan card", "id proof", "documents before interview"]):
        return {
            "score": 0.8,
            "reason": "Job post asks for sensitive documents before interview"
        }

    # Medium Risk — non-standard apply channels
    medium_terms = ["whatsapp", "telegram", "forms.gle", "google form", "dm us"]

    medium_hits = [t for t in medium_terms if t in text]

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