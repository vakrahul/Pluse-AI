"""Validation agent — guardrails for queries and responses."""

from __future__ import annotations

from backend.agents.state import AgentState
from backend.graph.cypher_templates import validate_cypher
from backend.semantic.metric_registry import get_allowed_measures


async def validation_node(state: AgentState) -> AgentState:
    errors = []

    if state.get("cube_query"):
        for measure in state["cube_query"].get("measures", []):
            allowed = get_allowed_measures()
            if measure not in allowed and not measure.startswith(("SalesFact.", "PrescriptionFact.", "HcpMaster.", "InteractionFact.", "TerritoryMaster.", "ProductMaster.")):
                errors.append(f"Unknown measure: {measure}")

    if state.get("cypher") and not validate_cypher(state["cypher"]):
        errors.append("Cypher failed security validation")

    injection_patterns = ["ignore previous", "system:", "drop table", "delete from"]
    q = state["question"].lower()
    if any(p in q for p in injection_patterns):
        errors.append("Potential prompt injection detected")

    # NOTE: Empty query_results is NOT a failure — Cube may return 0 rows for
    # valid queries with filters that match nothing. Only fail on actual API errors.
    if state.get("error"):
        errors.append(f"Query error: {state['error'][:120]}")

    if errors:
        return {
            **state,
            "validation_status": "fail",
            "validation_message": "; ".join(errors),
        }

    return {**state, "validation_status": "pass", "validation_message": "OK"}
