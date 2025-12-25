import pytest

from analyzer.rules.urgent_language import urgent_language_rule
from analyzer.parsing.schema import JDContext, CompanyInfo, JobRoleInfo, SalaryInfo


def make_ctx(text=""):
    return JDContext(
        raw_text=text,
        company=CompanyInfo(name="TestCorp"),
        job=JobRoleInfo(title="Tester"),
        salary=SalaryInfo(),
        responsibilities=[],
        requirements=[],
        benefits=[],
        emails=[],
        confidence_score=1.0
    )


def test_detects_urgent_language():
    ctx = make_ctx("Urgent hiring! Join immediately for this role.")
    result = urgent_language_rule(ctx)

    assert result["score"] > 0
    assert "urgent" in result["reason"].lower()


def test_no_urgent_language():
    ctx = make_ctx("We are hiring a software engineer with 3 years experience.")
    result = urgent_language_rule(ctx)

    assert result["score"] == 0.0
    assert result["reason"] is None