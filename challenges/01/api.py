"""
Challenge 01 — API helpers
All outbound HTTP calls live here to keep agent.py clean.
At Level 1 there are no asset URLs to fetch, but the helper is
ready for levels that do require fetching context documents.
"""

import httpx


async def fetch_asset(url: str, timeout: float = 8.0) -> str:
    """
    Fetches a single asset URL and returns its text body.
    Used by higher levels that pass context URLs in `assets`.
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_assets(urls: list[str]) -> list[str]:
    """
    Fetches multiple asset URLs concurrently and returns their text bodies
    in the same order.  Any failed URL returns an empty string so the
    agent can continue with partial context.
    """
    import asyncio

    async def _safe_fetch(url: str) -> str:
        try:
            return await fetch_asset(url)
        except Exception:
            return ""

    return await asyncio.gather(*[_safe_fetch(u) for u in urls])
