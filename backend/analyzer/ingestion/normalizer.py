import re
import html
from typing import Optional


def _clean_unicode(text: str) -> str:
    """
    Handles unicode oddities & HTML entities.
    """
    text = html.unescape(text)

    replacements = {
        "\u00A0": " ",   # non-breaking space
        "\u200B": "",    # zero width space
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2022": "-",   # bullet
        "\u25CF": "-",   # filled bullet
        "\u2212": "-",   # minus sign
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text


def _normalize_bullets(text: str) -> str:
    """
    Normalizes bullet formatting so parsing becomes predictable.
    Turns weird bullet formats into:
        - something
    """

    # Convert common bullet styles to dash bullets
    bullet_patterns = [
        r"•\s*", r"▪\s*", r"‣\s*", r"►\s*", r"»\s*", r"-\s*•\s*",
    ]

    for pat in bullet_patterns:
        text = re.sub(pat, "- ", text)

    return text


def _collapse_whitespace(text: str) -> str:
    """
    Structure-preserving whitespace cleanup.
    Does NOT aggressively flatten paragraphs.
    """
    text = text.replace("\r", "\n")

    # collapse 3+ newlines -> 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # collapse 2+ spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    # strip trailing spaces on each line
    text = "\n".join(line.strip() for line in text.split("\n"))

    return text.strip()


def _remove_trash_lines(text: str) -> str:
    """
    Removes obvious garbage / leftover UI crap without hurting JD meaning.
    Very conservative.
    """
    cleaned_lines = []

    trash_patterns = [
        r"^\s*$",
        r"^cookies? policy",
        r"^privacy policy",
        r"^terms and conditions",
        r"^advertisement",
        r"^subscribe",
        r"^sign up",
        r"^login",
    ]

    for line in text.split("\n"):
        lower = line.strip().lower()

        if any(re.match(p, lower) for p in trash_patterns):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def normalize_job_description(text: str) -> Optional[str]:
    """
    Production-grade normalization.

    Goals:
    - Preserve structure
    - Preserve meaning
    - Remove garbage
    - Clean unicode & bullets
    - Ensure minimum usable JD length
    """

    if not text:
        return None

    text = _clean_unicode(text)
    text = _normalize_bullets(text)
    text = _collapse_whitespace(text)
    text = _remove_trash_lines(text)

    # final sanity
    if len(text) < 200:
        return None

    return text