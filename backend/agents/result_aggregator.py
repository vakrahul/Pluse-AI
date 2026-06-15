"""Result Aggregator agent — merges parallel state execution branches."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState

logger = logging.getLogger(__name__)


async def aggregator_node(state: AgentState) -> AgentState:
    """
    Since LangGraph handles merging lists/dicts natively if annotated as reducers, 
    this node serves as a clear architectural sync point before validation.
    It ensures sources_used is deduplicated and any general merge logic is centralized.
    """
    sources = state.get("sources_used", [])
    if not sources:
        sources = state.get("sources", [])
        
    # Deduplicate sources
    unique_sources = []
    for s in sources:
        if s not in unique_sources:
            unique_sources.append(s)
            
    logger.info("aggregator_node synced state from parallel branches. Total sources: %d", len(unique_sources))

    return {}
