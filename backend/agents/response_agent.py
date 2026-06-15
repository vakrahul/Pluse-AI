"""Response agent — Payer360 executive answer synthesis."""

from __future__ import annotations

import logging
import time

from backend.agents.state import AgentState
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

RESPONSE_SYSTEM = """You are Payer360 Copilot, an enterprise AI assistant for pharma payer analytics.

RESPONSE FORMAT — always use this exact 6-part structure for data or knowledge questions:

Executive Summary

Primary Finding:
<one sentence stating the most important result>

Key Metrics:
- <Metric 1 label>: <value>
- <Metric 2 label>: <value>
- <Metric 3 label>: <value>

Business Context:
<one to two sentences explaining what this means for payer strategy, access, or formulary management>

Recommendation:
<one clear, actionable next step for the account manager, analyst, or leadership>

Sources: <list sources>
Confidence: High | Medium | Low

PAYER360 TERMINOLOGY TO USE:
- MCO (Managed Care Organization) not "payer"
- HPM Value not "formulary tier"
- Access Position: Advantage / Parity / Disadvantage
- Book of Business: Commercial / Medicare / Medicaid
- Benefit Type: PHARMACY BENEFIT / MEDICAL BENEFIT
- GNE brands: Ocrevus, Xolair, Actemra, Vabysmo, Hemlibra
- oasis_normalized / oasis_summarized (not "database")

RULES:
- NEVER use emojis, markdown bold (**text**), or pipe table syntax (|).
- Use plain dash bullets (-) only.
- Base answers ONLY on provided data — never invent figures.
- If question is conversational (hi, hello), skip the structure and reply warmly.
- Keep total response under 250 words.
- For metadata questions: list table names with their schema prefix.
- For hierarchy questions: describe the MCO tree structure clearly.
- If no data available: say so clearly and suggest what the user can try."""


async def response_node(state: AgentState) -> AgentState:
    answer_text = ""
    if llm_client.available:
        try:
            context = _build_context(state)
            answer = await llm_client.chat(RESPONSE_SYSTEM, context)
            if answer:
                answer_text = answer
        except Exception as e:
            logger.error("response_node LLM failed, using fallback: %s", e)

    if not answer_text:
        answer_text = _rule_based_response(state)
        
    # Append Query Audit
    query_id = state.get("query_id", "N/A")
    start_time = state.get("execution_start_time", time.time())
    exec_time = round(time.time() - start_time, 2)
    plan = ", ".join(state.get("plan", []))
    raw_sources = state.get("sources_used", [])
    
    # Deduplicate while preserving order
    unique_sources = []
    for s in raw_sources:
        if s not in unique_sources:
            unique_sources.append(s)
            
    sources = ", ".join(unique_sources)
    
    audit_trace = (
        "\n\n---\n"
        "**Query Audit**\n"
        f"- **Question**: {state.get('question', '')}\n"
        f"- **Intent**: {state.get('intent', 'unknown')}\n"
        f"- **Plan**: {plan}\n"
        f"- **Sources**: {sources}\n"
        f"- **Execution Time**: {exec_time}s\n"
        f"- **Query ID**: {query_id}"
    )
    
    final_answer = answer_text + audit_trace

    return {"final_answer": final_answer}


def _build_context(state: AgentState) -> str:
    question = state.get("question", "")
    intent = state.get("intent", "unknown")
    entities = state.get("entities", {})

    parts = [
        f"User question: {question}",
        f"Detected intent: {intent}",
        f"Extracted entities: {entities}",
    ]

    # Analytics results (Cube)
    results = state.get("query_results", [])
    if results:
        parts.append(f"\nAnalytics data ({len(results)} rows, showing top 10):")
        for row in results[:10]:
            parts.append("  " + ", ".join(f"{k}: {v}" for k, v in row.items()))
    elif intent == "analytics":
        parts.append("\nNo analytics data returned. Cube may be unavailable or the filter matched nothing.")

    # Graph results (Neo4j MCO hierarchy)
    graph = state.get("graph_results", [])
    if graph:
        parts.append(f"\nMCO Hierarchy data ({len(graph)} records):")
        for row in graph[:10]:
            parts.append("  " + ", ".join(f"{k}: {v}" for k, v in row.items() if v))

    # RAG knowledge chunks
    chunks = state.get("rag_chunks", [])
    if chunks:
        parts.append("\nPayer360 knowledge base context:")
        for c in chunks[:4]:
            parts.append(c.get("text", "")[:500])

    # Catalog results (metadata)
    catalog = state.get("catalog_results")
    if catalog and catalog.get("answer_text"):
        parts.append(f"\nData catalog results:\n{catalog['answer_text']}")

    # Validation note
    if state.get("validation_status") == "fail":
        parts.append(f"\nValidation note: {state.get('validation_message', '')}")

    return "\n".join(parts)


def _rule_based_response(state: AgentState) -> str:
    """Fallback when LLM is unavailable."""
    question = state.get("question", "").lower().strip()
    intent = state.get("intent", "")

    # Greetings
    if question in {"hi", "hello", "hey", "hii", "help", "helo"} or len(question) <= 5:
        return (
            "Hello! I'm Payer360 Copilot, your enterprise payer analytics assistant.\n\n"
            "I can help you with:\n"
            "- Knowledge: What is HPM value? What is LAAD? What does Advantage mean?\n"
            "- Metadata: Which table contains market share? Where is formulary data stored?\n"
            "- Hierarchy: Show MCO hierarchy for Aetna. Who is the parent of BlueCross?\n"
            "- Analytics: Show formulary coverage for Ocrevus. How many MCOs are in Medicare?\n\n"
            "Try asking: 'What is formulary status?' or 'Show MCO hierarchy for Aetna'"
        )

    parts = []

    # Catalog (metadata)
    catalog = state.get("catalog_results")
    if catalog and catalog.get("answer_text"):
        parts.append(catalog["answer_text"])

    # Graph (hierarchy)
    graph = state.get("graph_results", [])
    if graph:
        parts.append(f"MCO Hierarchy ({len(graph)} result(s)):")
        for row in graph[:5]:
            parts.append("  - " + ", ".join(f"{k}: {v}" for k, v in row.items() if v))

    # Analytics (Cube)
    results = state.get("query_results", [])
    if results:
        parts.append(f"Analytics results ({len(results)} rows):")
        for row in results[:5]:
            parts.append("  - " + ", ".join(f"{k}: {v}" for k, v in row.items()))

    # Knowledge (RAG)
    chunks = state.get("rag_chunks", [])
    if chunks:
        parts.append("Payer360 Knowledge:")
        parts.append(chunks[0].get("text", "")[:500])

    raw_sources = state.get("sources_used", [])
    unique_sources = []
    for s in raw_sources:
        if s not in unique_sources:
            unique_sources.append(s)
    
    if unique_sources:
        parts.append(f"\nSources: {', '.join(unique_sources[:3])}")

    if not parts:
        return (
            "I couldn't find relevant data for your question.\n"
            "Try: 'What is HPM value?', 'Which table contains market share?', or "
            "'Show MCO hierarchy for Aetna.'"
        )

    return "\n".join(parts)
