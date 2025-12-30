from analyzer.parsing.detectors.experience_detector import detect_experience as extract_experience
from analyzer.parsing.detectors.location_detector import detect_location as extract_location
from analyzer.parsing.detectors.employment_type_detector import detect_employment_type as extract_employment_type
from analyzer.parsing.detectors.hiring_flow_detector import detect_hiring_flow as extract_hiring_flow
from analyzer.parsing.detectors.salary_detector import detect_salary as extract_salary_info

# -------- Required Schema Imports --------
from analyzer.parsing.schema import (
    JDContext,
    SalaryInfo,
    JobRoleInfo,
    CompanyInfo
)

import re

# -------- Email Extraction Pattern --------
EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


# -------- Company Extraction Helper --------
def parse_company(raw_text: str) -> CompanyInfo:
    """
    Lightweight heuristic company extractor.
    If first line looks like a company name → assume it.
    """
    if not raw_text:
        return CompanyInfo()

    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    if not lines:
        return CompanyInfo()

    first = lines[0]

    # avoid false positives like: "We are hiring", "Urgent Hiring"
    lowered = first.lower()
    if any(k in lowered for k in ["hiring", "urgent", "apply", "job"]):
        return CompanyInfo()

    # if line is short enough → likely a company label
    if len(first.split()) <= 6:
        return CompanyInfo(name=first, inferred_from="first_line")

    return CompanyInfo()
def parse_jd(raw_text: str) -> JDContext:
    """
    Main JD → Structured Context parser (FINAL STRUCTURED VERSION)
    Consumes detector dict outputs instead of tuple unpacking.
    """

    if not raw_text or len(raw_text.strip()) < 30:
        return JDContext(raw_text=raw_text or "", confidence_score=0.2)

    text = raw_text.strip()

    # ---------- Run detectors (each returns dict now) ----------
    exp_data = extract_experience(text) or {}
    loc_data = extract_location(text) or {}
    emp_data = extract_employment_type(text) or {}
    hiring_data = extract_hiring_flow(text) or {}
    salary_data = extract_salary_info(text) or {}

    # ---------- EXPERIENCE ----------
    years_min = exp_data.get("years_min")
    years_max = exp_data.get("years_max")
    exp_conf = exp_data.get("confidence", 0.0)

    # ---------- LOCATION ----------
    location_name = loc_data.get("location")
    loc_conf = loc_data.get("location_confidence", 0.0)
    remote_flag = loc_data.get("remote_mode")
    remote_conf = loc_data.get("remote_confidence", 0.0)

    # ---------- EMPLOYMENT ----------
    employment_type = emp_data.get("employment_type")
    emp_conf = emp_data.get("confidence", 0.0)

    # ---------- HIRING FLOW ----------
    hiring_steps = hiring_data.get("steps", [])
    hiring_conf = hiring_data.get("confidence", 0.0)

    # ---------- SALARY ----------
    salary_obj = SalaryInfo(
        raw_text=salary_data.get("raw_text"),
        currency=salary_data.get("currency"),
        amount_min=salary_data.get("amount_min"),
        amount_max=salary_data.get("amount_max"),
        frequency=salary_data.get("frequency"),
        confidence=salary_data.get("confidence", 0.0),
    )

    # ---------- EMAILS ----------
    emails = list(set(EMAIL_REGEX.findall(text))) if text else []

    # ---------- COMPANY ----------
    company_info = parse_company(text)

    # ---------- JOB ROLE ----------
    job_role = JobRoleInfo(
        title=None,
        years_experience=years_min if years_min is not None else None,
        experience_confidence=exp_conf,
        remote_mode=remote_flag,
        remote_confidence=remote_conf,
        employment_type=employment_type,
        employment_confidence=emp_conf,
        location=location_name,
        location_confidence=loc_conf,
    )

    # ---------- CONFIDENCE ----------
    confidences = [
        exp_conf,
        loc_conf,
        emp_conf,
        hiring_conf,
        salary_data.get("confidence", 0.0),
    ]
    confidences = [c for c in confidences if c]

    overall_conf = 0.5
    if confidences:
        overall_conf = round(sum(confidences) / len(confidences), 2)

    return JDContext(
        raw_text=text,
        company=company_info,
        job=job_role,
        salary=salary_obj,
        responsibilities=[],
        requirements=[],
        benefits=[],
        emails=emails,
        phone_numbers=[],
        urls=[],
        hiring_flow=hiring_steps,
        confidence_score=overall_conf,
    )