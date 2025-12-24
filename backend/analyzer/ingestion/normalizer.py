import re
from typing import Optional


def normalize_job_description(text: str) -> Optional[str]:
    """
    Light normalization only.
    Does NOT remove content aggressively.
    """
    if not text:
        return None

    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    text = text.strip()

    if len(text) < 200:
        return None

    return text