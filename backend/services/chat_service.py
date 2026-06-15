"""Chat service — orchestrates LangGraph agent pipeline."""

from __future__ import annotations

import uuid
from typing import Any, AsyncGenerator

from backend.agents.graph import agent_graph
from backend.agents.state import AgentState


async def run_chat(question: str, session_id: str | None = None, user_role: str = "analyst") -> dict[str, Any]:
    session_id = session_id or str(uuid.uuid4())
    initial: AgentState = {
        "question": question,
        "session_id": session_id,
        "user_role": user_role,
        "sources": [],
    }
    result = await agent_graph.ainvoke(initial)
    return {
        "session_id": session_id,
        "question": question,
        "intent": result.get("intent"),
        "answer": result.get("final_answer", ""),
        "data": result.get("query_results", []),
        "graph_data": result.get("graph_results", []),
        "chart": result.get("chart_recommendation"),
        "cube_query": result.get("cube_query"),
        "sources": result.get("sources", []),
        "validation": result.get("validation_status"),
        "error": result.get("error"),
    }


async def stream_chat(question: str, session_id: str | None = None) -> AsyncGenerator[dict, None]:
    yield {"event": "status", "data": "Classifying intent..."}
    result = await run_chat(question, session_id)
    yield {"event": "intent", "data": result.get("intent")}
    if result.get("data"):
        yield {"event": "data", "data": result["data"][:10]}
    if result.get("chart"):
        yield {"event": "chart", "data": result["chart"]}
    yield {"event": "answer", "data": result.get("answer", "")}
    yield {"event": "done", "data": result}
