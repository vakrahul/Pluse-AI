"""Planner agent — maps intent to parallel execution paths."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState

logger = logging.getLogger(__name__)


async def planner_node(state: AgentState) -> AgentState:
    intent = state.get("intent", "analytics")
    question = state.get("question", "").lower()
    
    plan = []
    
    # User specifically requested a graph/network chart
    wants_graph_chart = "graph chart" in question or "network chart" in question
    
    if wants_graph_chart:
        # Must execute graph node to get Neo4j topology
        plan.append("graph_node")
    elif intent == "knowledge":
        plan.append("rag_node")
    elif intent == "metadata":
        plan.append("catalog_node")
    elif intent == "hierarchy":
        plan.append("graph_node")
    elif intent == "analytics":
        plan.append("sql_node")
    elif intent == "hybrid":
        plan.extend(["sql_node", "rag_node"])
    else:
        plan.append("sql_node")
        
    # Remove duplicates just in case
    plan = list(dict.fromkeys(plan))
    
    logger.info("planner_node created plan: %s", plan)
    
    return {"plan": plan}
