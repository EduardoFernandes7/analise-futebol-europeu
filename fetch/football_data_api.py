import time

import requests

from fetch.config import API_BASE_URL, API_KEY

# Tier gratuito: 10 requisições/minuto. 7s de intervalo mantém uma margem segura.
REQUEST_INTERVAL_SECONDS = 7

_session = requests.Session()
_session.headers.update({"X-Auth-Token": API_KEY})
_last_request_at = 0.0


def _get(path: str, params: dict | None = None) -> dict:
    global _last_request_at

    elapsed = time.monotonic() - _last_request_at
    if elapsed < REQUEST_INTERVAL_SECONDS:
        time.sleep(REQUEST_INTERVAL_SECONDS - elapsed)

    response = _session.get(f"{API_BASE_URL}{path}", params=params)
    _last_request_at = time.monotonic()

    if response.status_code == 429:
        # Estourou o rate limit mesmo com o intervalo — espera um pouco mais e tenta de novo.
        time.sleep(60)
        response = _session.get(f"{API_BASE_URL}{path}", params=params)
        _last_request_at = time.monotonic()

    response.raise_for_status()
    return response.json()


def get_matches(competition_code: str, season: int) -> dict:
    return _get(f"/competitions/{competition_code}/matches", params={"season": season})


def get_standings(competition_code: str, season: int) -> dict:
    return _get(f"/competitions/{competition_code}/standings", params={"season": season})
