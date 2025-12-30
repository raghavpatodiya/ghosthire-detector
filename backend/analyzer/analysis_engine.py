"""
analysis_engine.py

Central Fraud Analysis Orchestrator

Now works ONLY on structured JDContext.
All rules receive the same canonical structured object.

Responsibilities of this layer:
- Validate JDContext input
- Execute rules safely
- Aggregate scores
- Combine explanations
- Provide additional NON‑fraud insights
"""

from typing import List, Dict

# ---- Rules ----
from analyzer.rules.urgent_language import urgent_language_rule
from analyzer.rules.salary_anomaly import unrealistic_salary_rule
from analyzer.rules.contact_info import poor_contact_info_rule
from analyzer.rules.missing_company_identity import missing_company_identity_rule
from analyzer.rules.hiring_process_absence import hiring_process_absence_rule
from analyzer.rules.over_promising_language import over_promising_language_rule
from analyzer.rules.suspicious_application_flow import suspicious_application_flow_rule
from analyzer.rules.role_salary_mismatch import role_salary_mismatch_rule
from analyzer.rules.generic_job_title import generic_job_title_rule
from analyzer.rules.urgency_density import urgency_density_rule
from analyzer.rules.language_inconsistency import language_inconsistency_rule
from analyzer.rules.copy_paste_jd import copy_paste_jd_rule

# ---- Schema ----
try:
    from analyzer.parsing.schema import JDContext
except Exception:
    JDContext = None

# ---- Insights (non-fraud) ----
from analyzer.insights.skill_extractor import extract_skills


def run_all_rules(jd_context) -> Dict:
    """
    Analysis Engine Entry Point

    Required:
        jd_context : JDContext

    Notes:
    - Raw text mode is intentionally removed.
    - If parsing fails, engine returns safe low‑confidence output.
    """

    # ===== Validate Structured Input =====
    if not JDContext or not isinstance(jd_context, JDContext):
        return {
            "rule_score": 0.0,
            "reasons": ["Invalid analysis input: JDContext required"],
            "insights": {
                "skills": {"skills_found": [], "skill_count": 0}
            }
        }

    raw_text = jd_context.raw_text or ""

    # ===== Rule Registry =====
    # Order generally grouped by theme to keep explanations naturally readable.
    rules = [
        # Urgency / psychological manipulation
        urgent_language_rule,
        urgency_density_rule,

        # Compensation integrity
        unrealistic_salary_rule,
        role_salary_mismatch_rule,

        # Identity / legitimacy
        missing_company_identity_rule,
        poor_contact_info_rule,

        # Job content credibility
        generic_job_title_rule,
        hiring_process_absence_rule,
        over_promising_language_rule,
        language_inconsistency_rule,

        # Behavioural / suspicious funnel
        suspicious_application_flow_rule,

        # Structural / duplicate-like patterns
        copy_paste_jd_rule,
    ]

    total_score = 0.0
    reasons: List[str] = []

    # ===== Execute Rules Safely =====
    for rule in rules:
        try:
            result = rule(jd_context)

            score = float(result.get("score", 0.0))
            reason = result.get("reason")

            total_score += score

            if reason:
                reasons.append(reason)

        except Exception:
            # A single faulty rule must never crash analysis
            continue

    # Cap score at 1.0
    total_score = round(min(total_score, 1.0), 2)

    # ===== Positive Insight Layer =====
    try:
        # Prefer structured meaningful content for skills instead of only raw text
        skill_basis_text = " ".join([
            raw_text,
            " ".join(jd_context.requirements or []),
            " ".join(jd_context.responsibilities or [])
        ])
        skills_insight = extract_skills(skill_basis_text)
    except Exception:
        skills_insight = {"skills_found": [], "skill_count": 0}

    return {
        "rule_score": total_score,
        "reasons": reasons,
        "insights": {
            "skills": skills_insight
        }
    }