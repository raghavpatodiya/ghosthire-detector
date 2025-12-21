"""
fraud_rules.py

Orchestrates all fraud detection rules.
Each rule is isolated and fault-tolerant.
"""

from typing import List, Dict

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


def run_all_rules(job_text: str) -> Dict:
    rules = [
        # urgency & pressure
        urgent_language_rule,
        urgency_density_rule,

        # compensation anomalies
        unrealistic_salary_rule,
        role_salary_mismatch_rule,

        # identity & contact
        missing_company_identity_rule,
        poor_contact_info_rule,

        # content & structure
        generic_job_title_rule,
        hiring_process_absence_rule,
        over_promising_language_rule,
        language_inconsistency_rule,

        # behavior / flow
        suspicious_application_flow_rule,

        # advanced (may be stubbed initially)
        copy_paste_jd_rule,
    ]

    total_score = 0.0
    reasons: List[str] = []

    for rule in rules:
        try:
            result = rule(job_text)
            total_score += result.get("score", 0.0)

            if result.get("reason"):
                reasons.append(result["reason"])

        except Exception:
            # one rule failing must not break the system
            continue

    return {
        "rule_score": round(min(total_score, 1.0), 2),
        "reasons": reasons
    }