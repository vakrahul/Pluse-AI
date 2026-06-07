"""Chart type selection logic."""

from __future__ import annotations

from typing import Any


def select_chart_type(cube_query: dict, results: list[dict]) -> str:
    if not results:
        return "bar"

    time_dims = cube_query.get("timeDimensions", [])
    measures = cube_query.get("measures", [])
    dimensions = cube_query.get("dimensions", [])

    if time_dims:
        return "line"

    if len(measures) >= 2 and not dimensions:
        return "scatter"

    if len(results) <= 6 and len(measures) == 1 and dimensions:
        q = str(cube_query).lower()
        if "share" in q or "percent" in q:
            return "pie"

    return "bar"
