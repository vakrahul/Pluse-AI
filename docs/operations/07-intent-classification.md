# Operation: Intent Classification

## Purpose
Route user questions to the correct data source: Cube (analytics), Neo4j (graph), or ChromaDB (knowledge).

## Intents
| Intent | Routes To | Example |
|--------|-----------|---------|
| analytics | Cube + PostgreSQL | "Show monthly sales trend" |
| graph | Neo4j | "Largest referral network" |
| knowledge | ChromaDB | "Why is Dr. X Gold tier?" |
| hybrid | All three | "Gold criteria + referral network for Dr. X" |

## Implementation
- Rule-based classifier in `backend/agents/intent_agent.py`
- Optional LLM enhancement via Cerebras when API key set
