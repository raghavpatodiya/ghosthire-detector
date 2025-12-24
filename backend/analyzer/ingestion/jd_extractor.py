from bs4 import BeautifulSoup
from typing import Optional


def extract_job_description(html: str) -> Optional[str]:
    """
    Extracts ALL visible readable text from HTML.
    No job-specific assumptions.
    """
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # remove non-visible / noise elements
    for tag in soup([
        "script", "style", "nav", "footer",
        "header", "aside", "noscript", "svg"
    ]):
        tag.decompose()

    body = soup.body
    if not body:
        return None

    text = body.get_text(separator="\n", strip=True)

    if not text or len(text) < 200:
        return None

    return text