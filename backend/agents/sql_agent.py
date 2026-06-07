"""SQL/Cube agent — LLM-powered query builder with verified schema fallback.

Schema ground truth sourced directly from cube/model/*.js files.
The LLM builds the query; the keyword fallback uses only validated
measure/dimension names that actually exist in Cube.
"""

from __future__ import annotations

import json
import logging
import re

from backend.agents.state import AgentState
from backend.semantic.cube_client import cube_client
from backend.utils.llm import llm_client

logger = logging.getLogger(__name__)

# ── Verified schema — sourced directly from cube/model/*.js ───────────────────
# NOTE: Update this whenever Cube schemas change.
CUBE_SCHEMA_PROMPT = """
You are a Cube.js query builder for a healthcare pharma analytics platform.

VERIFIED MEASURES (ONLY use these exact strings — nothing else):
SalesFact:
- SalesFact.totalSales         → total net revenue (sales, revenue, money, income)
- SalesFact.grossSales         → gross sales before discounts
- SalesFact.unitsSold          → units sold
- SalesFact.hcpPerformance     → revenue per HCP (top doctors by sales)
- SalesFact.territoryPerformance → revenue per territory
- SalesFact.productPerformance → revenue per product/brand
- SalesFact.avgDiscountPct     → average discount %
- SalesFact.count              → count of sales transactions

PrescriptionFact:
- PrescriptionFact.prescriptionCount    → total Rx / TRx (prescriptions written)
- PrescriptionFact.newPrescriptionCount → new Rx / NRx only
- PrescriptionFact.refillPrescriptionCount → refill Rx
- PrescriptionFact.patientCount         → patient count

HcpMaster:
- HcpMaster.count              → number of HCPs (how many doctors)
- HcpMaster.avgSegmentationScore → average HCP score
- HcpMaster.kolCount           → count of KOLs (key opinion leaders)

ProductMaster:
- ProductMaster.count          → number of products
TerritoryMaster:
- TerritoryMaster.count        → number of territories
- TerritoryMaster.salesTarget  → total sales target

VERIFIED DIMENSIONS (ONLY use these exact strings):
HcpMaster:
- HcpMaster.fullName           → doctor full name (filter for specific doctor)
- HcpMaster.firstName          → first name
- HcpMaster.lastName           → last name
- HcpMaster.specialty          → Cardiology, Endocrinology, Oncology, Neurology, Gastroenterology, Pulmonology, Rheumatology, Nephrology, Dermatology, General Practice
- HcpMaster.tier               → Gold, Silver, Bronze
- HcpMaster.city               → Bangalore, Mumbai, Delhi, Chennai, Hyderabad, Pune, Kolkata
- HcpMaster.state              → Karnataka, Maharashtra, etc.
- HcpMaster.isKol              → true/false (Key Opinion Leader)
- HcpMaster.referralCount      → number of referrals
- HcpMaster.segmentationScore  → score 0-100

ProductMaster:
- ProductMaster.productName    → product/brand name
- ProductMaster.brandName      → brand name
- ProductMaster.therapeuticArea → Diabetes, Cardiology, Oncology, Neurology, Gastroenterology, Pulmonology, Rheumatology, Nephrology
- ProductMaster.indication     → disease indication

TerritoryMaster:
- TerritoryMaster.territoryName → territory name
- TerritoryMaster.region       → region
- TerritoryMaster.zone         → zone

TIME DIMENSIONS:
- SalesFact.saleDate           → use for sales trends
- PrescriptionFact.rxDate      → use for prescription trends

IMPORTANT DATE RANGE: The data covers January 2023 to December 2024.
ALWAYS use dateRange "2023-01-01 to 2024-12-31" for time dimensions.
DO NOT use "last 12 months" or "last 6 months" — the data will not match.

OUTPUT — return ONLY valid JSON, no explanation:
{
  "measures": ["SalesFact.totalSales"],
  "dimensions": ["ProductMaster.therapeuticArea"],
  "filters": [{"member": "ProductMaster.therapeuticArea", "operator": "equals", "values": ["Cardiology"]}],
  "timeDimensions": [{"dimension": "SalesFact.saleDate", "granularity": "month", "dateRange": "2023-01-01 to 2024-12-31"}],
  "order": {"SalesFact.totalSales": "desc"},
  "limit": 10
}

RULES:
- Always include at least one measure from the verified list above.
- NEVER invent measures or dimensions not listed — this will cause Cube to return 0 rows.
- For HCP specialty filters, use HcpMaster.specialty (not ProductMaster.therapeuticArea).
- For product/brand analysis, use ProductMaster.therapeuticArea or ProductMaster.productName.
- Return ONLY the JSON object — no markdown, no explanation.
"""

# ── Data range constant (data covers 2023-2024) ────────────────────────────────
DATA_DATE_RANGE = "2023-01-01 to 2024-12-31"


def _keyword_fallback(question: str, entities: dict) -> dict:
    """Fallback using only verified Cube measure/dimension names."""
    q = question.lower()

    # Named doctor lookup
    if entities.get("hcp_name"):
        return {
            "measures": ["SalesFact.hcpPerformance", "PrescriptionFact.prescriptionCount"],
            "dimensions": ["HcpMaster.fullName", "HcpMaster.tier", "HcpMaster.specialty", "HcpMaster.city"],
            "filters": [{"member": "HcpMaster.fullName", "operator": "contains", "values": [entities["hcp_name"]]}],
            "limit": 5,
        }

    # Trend / time series
    if any(k in q for k in ["trend", "monthly", "quarterly", "over time", "by month", "by quarter"]):
        gran = "quarter" if "quarter" in q else "month"
        query: dict = {
            "measures": ["SalesFact.totalSales"],
            "timeDimensions": [{"dimension": "SalesFact.saleDate", "granularity": gran, "dateRange": DATA_DATE_RANGE}],
            "order": {"SalesFact.saleDate": "asc"},
        }
        # Add therapeutic area filter if detected
        if entities.get("therapeutic_area"):
            query["filters"] = [{"member": "ProductMaster.therapeuticArea", "operator": "equals", "values": [entities["therapeutic_area"]]}]
        # Add specialty dimension if it's an HCP specialty question
        if entities.get("specialty"):
            query["dimensions"] = ["ProductMaster.therapeuticArea"]
        return query

    # Prescription queries
    if any(k in q for k in ["prescription", "rx", "trx", "nrx", "prescribe"]):
        dims: list[str] = []
        if any(k in q for k in ["specialty", "cardio", "oncol", "diabet", "neurol"]):
            dims.append("HcpMaster.specialty")
        if "tier" in q or any(k in q for k in ["gold", "silver", "bronze"]):
            dims.append("HcpMaster.tier")
        if "product" in q or "brand" in q:
            dims.append("ProductMaster.productName")
        if not dims:
            dims = ["HcpMaster.tier"]

        filters: list[dict] = []
        if entities.get("specialty"):
            filters.append({"member": "HcpMaster.specialty", "operator": "equals", "values": [entities["specialty"]]})
        if entities.get("tier"):
            filters.append({"member": "HcpMaster.tier", "operator": "equals", "values": [entities["tier"]]})
        if entities.get("city"):
            filters.append({"member": "HcpMaster.city", "operator": "equals", "values": [entities["city"]]})

        return {
            "measures": ["PrescriptionFact.prescriptionCount"],
            "dimensions": dims,
            "filters": filters,
            "order": {"PrescriptionFact.prescriptionCount": "desc"},
            "limit": 15,
        }

    # Territory analysis
    if any(k in q for k in ["territory", "region", "zone"]):
        return {
            "measures": ["SalesFact.territoryPerformance"],
            "dimensions": ["TerritoryMaster.territoryName", "TerritoryMaster.region"],
            "order": {"SalesFact.territoryPerformance": "desc"},
            "limit": 15,
        }

    # Product / market share / brand
    if any(k in q for k in ["product", "brand", "market share", "compare", "therapeutic"]):
        filters = []
        if entities.get("therapeutic_area"):
            filters.append({"member": "ProductMaster.therapeuticArea", "operator": "equals", "values": [entities["therapeutic_area"]]})
        return {
            "measures": ["SalesFact.totalSales", "SalesFact.unitsSold"],
            "dimensions": ["ProductMaster.productName", "ProductMaster.therapeuticArea"],
            "filters": filters,
            "order": {"SalesFact.totalSales": "desc"},
            "limit": 20,
        }

    # HCP count / tier / segmentation
    if any(k in q for k in ["how many", "count", "tier", "gold", "silver", "bronze", "kol", "segmentation"]):
        dims = []
        filters = []
        if any(k in q for k in ["tier", "gold", "silver", "bronze"]):
            dims.append("HcpMaster.tier")
        if any(k in q for k in ["specialty", "cardio", "oncol", "diabet", "neurol"]):
            dims.append("HcpMaster.specialty")
        for tier in ["Gold", "Silver", "Bronze"]:
            if tier.lower() in q:
                filters.append({"member": "HcpMaster.tier", "operator": "equals", "values": [tier]})
                break
        if entities.get("specialty"):
            filters.append({"member": "HcpMaster.specialty", "operator": "equals", "values": [entities["specialty"]]})
        if entities.get("city"):
            filters.append({"member": "HcpMaster.city", "operator": "equals", "values": [entities["city"]]})
        return {
            "measures": ["HcpMaster.count"],
            "dimensions": dims or ["HcpMaster.tier"],
            "filters": filters,
            "order": {"HcpMaster.count": "desc"},
        }

    # Default — top HCPs by revenue with optional specialty/city filter
    dims = ["HcpMaster.fullName", "HcpMaster.specialty", "HcpMaster.city", "HcpMaster.tier"]
    filters = []
    if entities.get("specialty"):
        filters.append({"member": "HcpMaster.specialty", "operator": "equals", "values": [entities["specialty"]]})
    if entities.get("city"):
        filters.append({"member": "HcpMaster.city", "operator": "equals", "values": [entities["city"]]})
    limit = entities.get("limit", 10)
    return {
        "measures": ["SalesFact.hcpPerformance", "PrescriptionFact.prescriptionCount"],
        "dimensions": dims,
        "filters": filters,
        "order": {"SalesFact.hcpPerformance": "desc"},
        "limit": limit,
    }


def _fix_date_range(query: dict) -> dict:
    """Ensure time dimensions always use the data date range (2023-2024),
    never 'last N months' which returns empty results for old data."""
    if not query.get("timeDimensions"):
        return query
    fixed = []
    for td in query["timeDimensions"]:
        dr = td.get("dateRange", "")
        if isinstance(dr, str) and ("last" in dr.lower() or "this" in dr.lower() or "yesterday" in dr.lower()):
            td = {**td, "dateRange": DATA_DATE_RANGE}
        fixed.append(td)
    return {**query, "timeDimensions": fixed}


def _validate_query(q: dict) -> bool:
    """Check the LLM output is a usable Cube query with real measures."""
    if not isinstance(q, dict):
        return False
    measures = q.get("measures", [])
    if not measures:
        return False
    if not all(isinstance(m, str) for m in measures):
        return False
    # All measures must start with a known cube name
    known_cubes = ("SalesFact.", "PrescriptionFact.", "HcpMaster.", "ProductMaster.",
                   "TerritoryMaster.", "InteractionFact.", "SalesRepMaster.", "HospitalMaster.")
    for m in measures:
        if not any(m.startswith(c) for c in known_cubes):
            logger.warning("LLM generated unknown measure: %s", m)
            return False
    return True


async def sql_node(state: AgentState) -> AgentState:
    question = state["question"]
    entities = state.get("entities", {})
    cube_query: dict = {}

    # ── 1. LLM-powered query generation ──────────────────────────────────────
    if llm_client.available:
        try:
            user_prompt = (
                f"User question: {question}\n"
                f"Extracted entities: {json.dumps(entities)}\n\n"
                "Build the Cube.js JSON query to answer this question. "
                "Use ONLY the verified measures and dimensions listed above."
            )
            raw = await llm_client.chat(CUBE_SCHEMA_PROMPT, user_prompt, temperature=0.0)
            if raw:
                match = re.search(r"\{[\s\S]*\}", raw)
                if match:
                    candidate = json.loads(match.group())
                    if _validate_query(candidate):
                        # Fix any relative date ranges before executing
                        cube_query = _fix_date_range(candidate)
                        logger.info("LLM built Cube query: %s", cube_query)
        except Exception as e:
            logger.warning("LLM Cube query builder failed, using keyword fallback: %s", e)

    # ── 2. Keyword fallback if LLM failed or unavailable ─────────────────────
    if not cube_query:
        cube_query = _keyword_fallback(question, entities)
        cube_query = _fix_date_range(cube_query)
        logger.info("Keyword fallback Cube query: %s", cube_query)

    # ── 3. Execute against Cube ───────────────────────────────────────────────
    results: list[dict] = []
    try:
        resp = await cube_client.load(cube_query)
        results = resp.get("data", [])
        logger.info("Cube returned %d rows for query: %s", len(results), cube_query.get("measures"))
    except Exception as e:
        logger.error("Cube query failed: %s | query: %s", e, cube_query)
        return {**state, "cube_query": cube_query, "query_results": [], "error": str(e)}

    return {
        **state,
        "cube_query": cube_query,
        "query_results": results,
        "sources": state.get("sources", []) + ["Cube: " + ", ".join(cube_query.get("measures", []))],
    }
