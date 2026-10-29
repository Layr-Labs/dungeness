"""Provider-reported charges, separate from pinned benchmark token prices."""
from decimal import Decimal, InvalidOperation
import asyncio
import json
import re

import httpx

from gateway_models import decode_response_documents


def amount(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        parsed = Decimal(str(value))
        if not parsed.is_finite() or not 0 <= parsed <= 1_000_000_000:
            return None
        return float(parsed)
    except InvalidOperation:
        return None


def response_charge(body, content_type):
    """Only provider response IDs and usage fields; never agent request fields."""
    identity, cost = None, None
    for document in decode_response_documents(body, content_type):
        if not isinstance(document, dict):
            continue
        value = document.get('response', document)
        if not isinstance(value, dict):
            continue
        candidate = value.get('id')
        if isinstance(candidate, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,200}', candidate):
            if identity is not None and identity != candidate:
                return None, None
            identity = candidate
        usage = value.get('usage')
        if isinstance(usage, dict) and 'cost' in usage:
            cost = amount(usage['cost'])
    return identity, cost


async def openrouter_charge(client, body, content_type, headers, model):
    identity, cost = response_charge(body, content_type)
    if cost is not None:
        return identity, cost, 'openrouter_usage'
    if identity is None:
        return None, None, 'unavailable'
    # Fixed HTTPS destination, no forwarded agent headers or URLs. This endpoint
    # is trusted-gateway-only; the harness cannot query another run's generation.
    for attempt in range(3):
        if attempt:
            await asyncio.sleep(0.5 * attempt)
        try:
            async with client.stream('GET', 'https://openrouter.ai/api/v1/generation',
                                     params={'id': identity}, headers=headers,
                                     timeout=5.0, follow_redirects=False) as response:
                if response.status_code == 404:
                    continue
                if response.status_code != 200:
                    break
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > 65536:
                        return identity, None, 'unavailable'
                document = json.loads(raw)
                data = document.get('data') if isinstance(document, dict) else None
                if (not isinstance(data, dict) or data.get('id') != identity
                        or data.get('model') != model):
                    break
                cost = amount(data.get('total_cost'))
                if cost is not None:
                    return identity, cost, 'openrouter_generation'
        except (httpx.HTTPError, ValueError, TypeError):
            break
    return identity, None, 'unavailable'
