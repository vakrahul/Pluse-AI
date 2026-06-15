import os
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

OUTPUT_DIR = "data/seed/output/payer360"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. MCO Profiles (Dimensions)
MCOS = [
    {"mcoId": "MCO-1", "mcoName": "UnitedHealth Group", "mcoCategory": "Plan", "bookOfBusiness": "Commercial", "isNational": True, "region": "National", "state": "All"},
    {"mcoId": "MCO-2", "mcoName": "Aetna", "mcoCategory": "Plan", "bookOfBusiness": "Commercial", "isNational": True, "region": "National", "state": "All"},
    {"mcoId": "MCO-3", "mcoName": "Gateway Health", "mcoCategory": "Plan", "bookOfBusiness": "Medicaid_Managed", "isNational": False, "region": "Northeast", "state": "PA"},
    {"mcoId": "MCO-4", "mcoName": "AllWays Health Partners", "mcoCategory": "Plan", "bookOfBusiness": "Government", "isNational": False, "region": "Northeast", "state": "MA"},
    {"mcoId": "MCO-5", "mcoName": "CVS Health", "mcoCategory": "PBM", "bookOfBusiness": "Commercial", "isNational": True, "region": "National", "state": "All"},
]

BRANDS = ["Ocrevus", "Hemlibra", "Xolair", "Actemra", "Vabysmo"]

# Generate PSU Claims (Patient Sub-Unit)
def generate_psu_claims(num_records=5000):
    records = []
    for _ in range(num_records):
        mco = random.choice(MCOS)
        brand = random.choice(BRANDS)
        # Ocrevus dominates
        if brand == "Ocrevus" and random.random() < 0.6:
            pass # Keep it
        elif brand != "Ocrevus" and random.random() < 0.8:
            brand = "Ocrevus"
            
        records.append({
            "psu_claim_id": str(uuid.uuid4()),
            "mdm_mco_id": mco["mcoId"],
            "product_brand_name": brand,
            "mdm_book_of_business": mco["bookOfBusiness"],
            "benefit_type": random.choice(["MEDICAL BENEFIT", "PHARMACY BENEFIT"]),
            "patient_count": random.randint(1, 10),
            "claim_date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "claim_status": random.choice(["Paid", "Rejected", "Reversed"])
        })
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(OUTPUT_DIR, "payer_360_psu_claims.csv"), index=False)
    print(f"Generated {len(df)} PSU Claims")

# Generate Sales Fact
def generate_sales(num_records=2000):
    records = []
    for _ in range(num_records):
        mco = random.choice(MCOS)
        brand = random.choice(BRANDS)
        records.append({
            "sale_id": str(uuid.uuid4()),
            "mdm_mco_id": mco["mcoId"],
            "product_brand_name": brand,
            "sale_amount_usd": round(random.uniform(5000.0, 50000.0), 2),
            "units_sold": random.randint(10, 500),
            "sale_date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "channel": random.choice(["Retail", "Specialty", "Mail Order", "Hospital"])
        })
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(OUTPUT_DIR, "payer_360_sales.csv"), index=False)
    print(f"Generated {len(df)} Sales Facts")

# Generate LAAD Claims
def generate_laad_claims(num_records=5000):
    records = []
    for _ in range(num_records):
        mco = random.choice(MCOS)
        records.append({
            "laad_claim_id": str(uuid.uuid4()),
            "mdm_mco_id": mco["mcoId"],
            "product_brand_name": random.choice(BRANDS),
            "adjudication_status": random.choice(["Approved", "Denied", "Prior Auth Required"]),
            "patient_out_of_pocket": round(random.uniform(0.0, 500.0), 2),
            "claim_date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        })
    df = pd.DataFrame(records)
    df.to_csv(os.path.join(OUTPUT_DIR, "payer_360_laad_claims.csv"), index=False)
    print(f"Generated {len(df)} LAAD Claims")

if __name__ == "__main__":
    generate_psu_claims()
    generate_sales()
    generate_laad_claims()
    print("Database generation complete!")
