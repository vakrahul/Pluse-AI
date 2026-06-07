"""Response agent — synthesizes final natural language answer."""

from __future__ import annotations

import logging

from backend.agents.state import AgentState
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

RESPONSE_SYSTEM = """You are PulseIQ, a healthcare pharma analytics copilot for enterprise clients.

RESPONSE FORMAT - always use this exact structure when answering data questions:

Executive Summary

Primary Finding:
<one sentence stating the most important result>

Key Metrics:
- <Metric 1 label>: <value in business-friendly format>
- <Metric 2 label>: <value>
- <Metric 3 label>: <value>

Business Insight:
<one to two sentences explaining what the data means commercially>

Recommendation:
<one clear, actionable recommendation>

RULES:
- NEVER use emojis, markdown symbols (**bold**), or pipe table syntax (|).
- Use plain dash bullets (-) only.
- Format numbers in executive language: $14.3B not 14306626486, 1.75M not 1750000.
- If the question is conversational (e.g. "hi", "hello"), skip the structure and reply warmly in plain text.
- Base answers ONLY on provided data - never invent figures.
- Keep total response under 200 words."""


async def response_node(state: AgentState) -> AgentState:
    # Always attempt an LLM answer — never surface raw validation errors to the user.
    # Validation failures are passed as context so the LLM can respond helpfully.
    if llm_client.available:
        try:
            context = _build_context(state)
            answer = await llm_client.chat(RESPONSE_SYSTEM, context)
            if answer:
                return {**state, "final_answer": answer}
        except Exception as e:
            logger.error("response_node LLM call failed, using fallback: %s", e)

    return {**state, "final_answer": _rule_based_response(state)}


def _build_context(state: AgentState) -> str:
    question = state.get("question", "")
    intent = state.get("intent", "unknown")
    parts = [
        f"User question: {question}",
        f"Detected intent: {intent}",
    ]

    results = state.get("query_results", [])
    if results:
        parts.append(f"\nAnalytics results ({len(results)} rows, showing top 10):")
        for row in results[:10]:
            parts.append("  " + ", ".join(f"{k}: {v}" for k, v in row.items()))
    else:
        # Tell the LLM data is unavailable so it doesn't hallucinate numbers
        parts.append(
            "\nNo analytics data was returned for this query. "
            "This may mean the filter matched nothing in the database, or Cube.js is unavailable. "
            "Explain this clearly and suggest the user try a broader question."
        )

    graph = state.get("graph_results", [])
    if graph:
        parts.append(f"\nGraph/network results ({len(graph)} records, showing top 10):")
        for row in graph[:10]:
            parts.append("  " + ", ".join(f"{k}: {v}" for k, v in row.items()))

    chunks = state.get("rag_chunks", [])
    if chunks:
        parts.append("\nKnowledge base context:")
        for c in chunks[:3]:
            parts.append(c.get("text", "")[:400])

    if state.get("chart_spec"):
        chart = state["chart_spec"]
        parts.append(f"\nA {chart.get('type', 'bar')} chart has been generated for visualization.")

    return "\n".join(parts)


def _rule_based_response(state: AgentState) -> str:
    question = state.get("question", "").lower().strip()

    # Handle greetings
    greetings = {"hi", "hello", "hey", "hii", "helo", "greetings"}
    if question in greetings or len(question) <= 5:
        return (
            "Hello! I'm PulseIQ, your healthcare analytics copilot.\n\n"
            "I can help you with:\n"
            "- Sales trends and performance metrics\n"
            "- HCP (doctor) rankings and tier classifications\n"
            "- Referral network analysis\n"
            "- Prescription data and market share\n"
            "- Compliance policies and KOL criteria\n\n"
            "Try asking: 'Which doctors have the largest referral network?' or "
            "'Show top cardiologists in Bangalore.'"
        )

    parts = []
    results = state.get("query_results", [])
    graph = state.get("graph_results", [])
    chunks = state.get("rag_chunks", [])

    if results:
        parts.append(f"Found {len(results)} analytics result(s):")
        for row in results[:5]:
            parts.append("  - " + ", ".join(f"{k}: {v}" for k, v in row.items()))

    if graph:
        parts.append(f"\nGraph analysis ({len(graph)} results):")
        for row in graph[:5]:
            parts.append("  - " + ", ".join(f"{k}: {v}" for k, v in row.items()))

    if chunks:
        parts.append("\nRelevant policy context:")
        parts.append(chunks[0].get("text", "")[:400])

    if state.get("chart_spec"):
        parts.append(f"\nChart generated: {state['chart_spec'].get('type', 'bar')} chart")

    if not parts:
        return "I couldn't find relevant data for your question. Please try rephrasing or ask about HCPs, sales, referrals, or tier rules."

    sources = state.get("sources", [])
    if sources:
        parts.append(f"\nSources: {', '.join(sources)}")

    return "\n".join(parts)
