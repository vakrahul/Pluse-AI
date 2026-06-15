"""Parameterized Cypher query templates for Payer360 MCO hierarchy — no destructive ops."""

from __future__ import annotations

TEMPLATES: dict[str, dict] = {
    "mco_hierarchy": {
        "description": "Show full hierarchy tree for a given MCO (3 levels deep)",
        "cypher": """
            MATCH (root:MCO)
            WHERE toLower(root.name) CONTAINS toLower($mco_name)
            OPTIONAL MATCH (root)-[:PARENT_OF*1..3]->(child:MCO)
            RETURN root.name AS root_mco, root.type AS root_type,
                   root.book_of_business AS root_bob,
                   collect(DISTINCT {
                       name: child.name,
                       type: child.type,
                       book_of_business: child.book_of_business,
                       region: child.region
                   }) AS children
            LIMIT 1
        """,
        "params": ["mco_name"],
    },
    "mco_parent": {
        "description": "Find the parent MCO of a given MCO",
        "cypher": """
            MATCH (parent:MCO)-[:PARENT_OF]->(child:MCO)
            WHERE toLower(child.name) CONTAINS toLower($mco_name)
            RETURN parent.name AS parent_mco, parent.type AS parent_type,
                   parent.book_of_business AS parent_bob,
                   child.name AS child_mco
            LIMIT 5
        """,
        "params": ["mco_name"],
    },
    "mco_children": {
        "description": "List direct child MCOs of a given parent MCO",
        "cypher": """
            MATCH (parent:MCO)-[:PARENT_OF]->(child:MCO)
            WHERE toLower(parent.name) CONTAINS toLower($mco_name)
            RETURN parent.name AS parent_mco,
                   child.name AS child_name,
                   child.type AS child_type,
                   child.book_of_business AS child_bob,
                   child.region AS region
            ORDER BY child.name
            LIMIT $limit
        """,
        "params": ["mco_name", "limit"],
    },
    "mco_benefit_types": {
        "description": "Show benefit types for a given MCO",
        "cypher": """
            MATCH (m:MCO)-[:HAS_BENEFIT_TYPE]->(b:BenefitType)
            WHERE toLower(m.name) CONTAINS toLower($mco_name)
            RETURN m.name AS mco_name, collect(b.name) AS benefit_types
            LIMIT 5
        """,
        "params": ["mco_name"],
    },
    "mcos_by_book_of_business": {
        "description": "List all MCOs under a given book of business",
        "cypher": """
            MATCH (m:MCO)-[:BELONGS_TO]->(b:BookOfBusiness)
            WHERE toLower(b.name) CONTAINS toLower($book_of_business)
            RETURN m.name AS mco_name, m.type AS mco_type, b.name AS book_of_business
            ORDER BY m.name
            LIMIT $limit
        """,
        "params": ["book_of_business", "limit"],
    },
    "national_mcos": {
        "description": "List all national MCOs",
        "cypher": """
            MATCH (m:MCO {is_national: true})
            RETURN m.name AS mco_name, m.type AS mco_type,
                   m.book_of_business AS book_of_business
            ORDER BY m.name
            LIMIT 20
        """,
        "params": [],
    },
    "mco_full_profile": {
        "description": "Full profile of an MCO including parent, children, and benefit types",
        "cypher": """
            MATCH (m:MCO)
            WHERE toLower(m.name) CONTAINS toLower($mco_name)
            OPTIONAL MATCH (parent:MCO)-[:PARENT_OF]->(m)
            OPTIONAL MATCH (m)-[:PARENT_OF]->(child:MCO)
            OPTIONAL MATCH (m)-[:HAS_BENEFIT_TYPE]->(bt:BenefitType)
            OPTIONAL MATCH (m)-[:BELONGS_TO]->(bob:BookOfBusiness)
            RETURN m.name AS mco_name, m.type AS mco_type,
                   parent.name AS parent_name,
                   collect(DISTINCT child.name) AS children,
                   collect(DISTINCT bt.name) AS benefit_types,
                   bob.name AS book_of_business
            LIMIT 1
        """,
        "params": ["mco_name"],
    },
}


def select_template(question: str, entities: dict) -> tuple[str, dict]:
    """Select the best Cypher template for a hierarchy question."""
    q = question.lower()
    mco_name = entities.get("mco_name", "")
    bob = entities.get("book_of_business", "")
    limit = entities.get("limit", 10)

    if bob and not mco_name:
        return TEMPLATES["mcos_by_book_of_business"]["cypher"], {
            "book_of_business": bob, "limit": limit
        }

    if "parent" in q or "who owns" in q or "owned by" in q:
        return TEMPLATES["mco_parent"]["cypher"], {"mco_name": mco_name or ""}

    if "children" in q or "child" in q or "plans under" in q or "owns" in q:
        return TEMPLATES["mco_children"]["cypher"], {"mco_name": mco_name or "", "limit": limit}

    if "benefit type" in q or "benefit types" in q:
        return TEMPLATES["mco_benefit_types"]["cypher"], {"mco_name": mco_name or ""}

    if "national" in q and not mco_name:
        return TEMPLATES["national_mcos"]["cypher"], {}

    if mco_name:
        return TEMPLATES["mco_hierarchy"]["cypher"], {"mco_name": mco_name}

    # Fallback: list all national MCOs
    return TEMPLATES["national_mcos"]["cypher"], {}


def validate_cypher(cypher: str) -> bool:
    """Block destructive Cypher operations."""
    upper = cypher.upper()
    blocked = ["DELETE", "DETACH", "DROP", "CREATE INDEX", "REMOVE", "SET ", "MERGE", "CREATE "]
    return not any(b in upper for b in blocked)
