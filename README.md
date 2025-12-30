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
Ingestion Layer (optional: URL → HTML → Text)
  ↓
Parsing Layer (raw JD → JDContext)
  ↓
Analysis Engine
  ├── Fraud Rules (JDContext-only)
  └── Insights
```

The backend is the source of truth.  
The frontend is a stateless consumer of API responses.

The backend processes ALL job descriptions into a structured JDContext before analysis. No rule runs on raw text anymore.

---

## Functional Overview

### Fraud Analysis
- Rule-based scoring system (0.0 – 1.0)
- Independent, failure-tolerant rules
- Deterministic and explainable outputs

Implemented fraud signals (via JDContext structured analysis):
- Urgent / pressure-driven hiring signals
- Urgency density anomalies
- Unrealistic salary or salary–experience mismatch
- Role–salary inconsistency
- Missing or vague company identity
- Generic / suspicious contact channels
- Over-promising language & guaranteed placement claims
- Suspicious / shortcut hiring process
- Generic or scam-pattern job titles
- Linguistic inconsistency & tone anomalies
- Reused / duplicated / template job descriptions

---

### Insights (Non-Scoring)
Structured insights are extracted independently of fraud scoring. Currently implemented:
- Skill / technology extraction
Returned as structured metadata and does not influence fraud risk score.

---

### Supported Inputs
- Raw job description text (pasted by user)
- Public job posting URL (server ingestion → scrape → extract → normalize → parse)

---

## Ingestion Layer (Enhanced)

The ingestion pipeline has been upgraded to behave closer to real-world production systems.

**Responsibilities**
- Fetch trusted HTML from public job URLs
- Apply realistic headers & redirects
- Validate content-type & encoding
- Extract readable job content
- Normalize and clean text
- Fail gracefully without crashing the pipeline

**Pipeline**
```
URL → fetch_url_content()  
       ↓  
HTML → extract_job_description()  
       ↓  
Text → normalize_job_description()  
       ↓  
debug/raw_jd.txt (captured for inspection)
```

Scraping never lives in frontend.  
Failures return clear API errors instead of breaking analysis.

---

## Parsing Layer (Structured JDContext)

All analysis is now **fully structured**.  
No fraud rule consumes raw text anymore — everything runs on parsed semantics.

**The parser now extracts:**
- 📍 Location + Remote / Hybrid / On‑site
- 🧠 Experience years (min / max where available)
- 💼 Employment type (Full‑time / Contract / Internship)
- 🏁 Hiring process structure (steps, interviews, shortcuts)
- 💸 Salary structure (amount, range, currency, frequency)
- 🏢 Company inference heuristics
- 📧 Verifiable emails
- Confidence scores per attribute
- Overall parsing confidence baseline

**Architecture**
```
Raw JD Text
 ↓
Parsing Detectors
 ↓
JDContext (structured representation)
 ↓
Fraud Rules + Insights
```

This significantly improves:
- Accuracy
- Explainability
- Real‑world reliability
- Extensibility (future ML & domain‑specific extractors)

---

## Backend Layout

```
backend/
├── app.py                     # API entry point
├── analyzer/
│   ├── analysis_engine.py     # Orchestrates rules + insights (JDContext only)
│   ├── rules/                 # Individual fraud rules (fault-tolerant)
│   ├── insights/              # Non-fraud analysis
│   ├── ingestion/             # URL → HTML → JD text
│   │   ├── url_fetcher.py
│   │   ├── jd_extractor.py
│   │   └── normalizer.py
│   └── parsing/
│       ├── jd_parser.py           # Converts text → JDContext
│       ├── schema.py              # JDContext + structured models
│       ├── detectors/             # Individual semantic extractors
│       │   ├── experience_detector.py
│       │   ├── location_detector.py
│       │   ├── employment_type_detector.py
│       │   ├── hiring_flow_detector.py
│       │   └── salary_detector.py
│       └── utils.py                 # shared parsing helpers
├── debug/
│   └── raw_jd.txt             # Temporary captured JD for inspection
├── utils/
│   └── loc_counter.py         # LOC calculation (backend + frontend)
├── tests/
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

Note:
All analysis now runs on JDContext (structured representation). Even pasted text is normalized and parsed before scoring.

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

Backend functionality is validated using pytest with coverage support, including ingestion, parsing, and analysis engine layers.

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

- No scraping logic in frontend
- Rules do not depend on each other
- Analysis engine operates ONLY on JDContext (not raw strings)
- Ingestion failures never crash analysis
- Rule failures never crash the engine
- Frontend remains a stateless consumer

---

## Roadmap

- Advanced parsing heuristics & ML-assisted extraction
- Domain-specific JD extractors (LinkedIn, Indeed, Naukri, etc.)
- Context-aware semantic fraud rules
- Embedding-based copy/paste similarity detection
- PDF & document ingestion pipeline
- Confidence calibration across rules

---

## Owner

Raghav Patodiya