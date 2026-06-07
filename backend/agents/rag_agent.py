"""RAG agent — retrieves business knowledge from ChromaDB."""

from __future__ import annotations

from backend.agents.state import AgentState
from backend.rag.chroma_client import chroma_rag


async def rag_node(state: AgentState) -> AgentState:
    question = state["question"]
    plan = state.get("plan", [])

    collections = None
    for step in plan:
        if step.get("agent") == "rag":
            collections = step.get("params", {}).get("collections")

    if "compliance" in question.lower() or "off-label" in question.lower():
        collections = ["compliance"]

    chunks = chroma_rag.query(question, collections=collections, n_results=5)
    sources = [f"RAG: {c['source']} ({c['collection']})" for c in chunks]

    return {
        **state,
        "rag_chunks": chunks,
        "sources": state.get("sources", []) + sources,
    }
