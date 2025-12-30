import re
from typing import Dict, List
from analyzer.parsing.schema import JDContext


def poor_contact_info_rule(jd_context: JDContext) -> Dict:
    """
    Detects suspicious or low-trust contact information.
    Works ONLY with JDContext now.
    """

    if not isinstance(jd_context, JDContext):
        return {"score": 0.0, "reason": None}

    text = (jd_context.raw_text or "")
    lower = text.lower()

    company_name = (jd_context.company.name or "").lower()

    # -------- Extract contacts (prefer structured, fallback to regex) --------
    emails: List[str] = []
    phones: List[str] = []

    if getattr(jd_context, "emails", None):
        emails = list(set(jd_context.emails))

    if not emails:
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

    if getattr(jd_context, "phones", None):
        phones = list(set(jd_context.phones))

    if not phones:
        phones = re.findall(r"\+?\d[\d\s\-]{8,}\d", text)

    # -------- Generic free email domains --------
    generic_domains = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
        "rediffmail.com", "protonmail.com"
    ]

    generic_hits = [e for e in emails if any(d in e.lower() for d in generic_domains)]

    if len(generic_hits) >= 2:
        return {
            "score": 0.9,
            "reason": "Multiple free-email addresses used instead of official company domain"
        }

    if len(generic_hits) == 1:
        return {
            "score": 0.8,
            "reason": "Job contact uses a generic email provider instead of company domain"
        }

    # -------- WhatsApp-only / Phone-only recruitment --------
    if ("whatsapp" in lower or "telegram" in lower) and phones:
        return {
            "score": 0.85,
            "reason": "Job post requests contact via WhatsApp/Telegram instead of official channels"
        }

    if phones and not emails:
        return {
            "score": 0.6,
            "reason": "Job post only provides phone contact without official email"
        }

    # -------- Corporate domain but mismatch with company --------
    if emails and company_name and len(company_name) > 3:
        corporate_emails = [e for e in emails if not any(d in e.lower() for d in generic_domains)]
        if corporate_emails:
            normalized_company = company_name.replace(" ", "")
            domains = [e.split("@")[1].lower() for e in corporate_emails]

            # allow partial similarity to reduce false positives
            domain_mismatch = not any(
                normalized_company in d or d.split(".")[0] in normalized_company
                for d in domains
            )

            if domain_mismatch:
                return {
                    "score": 0.55,
                    "reason": "Corporate email domain does not appear related to stated company"
                }

    return {"score": 0.0, "reason": None}