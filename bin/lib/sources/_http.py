"""Shared HTTP helper for adapters: identifying UA, timeout, polite backoff.

Rate limiting (≤1 req/sec/host) is enforced by the caller (fetch.py), which
sequences adapters. This module just makes each individual request well-behaved.
"""
from __future__ import annotations

import time

import httpx

USER_AGENT = "annabels-jobseeker/1.0 (personal job search)"
TIMEOUT = 20.0
MAX_RETRIES = 3


def get_json(url: str, params: dict | None = None) -> dict | list:
    """GET `url`, return parsed JSON. Retries on transient errors with backoff.

    Raises httpx.HTTPStatusError on a non-retryable 4xx (except 429), or after
    exhausting retries. The caller catches this per-adapter so one broken
    endpoint does not kill the sweep.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = httpx.get(url, params=params, headers=headers, timeout=TIMEOUT)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"retryable status {resp.status_code}",
                    request=resp.request,
                    response=resp,
                )
            resp.raise_for_status()
            return resp.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # 1s, 2s
    assert last_exc is not None
    raise last_exc
