from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SalaryInfo:
    raw_text: Optional[str] = None
    currency: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    frequency: Optional[str] = None  # monthly / yearly / hourly


@dataclass
class CompanyInfo:
    name: Optional[str] = None
    inferred_from: Optional[str] = None  # title/meta/url/page text


@dataclass
class JobRoleInfo:
    title: Optional[str] = None
    seniority: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None  # full-time, contract etc


@dataclass
class JDContext:
    """
    Structured representation of a Job Description.
    This is what rules & insights layer will consume.
    """

    raw_text: str

    company: CompanyInfo = field(default_factory=CompanyInfo)
    job: JobRoleInfo = field(default_factory=JobRoleInfo)
    salary: SalaryInfo = field(default_factory=SalaryInfo)

    responsibilities: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)

    emails: List[str] = field(default_factory=list)
    phone_numbers: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)

    detected_language: Optional[str] = "en"

    # metadata
    confidence_score: float = 0.0