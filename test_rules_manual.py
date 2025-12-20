from backend.analyzer.fraud_rules import run_all_rules

job_text = """
Urgent hiring! Join immediately.
Earn ₹80,000 per month. No experience required.
Contact us at randomcompany@gmail.com
"""

result = run_all_rules(job_text)
print(result)