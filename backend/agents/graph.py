"""LangGraph orchestrator for multi-agent healthcare analytics."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.agents.graph_agent import graph_node
from backend.agents.intent_agent import intent_node
from backend.agents.query_planner_agent import planner_node
from backend.agents.rag_agent import rag_node
from backend.agents.response_agent import response_node
from backend.agents.sql_agent import sql_node
from backend.agents.state import AgentState
from backend.agents.validation_agent import validation_node
from backend.agents.visualization_agent import visualization_node


def _route_after_planner(state: AgentState) -> list[str]:
    intent = state.get("intent", "analytics")
    routes = []
    if intent in ("analytics", "hybrid", "visualization"):
        routes.append("sql")
    if intent in ("graph", "hybrid"):
        routes.append("graph")
    if intent in ("knowledge", "hybrid"):
        routes.append("rag")
    return routes or ["sql"]


def _merge_parallel(state: AgentState) -> AgentState:
    return state


def _route_after_validation(state: AgentState) -> str:
    if state.get("validation_status") == "fail":
        return "response_node"
    return "visualization_node"


def build_agent_graph():
    workflow = StateGraph(AgentState)

    # Node names must not collide with AgentState field names.
    # All nodes are suffixed with '_node' to avoid conflicts.
    workflow.add_node("intent_node", intent_node)
    workflow.add_node("planner_node", planner_node)
    workflow.add_node("sql_node", sql_node)
    workflow.add_node("graph_node", graph_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("merge_node", _merge_parallel)
    workflow.add_node("validation_node", validation_node)
    workflow.add_node("visualization_node", visualization_node)
    workflow.add_node("response_node", response_node)

    workflow.add_edge(START, "intent_node")
    workflow.add_edge("intent_node", "planner_node")

    def route_executor(state: AgentState) -> str:
        intent = state.get("intent", "analytics")
        if intent == "graph":
            return "graph_node"
        if intent == "knowledge":
            return "rag_node"
        if intent == "hybrid":
            return "sql_node"  # hybrid: sql first, then graph/rag via sequential extension
        return "sql_node"

    workflow.add_conditional_edges("planner_node", route_executor, {
        "sql_node": "sql_node",
        "graph_node": "graph_node",
        "rag_node": "rag_node",
    })

    async def after_sql(state: AgentState) -> str:
        if state.get("intent") == "hybrid":
            return "graph_node"
        return "validation_node"

    async def after_graph(state: AgentState) -> str:
        if state.get("intent") == "hybrid" and not state.get("rag_chunks"):
            return "rag_node"
        return "validation_node"

    workflow.add_conditional_edges("sql_node", after_sql, {"graph_node": "graph_node", "validation_node": "validation_node"})
    workflow.add_conditional_edges("graph_node", after_graph, {"rag_node": "rag_node", "validation_node": "validation_node"})
    workflow.add_edge("rag_node", "validation_node")

    workflow.add_conditional_edges("validation_node", _route_after_validation, {
        "visualization_node": "visualization_node",
        "response_node": "response_node",
    })
    workflow.add_edge("visualization_node", "response_node")
    workflow.add_edge("response_node", END)

    return workflow.compile()


agent_graph = build_agent_graph()
