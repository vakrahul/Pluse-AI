"""Canonical metric definitions — sourced from cube/model/*.js.
LLM agents MUST use only these measures — never invent metrics.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    cube_measure: str
    business_definition: str
    format: str = "number"


# Ground-truth measures from cube/model/*.js files
METRIC_REGISTRY: dict[str, MetricDefinition] = {
    "totalSales": MetricDefinition(
        name="totalSales",
        cube_measure="SalesFact.totalSales",
        business_definition="Total net sales revenue after discounts. SUM(net_sales).",
        format="currency",
    ),
    "grossSales": MetricDefinition(
        name="grossSales",
        cube_measure="SalesFact.grossSales",
        business_definition="Total gross sales before discounts. SUM(gross_sales).",
        format="currency",
    ),
    "unitsSold": MetricDefinition(
        name="unitsSold",
        cube_measure="SalesFact.unitsSold",
        business_definition="Total units sold across all transactions. SUM(units_sold).",
        format="number",
    ),
    "hcpPerformance": MetricDefinition(
        name="hcpPerformance",
        cube_measure="SalesFact.hcpPerformance",
        business_definition="Net sales attributed to each HCP. Use with HcpMaster dimensions.",
        format="currency",
    ),
    "territoryPerformance": MetricDefinition(
        name="territoryPerformance",
        cube_measure="SalesFact.territoryPerformance",
        business_definition="Net sales ranked by territory. Use with TerritoryMaster dimensions.",
        format="currency",
    ),
    "productPerformance": MetricDefinition(
        name="productPerformance",
        cube_measure="SalesFact.productPerformance",
        business_definition="Net sales ranked by product. Use with ProductMaster dimensions.",
        format="currency",
    ),
    "avgDiscountPct": MetricDefinition(
        name="avgDiscountPct",
        cube_measure="SalesFact.avgDiscountPct",
        business_definition="Average discount percentage across sales transactions.",
        format="percent",
    ),
    "prescriptionCount": MetricDefinition(
        name="prescriptionCount",
        cube_measure="PrescriptionFact.prescriptionCount",
        business_definition="Total prescriptions (TRx) written. SUM(rx_count).",
        format="number",
    ),
    "newPrescriptionCount": MetricDefinition(
        name="newPrescriptionCount",
        cube_measure="PrescriptionFact.newPrescriptionCount",
        business_definition="New prescriptions only (NRx). SUM(new_rx_count).",
        format="number",
    ),
    "refillPrescriptionCount": MetricDefinition(
        name="refillPrescriptionCount",
        cube_measure="PrescriptionFact.refillPrescriptionCount",
        business_definition="Refill prescriptions. SUM(refill_rx_count).",
        format="number",
    ),
    "patientCount": MetricDefinition(
        name="patientCount",
        cube_measure="PrescriptionFact.patientCount",
        business_definition="Total unique patients (aggregated). SUM(patient_count).",
        format="number",
    ),
    "hcpCount": MetricDefinition(
        name="hcpCount",
        cube_measure="HcpMaster.count",
        business_definition="Total number of HCPs. Use with HcpMaster.tier or HcpMaster.specialty.",
        format="number",
    ),
    "kolCount": MetricDefinition(
        name="kolCount",
        cube_measure="HcpMaster.kolCount",
        business_definition="Count of Key Opinion Leaders (is_kol = true).",
        format="number",
    ),
    "avgSegmentationScore": MetricDefinition(
        name="avgSegmentationScore",
        cube_measure="HcpMaster.avgSegmentationScore",
        business_definition="Average HCP segmentation score (0-100). Higher = more valuable.",
        format="number",
    ),
}


def get_allowed_measures() -> list[str]:
    return [m.cube_measure for m in METRIC_REGISTRY.values()]


def get_metric_prompt_context() -> str:
    lines = ["VERIFIED CUBE MEASURES (use ONLY these):"]
    for m in METRIC_REGISTRY.values():
        lines.append(f"- {m.cube_measure}: {m.business_definition}")
    return "\n".join(lines)


def validate_measure(measure: str) -> bool:
    allowed = get_allowed_measures()
    return measure in allowed
