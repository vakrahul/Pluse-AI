"""Document chunking for RAG knowledge base."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source: str
    collection: str
    chunk_id: str


def _make_id(collection: str, source: str, idx: int) -> str:
    """Generate a globally unique chunk ID that includes filename + index."""
    # Use a short hash of the source filename so IDs are stable and unique
    # across multiple files in the same collection.
    file_hash = hashlib.md5(source.encode()).hexdigest()[:8]
    return f"{collection}_{file_hash}_{idx}"


def chunk_text(
    text: str,
    source: str,
    collection: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> list[Chunk]:
    paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    chunks: list[Chunk] = []
    buffer = ""
    idx = 0

    for para in paragraphs:
        if len(buffer) + len(para) + 1 <= chunk_size:
            buffer = f"{buffer}\n\n{para}".strip() if buffer else para
        else:
            if buffer:
                chunks.append(Chunk(buffer, source, collection, _make_id(collection, source, idx)))
                idx += 1
            if len(para) > chunk_size:
                words = para.split()
                start = 0
                while start < len(words):
                    piece = " ".join(words[start : start + chunk_size // 5])
                    chunks.append(Chunk(piece, source, collection, _make_id(collection, source, idx)))
                    idx += 1
                    start += chunk_size // 5 - overlap // 10
                buffer = ""
            else:
                buffer = para

    if buffer:
        chunks.append(Chunk(buffer, source, collection, _make_id(collection, source, idx)))

    return chunks
