import requests


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_url_content(url: str, timeout: int = 10) -> str:
    """
    Fetch raw HTML content from a job posting URL.
    Returns HTML as string.
    Raises Exception on failure.
    """
    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True,
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")

    if response.status_code != 200:
        raise Exception(f"Non-200 status code received: {response.status_code}")

    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        raise Exception("URL did not return HTML content")

    return response.text