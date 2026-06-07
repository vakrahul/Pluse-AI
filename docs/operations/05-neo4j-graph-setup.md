# Operation: Neo4j Graph Setup

## Purpose
Load HCP referral networks, prescribing relationships, and rep visit patterns into Neo4j.

## Graph Schema
- Nodes: HCP, Product, Hospital, Territory, SalesRep
- Relationships: PRESCRIBES, WORKS_AT, LOCATED_IN, REFERS, VISITS

## Step-by-step
```powershell
docker compose -f infrastructure/docker/docker-compose.yml up -d neo4j
cd data/neo4j
pip install -r requirements.txt
python load_graph.py
```

## Sample Cypher
```cypher
MATCH (h:HCP)-[:REFERS*1..2]->(t:HCP)
RETURN h.name, count(t) AS influenced ORDER BY influenced DESC LIMIT 10
```
