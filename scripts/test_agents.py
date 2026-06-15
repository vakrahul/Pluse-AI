import sys
sys.path.insert(0, '.')

from backend.agents.state import AgentState
from backend.agents.intent_agent import intent_node, _rule_classify, _extract_entities
from backend.agents.catalog_agent import catalog_node
from backend.agents.graph_agent import graph_node
from backend.agents.rag_agent import rag_node
from backend.agents.sql_agent import sql_node
from backend.agents.validation_agent import validation_node
from backend.agents.response_agent import response_node
from backend.graph.cypher_templates import select_template, validate_cypher
from backend.services.catalog_service import catalog_service
print("All imports OK")

tests = [
    ("What is HPM value?", "knowledge"),
    ("Which table contains market share?", "metadata"),
    ("Show MCO hierarchy for Aetna", "hierarchy"),
    ("Show formulary coverage for Ocrevus", "analytics"),
    ("Explain formulary status and show coverage for Ocrevus", "hybrid"),
    ("Who is the parent of BlueCross?", "hierarchy"),
    ("What child plans does UHC own?", "hierarchy"),
    ("What is LAAD?", "knowledge"),
    ("Which columns relate to claims?", "metadata"),
]

print("\nIntent classification:")
all_pass = True
for q, expected in tests:
    got = _rule_classify(q)
    status = "PASS" if got == expected else "FAIL"
    if got != expected:
        all_pass = False
    print(f"  [{status}] {q[:50]!r} -> {got}")

print("\nEntity extraction:")
e = _extract_entities("Show formulary coverage for Ocrevus at Aetna in Medicare")
print(f"  brand={e.get('brand')}, mco={e.get('mco_name')}, bob={e.get('book_of_business')}")

print("\nCypher template selection:")
cypher, params = select_template("Show MCO hierarchy for Aetna", {"mco_name": "Aetna"})
print(f"  Hierarchy template OK, params={params}")
cypher2, params2 = select_template("What child plans does UHC own?", {"mco_name": "UHC"})
print(f"  Children template OK, params={params2}")

print(f"\n{'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
