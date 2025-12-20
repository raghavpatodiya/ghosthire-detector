# GhostHire Detector

GhostHire Detector identifies potentially fake or scam job postings using a transparent, rule-based approach.

It analyzes job description text and flags common fraud patterns, returning both a risk score and clear reasons for why a posting may be suspicious.

---

## Current Features

- Rule-based fraud detection engine
- Detects:
  - Urgent or pressure-driven hiring language
  - Unrealistic salary claims without experience requirements
  - Use of generic email providers (e.g. Gmail)
- Produces:
  - Fraud risk score (0.0 – 1.0)
  - Human-readable reasons for each triggered rule

---

## How It Works

1. Job description text is normalized
2. Independent fraud rules are applied
3. Each rule contributes a weighted score
4. Final score is capped at `1.0`
5. Reasons are returned alongside the score

---

## Project Structure (Current)