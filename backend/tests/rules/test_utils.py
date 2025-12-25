

from analyzer.parsing.schema import JDContext, CompanyInfo, JobRoleInfo, SalaryInfo


def make_context(
    text: str = "",
    title: str = "Test Role",
    company: str = "TestCorp",
    salary_text: str = None,
    emails=None,
    responsibilities=None,
    requirements=None,
    benefits=None,
    confidence: float = 1.0,
):
    """
    Unified JDContext builder for all rule tests.
    Keeps tests clean and avoids duplication.
    """

    return JDContext(
        raw_text=text or "",
        company=CompanyInfo(name=company),
        job=JobRoleInfo(title=title),
        salary=SalaryInfo(raw_text=salary_text),
        responsibilities=responsibilities or [],
        requirements=requirements or [],
        benefits=benefits or [],
        emails=emails or [],
        confidence_score=confidence,
    )