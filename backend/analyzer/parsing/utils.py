"""
Shared parsing utilities used by detectors and JD parser.
Keep this lightweight, deterministic, and ML‑agnostic.
"""

import re
from typing import List, Tuple


def safe_lower(text: str) -> str:
    """Lowercase safely."""
    return text.lower() if isinstance(text, str) else ""


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace aggressively while preserving line meaning.
    """
    if not text:
        return ""
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def split_lines(text: str) -> List[str]:
    """Return cleaned non-empty lines."""
    if not text:
        return []
    lines = [l.strip() for l in text.split("\n")]
    return [l for l in lines if l]


def find_section_blocks(text: str, keywords: List[str]) -> List[str]:
    """
    Attempts to extract logical content blocks around headings like:
      Responsibilities / Requirements / Qualifications / Benefits etc.
    """
    if not text:
        return []

    lines = split_lines(text)
    results = []
    capture = False
    buffer = []

    for line in lines:
        lower = line.lower()

        if any(k in lower for k in keywords):
            if buffer:
                results.append("\n".join(buffer))
            buffer = []
            capture = True
            continue

        if capture:
            # Stop capturing if we hit another big obvious heading
            if re.match(r"^[A-Z][A-Za-z\s]{3,}$", line):
                capture = False
                if buffer:
                    results.append("\n".join(buffer))
                buffer = []
                continue

            buffer.append(line)

    if buffer:
        results.append("\n".join(buffer))

    return results


def extract_bullets(block: str) -> List[str]:
    """
    Extract bullet style lines:
      - bullet
      * bullet
      • bullet
    """
    if not block:
        return []

    lines = block.split("\n")
    bullets = []

    for l in lines:
        match = re.match(r"^\s*[-*•]\s+(.*)", l.strip())
        if match:
            bullets.append(match.group(1).strip())

    return bullets


def clamp_confidence(value: float) -> float:
    """
    Ensure confidence stays within 0‑1 range.
    """
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return round(value, 2)
