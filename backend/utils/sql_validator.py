"""SQL validation guardrails."""

from __future__ import annotations

import re

import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import DML


BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "Empty SQL"

    if BLOCKED_KEYWORDS.search(sql):
        return False, "Only SELECT queries are allowed"

    parsed: list[Statement] = sqlparse.parse(sql)
    if not parsed:
        return False, "Could not parse SQL"

    for stmt in parsed:
        if stmt.get_type() != "SELECT" and stmt.token_first(skip_cm=True):
            first = stmt.token_first(skip_cm=True)
            if first and first.ttype in DML and first.value.upper() != "SELECT":
                return False, f"Blocked statement type: {first.value}"

    if "pg_catalog" in sql.lower() or "information_schema" in sql.lower():
        return False, "System catalog access blocked"

    if "limit" not in sql.lower():
        sql = sql.rstrip(";") + " LIMIT 1000"

    return True, sql
