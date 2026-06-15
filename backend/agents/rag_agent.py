"""RAG agent — retrieves Payer360 knowledge from ChromaDB."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState
from backend.rag.chroma_client import chroma_rag

logger = logging.getLogger(__name__)


async def rag_node(state: AgentState) -> AgentState:
    question = state["question"]
    intent = state.get("intent", "knowledge")

    # Route to most relevant collection based on question content
    q = question.lower()
    if any(k in q for k in ["things to know", "caveat", "additive", "not additive",
                              "flag", "double count", "time lag", "warning"]):
        collections = ["payer360_caveats", "payer360_knowledge"]
    elif any(k in q for k in ["sample question", "example", "what can you answer",
                                "how to ask", "demo"]):
        collections = ["payer360_faq"]
    else:
        # Default: search both knowledge and faq
        collections = ["payer360_knowledge", "payer360_faq"]

    chunks = chroma_rag.query(question, collections=collections, n_results=5)
    sources = [f"RAG: {c['source']} [{c['collection']}]" for c in chunks]

    logger.info("rag_node retrieved %d chunks for: %s", len(chunks), question[:60])

    return {
        "rag_chunks": chunks,
        "sources_used": sources,
    }
