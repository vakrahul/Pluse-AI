"""
Payer360 Metadata Catalog Service.

Loads table_catalog.json, column_catalog.json, relationship_catalog.json
and provides fast search methods to answer questions like:
  - Which table contains market share?
  - Which columns define formulary status?
  - Show all claims-related tables.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CATALOG_DIR = Path(__file__).resolve().parents[2] / "data" / "catalog"


class CatalogService:
    def __init__(self) -> None:
        self.tables: list[dict] = []
        self.columns: list[dict] = []
        self.relationships: list[dict] = []
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        try:
            self.tables = json.loads((CATALOG_DIR / "table_catalog.json").read_text(encoding="utf-8"))
            self.columns = json.loads((CATALOG_DIR / "column_catalog.json").read_text(encoding="utf-8"))
            self.relationships = json.loads((CATALOG_DIR / "relationship_catalog.json").read_text(encoding="utf-8"))
            self._loaded = True
            logger.info("Catalog loaded: %d tables, %d columns", len(self.tables), len(self.columns))
        except Exception as e:
            logger.error("Failed to load catalog: %s", e)
            self.tables, self.columns, self.relationships = [], [], []

    # ── Table search ──────────────────────────────────────────────────────────

    def search_tables(self, query: str, top_k: int = 5) -> list[dict]:
        """Find tables whose name, description, or subject area matches the query."""
        self._load()
        q = query.lower()
        scored: list[tuple[int, dict]] = []
        for tbl in self.tables:
            score = 0
            name = tbl.get("name", "").lower()
            desc = tbl.get("description", "").lower()
            subj = tbl.get("subject_area", "").lower()
            sample_q = tbl.get("sample_question", "").lower()

            if q in name:
                score += 10
            if q in desc:
                score += 5
            if q in subj:
                score += 4
            if q in sample_q:
                score += 3
            # keyword overlap
            for word in q.split():
                if len(word) < 3:
                    continue
                if word in name:
                    score += 3
                if word in desc:
                    score += 2
                if word in subj:
                    score += 1

            if score > 0:
                scored.append((score, tbl))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:top_k]]

    def get_table(self, table_name: str) -> dict | None:
        """Get a single table by exact or partial name match."""
        self._load()
        tbl_lower = table_name.lower()
        for tbl in self.tables:
            if tbl["name"].lower() == tbl_lower:
                return tbl
        for tbl in self.tables:
            if tbl_lower in tbl["name"].lower():
                return tbl
        return None

    def tables_by_subject(self, subject_area: str) -> list[dict]:
        """Return all tables for a given subject area."""
        self._load()
        return [t for t in self.tables if subject_area.lower() in t.get("subject_area", "").lower()]

    # ── Column search ─────────────────────────────────────────────────────────

    def search_columns(self, query: str, top_k: int = 10) -> list[dict]:
        """Find columns whose name or description matches the query."""
        self._load()
        q = query.lower()
        scored: list[tuple[int, dict]] = []
        for col in self.columns:
            score = 0
            col_name = col.get("column", "").lower()
            desc = col.get("description", "").lower()
            table = col.get("table", "").lower()

            if q in col_name:
                score += 8
            if q in desc:
                score += 4
            if q in table:
                score += 2
            for word in q.split():
                if len(word) < 3:
                    continue
                if word in col_name:
                    score += 3
                if word in desc:
                    score += 1

            if score > 0:
                scored.append((score, col))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]

    def get_table_columns(self, table_name: str) -> list[dict]:
        """Return all columns for a specific table."""
        self._load()
        tbl_lower = table_name.lower()
        return [c for c in self.columns if tbl_lower in c.get("table", "").lower()]

    # ── Relationship search ───────────────────────────────────────────────────

    def get_relationships(self, table_name: str) -> list[dict]:
        """Return all known relationships for a table."""
        self._load()
        tbl_lower = table_name.lower()
        return [
            r for r in self.relationships
            if tbl_lower in r.get("from_table", "").lower()
            or tbl_lower in r.get("to_table", "").lower()
        ]

    # ── Structured answer builder ─────────────────────────────────────────────

    def answer_metadata_question(self, question: str, entities: dict) -> dict[str, Any]:
        """
        Main entry point: takes a metadata question, returns a structured answer dict.
        Used by the catalog_agent.
        """
        self._load()
        q = question.lower()
        results: dict[str, Any] = {
            "question": question,
            "matched_tables": [],
            "matched_columns": [],
            "answer_text": "",
        }

        # 1. "which table / where / find table" → table search
        table_trigger = any(k in q for k in [
            "which table", "what table", "where is", "where can i find",
            "which database", "find table", "contains", "stores", "table for",
            "table has", "table with",
        ])

        # 2. "which columns / show columns / fields in" → column search
        col_trigger = any(k in q for k in [
            "which column", "what column", "show column", "list column",
            "columns in", "fields in", "columns for", "columns related",
            "attributes", "fields related",
        ])

        # 3. Subject area from entities
        subject_hint = entities.get("subject_area", "")

        # Build search terms from question (remove stopwords)
        stopwords = {"which", "what", "where", "show", "list", "all", "the", "a", "an",
                     "is", "are", "in", "for", "can", "i", "find", "table", "column",
                     "contains", "related", "to", "of", "and", "or"}
        search_terms = " ".join(w for w in q.split() if w not in stopwords and len(w) > 2)

        if not search_terms:
            search_terms = q

        if table_trigger or (not col_trigger and not subject_hint):
            tables = self.search_tables(search_terms)
            results["matched_tables"] = tables

        if col_trigger:
            cols = self.search_columns(search_terms)
            results["matched_columns"] = cols

        if subject_hint:
            subj_tables = self.tables_by_subject(subject_hint)
            existing_names = {t["name"] for t in results["matched_tables"]}
            results["matched_tables"] += [t for t in subj_tables if t["name"] not in existing_names]

        # Build human-readable answer text
        lines = []
        if results["matched_tables"]:
            lines.append(f"Found {len(results['matched_tables'])} relevant table(s):")
            for tbl in results["matched_tables"][:5]:
                schema = tbl.get("schema", "oasis_normalized")
                name = tbl.get("name", "")
                desc = tbl.get("description", "")[:100]
                subj = tbl.get("subject_area", "")
                lines.append(f"  - {schema}.{name} [{subj}]")
                if desc:
                    lines.append(f"    {desc}")

        if results["matched_columns"]:
            lines.append(f"\nFound {len(results['matched_columns'])} relevant column(s):")
            for col in results["matched_columns"][:8]:
                dtype = col.get("data_type", "")
                desc = col.get("description", "")[:80]
                tbl = col.get("table", "")
                lines.append(f"  - {col['column']} ({dtype}) in {tbl}: {desc}")

        if not lines:
            lines.append("No matching tables or columns found for your query.")
            lines.append("Try asking: 'Which table contains claims data?' or 'Show columns for formulary'")

        results["answer_text"] = "\n".join(lines)
        return results


# Singleton
catalog_service = CatalogService()
