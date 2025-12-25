import pytest

from analyzer.rules.contact_info import poor_contact_info_rule as contact_info_rule
from analyzer.parsing.schema import JDContext, CompanyInfo, JobRoleInfo, SalaryInfo


def make_ctx(text="", emails=None):
    return JDContext(
        raw_text=text,
        company=CompanyInfo(name="TestCorp"),
        job=JobRoleInfo(title="Tester"),
        salary=SalaryInfo(),
        responsibilities=[],
        requirements=[],
        benefits=[],
        emails=emails or [],
        confidence_score=1.0
    )


def test_flags_gmail_contact():
    ctx = make_ctx(
        text="Contact us at hiringteam@gmail.com",
        emails=["hiringteam@gmail.com"]
    )

    result = contact_info_rule(ctx)

    assert result["score"] > 0
    assert "email" in result["reason"].lower()


def test_flags_yahoo_outlook_generic_domains():
    ctx = make_ctx(
        text="Reach us at fakehr@yahoo.com",
        emails=["fakehr@yahoo.com"]
    )

    result = contact_info_rule(ctx)

    assert result["score"] > 0


def test_company_domain_should_not_flag():
    ctx = make_ctx(
    text="Contact hr@testcorp.com",
    emails=["hr@testcorp.com"]
)

    result = contact_info_rule(ctx)

    assert result["score"] == 0.0
    assert result["reason"] is None


def test_no_email_returns_safe():
    ctx = make_ctx(text="No email here")

    result = contact_info_rule(ctx)

    assert result["score"] == 0.4


def test_multiple_emails_only_flags_if_any_are_generic():
    ctx = make_ctx(
        emails=["hr@company.com", "fraud@gmail.com"]
    )

    result = contact_info_rule(ctx)

    assert result["score"] > 0