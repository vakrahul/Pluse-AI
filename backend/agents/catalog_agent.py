"""Catalog agent — answers metadata questions using the structured Payer360 catalog."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState
from backend.services.catalog_service import catalog_service

logger = logging.getLogger(__name__)


async def catalog_node(state: AgentState) -> AgentState:
    """
    Handles 'metadata' intent questions:
      - Which table contains market share?
      - Which columns define formulary status?
      - Show all claims-related tables.
    """
    question = state["question"]
    entities = state.get("entities", {})

    try:
        result = catalog_service.answer_metadata_question(question, entities)
        return {
            "catalog_results": result,
            "sources_used": ["Payer360 Data Catalog"],
        }
    except Exception as e:
        logger.error("catalog_node failed: %s", e)
        return {
            **state,
            "catalog_results": {
                "question": question,
                "matched_tables": [],
                "matched_columns": [],
                "answer_text": "Catalog lookup failed. Please try rephrasing your question.",
            },
            "error": str(e),
        }
