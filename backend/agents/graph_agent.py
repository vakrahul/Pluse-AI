"""Graph agent — executes Neo4j Cypher via templates."""

from __future__ import annotations

from backend.agents.state import AgentState
from backend.graph.cypher_templates import TEMPLATES, validate_cypher
from backend.graph.neo4j_client import neo4j_client


async def graph_node(state: AgentState) -> AgentState:
    question = state["question"].lower()
    entities = state.get("entities", {})
    plan = state.get("plan", [])

    template_key = "top_referrers"
    params: dict = {"limit": 10}

    for step in plan:
        if step.get("agent") == "graph":
            action = step.get("action", "")
            if action == "referral_network" and entities.get("hcp_name"):
                template_key = "referral_network"
                params = {"hcp_name": entities["hcp_name"]}
            elif "influence" in question or "largest" in question:
                template_key = "influence_network"
                params = {"limit": 10}
            break

    if "influence" in question or "largest referral" in question:
        template_key = "influence_network"
        params = {"limit": 10}

    template = TEMPLATES[template_key]
    cypher = template["cypher"]

    if not validate_cypher(cypher):
        return {**state, "error": "Invalid Cypher blocked by validator"}

    try:
        results = await neo4j_client.run(cypher, params)
    except Exception as e:
        return {**state, "cypher": cypher, "cypher_params": params, "graph_results": [], "error": str(e)}

    return {
        **state,
        "cypher": cypher,
        "cypher_params": params,
        "graph_results": results,
        "sources": state.get("sources", []) + [f"Neo4j: {template_key}"],
    }
