

import requests

from config import HEADERS, HTTP_TIMEOUT_SECONDS


def request_json(url: str, params: dict) -> dict:
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=HTTP_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
