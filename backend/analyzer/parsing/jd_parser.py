import re
from typing import Optional

from analyzer.parsing.schema import JDContext, SalaryInfo, CompanyInfo, JobRoleInfo


TITLE_PATTERN = re.compile(r"\[TITLE\](.*)")
META_PATTERN = re.compile(r"\[META\](.*)")
HEADING_PATTERN = re.compile(r"\[(H\d)\](.*)")


SALARY_REGEX = re.compile(
    r"(₹|\$|€)\s?([\d,]+)(?:.*?(month|year|hour))?",
    re.IGNORECASE
)


EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


def parse_salary(text: str) -> SalaryInfo:
    match = SALARY_REGEX.search(text)
    if not match:
        return SalaryInfo()

    currency = match.group(1)
    amount = match.group(2).replace(",", "")
    freq = match.group(3) or "unknown"

    return SalaryInfo(
        raw_text=match.group(0),
        currency=currency,
        amount_min=float(amount),
        amount_max=float(amount),
        frequency=freq.lower()
    )


def parse_company_from_title(title: Optional[str]) -> CompanyInfo:
    if not title:
        return CompanyInfo()

    if "|" in title:
        possible_company = title.split("|")[-1].strip()
        if len(possible_company.split()) <= 5:
            return CompanyInfo(
                name=possible_company,
                inferred_from="title"
            )

    return CompanyInfo()


def parse_headings_and_sections(lines):
    responsibilities = []
    requirements = []
    benefits = []

    current_section = None

    for line in lines:
        lower = line.lower()

        if "responsibilities" in lower:
            current_section = "responsibilities"
            continue

        if "requirements" in lower or "skills" in lower:
            current_section = "requirements"
            continue

        if "benefits" in lower or "perks" in lower:
            current_section = "benefits"
            continue

        if line.startswith("- "):
            bullet = line[2:].strip()

            if current_section == "responsibilities":
                responsibilities.append(bullet)
            elif current_section == "requirements":
                requirements.append(bullet)
            elif current_section == "benefits":
                benefits.append(bullet)

    return responsibilities, requirements, benefits


def parse_jd(raw_text: str) -> JDContext:
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

    title = None
    meta_lines = []

    for line in lines:
        if "[TITLE]" in line:
            title = line.replace("[TITLE]", "").strip()

        elif "[META]" in line:
            meta_lines.append(line.replace("[META]", "").strip())

    salary = parse_salary(raw_text)
    company = parse_company_from_title(title)

    emails = EMAIL_REGEX.findall(raw_text)

    responsibilities, requirements, benefits = parse_headings_and_sections(lines)

    context = JDContext(
        raw_text=raw_text,
        company=company,
        job=JobRoleInfo(title=title),
        salary=salary,
        responsibilities=responsibilities,
        requirements=requirements,
        benefits=benefits,
        emails=list(set(emails)),
        confidence_score=0.6  # baseline heuristic
    )

    return context