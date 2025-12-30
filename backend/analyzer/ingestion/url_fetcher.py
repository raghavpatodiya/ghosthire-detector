"""
url_fetcher.py

Responsible for safely and reliably fetching raw HTML content
from external job posting URLs.

Goals:
- Network reliability (retries, timeout)
- Security (no file:// etc, only http/https)
- Validation (must return meaningful HTML)
- Helpful failure reasons (not vague errors)
"""

import re
import requests
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


CAPTCHA_KEYWORDS = [
    "captcha",
    "robot check",
    "verify you are human",
    "cloudflare",
    "are you a robot",
]


def _is_html_response(response: requests.Response) -> bool:
    content_type = response.headers.get("Content-Type", "").lower()
    return "text/html" in content_type or "application/xhtml" in content_type


def _looks_like_captcha(html: str) -> bool:
    if not html:
        return False
    lower = html.lower()
    return any(word in lower for word in CAPTCHA_KEYWORDS)


def _validate_url(url: str):
    if not url:
        raise Exception("URL is empty")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise Exception("Only http/https URLs are allowed")

    if not parsed.netloc:
        raise Exception("Invalid URL provided")


def _build_session():
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def fetch_url_content(url: str, timeout: int = 10):
    """
    Fetch raw HTML content from a URL in a robust, production-safe way.

    Returns dict:
    {
        "success": bool,
        "status_code": int | None,
        "html": str | None,
        "reason": str | None,
    }
    """

    _validate_url(url)

    session = _build_session()

    try:
        response = session.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=(5, timeout),  # connect timeout, read timeout
            allow_redirects=True,
        )
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status_code": None,
            "html": None,
            "reason": "network_timeout",
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "status_code": None,
            "html": None,
            "reason": f"network_error: {str(e)}",
        }

    status = response.status_code

    if status >= 400:
        return {
            "success": False,
            "status_code": status,
            "html": None,
            "reason": f"http_error_{status}",
        }

    if not _is_html_response(response):
        return {
            "success": False,
            "status_code": status,
            "html": None,
            "reason": "non_html_content",
        }

    html = response.text or ""

    # Hard fail if suspiciously tiny
    if len(html.strip()) < 200:
        return {
            "success": False,
            "status_code": status,
            "html": html,
            "reason": "empty_or_too_small",
        }

    # Detect captcha / bot challenges
    if _looks_like_captcha(html):
        return {
            "success": False,
            "status_code": status,
            "html": html,
            "reason": "blocked_by_site_captcha",
        }

    # Safety: large pages truncated (protect memory)
    if len(html) > 2_000_000:  # 2MB
        html = html[:2_000_000]

    return {
        "success": True,
        "status_code": status,
        "html": html,
        "reason": None,
    }