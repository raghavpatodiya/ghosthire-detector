from bs4 import BeautifulSoup
from typing import Optional


NOISE_KEYWORDS = (
    "cookie", "consent", "banner", "modal",
    "popup", "subscribe", "newsletter"
)


def _is_noise_element(tag) -> bool:
    # hidden elements
    if tag.has_attr("aria-hidden") and tag["aria-hidden"] == "true":
        return True

    if tag.has_attr("style") and "display:none" in tag["style"].replace(" ", ""):
        return True

    # noisy classes / ids
    classes = " ".join(tag.get("class", [])).lower()
    element_id = (tag.get("id") or "").lower()

    return any(k in classes or k in element_id for k in NOISE_KEYWORDS)


def extract_job_description(html: str) -> Optional[str]:
    """
    Extracts readable text from HTML while preserving basic structure.
    Output is a single text blob suitable for downstream parsing.
    """
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    extracted_lines = []

    # ---- Page title (high-signal metadata) ----
    if soup.title and soup.title.string:
        extracted_lines.append(f"[TITLE] {soup.title.string.strip()}")

    # ---- Meta descriptions (optional but useful) ----
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")

        if name in ("description", "og:title", "og:description") and content:
            extracted_lines.append(f"[META] {content.strip()}")

    # ---- Remove noise elements ----
    for tag in soup([
        "script", "style", "nav", "footer",
        "header", "aside", "noscript", "svg"
    ]):
        tag.decompose()

    for tag in soup.find_all(_is_noise_element):
        tag.decompose()

    body = soup.body
    if not body:
        return None

    # ---- Preserve structure ----
    for element in body.descendants:
        if not hasattr(element, "name"):
            continue

        if element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            text = element.get_text(strip=True)
            if text:
                extracted_lines.append(f"[{element.name.upper()}] {text}")

        elif element.name == "li":
            text = element.get_text(strip=True)
            if text:
                extracted_lines.append(f"- {text}")

        elif element.name in ("p", "span", "div"):
            text = element.get_text(strip=True)
            if text and len(text) > 30:
                extracted_lines.append(text)

    # ---- Deduplicate while preserving order ----
    seen = set()
    unique_lines = []
    for line in extracted_lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    combined_text = "\n".join(unique_lines)

    if len(combined_text) < 300:
        return None

    return combined_text