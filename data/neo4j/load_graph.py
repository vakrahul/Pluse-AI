#!/usr/bin/env python3
"""Load PostgreSQL healthcare data into Neo4j graph.

Uses UNWIND batch inserts (500 rows per tx) instead of individual
session.run() calls — dramatically faster and avoids socket timeouts.
Includes a Neo4j readiness check that waits up to 90 seconds.
"""

from __future__ import annotations

import os
import random
import time

import psycopg2
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

PG = dict(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    dbname=os.getenv("POSTGRES_DB", "healthcare_analytics"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4jpassword")

BATCH_SIZE = 500  # rows per UNWIND transaction


# ── Helpers ───────────────────────────────────────────────────────────────────

def pg_query(sql: str) -> list[tuple]:
    conn = psycopg2.connect(**PG)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def wait_for_neo4j(uri: str, user: str, password: str, timeout: int = 90) -> GraphDatabase:
    """Block until Neo4j is accepting connections, then return the driver."""
    print(f"Waiting for Neo4j at {uri} (timeout={timeout}s)...")
    deadline = time.time() + timeout
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password),
                                          connection_timeout=5)
            with driver.session() as session:
                session.run("RETURN 1")
            print(f"  Neo4j ready after {attempt} attempt(s).")
            return driver
        except (ServiceUnavailable, AuthError, Exception) as e:
            remaining = int(deadline - time.time())
            print(f"  Not ready yet ({e.__class__.__name__}), retrying... ({remaining}s left)")
            time.sleep(5)
    raise RuntimeError(f"Neo4j did not become ready within {timeout}s — is the container running?")


def batches(rows: list, size: int):
    """Yield successive chunks of `size` from rows."""
    for i in range(0, len(rows), size):
        yield rows[i : i + size]


def unwind(session, cypher: str, batch: list[dict]) -> None:
    """Execute an UNWIND query with a batch of parameter dicts."""
    session.run(cypher, rows=batch)


# ── Loaders ───────────────────────────────────────────────────────────────────

def clear_db(driver) -> None:
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    print("  Cleared existing graph data.")


def load_territories(driver) -> None:
    rows = pg_query("SELECT territory_id, territory_name, region FROM dim.territory_master")
    data = [{"id": r[0], "name": r[1], "region": r[2]} for r in rows]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session,
                   "UNWIND $rows AS r CREATE (:Territory {territory_id:r.id, name:r.name, region:r.region})",
                   batch)
    print(f"  Territory: {len(data):,}")


def load_hospitals(driver) -> None:
    rows = pg_query("SELECT hospital_id, hospital_name, city, territory_id FROM dim.hospital_master")
    data = [{"id": r[0], "name": r[1], "city": r[2], "tid": r[3]} for r in rows]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session,
                   "UNWIND $rows AS r CREATE (:Hospital {hospital_id:r.id, name:r.name, city:r.city, territory_id:r.tid})",
                   batch)
    print(f"  Hospital: {len(data):,}")


def load_products(driver) -> None:
    rows = pg_query("SELECT product_id, product_name, therapeutic_area FROM dim.product_master")
    data = [{"id": r[0], "name": r[1], "area": r[2]} for r in rows]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session,
                   "UNWIND $rows AS r CREATE (:Product {product_id:r.id, name:r.name, therapeutic_area:r.area})",
                   batch)
    print(f"  Product: {len(data):,}")


def load_sales_reps(driver) -> None:
    rows = pg_query("SELECT rep_id, first_name, last_name, territory_id FROM dim.sales_rep_master")
    data = [{"id": r[0], "name": f"{r[1]} {r[2]}", "tid": r[3]} for r in rows]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session,
                   "UNWIND $rows AS r CREATE (:SalesRep {rep_id:r.id, name:r.name, territory_id:r.tid})",
                   batch)
    print(f"  SalesRep: {len(data):,}")


def load_hcps(driver) -> None:
    rows = pg_query("""
        SELECT hcp_id, first_name, last_name, specialty, tier,
               city, hospital_id, territory_id, referral_count, is_kol
        FROM dim.hcp_master
    """)
    data = [
        {"id": r[0], "name": f"{r[1]} {r[2]}", "spec": r[3], "tier": r[4],
         "city": r[5], "hid": r[6], "tid": r[7], "rc": r[8], "kol": r[9]}
        for r in rows
    ]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session, """
                UNWIND $rows AS r
                CREATE (:HCP {
                    hcp_id:r.id, name:r.name, specialty:r.spec, tier:r.tier,
                    city:r.city, hospital_id:r.hid, territory_id:r.tid,
                    referral_count:r.rc, is_kol:r.kol
                })
            """, batch)
    print(f"  HCP: {len(data):,}")


def load_relationships(driver) -> None:
    with driver.session() as session:
        # Hospital → Territory
        session.run("""
            MATCH (h:Hospital), (t:Territory)
            WHERE h.territory_id = t.territory_id
            MERGE (h)-[:LOCATED_IN]->(t)
        """)
        # HCP → Hospital
        session.run("""
            MATCH (h:HCP), (hos:Hospital)
            WHERE h.hospital_id = hos.hospital_id
            MERGE (h)-[:WORKS_AT]->(hos)
        """)
    print("  Structural relationships created.")


def load_prescribes(driver) -> None:
    rows = pg_query("""
        SELECT hcp_id, product_id, SUM(rx_count)::int, MAX(rx_date)::text
        FROM fact.prescription_fact
        GROUP BY hcp_id, product_id
    """)
    data = [{"hid": r[0], "pid": r[1], "rx": r[2], "dt": str(r[3])} for r in rows]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session, """
                UNWIND $rows AS r
                MATCH (h:HCP {hcp_id:r.hid}), (p:Product {product_id:r.pid})
                MERGE (h)-[rel:PRESCRIBES]->(p)
                SET rel.rx_count=r.rx, rel.last_rx_date=r.dt
            """, batch)
    print(f"  PRESCRIBES edges: {len(data):,}")


def load_visits(driver) -> None:
    rows = pg_query("""
        SELECT rep_id, hcp_id, COUNT(*)::int, MAX(interaction_date)::text
        FROM fact.interaction_fact
        GROUP BY rep_id, hcp_id
    """)
    data = [{"rid": r[0], "hid": r[1], "cnt": r[2], "dt": str(r[3])} for r in rows]
    with driver.session() as session:
        for batch in batches(data, BATCH_SIZE):
            unwind(session, """
                UNWIND $rows AS r
                MATCH (rep:SalesRep {rep_id:r.rid}), (h:HCP {hcp_id:r.hid})
                MERGE (rep)-[v:VISITS]->(h)
                SET v.count=r.cnt, v.last_visit=r.dt
            """, batch)
    print(f"  VISITS edges: {len(data):,}")


def load_referrals(driver) -> None:
    """Generate REFERS edges — batch UNWIND to avoid individual query overhead."""
    hcps = pg_query(
        "SELECT hcp_id, specialty, referral_count FROM dim.hcp_master WHERE referral_count > 0"
    )
    all_ids = [h[0] for h in hcps]
    random.seed(42)

    refers_data = []
    for hcp_id, specialty, ref_count in hcps:
        targets = random.sample(all_ids, min(ref_count, len(all_ids) - 1))
        for target in targets:
            if target == hcp_id:
                continue
            refers_data.append({
                "from_id": hcp_id,
                "to_id": target,
                "strength": round(random.uniform(0.3, 1.0), 2),
            })

    with driver.session() as session:
        for batch in batches(refers_data, BATCH_SIZE):
            unwind(session, """
                UNWIND $rows AS r
                MATCH (a:HCP {hcp_id:r.from_id}), (b:HCP {hcp_id:r.to_id})
                MERGE (a)-[rel:REFERS]->(b)
                SET rel.strength=r.strength, rel.referral_count=1
            """, batch)
    print(f"  REFERS edges: {len(refers_data):,}")


# ── Schema ────────────────────────────────────────────────────────────────────

def apply_schema(driver) -> None:
    schema_path = os.path.join(os.path.dirname(__file__), "schema.cypher")
    if not os.path.exists(schema_path):
        print("  No schema.cypher found — skipping index creation.")
        return
    with driver.session() as session:
        for stmt in open(schema_path, encoding="utf-8").read().split(";"):
            stmt = stmt.strip()
            if stmt and not stmt.startswith("//"):
                try:
                    session.run(stmt)
                except Exception as e:
                    print(f"  Schema warn: {e}")
    print("  Schema/indexes applied.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # Wait for Neo4j to be fully ready before starting
    driver = wait_for_neo4j(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, timeout=90)

    apply_schema(driver)

    print("Clearing old data...")
    clear_db(driver)

    print("Loading nodes...")
    load_territories(driver)
    load_hospitals(driver)
    load_products(driver)
    load_sales_reps(driver)
    load_hcps(driver)

    print("Loading relationships...")
    load_relationships(driver)
    load_prescribes(driver)
    load_visits(driver)

    print("Loading referral network...")
    load_referrals(driver)

    with driver.session() as session:
        counts = session.run(
            "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY label"
        ).data()
        for c in counts:
            print(f"  {c['label']}: {c['cnt']:,}")

    driver.close()
    print("Neo4j load complete.")


if __name__ == "__main__":
    main()
