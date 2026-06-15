"""SQL/Cube agent — Payer360 analytics via Cube.js."""

from __future__ import annotations

import json
import logging
import re

from backend.agents.state import AgentState
from backend.prompts.payer360_schema import PAYER360_CUBE_SCHEMA
from backend.semantic.cube_client import cube_client
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

KNOWN_CUBES = ("McoProfile.", "Formulary.", "McoHierarchy.")


def _keyword_fallback(question: str, entities: dict) -> dict:
    """Rule-based Cube query builder using only verified Payer360 measures/dimensions."""
    q = question.lower()
    brand = entities.get("brand")
    mco_name = entities.get("mco_name")
    bob = entities.get("book_of_business")
    limit = entities.get("limit", 10)

    # Formulary / access position / HPM
    if any(k in q for k in ["formulary", "coverage", "hpm", "access position", "preferred", "pa required"]):
        filters = []
        if brand:
            filters.append({"member": "Formulary.productBrandName", "operator": "equals", "values": [brand]})
        if mco_name:
            filters.append({"member": "Formulary.mcoName", "operator": "contains", "values": [mco_name]})
        if bob:
            filters.append({"member": "Formulary.bookOfBusiness", "operator": "equals", "values": [bob]})
        return {
            "measures": ["Formulary.count"],
            "dimensions": ["Formulary.mcoName", "Formulary.productBrandName",
                           "Formulary.hpmValue", "Formulary.accessPosition"],
            "filters": filters,
            "order": {"Formulary.mcoName": "asc"},
            "limit": limit,
        }

    # Access position comparison
    if "market share" in q or "access position" in q:
        filters = []
        if brand:
            filters.append({"member": "Formulary.productBrandName", "operator": "equals", "values": [brand]})
        return {
            "measures": ["Formulary.advantageCount", "Formulary.parityCount", "Formulary.disadvantageCount"],
            "dimensions": ["Formulary.productBrandName"],
            "filters": filters,
            "order": {"Formulary.advantageCount": "desc"},
            "limit": limit,
        }

    # MCO counts / book of business
    if any(k in q for k in ["how many mco", "mco count", "list mco", "show mco", "book of business"]):
        filters = []
        if bob:
            filters.append({"member": "McoProfile.bookOfBusiness", "operator": "equals", "values": [bob]})
        return {
            "measures": ["McoProfile.count"],
            "dimensions": ["McoProfile.bookOfBusiness", "McoProfile.mcoCategory"],
            "filters": filters,
            "order": {"McoProfile.count": "desc"},
        }

    # Default: formulary overview
    return {
        "measures": ["Formulary.count", "Formulary.advantageCount"],
        "dimensions": ["Formulary.productBrandName", "Formulary.accessPosition"],
        "order": {"Formulary.count": "desc"},
        "limit": limit,
    }


def _validate_query(q: dict) -> bool:
    if not isinstance(q, dict):
        return False
    measures = q.get("measures", [])
    if not measures:
        return False
    return all(any(m.startswith(c) for c in KNOWN_CUBES) for m in measures if isinstance(m, str))


async def sql_node(state: AgentState) -> AgentState:
    question = state["question"]
    entities = state.get("entities", {})
    cube_query: dict = {}

    # 1. LLM-powered query generation
    if llm_client.available:
        try:
            user_prompt = (
                f"User question: {question}\n"
                f"Extracted entities: {json.dumps(entities)}\n\n"
                "Build the Cube.js JSON query using ONLY the verified measures and dimensions above."
            )
            raw = await llm_client.chat(PAYER360_CUBE_SCHEMA, user_prompt, temperature=0.0)
            if raw:
                match = re.search(r"\{[\s\S]*\}", raw)
                if match:
                    candidate = json.loads(match.group())
                    if _validate_query(candidate):
                        cube_query = candidate
                        logger.info("LLM built Payer360 Cube query: %s", cube_query)
        except Exception as e:
            logger.warning("LLM Cube query builder failed, using keyword fallback: %s", e)

    # 2. Keyword fallback
    if not cube_query:
        cube_query = _keyword_fallback(question, entities)
        logger.info("Keyword fallback Cube query: %s", cube_query)

    # 3. Execute against Cube
    results: list[dict] = []
    try:
        resp = await cube_client.load(cube_query)
        results = resp.get("data", [])
        logger.info("Cube returned %d rows", len(results))
    except Exception as e:
        logger.error("Cube query failed: %s", e)
        return {**state, "cube_query": cube_query, "query_results": [], "error": str(e)}

    return {
        "cube_query": cube_query,
        "query_results": results,
        "sources_used": ["Cube: " + ", ".join(cube_query.get("measures", []))],
    }
