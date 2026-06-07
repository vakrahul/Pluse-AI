"""Parameterized Cypher query templates — no free-form destructive ops."""

from __future__ import annotations

TEMPLATES: dict[str, dict] = {
    "top_referrers": {
        "description": "HCPs with largest outbound referral network",
        "cypher": """
            MATCH (h:HCP)-[r:REFERS]->(target:HCP)
            WITH h, count(target) AS referral_out, sum(r.strength) AS total_strength
            RETURN h.name AS hcp_name, h.specialty AS specialty, h.city AS city,
                   h.tier AS tier, referral_out, round(total_strength, 2) AS strength
            ORDER BY referral_out DESC, total_strength DESC
            LIMIT $limit
        """,
        "params": ["limit"],
    },
    "referral_network": {
        "description": "Referral network for a specific HCP",
        "cypher": """
            MATCH (h:HCP)
            WHERE toLower(h.name) CONTAINS toLower($hcp_name)
            OPTIONAL MATCH (h)-[r:REFERS]->(target:HCP)
            RETURN h.name AS source, h.tier AS tier, h.specialty AS specialty,
                   collect({name: target.name, specialty: target.specialty, strength: r.strength}) AS referrals
            LIMIT 5
        """,
        "params": ["hcp_name"],
    },
    "influence_network": {
        "description": "HCPs who influence the largest referral networks (multi-hop)",
        "cypher": """
            MATCH (h:HCP)-[:REFERS*1..2]->(influenced:HCP)
            WITH h, count(DISTINCT influenced) AS influenced_count
            RETURN h.name AS hcp_name, h.specialty AS specialty, h.tier AS tier,
                   influenced_count
            ORDER BY influenced_count DESC
            LIMIT $limit
        """,
        "params": ["limit"],
    },
    "hcp_prescribing": {
        "description": "Products prescribed by HCP",
        "cypher": """
            MATCH (h:HCP)-[p:PRESCRIBES]->(prod:Product)
            WHERE toLower(h.name) CONTAINS toLower($hcp_name)
            RETURN h.name AS hcp_name, prod.name AS product, prod.therapeutic_area AS area,
                   p.rx_count AS rx_count
            ORDER BY p.rx_count DESC
            LIMIT 20
        """,
        "params": ["hcp_name"],
    },
    "rep_coverage_gaps": {
        "description": "Gold tier HCPs with low rep visit counts",
        "cypher": """
            MATCH (h:HCP {tier: 'Gold'})
            OPTIONAL MATCH (r:SalesRep)-[v:VISITS]->(h)
            WITH h, coalesce(sum(v.count), 0) AS visits
            WHERE visits < 3
            RETURN h.name AS hcp_name, h.city AS city, h.specialty AS specialty, visits
            ORDER BY visits ASC
            LIMIT $limit
        """,
        "params": ["limit"],
    },
}


def validate_cypher(cypher: str) -> bool:
    """Block destructive Cypher operations."""
    upper = cypher.upper()
    blocked = ["DELETE", "DETACH", "DROP", "CREATE INDEX", "REMOVE", "SET ", "MERGE"]
    # Allow MERGE only in load scripts, not agent queries
    agent_blocked = ["DELETE", "DETACH", "DROP", "CREATE ", "REMOVE", "MERGE", "SET "]
    return not any(b in upper for b in agent_blocked)
