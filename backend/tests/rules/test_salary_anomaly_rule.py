import pytest

from analyzer.rules.salary_anomaly import unrealistic_salary_rule as salary_anomaly_rule
from analyzer.parsing.schema import JDContext, CompanyInfo, JobRoleInfo, SalaryInfo


def make_ctx(text="", salary_text=None):
    return JDContext(
        raw_text=text,
        company=CompanyInfo(name="TestCorp"),
        job=JobRoleInfo(title="Software Engineer"),
        salary=SalaryInfo(raw_text=salary_text),
        responsibilities=[],
        requirements=[],
        benefits=[],
        emails=[],
        confidence_score=1.0
    )


def test_flags_unrealistic_salary_without_experience():
    jd = """
    Earn ₹120000 per month.
    No experience required.
    """
    ctx = make_ctx(text=jd, salary_text="₹120000 per month")
    result = salary_anomaly_rule(ctx)

    assert result["score"] > 0
    assert "salary" in result["reason"].lower()


def test_does_not_flag_reasonable_salary():
    jd = "Salary ₹50000 per month with 3 years experience required"
    ctx = make_ctx(text=jd, salary_text="₹50000 per month")
    result = salary_anomaly_rule(ctx)

    assert result["score"] == 0.0
    assert result["reason"] is None


def test_handles_missing_salary_gracefully():
    ctx = make_ctx(text="We pay well")
    result = salary_anomaly_rule(ctx)

    assert result["score"] == 0.0


def test_high_salary_with_experience_should_not_flag():
    jd = """
    Salary ₹120000 per month.
    Requires 7+ years experience.
    """
    ctx = make_ctx(text=jd, salary_text="₹120000 per month")
    result = salary_anomaly_rule(ctx)

    assert result["score"] == 0.0
