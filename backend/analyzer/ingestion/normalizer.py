import re
from typing import Optional


def normalize_job_description(text: str) -> Optional[str]:
    """
    Cleans and normalizes extracted job description text.
    Returns normalized text or None if unusable.
    """
    if not text:
        return None

    # normalize whitespace
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    # remove very short lines (noise)
    lines = [
        line.strip()
        for line in text.split("\n")
        if len(line.strip()) > 30
    ]

    if not lines:
        return None

    normalized_text = "\n".join(lines)

    # final sanity check
    if len(normalized_text) < 200:
        return None

    return normalized_text