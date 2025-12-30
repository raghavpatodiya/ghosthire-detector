"""
jd_extractor.py

Responsible for extracting a meaningful, structured textual job description
from raw HTML. This module aims to be resilient across different job portals,
company career pages, and generic web pages.

Goals:
- Portal-aware extraction (LinkedIn / Indeed / Naukri / others)
- Preserve important structure (titles, sections, bullets)
- Aggressively remove noise (ads, cookie banners, UI chrome)
- Never silently return garbage: predictable failure cases
"""

from bs4 import BeautifulSoup
from typing import Optional, List


# --- Noise detection keywords ---
NOISE_KEYWORDS = (
    "cookie", "consent", "banner", "modal",
    "popup", "subscribe", "newsletter",
    "tracking", "advert", "promo"
)


def _is_noise_element(tag) -> bool:
    if not tag:
        return False

    # Hidden elements
    if tag.has_attr("aria-hidden") and tag["aria-hidden"] == "true":
        return True

    if tag.has_attr("style") and "display:none" in tag["style"].replace(" ", ""):
        return True

    # Noisy classes / ids
    classes = " ".join(tag.get("class", [])).lower()
    element_id = (tag.get("id") or "").lower()

    return any(k in classes or k in element_id for k in NOISE_KEYWORDS)


def _detect_source(soup: BeautifulSoup) -> str:
    """
    Best-effort source detection.
    This helps us choose extraction strategies.
    """

    html_text = soup.get_text(" ", strip=True).lower()

    if "linkedin" in html_text or "jobs-details" in html_text:
        return "linkedin"

    if "indeed" in html_text or "jobDescriptionText" in html_text:
        return "indeed"

    if "naukri" in html_text or "naukri.com" in html_text:
        return "naukri"

    if "wellfound" in html_text or "angel.co" in html_text:
        return "wellfound"

    return "generic"


def _extract_from_known_portal(soup: BeautifulSoup, source: str) -> Optional[str]:
    """
    Portal-specific extraction rules.
    Returns None if portal structure not found.
    """

    candidates: List[str] = []

    if source == "linkedin":
        selectors = [
            {"class": "jobs-description"},
            {"class": "jobs-box__html-content"},
            {"class": "show-more-less-html__markup"},
        ]
        candidates = _extract_by_selectors(soup, selectors)

    elif source == "indeed":
        selectors = [
            {"id": "jobDescriptionText"},
            {"class": "jobsearch-jobDescriptionText"},
        ]
        candidates = _extract_by_selectors(soup, selectors)

    elif source == "naukri":
        selectors = [
            {"class": "job-desc"},
            {"class": "jd-container"},
            {"class": "description"},
        ]
        candidates = _extract_by_selectors(soup, selectors)

    elif source == "wellfound":
        selectors = [
            {"class": "job-description"},
            {"class": "styles__Description"},
        ]
        candidates = _extract_by_selectors(soup, selectors)

    if candidates:
        combined = "\n".join(candidates)
        return combined if len(combined) > 250 else None

    return None


def _extract_by_selectors(soup: BeautifulSoup, selectors: List[dict]) -> List[str]:
    collected = []

    for selector in selectors:
        section = soup.find(attrs=selector)
        if not section:
            continue

        text = section.get_text("\n", strip=True)
        if text and len(text) > 200:
            collected.append(text)

    return collected


def _fallback_largest_block(soup: BeautifulSoup) -> Optional[str]:
    """
    Fallback when no structured block is found.
    Finds the largest meaningful textual region.
    """

    body = soup.body
    if not body:
        return None

    # gather paragraph-like elements
    blocks = []
    for tag in body.find_all(["p", "div", "section"]):
        if _is_noise_element(tag):
            continue

        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        # basic sanity: should look like real language, not random UI
        if len(text) > 120 and (" " in text):
            blocks.append(text)

    if not blocks:
        return None

    largest = max(blocks, key=len)

    return largest if len(largest) > 200 else None


def extract_job_description(html: str) -> Optional[str]:
    """
    Extracts readable job description text from HTML while preserving basic structure.
    Output is a structured text blob suitable for downstream parsing.

    Returns:
        str  -> extracted JD text
        None -> extraction failed
    """

    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    extracted_lines = []

    # ---- Page title (high-signal metadata) ----
    if soup.title and soup.title.string:
        extracted_lines.append(f"[TITLE] {soup.title.string.strip()}")

    # ---- Meta descriptions ----
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")

        if name in ("description", "og:title", "og:description") and content:
            extracted_lines.append(f"[META] {content.strip()}")

    # ---- Remove obvious noise ----
    for tag in soup([
        "script", "style", "nav", "footer",
        "header", "aside", "noscript", "svg"
    ]):
        tag.decompose()

    for tag in soup.find_all(_is_noise_element):
        tag.decompose()

    # ---- Portal-aware extraction ----
    source = _detect_source(soup)
    portal_text = _extract_from_known_portal(soup, source)

    if portal_text:
        extracted_lines.append(portal_text)
    else:
        fallback = _fallback_largest_block(soup)
        if fallback:
            extracted_lines.append(fallback)

    # ---- Final assembly ----
    combined = "\n".join(extracted_lines).strip()

    if len(combined) < 250:
        return None

    return combined