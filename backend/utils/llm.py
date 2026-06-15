"""LLM client for Gemini API using OpenAI compatibility.

This client uses the single Gemini API key provided by the user.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI
from backend.utils.config import settings

logger = logging.getLogger(__name__)

# ── LLMClient ─────────────────────────────────────────────────────────────────

class LLMClient:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if not self.api_key:
            logger.warning("No API key found in GEMINI_API_KEY — LLM disabled.")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key or "disabled",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.1,
    ) -> str:
        """Call the Gemini LLM."""
        if not self.available:
            return ""

        try:
            resp = await self.client.chat.completions.create(
                model=settings.gemini_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=2048,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.error("LLM Error: %s", str(e)[:200])
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
