#!/usr/bin/env python3
"""Verify Cube semantic layer is working with sample queries."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

CUBE_URL = os.getenv("CUBEJS_API_URL", "http://localhost:4000/cubejs-api/v1")
CUBE_SECRET = os.getenv("CUBEJS_API_SECRET", "healthcare_cube_secret_change_in_prod")

TEST_QUERIES = [
    {
        "name": "Total Sales",
        "query": {
            "measures": ["SalesFact.totalSales"],
        },
    },
    {
        "name": "Top Cardiologists in Bangalore",
        "query": {
            "measures": ["SalesFact.hcpPerformance"],
            "dimensions": ["HcpMaster.fullName", "HcpMaster.specialty", "HcpMaster.city"],
            "filters": [
                {"member": "HcpMaster.specialty", "operator": "equals", "values": ["Cardiology"]},
                {"member": "HcpMaster.city", "operator": "equals", "values": ["Bangalore"]},
            ],
            "order": {"SalesFact.hcpPerformance": "desc"},
            "limit": 10,
        },
    },
    {
        "name": "Monthly Sales Trend - Diabetes",
        "query": {
            "measures": ["SalesFact.totalSales"],
            "timeDimensions": [
                {"dimension": "SalesFact.saleDate", "granularity": "month", "dateRange": "last 12 months"}
            ],
            "filters": [
                {"member": "ProductMaster.therapeuticArea", "operator": "equals", "values": ["Diabetes"]},
            ],
            "order": {"SalesFact.saleDate": "asc"},
        },
    },
    {
        "name": "Prescription Count by Tier",
        "query": {
            "measures": ["PrescriptionFact.prescriptionCount"],
            "dimensions": ["HcpMaster.tier"],
            "order": {"PrescriptionFact.prescriptionCount": "desc"},
        },
    },
    {
        "name": "Territory Performance",
        "query": {
            "measures": ["SalesFact.territoryPerformance"],
            "dimensions": ["TerritoryMaster.territoryName", "TerritoryMaster.region"],
            "order": {"SalesFact.territoryPerformance": "desc"},
            "limit": 10,
        },
    },
    {
        "name": "Product Performance by Therapeutic Area",
        "query": {
            "measures": ["SalesFact.productPerformance"],
            "dimensions": ["ProductMaster.productName", "ProductMaster.therapeuticArea"],
            "order": {"SalesFact.productPerformance": "desc"},
            "limit": 10,
        },
    },
    {
        "name": "HCP Count by Tier",
        "query": {
            "measures": ["HcpMaster.count"],
            "dimensions": ["HcpMaster.tier", "HcpMaster.specialty"],
            "order": {"HcpMaster.count": "desc"},
        },
    },
    {
        "name": "Rep Interactions by Type",
        "query": {
            "measures": ["InteractionFact.count", "InteractionFact.avgDurationMinutes"],
            "dimensions": ["InteractionFact.interactionType"],
        },
    },
]


def wait_for_cube(max_wait: int = 60) -> bool:
    meta_url = f"{CUBE_URL}/meta"
    for i in range(max_wait):
        try:
            req = urllib.request.Request(meta_url, headers={"Authorization": CUBE_SECRET})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def run_query(query: dict) -> dict:
    payload = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        f"{CUBE_URL}/load",
        data=payload,
        headers={
            "Authorization": CUBE_SECRET,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def main() -> int:
    print(f"Cube URL: {CUBE_URL}")
    print("Waiting for Cube to be ready...")
    if not wait_for_cube():
        print("ERROR: Cube not reachable. Run: docker compose -f infrastructure/docker/docker-compose.yml up -d")
        return 1

    print("Cube is ready.\n")
    passed = 0
    failed = 0

    for test in TEST_QUERIES:
        name = test["name"]
        try:
            result = run_query(test["query"])
            rows = result.get("data", [])
            print(f"PASS: {name} ({len(rows)} rows)")
            if rows:
                print(f"       Sample: {json.dumps(rows[0])[:120]}...")
            passed += 1
        except Exception as e:
            print(f"FAIL: {name} -> {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
