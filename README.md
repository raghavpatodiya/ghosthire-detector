# ghosthire-detector

ghosthire-detector/
│
├── data/
│   ├── raw/                # Scraped job posts
│   ├── processed/          # Cleaned & feature-ready data
│   └── samples/            # Safe demo datasets
│
├── scraper/
│   ├── __init__.py
│   ├── job_scraper.py
│   └── validators.py
│
├── analyzer/
│   ├── __init__.py
│   ├── text_features.py    # NLP features
│   ├── fraud_rules.py      # Heuristic rules
│   ├── ml_model.py         # ML-based scoring
│   └── scorer.py           # Final risk score
│
├── api/
│   ├── main.py             # FastAPI app
│   └── schemas.py
│
├── tests/
│   ├── test_rules.py
│   ├── test_scorer.py
│
├── notebooks/
│   └── exploration.ipynb   # Feature research
│
├── .gitignore
├── requirements.txt
├── README.md
└── LICENSE