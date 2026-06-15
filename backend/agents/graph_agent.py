"""Graph agent — MCO hierarchy traversal via Neo4j (Payer360)."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState
from backend.graph.cypher_templates import select_template, validate_cypher
from backend.graph.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)


async def graph_node(state: AgentState) -> AgentState:
    """
    Handles 'hierarchy' intent:
      - Show MCO hierarchy for Aetna
      - Who is the parent of BlueCross?
      - What child plans does UHC own?
      - What benefit types exist under Cigna?
    """
    question = state["question"]
    entities = state.get("entities", {})

    try:
        cypher, params = select_template(question, entities)

        if not validate_cypher(cypher):
            return {
                **state,
                "graph_results": [],
                "error": "Cypher security validation failed",
            }

        results = await neo4j_client.run(cypher, params)
        sources = [f"Neo4j: MCO Hierarchy ({len(results)} records)"]

        logger.info("graph_node returned %d records for: %s", len(results), question)

        return {
            "cypher": cypher,
            "cypher_params": params,
            "graph_results": results,
            "sources_used": sources,
        }

    except Exception as e:
        logger.error("graph_node failed: %s", e)
        return {
            **state,
            "graph_results": [],
            "error": f"Neo4j query failed: {str(e)[:100]}",
        }
