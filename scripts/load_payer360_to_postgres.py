#!/usr/bin/env python3
"""
Load Payer360 synthetic CSVs into PostgreSQL under oasis_normalized schema.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.utils.config import settings

CSV_DIR = Path(__file__).resolve().parents[1] / "data" / "seed" / "output" / "payer360"

DSN = (
    f"host={settings.postgres_host} port={settings.postgres_port} "
    f"dbname={settings.postgres_db} user={settings.postgres_user} "
    f"password={settings.postgres_password}"
)

DDL = """
CREATE SCHEMA IF NOT EXISTS oasis_normalized;

DROP TABLE IF EXISTS oasis_normalized.payer_360_formulary_rollup;
DROP TABLE IF EXISTS oasis_normalized.payer_360_mco_hierarchy;
DROP TABLE IF EXISTS oasis_normalized.payer_360_master_mco_profile;
DROP TABLE IF EXISTS oasis_normalized.payer_360_psu_claims;
DROP TABLE IF EXISTS oasis_normalized.payer_360_sales;
DROP TABLE IF EXISTS oasis_normalized.payer_360_laad_claims;

CREATE TABLE oasis_normalized.payer_360_master_mco_profile (
    mdm_mco_id          VARCHAR(20) PRIMARY KEY,
    mdm_mco_name        VARCHAR(200),
    mdm_mco_category    VARCHAR(100),
    mdm_book_of_business VARCHAR(100),
    mdm_parent_id       VARCHAR(20),
    is_national         BOOLEAN,
    region              VARCHAR(100),
    state               VARCHAR(100)
);

CREATE TABLE oasis_normalized.payer_360_mco_hierarchy (
    mdm_parent_id       VARCHAR(20),
    mdm_parent_name     VARCHAR(200),
    mdm_child_id        VARCHAR(20),
    mdm_child_name      VARCHAR(200),
    mdm_mco_category    VARCHAR(100),
    mdm_book_of_business VARCHAR(100),
    benefit_type        VARCHAR(50),
    payer_360_hashkey   VARCHAR(100) PRIMARY KEY
);

CREATE TABLE oasis_normalized.payer_360_formulary_rollup (
    mdm_mco_id          VARCHAR(20),
    mdm_mco_name        VARCHAR(200),
    mdm_mco_category    VARCHAR(100),
    mdm_book_of_business VARCHAR(100),
    product_brand_name  VARCHAR(100),
    hpm_value           VARCHAR(100),
    access_position     VARCHAR(50),
    formulary_date      VARCHAR(10),
    benefit_type        VARCHAR(50),
    payer_360_hashkey   VARCHAR(100) PRIMARY KEY
);

CREATE TABLE oasis_normalized.payer_360_psu_claims (
    psu_claim_id        VARCHAR(100) PRIMARY KEY,
    mdm_mco_id          VARCHAR(20),
    product_brand_name  VARCHAR(100),
    mdm_book_of_business VARCHAR(100),
    benefit_type        VARCHAR(50),
    patient_count       INTEGER,
    claim_date          DATE,
    claim_status        VARCHAR(50)
);

CREATE TABLE oasis_normalized.payer_360_sales (
    sale_id             VARCHAR(100) PRIMARY KEY,
    mdm_mco_id          VARCHAR(20),
    product_brand_name  VARCHAR(100),
    sale_amount_usd     NUMERIC(15, 2),
    units_sold          INTEGER,
    sale_date           DATE,
    channel             VARCHAR(100)
);

CREATE TABLE oasis_normalized.payer_360_laad_claims (
    laad_claim_id       VARCHAR(100) PRIMARY KEY,
    mdm_mco_id          VARCHAR(20),
    product_brand_name  VARCHAR(100),
    adjudication_status VARCHAR(50),
    patient_out_of_pocket NUMERIC(15, 2),
    claim_date          DATE
);
"""


def load_csv(conn, table: str, csv_path: Path):
    if not csv_path.exists():
        print(f"   SKIP: {csv_path.name} not found")
        return 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return 0

    cols = list(rows[0].keys())
    values = []
    for row in rows:
        vals = []
        for col in cols:
            val = row[col]
            if val == "" or val == "None":
                vals.append(None)
            elif val.lower() == "true":
                vals.append(True)
            elif val.lower() == "false":
                vals.append(False)
            else:
                vals.append(val)
        values.append(tuple(vals))

    col_str = ", ".join(cols)
    with conn.cursor() as cur:
        execute_values(
            cur,
            f"INSERT INTO {table} ({col_str}) VALUES %s ON CONFLICT DO NOTHING",
            values,
        )
    return len(values)


def main():
    print(f"Connecting to PostgreSQL at {settings.postgres_host}:{settings.postgres_port}...")
    try:
        conn = psycopg2.connect(DSN)
        conn.autocommit = False
    except Exception as e:
        print(f"ERROR: Cannot connect to PostgreSQL: {e}")
        print("Make sure Docker is running: docker compose up -d")
        sys.exit(1)

    try:
        print("Creating oasis_normalized schema and tables...")
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
        print("Schema created.")

        tables = [
            ("oasis_normalized.payer_360_master_mco_profile", "payer_360_mco_profile.csv"),
            ("oasis_normalized.payer_360_mco_hierarchy",      "payer_360_mco_hierarchy.csv"),
            ("oasis_normalized.payer_360_formulary_rollup",   "payer_360_formulary_rollup.csv"),
            ("oasis_normalized.payer_360_psu_claims",         "payer_360_psu_claims.csv"),
            ("oasis_normalized.payer_360_sales",              "payer_360_sales.csv"),
            ("oasis_normalized.payer_360_laad_claims",        "payer_360_laad_claims.csv"),
        ]

        for table, filename in tables:
            csv_path = CSV_DIR / filename
            print(f"Loading {filename}...")
            n = load_csv(conn, table, csv_path)
            conn.commit()
            print(f"   {n} rows -> {table}")

        print("\nVerifying row counts...")
        with conn.cursor() as cur:
            for table, _ in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"   {table}: {count} rows")

        print("\nPostgreSQL load complete.")

    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
