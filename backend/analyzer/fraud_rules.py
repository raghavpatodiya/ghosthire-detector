"""
fraud_rules.py

Orchestrates all fraud detection rules.
Each rule is isolated and fault-tolerant.
"""

from typing import List, Dict

from analyzer.rules.urgent_language import urgent_language_rule
from analyzer.rules.salary_anomaly import unrealistic_salary_rule
from analyzer.rules.contact_info import poor_contact_info_rule


def run_all_rules(job_text: str) -> Dict:
    rules = [
        urgent_language_rule,
        unrealistic_salary_rule,
        poor_contact_info_rule,
    ]

    total_score = 0.0
    reasons: List[str] = []

    for rule in rules:
        try:
            result = rule(job_text)
            total_score += result.get("score", 0.0)

            if result.get("reason"):
                reasons.append(result["reason"])

        except Exception as e:
            # rule failure should never break the system
            continue

    return {
        "rule_score": round(min(total_score, 1.0), 2),
        "reasons": reasons
    }