import time

import httpx

from capstone_test.core.logging import logger

_client: httpx.Client | None = None


def get_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(timeout=30.0, follow_redirects=True)
    return _client


def get_with_retry(
    url: str,
    params: dict | None = None,
    max_retries: int = 3,
) -> httpx.Response:
    client = get_client()
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response
        except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.NetworkError) as exc:
            last_exc = exc
            if attempt < max_retries:
                wait = 2**attempt
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {exc}. "
                    f"Retrying in {wait}s"
                )
                time.sleep(wait)

    raise last_exc