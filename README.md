# GhostHire Detector

GhostHire Detector is a backend-driven system for analyzing job postings and identifying potential fraud patterns using a deterministic, rule-based engine. It exposes a RESTful Flask API and a lightweight React client for interaction and visualization.

The system prioritizes:
- Explainability over black-box scoring
- Fault isolation across rules
- Clear separation of ingestion, analysis, and presentation
- Automated testability

---

## System Architecture

```
Client (React)
  ↓
API Layer (Flask)
  ↓
Ingestion Pipeline (optional)
  ↓
Analysis Engine
  ├── Fraud Rules
  └── Insights
```

The backend is the source of truth.  
The frontend is a stateless consumer of API responses.

---

## Functional Overview

### Fraud Analysis
- Rule-based scoring system (0.0 – 1.0)
- Independent, failure-tolerant rules
- Deterministic and explainable outputs

Implemented fraud signals:
- Urgent / pressure-driven language
- Salary anomalies
- Generic contact information
- Missing or vague company identity
- Over-promising language
- Suspicious application flow
- Generic job titles
- Role–salary mismatch
- Linguistic inconsistency
- Reused / copy-pasted job descriptions
- Missing hiring process details
- Urgency density anomalies

---

### Insights (Non-Scoring)
- Skill and keyword extraction from job descriptions
- Returned as structured metadata
- Does not influence fraud score

---

### Supported Inputs
- Raw job description text
- Job posting URL (server-side ingestion)

---

## Backend Layout

```
backend/
├── app.py                     # API entry point
├── analyzer/
│   ├── analysis_engine.py     # Orchestrates rules and insights
│   ├── rules/                 # Individual fraud rules
│   ├── insights/              # Non-fraud signal extractors
│   └── ingestion/             # URL → text pipeline
│       ├── url_fetcher.py
│       ├── jd_extractor.py
│       └── normalizer.py
├── tests/                     # pytest-based test suite
│   ├── rules/
│   ├── ingestion/
│   ├── insights/
│   └── test_analysis_engine.py
├── requirements.txt
└── pytest.ini
```

---

## Frontend Layout

```
frontend/ghosthire-ui/
├── src/
│   ├── components/
│   │   ├── LandingOptions.js
│   │   ├── JDTextInput.js
│   │   └── JDUrlInput.js
│   ├── App.js
│   ├── App.css
│   └── index.js
└── package.json
```

---

## API Specification

### POST `/analyze`

#### Request (text input)
```json
{
  "job_text": "Job description content"
}
```

#### Request (URL input)
```json
{
  "job_url": "https://example.com/job-posting"
}
```

#### Response
```json
{
  "rule_score": 0.8,
  "reasons": [
    "Urgent call-to-action language detected",
    "Generic email contact used instead of company domain"
  ],
  "insights": {
    "skills": {
      "skills_found": ["python", "react"],
      "skill_count": 2
    }
  }
}
```

---

## Local Development

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Runs on:
```
http://127.0.0.1:5000
```

---

### Frontend
```bash
cd frontend/ghosthire-ui
npm install
npm start
```

Runs on:
```
http://localhost:3000
```

---

## Testing

All backend logic is covered via automated tests.

```bash
cd backend
pytest
```

With coverage:
```bash
pytest --cov=analyzer --cov-report=term-missing
```

---

## Design Constraints

- No scraping logic in the frontend
- No rule inter-dependencies
- Analysis engine operates only on normalized text
- Ingestion failures do not affect analysis stability
- UI changes must not require backend refactors

---

## Roadmap

- Domain-specific JD extractors
- Context-aware semantic rules
- Embedding-based similarity detection
- PDF and document ingestion
- Rule confidence weighting and calibration

---

## Owner

Raghav Patodiya