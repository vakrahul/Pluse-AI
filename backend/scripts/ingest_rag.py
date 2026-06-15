#!/usr/bin/env python3
"""Ingest Payer360 RAG documents into ChromaDB."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.rag.chroma_client import chroma_rag

if __name__ == "__main__":
    print("Ingesting Payer360 knowledge base into ChromaDB (force reload)...")
    counts = chroma_rag.ingest_all(force=True)
    for name, count in counts.items():
        print(f"  {name}: {count} chunks")
    print("RAG ingestion complete.")
