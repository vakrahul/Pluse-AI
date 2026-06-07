"""LLM client with API key rotation pool.

Keys are read from CEREBRAS_API_KEYS (comma-separated).
On a 429 RateLimitError the client instantly rotates to the next key and
tries ALL keys before giving up. After exhausting all keys it waits and
retries the full pool a second time. Any persistent failure falls back
to rule-based responses — never raises.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI, RateLimitError, APIStatusError

from backend.utils.config import settings

logger = logging.getLogger(__name__)

# ── Key pool setup ────────────────────────────────────────────────────────────

def _build_key_pool() -> list[str]:
    raw = settings.cerebras_api_keys or ""
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if not keys:
        logger.warning("No API keys found in CEREBRAS_API_KEYS — LLM disabled.")
    else:
        logger.info("LLM key pool loaded: %d key(s).", len(keys))
    return keys


_KEY_POOL: list[str] = _build_key_pool()
_POOL_SIZE: int = len(_KEY_POOL)

# Index of the currently active key — persists across requests so a
# rate-limited key stays skipped until the pool wraps around again.
_active_key_index: int = 0

# Track which keys are temporarily rate-limited (reset after full rotation)
_rate_limited: set[int] = set()


def _get_client(key_index: int) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=_KEY_POOL[key_index],
        base_url=settings.cerebras_base_url,
    )


def _next_key(current: int) -> int:
    """Return next key index, wrapping around pool size."""
    return (current + 1) % _POOL_SIZE


# ── LLMClient ─────────────────────────────────────────────────────────────────

class LLMClient:
    @property
    def available(self) -> bool:
        return _POOL_SIZE > 0

    async def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.1,
    ) -> str:
        """
        Call the LLM, trying ALL keys in the pool before giving up.

        Strategy:
          Pass 1: Try every key once, rotating instantly on 429 or 5xx.
          Pass 2: Wait 4 seconds, then try every key once more.
          If all 5 keys fail both passes → return '' (rule-based fallback).
        """
        if not self.available:
            return ""

        global _active_key_index, _rate_limited

        for pool_pass in range(2):
            tried_keys: set[int] = set()

            for attempt in range(_POOL_SIZE):
                key_idx = _active_key_index
                tried_keys.add(key_idx)
                client = _get_client(key_idx)

                logger.debug(
                    "Pass %d, attempt %d: trying key #%d",
                    pool_pass + 1, attempt + 1, key_idx + 1,
                )

                try:
                    resp = await client.chat.completions.create(
                        model=settings.cerebras_model,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        temperature=temperature,
                        max_tokens=1024,
                    )
                    content = resp.choices[0].message.content or ""
                    if content:
                        # Success — clear any rate-limit flags for this key
                        _rate_limited.discard(key_idx)
                        return content

                except RateLimitError as e:
                    logger.warning(
                        "Key #%d rate-limited (429) — rotating to next key. Error: %s",
                        key_idx + 1, str(e)[:120],
                    )
                    _rate_limited.add(key_idx)
                    # Rotate immediately — no sleep between keys
                    _active_key_index = _next_key(key_idx)

                except APIStatusError as e:
                    if e.status_code and e.status_code >= 500:
                        logger.warning(
                            "Key #%d server error %d — rotating.",
                            key_idx + 1, e.status_code,
                        )
                        _active_key_index = _next_key(key_idx)
                    else:
                        # 4xx other than 429 (bad key, wrong model, etc.)
                        logger.error(
                            "Key #%d returned %d error — skipping: %s",
                            key_idx + 1, e.status_code or 0, str(e)[:120],
                        )
                        _active_key_index = _next_key(key_idx)

                except Exception as e:
                    logger.error(
                        "Key #%d unexpected error — fallback immediately: %s",
                        key_idx + 1, str(e)[:200],
                    )
                    # Non-API errors (network, parse) — don't rotate, just fail fast
                    return ""

                # If we've tried all keys in this pass, break inner loop
                next_idx = _active_key_index
                if next_idx in tried_keys and len(tried_keys) >= _POOL_SIZE:
                    break

            # All keys tried in this pass
            if pool_pass == 0:
                wait_secs = 4
                logger.warning(
                    "All %d keys exhausted in pass 1 — waiting %ds before pass 2...",
                    _POOL_SIZE, wait_secs,
                )
                _rate_limited.clear()  # Reset rate-limit memory for second pass
                await asyncio.sleep(wait_secs)
                # Start second pass from the key AFTER the last one tried
                # (might be fresher after the wait)
                _active_key_index = _next_key(_active_key_index)

        logger.error(
            "All %d API keys failed across both passes — using rule-based fallback.",
            _POOL_SIZE,
        )
        return ""

    async def chat_json(self, system: str, user: str) -> dict[str, Any]:
        """Call LLM and parse the first JSON object from the response."""
        raw = await self.chat(system, user, temperature=0.0)
        if not raw:
            return {}
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {}


llm_client = LLMClient()
