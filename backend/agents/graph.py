"""LangGraph orchestrator — Payer360 10-agent pipeline."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.agents.catalog_agent import catalog_node
from backend.agents.evaluation_agent import evaluation_node
from backend.agents.graph_agent import graph_node
from backend.agents.intent_agent import intent_node
from backend.agents.planner_agent import planner_node
from backend.agents.rag_agent import rag_node
from backend.agents.response_agent import response_node
from backend.agents.result_aggregator import aggregator_node
from backend.agents.sql_agent import sql_node
from backend.agents.state import AgentState
from backend.agents.validation_agent import validation_node
from backend.agents.visualization_agent import visualization_node


def _route_from_planner(state: AgentState) -> list[str]:
    """Returns the list of agent nodes to execute in parallel based on the plan."""
    return state.get("plan", ["sql_node"])


def build_agent_graph():
    workflow = StateGraph(AgentState)

    # Register all 10 nodes
    workflow.add_node("intent_node", intent_node)
    workflow.add_node("planner_node", planner_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("catalog_node", catalog_node)
    workflow.add_node("graph_node", graph_node)
    workflow.add_node("sql_node", sql_node)
    workflow.add_node("aggregator_node", aggregator_node)
    workflow.add_node("validation_node", validation_node)
    workflow.add_node("visualization_node", visualization_node)
    workflow.add_node("response_node", response_node)
    workflow.add_node("evaluation_node", evaluation_node)

    # 1. Entry point -> Intent -> Planner
    workflow.add_edge(START, "intent_node")
    workflow.add_edge("intent_node", "planner_node")

    # 2. Planner -> Parallel execution branches
    workflow.add_conditional_edges(
        "planner_node",
        _route_from_planner,
        ["rag_node", "catalog_node", "graph_node", "sql_node"]
    )

    # 3. Parallel branches -> Aggregator (Sync point)
    workflow.add_edge("rag_node", "aggregator_node")
    workflow.add_edge("catalog_node", "aggregator_node")
    workflow.add_edge("graph_node", "aggregator_node")
    workflow.add_edge("sql_node", "aggregator_node")

    # 4. Sequential post-execution pipeline
    workflow.add_edge("aggregator_node", "validation_node")
    workflow.add_edge("validation_node", "visualization_node")
    workflow.add_edge("visualization_node", "response_node")
    workflow.add_edge("response_node", "evaluation_node")
    
    # 5. End
    workflow.add_edge("evaluation_node", END)

    return workflow.compile()


agent_graph = build_agent_graph()
