from bs4 import BeautifulSoup
from typing import Optional


def extract_job_description(html: str) -> Optional[str]:
    """
    Extracts job description text from raw HTML.
    Returns cleaned text or None if extraction fails.
    """
    soup = BeautifulSoup(html, "html.parser")

    # remove non-content tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # common job description containers (best-effort)
    possible_containers = [
        {"id": "job-description"},
        {"class": "job-description"},
        {"class": "description"},
        {"class": "job_desc"},
        {"class": "jobDescription"},
    ]

    for selector in possible_containers:
        container = soup.find(attrs=selector)
        if container:
            text = container.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return text

    # fallback: largest text block
    paragraphs = soup.find_all("p")
    if not paragraphs:
        return None

    longest_block = ""
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > len(longest_block):
            longest_block = text

    if len(longest_block) < 200:
        return None

    return longest_block