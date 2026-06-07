"""Visualization agent — selects chart type and builds spec."""

from __future__ import annotations

from backend.agents.state import AgentState
from backend.charts.selector import select_chart_type
from backend.charts.spec_builder import build_chart_spec


async def visualization_node(state: AgentState) -> AgentState:
    results = state.get("query_results", [])
    if not results:
        return {**state, "chart_spec": None}

    chart_type = select_chart_type(state.get("cube_query", {}), results)
    title = _build_title(state)
    spec = build_chart_spec(chart_type, results, title)

    return {**state, "chart_spec": spec}


def _build_title(state: AgentState) -> str:
    q = state["question"]
    if len(q) > 60:
        return q[:57] + "..."
    return q
