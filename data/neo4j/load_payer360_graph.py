#!/usr/bin/env python3
"""
Load Payer360 MCO Hierarchy into Neo4j.

Creates the following graph model:
  (:MCO {id, name, type, book_of_business, region, state, is_national})
  (:BenefitType {name})          -- PHARMACY BENEFIT | MEDICAL BENEFIT
  (:BookOfBusiness {name})       -- Commercial | Medicare | Medicaid | etc.
  (:Region {name})               -- National | Northeast | Southeast | etc.

  (:MCO)-[:PARENT_OF]->(:MCO)
  (:MCO)-[:HAS_BENEFIT_TYPE]->(:BenefitType)
  (:MCO)-[:BELONGS_TO]->(:BookOfBusiness)
  (:MCO)-[:LOCATED_IN]->(:Region)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from neo4j import GraphDatabase

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.utils.config import settings

CSV_DIR = Path(__file__).resolve().parents[2] / "data" / "seed" / "output" / "payer360"

# ── Cypher statements ─────────────────────────────────────────────────────────

CLEAR_CYPHER = """
MATCH (n) DETACH DELETE n
"""

CONSTRAINTS_CYPHER = [
    "CREATE CONSTRAINT mco_id IF NOT EXISTS FOR (m:MCO) REQUIRE m.id IS UNIQUE",
    "CREATE CONSTRAINT bob_name IF NOT EXISTS FOR (b:BookOfBusiness) REQUIRE b.name IS UNIQUE",
    "CREATE CONSTRAINT bt_name IF NOT EXISTS FOR (b:BenefitType) REQUIRE b.name IS UNIQUE",
    "CREATE CONSTRAINT region_name IF NOT EXISTS FOR (r:Region) REQUIRE r.name IS UNIQUE",
]

CREATE_MCO_CYPHER = """
MERGE (m:MCO {id: $id})
SET m.name = $name,
    m.type = $type,
    m.book_of_business = $book_of_business,
    m.region = $region,
    m.state = $state,
    m.is_national = $is_national
"""

LINK_BOB_CYPHER = """
MERGE (b:BookOfBusiness {name: $bob})
WITH b
MATCH (m:MCO {id: $mco_id})
MERGE (m)-[:BELONGS_TO]->(b)
"""

LINK_REGION_CYPHER = """
MERGE (r:Region {name: $region})
WITH r
MATCH (m:MCO {id: $mco_id})
MERGE (m)-[:LOCATED_IN]->(r)
"""

CREATE_HIERARCHY_CYPHER = """
MATCH (parent:MCO {id: $parent_id})
MATCH (child:MCO {id: $child_id})
MERGE (parent)-[:PARENT_OF]->(child)
"""

LINK_BENEFIT_CYPHER = """
MERGE (b:BenefitType {name: $benefit_type})
WITH b
MATCH (m:MCO {id: $mco_id})
MERGE (m)-[:HAS_BENEFIT_TYPE]->(b)
"""


def load_csv_file(filename: str) -> list[dict]:
    path = CSV_DIR / filename
    if not path.exists():
        print(f"  SKIP: {filename} not found. Run generate_payer360_data.py first.")
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run(driver, cypher: str, params: dict | None = None):
    with driver.session() as session:
        session.run(cypher, params or {})


def run_many(driver, cypher: str, rows: list[dict]):
    with driver.session() as session:
        for row in rows:
            session.run(cypher, row)


def main():
    print(f"Connecting to Neo4j at {settings.neo4j_uri}...")
    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        driver.verify_connectivity()
        print("Connected.")
    except Exception as e:
        print(f"ERROR: Cannot connect to Neo4j: {e}")
        print("Make sure Docker is running: docker compose up -d")
        sys.exit(1)

    print("\nClearing existing graph data...")
    run(driver, CLEAR_CYPHER)

    print("Creating constraints...")
    for c in CONSTRAINTS_CYPHER:
        try:
            run(driver, c)
        except Exception:
            pass  # Constraint may already exist

    # ── Load MCO profiles ──────────────────────────────────────────────────────
    print("\nLoading MCO profiles as graph nodes...")
    profiles = load_csv_file("payer_360_mco_profile.csv")
    if not profiles:
        print("No profile data. Exiting.")
        sys.exit(1)

    for p in profiles:
        run(driver, CREATE_MCO_CYPHER, {
            "id": p["mdm_mco_id"],
            "name": p["mdm_mco_name"],
            "type": p["mdm_mco_category"],
            "book_of_business": p["mdm_book_of_business"],
            "region": p["region"] or "Unknown",
            "state": p["state"] or "",
            "is_national": p["is_national"].lower() == "true",
        })

        run(driver, LINK_BOB_CYPHER, {
            "bob": p["mdm_book_of_business"],
            "mco_id": p["mdm_mco_id"],
        })

        if p.get("region"):
            run(driver, LINK_REGION_CYPHER, {
                "region": p["region"],
                "mco_id": p["mdm_mco_id"],
            })

    print(f"  {len(profiles)} MCO nodes created.")

    # ── Load hierarchy relationships ───────────────────────────────────────────
    print("\nBuilding MCO hierarchy relationships...")
    hierarchy = load_csv_file("payer_360_mco_hierarchy.csv")
    benefit_done: set[tuple] = set()
    hierarchy_done: set[tuple] = set()
    h_count = 0
    b_count = 0

    for row in hierarchy:
        parent_id = row["mdm_parent_id"]
        child_id = row["mdm_child_id"]
        benefit = row["benefit_type"]

        # PARENT_OF (deduplicated)
        key = (parent_id, child_id)
        if key not in hierarchy_done:
            run(driver, CREATE_HIERARCHY_CYPHER, {
                "parent_id": parent_id,
                "child_id": child_id,
            })
            hierarchy_done.add(key)
            h_count += 1

        # HAS_BENEFIT_TYPE on child (deduplicated)
        bkey = (child_id, benefit)
        if bkey not in benefit_done:
            run(driver, LINK_BENEFIT_CYPHER, {
                "mco_id": child_id,
                "benefit_type": benefit,
            })
            benefit_done.add(bkey)
            b_count += 1

    print(f"  {h_count} PARENT_OF relationships created.")
    print(f"  {b_count} HAS_BENEFIT_TYPE relationships created.")

    # ── Verification ───────────────────────────────────────────────────────────
    print("\nVerifying graph...")
    with driver.session() as session:
        counts = {
            "MCO nodes": session.run("MATCH (m:MCO) RETURN count(m) AS c").single()["c"],
            "BookOfBusiness nodes": session.run("MATCH (b:BookOfBusiness) RETURN count(b) AS c").single()["c"],
            "BenefitType nodes": session.run("MATCH (b:BenefitType) RETURN count(b) AS c").single()["c"],
            "Region nodes": session.run("MATCH (r:Region) RETURN count(r) AS c").single()["c"],
            "PARENT_OF edges": session.run("MATCH ()-[r:PARENT_OF]->() RETURN count(r) AS c").single()["c"],
            "HAS_BENEFIT_TYPE edges": session.run("MATCH ()-[r:HAS_BENEFIT_TYPE]->() RETURN count(r) AS c").single()["c"],
            "BELONGS_TO edges": session.run("MATCH ()-[r:BELONGS_TO]->() RETURN count(r) AS c").single()["c"],
        }
        for label, count in counts.items():
            print(f"  {label}: {count}")

        # Test Aetna hierarchy
        print("\n--- Sample: Aetna hierarchy ---")
        result = session.run("""
            MATCH (p:MCO {name: 'Aetna'})-[:PARENT_OF]->(child:MCO)
            RETURN child.name AS child, child.book_of_business AS bob
            LIMIT 5
        """)
        for rec in result:
            print(f"  Aetna -> {rec['child']} [{rec['bob']}]")

        # Test UHC children
        print("\n--- Sample: UHC children ---")
        result = session.run("""
            MATCH (p:MCO)-[:PARENT_OF]->(child:MCO)
            WHERE p.name CONTAINS 'UnitedHealth'
            RETURN child.name AS child, child.type AS type
            LIMIT 5
        """)
        for rec in result:
            print(f"  UHC -> {rec['child']} [{rec['type']}]")

    driver.close()
    print("\nNeo4j graph load complete.")


if __name__ == "__main__":
    main()
