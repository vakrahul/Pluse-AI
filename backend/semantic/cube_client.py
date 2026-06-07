"""Cube.js REST API client for semantic layer queries."""

from __future__ import annotations

from typing import Any

import httpx

from backend.utils.config import settings


class CubeClient:
    def __init__(self) -> None:
        self.base_url = settings.cubejs_api_url.rstrip("/")
        self.headers = {
            "Authorization": settings.cubejs_api_secret,
            "Content-Type": "application/json",
        }

    async def load(self, query: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/load",
                json={"query": query},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def meta(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/meta",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def sql(self, query: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/sql",
                json={"query": query},
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()


cube_client = CubeClient()
