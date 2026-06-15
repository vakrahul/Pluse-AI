"""Visualization agent — recommends chart types."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState

logger = logging.getLogger(__name__)


async def visualization_node(state: AgentState) -> AgentState:
    question = state.get("question", "").lower()
    intent = state.get("intent", "")
    
    chart_type = None

    if "graph chart" in question or "network chart" in question:
        chart_type = "network"
    elif intent == "hierarchy" or state.get("graph_results"):
        chart_type = "tree"
    elif "trend" in question or "over time" in question:
        chart_type = "line"
    elif "compare" in question or "versus" in question or "vs" in question:
        chart_type = "bar"
    elif "distribution" in question or "share of" in question or "split" in question:
        chart_type = "pie"
    elif state.get("cube_query"):
        # Default for most analytics
        chart_type = "bar"
        
    recommendation = {"chart": chart_type} if chart_type else {}
    
    logger.info("visualization_node recommended: %s", recommendation)
    
    return {"chart_recommendation": recommendation}
