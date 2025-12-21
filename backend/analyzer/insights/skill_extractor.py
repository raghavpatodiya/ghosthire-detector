import re
from typing import Dict, List


COMMON_SKILLS = [
    # languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",

    # frameworks / libs
    "react", "angular", "vue", "spring", "spring boot", "django", "flask",
    "node", "express",

    # data / backend
    "sql", "postgresql", "mysql", "mongodb", "redis", "kafka",

    # cloud / devops
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins",

    # testing / tools
    "selenium", "jmeter", "pytest", "junit",

    # misc
    "rest", "microservices", "linux", "git"
]


def extract_skills(job_text: str) -> Dict:
    """
    Extracts required skills/keywords from a job description.
    This is a positive insight feature (no scoring).
    """
    text = job_text.lower()
    found_skills: List[str] = []

    for skill in COMMON_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text):
            found_skills.append(skill)

    return {
        "skills_found": sorted(set(found_skills)),
        "skill_count": len(set(found_skills))
    }