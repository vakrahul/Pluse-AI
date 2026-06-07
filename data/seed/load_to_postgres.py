#!/usr/bin/env python3
"""Load generated CSVs into PostgreSQL."""

from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from psycopg2 import sql

OUTPUT_DIR = Path(__file__).parent / "output"

TABLE_MAP = {
    "territory_master.csv": ("dim", "territory_master"),
    "hospital_master.csv": ("dim", "hospital_master"),
    "product_master.csv": ("dim", "product_master"),
    "sales_rep_master.csv": ("dim", "sales_rep_master"),
    "hcp_master.csv": ("dim", "hcp_master"),
    "sales_fact.csv": ("fact", "sales_fact"),
    "prescription_fact.csv": ("fact", "prescription_fact"),
    "interaction_fact.csv": ("fact", "interaction_fact"),
}


def get_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "healthcare_analytics"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def truncate_tables(cur) -> None:
    cur.execute("""
        TRUNCATE TABLE
            fact.interaction_fact,
            fact.prescription_fact,
            fact.sales_fact,
            dim.hcp_master,
            dim.sales_rep_master,
            dim.product_master,
            dim.hospital_master,
            dim.territory_master
        CASCADE
    """)


def load_csv(cur, csv_file: str, schema: str, table: str) -> int:
    path = OUTPUT_DIR / csv_file
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Run generate_synthetic_data.py first.")

    with path.open("r", encoding="utf-8") as f:
        # Read the header line to get the explicit column list from the CSV.
        # This is required because the DB tables have auto-generated BIGSERIAL
        # primary key columns (sales_id, rx_id, interaction_id) that are NOT
        # present in the CSV — positional COPY would try to fill them and fail.
        header = f.readline().strip().split(",")
        col_identifiers = sql.SQL(", ").join(sql.Identifier(c) for c in header)
        copy_sql = sql.SQL(
            "COPY {schema}.{table} ({cols}) FROM STDIN WITH (FORMAT CSV)"
        ).format(
            schema=sql.Identifier(schema),
            table=sql.Identifier(table),
            cols=col_identifiers,
        ).as_string(cur.connection)
        cur.copy_expert(copy_sql, f)

    cur.execute(
        sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
            sql.Identifier(schema), sql.Identifier(table)
        )
    )
    return cur.fetchone()[0]


def main() -> None:
    conn = get_conn()
    conn.autocommit = False
    cur = conn.cursor()

    try:
        print("Truncating existing data...")
        truncate_tables(cur)

        for csv_file, (schema, table) in TABLE_MAP.items():
            count = load_csv(cur, csv_file, schema, table)
            print(f"  Loaded {count:,} rows -> {schema}.{table}")

        cur.execute("SELECT COUNT(*) FROM dim.hcp_master")
        hcp_count = cur.fetchone()[0]
        cur.execute("""
            SELECT
                (SELECT COUNT(*) FROM fact.sales_fact) +
                (SELECT COUNT(*) FROM fact.prescription_fact) +
                (SELECT COUNT(*) FROM fact.interaction_fact)
        """)
        fact_count = cur.fetchone()[0]

        assert 500 <= hcp_count <= 1000, f"HCP count {hcp_count} out of range"
        assert fact_count >= 100_000, f"Fact count {fact_count} below 100K"

        conn.commit()
        print(f"\nLoad complete: {hcp_count:,} HCPs, {fact_count:,} fact rows")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
