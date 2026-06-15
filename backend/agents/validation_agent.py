"""Validation agent — Payer360 schema guardrails."""

from __future__ import annotations

from backend.agents.state import AgentState
from backend.graph.cypher_templates import validate_cypher

KNOWN_CUBE_PREFIXES = ("McoProfile.", "Formulary.", "McoHierarchy.")

INJECTION_PATTERNS = [
    "ignore previous", "system:", "drop table", "delete from",
    "ignore all", "disregard", "new instructions",
]


async def validation_node(state: AgentState) -> AgentState:
    errors = []

    # Validate Cube measures
    if state.get("cube_query"):
        for measure in state["cube_query"].get("measures", []):
            if not any(measure.startswith(p) for p in KNOWN_CUBE_PREFIXES):
                errors.append(f"Unknown Cube measure: {measure}")

    # Validate Cypher (MCO hierarchy queries)
    if state.get("cypher") and not validate_cypher(state["cypher"]):
        errors.append("Cypher failed security validation")

    # Prompt injection detection
    q = state.get("question", "").lower()
    if any(p in q for p in INJECTION_PATTERNS):
        errors.append("Potential prompt injection detected")

    # Pass-through query errors (empty results are NOT failures)
    if state.get("error"):
        errors.append(f"Query error: {state['error'][:120]}")

    if errors:
        return {
            "validation_status": "fail",
            "validation_message": "; ".join(errors),
        }

    return {"validation_status": "pass", "validation_message": "Analytics validated"}
