import re
from typing import Dict, List, Set


# Canonical skill → aliases
SKILL_MAP = {
    # languages
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "c++": ["c++"],
    "c#": ["c#", "c sharp"],
    "go": ["go", "golang"],
    "rust": ["rust"],

    # frameworks / libs
    "react": ["react", "reactjs"],
    "angular": ["angular", "angularjs"],
    "vue": ["vue", "vuejs"],
    "spring": ["spring"],
    "spring boot": ["spring boot"],
    "django": ["django"],
    "flask": ["flask"],
    "node": ["node", "nodejs"],
    "express": ["express"],

    # data / backend
    "sql": ["sql"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "kafka": ["kafka"],

    # cloud / devops
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "ci/cd": ["ci/cd", "ci cd", "continuous integration"],

    # testing / tools
    "selenium": ["selenium"],
    "jmeter": ["jmeter"],
    "pytest": ["pytest"],
    "junit": ["junit"],

    # architecture / misc
    "rest": ["rest", "restful"],
    "microservices": ["microservices", "microservice"],
    "linux": ["linux"],
    "git": ["git"]
}


def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#/ ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return f" {text} "


def extract_skills(job_text: str) -> Dict:
    """
    Extracts skills and technologies from a job description.
    Deterministic, alias-aware, and false-positive resistant.
    """
    if not job_text:
        return {"skills_found": [], "skill_count": 0}

    text = _normalize_text(job_text)
    found: Set[str] = set()

    for canonical_skill, aliases in SKILL_MAP.items():
        for alias in aliases:
            pattern = f" {re.escape(alias)} "
            if pattern in text:
                found.add(canonical_skill)
                break

    return {
        "skills_found": sorted(found),
        "skill_count": len(found)
    }