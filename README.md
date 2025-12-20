# GhostHire Detector

GhostHire Detector identifies potentially fake or scam job postings using a transparent, rule-based analysis engine.

It exposes a lightweight **Flask API** consumed by a **React UI**, keeping fraud logic and interface cleanly separated.

---

## Current Features

- Rule-based job fraud detection engine
- Detects:
  - Urgent or pressure-driven hiring language
  - Unrealistic salary claims without experience requirements
  - Use of generic email providers (e.g. Gmail)
- Returns:
  - Fraud risk score (0.0 – 1.0)
  - Human-readable reasons explaining the score
- Simple React UI to analyze job descriptions

---

## Architecture