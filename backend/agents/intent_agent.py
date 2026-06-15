"""Intent classification + entity extraction agent — Payer360 domain."""

from __future__ import annotations

import logging
import re
import time
import uuid

from backend.agents.state import AgentState
from backend.prompts.intent import INTENT_SYSTEM_PROMPT
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

# ── Keyword lists ─────────────────────────────────────────────────────────────
KNOWLEDGE_KEYWORDS = [
    "what is", "what are", "define", "definition", "explain", "meaning",
    "how is", "why is", "what does", "hpm", "laad", "plantrak", "imputed",
    "book of business", "access position", "formulary status", "benefit type",
    "market share metric", "mco", "pbm", "gpo", "psd", "additive",
    "things to know", "how to", "what does it mean",
]

METADATA_KEYWORDS = [
    "which table", "what table", "where is", "where can i find",
    "which column", "what column", "show column", "list column",
    "contains", "stores", "find table", "table for", "table has",
    "fields in", "columns in", "columns related", "which database",
    "which schema", "oasis_normalized", "oasis_summarized",
]

HIERARCHY_KEYWORDS = [
    "hierarchy", "parent of", "parent mco", "child", "children",
    "who owns", "under", "mco tree", "plan tree", "subsidiary",
    "owned by", "belongs to", "show mco", "mco structure",
    "plans under", "benefit types under",
]

ANALYTICS_KEYWORDS = [
    "show", "list", "how many", "count", "total", "top", "market share",
    "formulary coverage", "access position for", "covered lives",
    "sales dollars", "claim count", "patient count", "formulary status for",
    "coverage for", "by mco", "by brand", "by book", "trend",
]

# ── Entity extractors ─────────────────────────────────────────────────────────
MCO_NAMES = {
    "aetna": "Aetna", "united": "UnitedHealth Group", "uhc": "UnitedHealth Group",
    "unitedhealth": "UnitedHealth Group", "cigna": "Cigna", "humana": "Humana",
    "centene": "Centene", "molina": "Molina Healthcare", "anthem": "Anthem",
    "elevance": "Anthem", "bluecross": "BlueCross BlueShield Association",
    "bcbs": "BlueCross BlueShield Association", "kaiser": "Kaiser Permanente",
    "cvs": "CVS Health / Aetna", "express scripts": "Express Scripts",
    "optumrx": "OptumRx", "prime therapeutics": "Prime Therapeutics",
}

GNE_BRANDS = {
    "ocrevus": "Ocrevus", "xolair": "Xolair", "actemra": "Actemra",
    "vabysmo": "Vabysmo", "hemlibra": "Hemlibra", "gazyva": "Gazyva",
    "polivy": "Polivy", "tecentriq": "Tecentriq", "alecensa": "Alecensa",
    "columvi": "Columvi",
}

BOOKS_OF_BUSINESS = {
    "commercial": "Commercial", "medicare": "Medicare", "medicaid": "Medicaid",
    "medicare advantage": "Medicare_Advantage", "medicaid managed": "Medicaid_Managed",
    "medicaid ffs": "Medicaid_FFS", "government": "Government",
}

BENEFIT_TYPES = {
    "pharmacy": "PHARMACY BENEFIT", "medical": "MEDICAL BENEFIT",
    "pharmacy benefit": "PHARMACY BENEFIT", "medical benefit": "MEDICAL BENEFIT",
}

METRICS = {
    "market share": "market_share", "claim count": "claim_count",
    "patient count": "patient_count", "sales": "sales_dollars",
    "lives": "lives", "formulary": "formulary_status",
    "access position": "access_position", "hpm": "formulary_status",
    "coverage": "formulary_status",
}


def _extract_entities(question: str) -> dict:
    q = question.lower()
    entities: dict = {}

    # MCO name
    for keyword, canonical in MCO_NAMES.items():
        if keyword in q:
            entities["mco_name"] = canonical
            break

    # Brand
    for keyword, canonical in GNE_BRANDS.items():
        if keyword in q:
            entities["brand"] = canonical
            break

    # Book of business
    for keyword, canonical in BOOKS_OF_BUSINESS.items():
        if keyword in q:
            entities["book_of_business"] = canonical
            break

    # Benefit type
    for keyword, canonical in BENEFIT_TYPES.items():
        if keyword in q:
            entities["benefit_type"] = canonical
            break

    # Metric
    for keyword, canonical in METRICS.items():
        if keyword in q:
            entities["metric"] = canonical
            break

    # Therapeutic area
    tas = ["ms", "resp", "optha", "ahr", "5glt", "hcc", "ra", "ln",
           "prostate", "cns", "heme", "kidney", "immunology", "oncology"]
    for ta in tas:
        if f" {ta} " in f" {q} " or q.startswith(ta) or q.endswith(ta):
            entities["therapeutic_area"] = ta.upper()
            break

    # Top N limit
    m = re.search(r"top\s+(\d+)", q)
    if m:
        entities["limit"] = int(m.group(1))

    # Date range
    m = re.search(r"(20\d\d|q[1-4]\s*20\d\d|last\s+\d+\s+months?)", q)
    if m:
        entities["date_range"] = m.group(1)

    return entities


def _rule_classify(question: str) -> str:
    q = question.lower().strip()

    # Greetings → knowledge (FAQ fallback)
    if len(q) <= 10 or q in {"hi", "hello", "hey", "hii", "help", "helo"}:
        return "knowledge"

    is_knowledge  = any(k in q for k in KNOWLEDGE_KEYWORDS)
    is_metadata   = any(k in q for k in METADATA_KEYWORDS)
    is_hierarchy  = any(k in q for k in HIERARCHY_KEYWORDS)
    is_analytics  = any(k in q for k in ANALYTICS_KEYWORDS)

    # Hybrid: needs 2+ capabilities
    active = sum([is_knowledge, is_metadata, is_hierarchy, is_analytics])
    if active >= 2:
        # Hierarchy + knowledge → hybrid
        if is_hierarchy and is_knowledge:
            return "hybrid"
        # Knowledge + analytics → hybrid
        if is_knowledge and is_analytics:
            return "hybrid"

    if is_hierarchy:
        return "hierarchy"
    if is_metadata:
        return "metadata"
    if is_knowledge:
        return "knowledge"
    if is_analytics:
        return "analytics"

    # Default: analytics (broadest net)
    return "analytics"


async def intent_node(state: AgentState) -> AgentState:
    question = state.get("question", "")
    entities = _extract_entities(question)
    intent = _rule_classify(question)
    
    # Initialize audit variables
    query_id = state.get("query_id") or str(uuid.uuid4())
    start_time = state.get("execution_start_time") or time.time()

    if llm_client.available:
        try:
            result = await llm_client.chat_json(
                INTENT_SYSTEM_PROMPT,
                f"Question: {question}",
            )
            if result.get("intent") in ("knowledge", "metadata", "hierarchy", "analytics", "hybrid"):
                intent = result["intent"]
            if isinstance(result.get("entities"), dict):
                entities = {**entities, **result["entities"]}
        except Exception as e:
            logger.warning("intent_node LLM failed, using rule-based fallback: %s", e)

    return {
        "intent": intent, 
        "entities": entities,
        "query_id": query_id,
        "execution_start_time": start_time
    }
