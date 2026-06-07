#!/usr/bin/env python3
"""Generate synthetic healthcare analytics data (500-1000 HCPs, 100K+ fact rows)."""

from __future__ import annotations

import csv
import os
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from faker import Faker

SEED = int(os.getenv("SEED", "42"))
HCP_COUNT = int(os.getenv("HCP_COUNT", "1000"))
SALES_FACT_COUNT = int(os.getenv("SALES_FACT_COUNT", "50000"))
PRESCRIPTION_FACT_COUNT = int(os.getenv("PRESCRIPTION_FACT_COUNT", "45000"))
INTERACTION_FACT_COUNT = int(os.getenv("INTERACTION_FACT_COUNT", "30000"))

assert 500 <= HCP_COUNT <= 1000, f"HCP_COUNT must be 500-1000, got {HCP_COUNT}"

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

fake = Faker("en_IN")
Faker.seed(SEED)
random.seed(SEED)

CITIES = [
    ("Bangalore", "Karnataka", 0.20),
    ("Mumbai", "Maharashtra", 0.18),
    ("Delhi", "Delhi", 0.15),
    ("Chennai", "Tamil Nadu", 0.12),
    ("Hyderabad", "Telangana", 0.12),
    ("Pune", "Maharashtra", 0.10),
    ("Kolkata", "West Bengal", 0.08),
    ("Ahmedabad", "Gujarat", 0.05),
]

SPECIALTIES = [
    ("Cardiology", 0.15),
    ("Endocrinology", 0.12),
    ("Oncology", 0.10),
    ("Neurology", 0.10),
    ("Gastroenterology", 0.08),
    ("Pulmonology", 0.08),
    ("Rheumatology", 0.07),
    ("Nephrology", 0.07),
    ("Dermatology", 0.08),
    ("General Practice", 0.15),
]

THERAPEUTIC_AREAS = [
    ("Diabetes", "Type 2 Diabetes Mellitus"),
    ("Cardiology", "Hypertension / Heart Failure"),
    ("Oncology", "Solid Tumors"),
    ("Neurology", "Multiple Sclerosis"),
    ("Gastroenterology", "IBD / Crohn's Disease"),
    ("Pulmonology", "Asthma / COPD"),
    ("Rheumatology", "Rheumatoid Arthritis"),
    ("Nephrology", "Chronic Kidney Disease"),
]

HOSPITAL_TYPES = ["Multi-Specialty", "Super-Specialty", "Teaching Hospital", "Corporate Hospital", "Clinic Chain"]
CHANNELS = ["Direct", "Distributor", "Hospital Pharmacy", "Retail Pharmacy"]
INTERACTION_TYPES = ["Visit", "Call", "Email", "Webinar", "Conference"]
OUTCOMES = ["Positive", "Neutral", "Follow-up Required", "Sample Provided", "No Response"]


def weighted_choice(choices):
    """Select a random choice weighted by the last element of each tuple.
    
    Returns: If tuple has 1 element, returns that element. Otherwise returns the tuple.
    """
    # Last element of each tuple is the weight, earlier elements are items
    items = [c[:-1] for c in choices]
    weights = [c[-1] for c in choices]
    selected = random.choices(items, weights=weights, k=1)[0]
    # Unpack single-element tuples to their element
    if isinstance(selected, tuple) and len(selected) == 1:
        return selected[0]
    return selected


def tier_from_score(score: float) -> str:
    if score >= 75:
        return "Gold"
    if score >= 45:
        return "Silver"
    return "Bronze"


def write_csv(name: str, headers: list[str], rows: list[list]) -> None:
    path = OUTPUT_DIR / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  Wrote {len(rows):,} rows -> {path}")


def generate_territories(n: int = 100) -> list[list]:
    rows = []
    for i in range(1, n + 1):
        city, state, _ = CITIES[i % len(CITIES)]
        rows.append([
            f"T{i:04d}",
            f"{city} Territory {i}",
            state,
            f"Zone-{(i % 4) + 1}",
            "India",
            round(random.uniform(5_000_000, 50_000_000), 2),
        ])
    return rows


def generate_hospitals(territories: list[list], n: int = 200) -> list[list]:
    rows = []
    for i in range(1, n + 1):
        city, state, _ = random.choice(CITIES)
        territory_id = territories[i % len(territories)][0]
        rows.append([
            f"H{i:04d}",
            f"{fake.company()} {random.choice(['Hospital', 'Medical Centre', 'Health City'])}",
            random.choice(HOSPITAL_TYPES),
            random.randint(50, 1500),
            city,
            state,
            territory_id,
            round(random.uniform(8.0, 35.0), 7),
            round(random.uniform(68.0, 95.0), 7),
        ])
    return rows


def generate_products(n: int = 50) -> list[list]:
    rows = []
    for i in range(1, n + 1):
        area, indication = THERAPEUTIC_AREAS[i % len(THERAPEUTIC_AREAS)]
        brand = fake.word().capitalize() + random.choice(["mab", "stat", "pril", "sartan", "formin"])
        rows.append([
            f"P{i:04d}",
            f"{brand} {area}",
            brand,
            area,
            indication,
            fake.word().upper() + str(random.randint(100, 999)),
            date(2015 + (i % 10), (i % 12) + 1, 1).isoformat(),
            True,
            round(random.uniform(500, 15000), 2),
        ])
    return rows


def generate_reps(territories: list[list], n: int = 150) -> list[list]:
    rows = []
    for i in range(1, n + 1):
        rows.append([
            f"R{i:04d}",
            fake.first_name(),
            fake.last_name(),
            f"rep{i}@pharma-health.com",
            territories[i % len(territories)][0],
            f"R{max(1, (i % 10)) :04d}" if i > 10 else None,
            (date.today() - timedelta(days=random.randint(365, 3650))).isoformat(),
            True,
        ])
    return rows


def generate_hcps(hospitals: list[list], territories: list[list]) -> list[list]:
    rows = []
    for i in range(1, HCP_COUNT + 1):
        city, state = weighted_choice(CITIES)
        specialty = weighted_choice(SPECIALTIES)
        score = round(random.betavariate(2, 5) * 100, 2)
        tier = tier_from_score(score)
        is_kol = tier == "Gold" and random.random() < 0.05
        hospital = hospitals[i % len(hospitals)]
        rows.append([
            f"HCP{i:05d}",
            f"NPI{random.randint(10**9, 10**10 - 1)}",
            fake.first_name(),
            fake.last_name(),
            specialty,
            f"{specialty} - {fake.word().capitalize()}",
            tier,
            score,
            city,
            state,
            "India",
            hospital[0],
            hospital[6],
            is_kol,
            random.randint(0, 50) if tier == "Gold" else random.randint(0, 15),
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ])
    return rows


def generate_sales(hcps: list[list], products: list[list], hospitals: list[list],
                   territories: list[list], reps: list[list]) -> list[list]:
    rows = []
    start_date = date(2023, 1, 1)
    for i in range(SALES_FACT_COUNT):
        hcp = random.choice(hcps)
        product = random.choice(products)
        rep = random.choice(reps)
        sale_date = start_date + timedelta(days=random.randint(0, 730))
        units = random.randint(1, 500)
        unit_price = float(product[8])
        gross = round(units * unit_price, 2)
        discount = round(random.uniform(0, 25), 2)
        net = round(gross * (1 - discount / 100), 2)
        rows.append([
            sale_date.isoformat(),
            product[0],
            hcp[0],
            hcp[11],
            hcp[12],
            rep[0],
            units,
            gross,
            net,
            discount,
            random.choice(CHANNELS),
        ])
    return rows


def generate_prescriptions(hcps: list[list], products: list[list]) -> list[list]:
    rows = []
    start_date = date(2023, 1, 1)
    for _ in range(PRESCRIPTION_FACT_COUNT):
        hcp = random.choice(hcps)
        product = random.choice(products)
        rx_date = start_date + timedelta(days=random.randint(0, 730))
        rx_count = random.randint(1, 200)
        new_rx = random.randint(0, rx_count // 2)
        rows.append([
            rx_date.isoformat(),
            product[0],
            hcp[0],
            random.randint(1, 50),
            rx_count,
            new_rx,
            rx_count - new_rx,
        ])
    return rows


def generate_interactions(hcps: list[list], reps: list[list]) -> list[list]:
    rows = []
    start = datetime(2023, 1, 1)
    for _ in range(INTERACTION_FACT_COUNT):
        hcp = random.choice(hcps)
        rep = random.choice(reps)
        interaction_date = start + timedelta(
            days=random.randint(0, 730),
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59),
        )
        rows.append([
            interaction_date.isoformat(),
            rep[0],
            hcp[0],
            random.choice(INTERACTION_TYPES),
            random.randint(5, 120),
            random.choice(OUTCOMES),
            random.randint(0, 10),
        ])
    return rows


def main() -> None:
    print(f"Generating synthetic data (SEED={SEED}, HCP_COUNT={HCP_COUNT})...")

    territories = generate_territories(100)
    write_csv("territory_master.csv",
              ["territory_id", "territory_name", "region", "zone", "country", "sales_target"],
              territories)

    hospitals = generate_hospitals(territories, 200)
    write_csv("hospital_master.csv",
              ["hospital_id", "hospital_name", "hospital_type", "bed_count", "city", "state",
               "territory_id", "latitude", "longitude"],
              hospitals)

    products = generate_products(50)
    write_csv("product_master.csv",
              ["product_id", "product_name", "brand_name", "therapeutic_area", "indication",
               "molecule", "launch_date", "is_active", "unit_price"],
              products)

    reps = generate_reps(territories, 150)
    write_csv("sales_rep_master.csv",
              ["rep_id", "first_name", "last_name", "email", "territory_id", "manager_id",
               "hire_date", "is_active"],
              reps)

    hcps = generate_hcps(hospitals, territories)
    write_csv("hcp_master.csv",
              ["hcp_id", "npi_number", "first_name", "last_name", "specialty", "sub_specialty",
               "tier", "segmentation_score", "city", "state", "country", "hospital_id",
               "territory_id", "is_kol", "referral_count", "created_at", "updated_at"],
              hcps)

    sales = generate_sales(hcps, products, hospitals, territories, reps)
    write_csv("sales_fact.csv",
              ["sale_date", "product_id", "hcp_id", "hospital_id", "territory_id", "rep_id",
               "units_sold", "gross_sales", "net_sales", "discount_pct", "channel"],
              sales)

    prescriptions = generate_prescriptions(hcps, products)
    write_csv("prescription_fact.csv",
              ["rx_date", "product_id", "hcp_id", "patient_count", "rx_count",
               "new_rx_count", "refill_rx_count"],
              prescriptions)

    interactions = generate_interactions(hcps, reps)
    write_csv("interaction_fact.csv",
              ["interaction_date", "rep_id", "hcp_id", "interaction_type",
               "duration_minutes", "outcome", "samples_provided"],
              interactions)

    total_facts = len(sales) + len(prescriptions) + len(interactions)
    assert 500 <= len(hcps) <= 1000, f"HCP count {len(hcps)} out of range"
    assert total_facts >= 100_000, f"Fact rows {total_facts} below 100K minimum"

    print(f"\nValidation passed:")
    print(f"  HCPs:        {len(hcps):,} (range 500-1,000)")
    print(f"  Sales:       {len(sales):,}")
    print(f"  Rx:          {len(prescriptions):,}")
    print(f"  Interactions:{len(interactions):,}")
    print(f"  Total facts: {total_facts:,} (min 100,000)")


if __name__ == "__main__":
    main()
