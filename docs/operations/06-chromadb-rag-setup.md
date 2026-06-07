# Operation: ChromaDB RAG Setup

## Purpose
Index compliance policies, segmentation rules, glossary, and sales guidelines for knowledge queries.

## Collections
| Collection | Source |
|------------|--------|
| compliance | data/rag/compliance/ |
| segmentation | data/rag/segmentation/ |
| glossary | data/rag/glossary/ |
| sales_guidelines | data/rag/sales_guidelines/ |

## Step-by-step
```powershell
pip install -r backend/requirements.txt
python backend/scripts/ingest_rag.py
```

## Retrieval Flow
1. Query embedded with ChromaDB default embedding
2. Top-k per collection (k=5)
3. Results merged and ranked by score
4. Passed to RAG agent for answer synthesis
