#!/usr/bin/env python3
"""
Generate synthetic Payer360 structural/reference data.

Uses ONLY dictionary-defined columns. NO fake claims, NO fake sales, NO fake market share.
Generates MCO profiles, hierarchy, and formulary reference data.

Output CSVs → data/seed/output/payer360/
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "seed" / "output" / "payer360"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Reference values from the Data Dictionary ─────────────────────────────────
MCO_TYPES = ["Plan", "PBM", "Health System", "IPA", "GPO"]
BOOKS_OF_BUSINESS = ["Commercial", "Medicare", "Medicaid", "Medicare_Advantage",
                     "Medicaid_Managed", "Medicaid_FFS", "Government", "Managed_Care"]
BENEFIT_TYPES = ["PHARMACY BENEFIT", "MEDICAL BENEFIT"]
REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West", "National"]

# Real-sounding MCO names (national + regional)
NATIONAL_MCOS = [
    ("UnitedHealth Group", "Plan"), ("Aetna", "Plan"), ("Cigna", "Plan"),
    ("Humana", "Plan"), ("Centene", "Plan"), ("Molina Healthcare", "Plan"),
    ("CVS Health / Aetna", "Plan"), ("Anthem / Elevance", "Plan"),
    ("BlueCross BlueShield Association", "Plan"), ("Kaiser Permanente", "Plan"),
    ("Express Scripts", "PBM"), ("CVS Caremark", "PBM"), ("OptumRx", "PBM"),
    ("MedImpact", "PBM"), ("Prime Therapeutics", "PBM"),
]

REGIONAL_MCO_TEMPLATES = [
    "BlueCross BlueShield of {state}", "HealthFirst {region}", "Meridian Health Plan",
    "Wellcare of {state}", "Amerigroup {region}", "Caresource {state}",
    "Superior Health Plan", "Absolute Total Care", "Sunflower Health Plan",
    "Gateway Health", "Aultcare", "Medical Associates", "UPMC Health Plan",
    "Capital BlueCross", "Independence Blue Cross", "Premera Blue Cross",
    "Regence BlueCross", "Providence Health Plan", "SelectHealth",
    "Harvard Pilgrim Health Care", "Tufts Health Plan", "Neighborhood Health Plan",
    "Mass General Brigham Health Plan", "Fallon Health", "AllWays Health Partners",
]

STATES = ["California", "Texas", "Florida", "New York", "Pennsylvania",
          "Ohio", "Georgia", "North Carolina", "Michigan", "New Jersey"]

GNE_BRANDS = ["Ocrevus", "Xolair", "Actemra", "Vabysmo", "Hemlibra",
               "Gazyva", "Polivy", "Columvi", "Tecentriq", "Alecensa"]

FORMULARY_STATUS_VALUES = [
    "Preferred Brand", "Non-Preferred Brand", "Prior Authorization Required",
    "Step Edit Required", "Quantity Limit", "Not Covered", "Specialty Tier",
    "Preferred Specialty", "Non-Preferred Specialty",
]

ACCESS_POSITIONS = ["Advantage", "Parity", "Disadvantage"]

HPM_VALUES = ["Preferred", "Non-Preferred", "PA Required", "Step Edit", "Not Covered",
               "Preferred Specialty", "Non-Preferred Specialty"]


def make_mco_id(i: int) -> str:
    return f"MDM_MCO_{i:05d}"


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ── Generate payer_360_master_mco_profile ─────────────────────────────────────
def generate_mco_profiles(n_total: int = 200) -> list[dict]:
    rows = []
    mco_id = 1

    # National MCOs first
    for name, mco_type in NATIONAL_MCOS:
        rows.append({
            "mdm_mco_id": make_mco_id(mco_id),
            "mdm_mco_name": name,
            "mdm_mco_category": mco_type,
            "mdm_book_of_business": random.choice(BOOKS_OF_BUSINESS),
            "mdm_parent_id": None,
            "is_national": True,
            "region": "National",
            "state": None,
        })
        mco_id += 1

    # Regional MCOs
    while len(rows) < n_total:
        template = random.choice(REGIONAL_MCO_TEMPLATES)
        state = random.choice(STATES)
        region = random.choice(REGIONS)
        name = template.replace("{state}", state).replace("{region}", region)
        # Assign parent: most regional MCOs belong to a national parent
        parent = random.choice(rows[:len(NATIONAL_MCOS)])
        rows.append({
            "mdm_mco_id": make_mco_id(mco_id),
            "mdm_mco_name": name,
            "mdm_mco_category": random.choice(MCO_TYPES),
            "mdm_book_of_business": random.choice(BOOKS_OF_BUSINESS),
            "mdm_parent_id": parent["mdm_mco_id"],
            "is_national": False,
            "region": region,
            "state": state,
        })
        mco_id += 1

    return rows


# ── Generate payer_360_mco_hierarchy ─────────────────────────────────────────
def generate_mco_hierarchy(profiles: list[dict]) -> list[dict]:
    rows = []
    national = [p for p in profiles if p["is_national"]]
    regional = [p for p in profiles if not p["is_national"]]

    # National → regional relationships
    for reg in regional:
        parent_id = reg["mdm_parent_id"]
        if not parent_id:
            continue
        parent = next((p for p in profiles if p["mdm_mco_id"] == parent_id), None)
        if not parent:
            continue
        for benefit in BENEFIT_TYPES:
            rows.append({
                "mdm_parent_id": parent["mdm_mco_id"],
                "mdm_parent_name": parent["mdm_mco_name"],
                "mdm_child_id": reg["mdm_mco_id"],
                "mdm_child_name": reg["mdm_mco_name"],
                "mdm_mco_category": reg["mdm_mco_category"],
                "mdm_book_of_business": reg["mdm_book_of_business"],
                "benefit_type": benefit,
                "payer_360_hashkey": f"HK_{parent['mdm_mco_id']}_{reg['mdm_mco_id']}_{benefit[:3]}",
            })
    return rows


# ── Generate payer_360_formulary_rollup ───────────────────────────────────────
def generate_formulary_rollup(profiles: list[dict]) -> list[dict]:
    rows = []
    start = date(2022, 1, 1)
    end = date(2024, 12, 31)

    # Sample of MCOs × brands × quarters
    sampled_mcos = random.sample(profiles, min(80, len(profiles)))
    for mco in sampled_mcos:
        for brand in GNE_BRANDS:
            # 4-8 quarterly snapshots per MCO × brand
            n_periods = random.randint(4, 8)
            base_status = random.choice(HPM_VALUES)
            base_access = random.choice(ACCESS_POSITIONS)
            for _ in range(n_periods):
                snap_date = random_date(start, end)
                # Occasional status change
                status = base_status if random.random() > 0.15 else random.choice(HPM_VALUES)
                access = base_access if random.random() > 0.2 else random.choice(ACCESS_POSITIONS)
                rows.append({
                    "mdm_mco_id": mco["mdm_mco_id"],
                    "mdm_mco_name": mco["mdm_mco_name"],
                    "mdm_mco_category": mco["mdm_mco_category"],
                    "mdm_book_of_business": mco["mdm_book_of_business"],
                    "product_brand_name": brand,
                    "hpm_value": status,
                    "access_position": access,
                    "formulary_date": snap_date.strftime("%Y%m"),
                    "benefit_type": random.choice(BENEFIT_TYPES),
                    "payer_360_hashkey": (
                        f"HK_{mco['mdm_mco_id']}_{brand[:3]}_{snap_date.strftime('%Y%m')}"
                    ),
                })
    return rows


# ── Write CSV ─────────────────────────────────────────────────────────────────
def write_csv(rows: list[dict], filename: str) -> Path:
    if not rows:
        return OUT_DIR / filename
    path = OUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def main():
    print("Generating Payer360 structural data (dictionary-defined columns only)...")
    print("No fake claims, no fake sales, no fake market share.")

    print("\n1. Generating MCO profiles...")
    profiles = generate_mco_profiles(200)
    path = write_csv(profiles, "payer_360_mco_profile.csv")
    print(f"   {len(profiles)} MCOs -> {path.name}")

    print("2. Generating MCO hierarchy...")
    hierarchy = generate_mco_hierarchy(profiles)
    path = write_csv(hierarchy, "payer_360_mco_hierarchy.csv")
    print(f"   {len(hierarchy)} hierarchy rows -> {path.name}")

    print("3. Generating formulary rollup...")
    formulary = generate_formulary_rollup(profiles)
    path = write_csv(formulary, "payer_360_formulary_rollup.csv")
    print(f"   {len(formulary)} formulary snapshots -> {path.name}")

    print(f"\nAll CSVs written to: {OUT_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()
