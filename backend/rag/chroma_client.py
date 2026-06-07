"""ChromaDB vector store client."""

from __future__ import annotations

import os
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.rag.chunker import chunk_text
from backend.utils.config import settings

RAG_ROOT = Path(__file__).resolve().parents[2] / "data" / "rag"

COLLECTIONS = {
    "compliance": RAG_ROOT / "compliance",
    "products": RAG_ROOT / "products",
    "glossary": RAG_ROOT / "glossary",
    "segmentation": RAG_ROOT / "segmentation",
    "sales_guidelines": RAG_ROOT / "sales_guidelines",
}


class ChromaRAG:
    def __init__(self) -> None:
        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._initialized = False

    def _get_or_create(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def ingest_all(self, force: bool = False) -> dict[str, int]:
        counts = {}
        for collection_name, dir_path in COLLECTIONS.items():
            if not dir_path.exists():
                continue
            collection = self._get_or_create(collection_name)

            if force:
                # Delete and recreate so new documents are picked up
                try:
                    self.client.delete_collection(collection_name)
                except Exception:
                    pass
                collection = self._get_or_create(collection_name)
            elif collection.count() > 0:
                counts[collection_name] = collection.count()
                continue

            all_chunks = []
            for md_file in dir_path.glob("**/*.md"):
                text = md_file.read_text(encoding="utf-8")
                overlap = 0 if collection_name == "glossary" else 64
                size = 300 if collection_name == "glossary" else 512
                chunks = chunk_text(text, str(md_file.name), collection_name, size, overlap)
                all_chunks.extend(chunks)

            if all_chunks:
                collection.add(
                    ids=[c.chunk_id for c in all_chunks],
                    documents=[c.text for c in all_chunks],
                    metadatas=[{"source": c.source, "collection": c.collection} for c in all_chunks],
                )
            counts[collection_name] = collection.count()

        self._initialized = True
        return counts

    def query(
        self,
        query_text: str,
        collections: list[str] | None = None,
        n_results: int = 5,
    ) -> list[dict]:
        if not self._initialized:
            self.ingest_all()

        target = collections or list(COLLECTIONS.keys())
        all_results = []

        for name in target:
            try:
                collection = self._get_or_create(name)
                if collection.count() == 0:
                    continue
                results = collection.query(query_texts=[query_text], n_results=min(n_results, 5))
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    dist = results["distances"][0][i] if results["distances"] else 0
                    all_results.append({
                        "text": doc,
                        "source": meta.get("source", name),
                        "collection": name,
                        "score": round(1 - dist, 4),
                    })
            except Exception:
                continue

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:n_results]


chroma_rag = ChromaRAG()
