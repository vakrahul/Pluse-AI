"""Intent classification agent — LLM-first with expanded keyword fallback."""

from __future__ import annotations

import logging
import re

from backend.agents.state import AgentState
from backend.prompts.intent import INTENT_SYSTEM_PROMPT
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

# ── Extended keyword lists ────────────────────────────────────────────────────
GRAPH_KEYWORDS = [
    "referral", "refer", "network", "influence", "influencer", "connected",
    "kol", "key opinion", "who visits", "visit pattern", "relationship",
    "refers to", "referred by", "strongest network", "most referrals",
]
KNOWLEDGE_KEYWORDS = [
    "why", "how is", "what is", "define", "definition", "explain",
    "classified", "classification", "gold", "silver", "bronze", "tier",
    "policy", "compliance", "guideline", "rule", "criteria", "off-label",
    "call planning", "sop", "kol criteria", "what does", "meaning",
]
ANALYTICS_KEYWORDS = [
    "sales", "trend", "top", "prescription", "rx", "trx", "nrx", "compare",
    "market share", "performance", "revenue", "quarterly", "monthly",
    "show", "list", "rank", "ranking", "how many", "count", "total",
    "best", "worst", "highest", "lowest", "which", "territory", "product",
    "specialty", "city", "region", "growth", "unit", "sold",
]

CITIES = ["bangalore", "mumbai", "delhi", "chennai", "hyderabad", "pune", "kolkata"]
SPECIALTIES = {
    "cardio": "Cardiology", "cardiology": "Cardiology",
    "diabetes": "Diabetes", "diabetol": "Diabetes",
    "oncol": "Oncology", "oncology": "Oncology",
    "endocrin": "Endocrinology", "endocrinology": "Endocrinology",
    "neurol": "Neurology", "neurology": "Neurology",
}
TIERS = ["gold", "silver", "bronze"]


def _extract_entities(question: str) -> dict:
    """Rule-based entity extraction — covers most common patterns."""
    entities: dict = {}
    q = question.lower()

    # City
    for city in CITIES:
        if city in q:
            entities["city"] = city.title()
            break

    # Specialty / therapeutic area
    for keyword, canonical in SPECIALTIES.items():
        if keyword in q:
            entities["specialty"] = canonical
            entities["therapeutic_area"] = canonical
            break

    # Tier
    for tier in TIERS:
        if tier in q:
            entities["tier"] = tier.title()
            break

    # Doctor name: "Dr. Smith" or "doctor Smith"
    dr_match = re.search(r"(?:dr\.?|doctor)\s+([a-z]+)", q, re.I)
    if dr_match:
        entities["hcp_name"] = dr_match.group(1).title()

    # Explicit product mention
    prod_match = re.search(r"(?:product|brand)\s+([a-z0-9\-]+)", q, re.I)
    if prod_match:
        entities["product"] = prod_match.group(1)

    # Granularity
    if "quarter" in q:
        entities["granularity"] = "quarter"
    elif "month" in q:
        entities["granularity"] = "month"
    elif "year" in q or "annual" in q:
        entities["granularity"] = "year"

    # Top N limit
    top_match = re.search(r"top\s+(\d+)", q)
    if top_match:
        entities["limit"] = int(top_match.group(1))
    best_match = re.search(r"best\s+(\d+)", q)
    if best_match:
        entities["limit"] = int(best_match.group(1))

    # Metric hint
    if any(k in q for k in ["prescription", "rx", "trx", "prescribe"]):
        entities["metric"] = "prescriptions"
    elif any(k in q for k in ["revenue", "sales", "money", "income"]):
        entities["metric"] = "sales"
    elif any(k in q for k in ["count", "how many", "number of"]):
        entities["metric"] = "count"
    elif "market share" in q:
        entities["metric"] = "market_share"

    return entities


def _rule_classify(question: str) -> str:
    """Keyword-based intent classification fallback."""
    q = question.lower()
    is_graph = any(k in q for k in GRAPH_KEYWORDS)
    is_knowledge = any(k in q for k in KNOWLEDGE_KEYWORDS)
    is_analytics = any(k in q for k in ANALYTICS_KEYWORDS)

    # Conversational / greeting → use knowledge (RAG will answer from FAQ)
    if len(q.strip()) <= 10 or q.strip() in {"hi", "hello", "hey", "hii", "help"}:
        return "knowledge"

    if is_graph and (is_knowledge or is_analytics):
        return "hybrid"
    if is_graph:
        return "graph"
    if is_knowledge and is_analytics:
        return "hybrid"
    if is_knowledge:
        return "knowledge"
    if is_analytics:
        return "analytics"
    return "analytics"


async def intent_node(state: AgentState) -> AgentState:
    question = state["question"]
    entities = _extract_entities(question)
    intent = _rule_classify(question)

    if llm_client.available:
        try:
            result = await llm_client.chat_json(
                INTENT_SYSTEM_PROMPT,
                f"Question: {question}",
            )
            if result.get("intent") in ("analytics", "graph", "knowledge", "hybrid"):
                intent = result["intent"]
            if isinstance(result.get("entities"), dict):
                # LLM entities override keyword entities (LLM is more precise)
                entities = {**entities, **result["entities"]}
        except Exception as e:
            logger.warning("intent_node LLM failed, using rule-based fallback: %s", e)

    return {
        **state,
        "intent": intent,
        "entities": entities,
    }
