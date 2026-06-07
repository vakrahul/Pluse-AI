"""Build Recharts-compatible chart specifications."""

from __future__ import annotations

from typing import Any


def build_chart_spec(chart_type: str, data: list[dict], title: str) -> dict[str, Any]:
    if not data:
        return {"type": chart_type, "data": [], "title": title}

    keys = list(data[0].keys())
    measure_keys = [k for k in keys if _is_numeric(data[0].get(k))]
    dim_keys = [k for k in keys if k not in measure_keys]

    x_key = dim_keys[0] if dim_keys else keys[0]
    y_keys = measure_keys if measure_keys else [keys[-1]]

    # Prefer time dimension as x-axis
    for k in keys:
        if "date" in k.lower() or k.endswith(".month") or k.endswith(".quarter"):
            x_key = k
            y_keys = [mk for mk in measure_keys if mk != k]
            break

    return {
        "type": chart_type,
        "data": data,
        "xKey": x_key,
        "yKeys": y_keys[:3],
        "title": title,
    }


def _is_numeric(val: Any) -> bool:
    if val is None:
        return False
    try:
        float(val)
        return True
    except (TypeError, ValueError):
        return False
