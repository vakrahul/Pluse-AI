"""Query planner agent — builds execution plan from intent."""

from __future__ import annotations

from backend.agents.state import AgentState, PlanStep


def _build_plan(intent: str, entities: dict) -> list[PlanStep]:
    plan: list[PlanStep] = []

    if intent in ("analytics", "hybrid", "visualization"):
        plan.append({"agent": "sql", "action": "cube_query", "params": entities})
    if intent in ("graph", "hybrid"):
        if entities.get("hcp_name"):
            plan.append({"agent": "graph", "action": "referral_network", "params": entities})
        else:
            plan.append({"agent": "graph", "action": "top_referrers", "params": {"limit": 10}})
    if intent in ("knowledge", "hybrid"):
        collections = ["segmentation"] if "gold" in str(entities).lower() or "tier" in str(entities) else None
        plan.append({"agent": "rag", "action": "retrieve", "params": {"collections": collections}})

    if not plan:
        plan.append({"agent": "sql", "action": "cube_query", "params": entities})

    return plan


async def planner_node(state: AgentState) -> AgentState:
    plan = _build_plan(state.get("intent", "analytics"), state.get("entities", {}))
    return {**state, "plan": plan}
