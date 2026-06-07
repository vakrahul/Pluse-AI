"""Neo4j graph database client."""

from __future__ import annotations

from typing import Any

from neo4j import AsyncGraphDatabase

from backend.utils.config import settings


class Neo4jClient:
    def __init__(self) -> None:
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return self._driver

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def run(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict]:
        driver = self._get_driver()
        async with driver.session() as session:
            result = await session.run(cypher, params or {})
            records = await result.data()
            return records

    async def health(self) -> bool:
        try:
            records = await self.run("RETURN 1 AS ok")
            return bool(records)
        except Exception:
            return False


neo4j_client = Neo4jClient()
