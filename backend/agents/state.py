from __future__ import annotations

from typing import Any, TypedDict, Annotated
import operator


class AgentState(TypedDict, total=False):
    # ── Input ──────────────────────────────────────────────────────────────────
    question: str
    session_id: str
    user_role: str              # analyst | account_manager | medical_affairs
    query_id: str
    execution_start_time: float

    # ── Routing ────────────────────────────────────────────────────────────────
    intent: str                 # knowledge | metadata | hierarchy | analytics | hybrid
    entities: dict[str, Any]   # mco_name, brand, therapeutic_area, benefit_type,
                                # book_of_business, metric, date_range, limit
    plan: list[str]             # List of agent nodes to execute in parallel

    # ── Agent outputs ──────────────────────────────────────────────────────────
    cube_query: dict[str, Any] | None       # analytics: Cube.js JSON query
    query_results: list[dict[str, Any]]     # analytics: rows from Cube
    cypher: str | None                      # hierarchy: Neo4j Cypher string
    cypher_params: dict[str, Any]           # hierarchy: Cypher parameters
    graph_results: list[dict[str, Any]]     # hierarchy: Neo4j rows
    rag_chunks: list[dict[str, Any]]        # knowledge: ChromaDB chunks
    catalog_results: dict[str, Any] | None  # metadata: catalog search results

    # ── Validation & response ──────────────────────────────────────────────────
    validation_status: str      # pass | fail
    validation_message: str
    chart_recommendation: dict[str, Any] # e.g. {"chart": "tree"}
    final_answer: str
    sources_used: Annotated[list[str], operator.add]     # explicit audit trace
    sources: list[str]          # legacy
    evaluation_result: dict[str, Any] # e.g. {"grade": "PASS", "reason": "...", "score": 0.91}
    error: str | None
