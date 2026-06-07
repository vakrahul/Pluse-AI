from __future__ import annotations

from typing import Any, TypedDict


class PlanStep(TypedDict, total=False):
    agent: str
    action: str
    params: dict[str, Any]


class AgentState(TypedDict, total=False):
    question: str
    session_id: str
    user_role: str
    intent: str
    entities: dict[str, Any]
    plan: list[PlanStep]
    cube_query: dict[str, Any] | None
    sql: str | None
    cypher: str | None
    cypher_params: dict[str, Any]
    rag_chunks: list[dict[str, Any]]
    query_results: list[dict[str, Any]]
    graph_results: list[dict[str, Any]]
    chart_spec: dict[str, Any] | None
    validation_status: str
    validation_message: str
    final_answer: str
    sources: list[str]
    error: str | None
