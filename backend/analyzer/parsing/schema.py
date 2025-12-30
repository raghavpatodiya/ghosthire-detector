from dataclasses import dataclass, field
from typing import List, Optional


# ---------------- Salary ----------------
@dataclass
class SalaryInfo:
    raw_text: Optional[str] = None
    currency: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    frequency: Optional[str] = None  # monthly / yearly / hourly
    confidence: float = 0.0


# ---------------- Company ----------------
@dataclass
class CompanyInfo:
    name: Optional[str] = None
    inferred_from: Optional[str] = None  # title/meta/url/page text
    confidence: float = 0.0


# ---------------- Job Role ----------------
@dataclass
class JobRoleInfo:
    title: Optional[str] = None
    seniority: Optional[str] = None

    location: Optional[str] = None
    location_confidence: float = 0.0

    employment_type: Optional[str] = None  # full-time, contract etc
    employment_confidence: float = 0.0

    years_experience: Optional[int] = None
    experience_confidence: float = 0.0

    remote_mode: Optional[str] = None  # remote / hybrid / onsite
    remote_confidence: float = 0.0


# ---------------- Hiring Flow ----------------
@dataclass
class HiringFlowInfo:
    steps: List[str] = field(default_factory=list)
    mentions_interview: bool = False
    confidence: float = 0.0


# ---------------- JD Context Root ----------------
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

    hiring_flow: HiringFlowInfo = field(default_factory=HiringFlowInfo)

    detected_language: Optional[str] = "en"

    # overall metadata
    confidence_score: float = 0.0