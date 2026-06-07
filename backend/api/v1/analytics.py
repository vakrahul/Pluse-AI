from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.semantic.cube_client import cube_client
from backend.semantic.metric_registry import METRIC_REGISTRY, get_allowed_measures, get_metric_prompt_context

router = APIRouter(prefix="/analytics", tags=["analytics"])


class CubeQueryRequest(BaseModel):
    measures: list[str] = Field(..., description="Cube measure names e.g. SalesFact.totalSales")
    dimensions: list[str] = Field(default_factory=list)
    filters: list[dict[str, Any]] = Field(default_factory=list)
    time_dimensions: list[dict[str, Any]] = Field(default_factory=list, alias="timeDimensions")
    order: dict[str, str] = Field(default_factory=dict)
    limit: int = Field(default=100, le=1000)

    model_config = {"populate_by_name": True}


@router.get("/measures")
async def list_measures():
    """Return canonical metric definitions. LLM must use only these measures."""
    return {
        "allowed_measures": get_allowed_measures(),
        "metrics": [
            {
                "name": m.name,
                "cube_measure": m.cube_measure,
                "business_definition": m.business_definition,
                "sql_expression": m.sql_expression,
                "format": m.format,
            }
            for m in METRIC_REGISTRY.values()
        ],
        "prompt_context": get_metric_prompt_context(),
    }


@router.post("/query")
async def execute_query(request: CubeQueryRequest):
    """Execute a Cube semantic layer query. Canonical business metrics are in metric_registry."""
    try:
        meta = await cube_client.meta()
        cube_measures = {
            m["name"]
            for c in meta.get("cubes", [])
            for m in c.get("measures", [])
        }
    except Exception:
        cube_measures = set(get_allowed_measures())

    for measure in request.measures:
        if measure not in cube_measures and measure not in get_allowed_measures():
            raise HTTPException(
                status_code=400,
                detail=f"Measure '{measure}' not found in Cube schema. Use GET /analytics/measures for canonical metrics.",
            )

    query: dict[str, Any] = {
        "measures": request.measures,
        "dimensions": request.dimensions,
        "filters": request.filters,
        "order": request.order,
        "limit": request.limit,
    }
    if request.time_dimensions:
        query["timeDimensions"] = request.time_dimensions

    try:
        result = await cube_client.load(query)
        return {"query": query, "data": result.get("data", []), "annotation": result.get("annotation", {})}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cube query failed: {e}") from e


@router.post("/query/sql")
async def preview_sql(request: CubeQueryRequest):
    """Preview the SQL Cube generates for a query (debug/validation)."""
    query: dict[str, Any] = {
        "measures": request.measures,
        "dimensions": request.dimensions,
        "filters": request.filters,
        "limit": request.limit,
    }
    if request.time_dimensions:
        query["timeDimensions"] = request.time_dimensions

    try:
        result = await cube_client.sql(query)
        return {"query": query, "sql": result}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Cube SQL preview failed: {e}") from e
