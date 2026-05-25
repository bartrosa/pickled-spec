"""Tests for :class:`pickled_data.drafter.MigrationDrafter`."""

from __future__ import annotations

from pickled_bdd.testing import CannedLLMClient
from pickled_data.drafter import RATIONALE_SENTINEL, MigrationDrafter

_VALID_SQL = """-- intent: add deleted_at to users
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  deleted_at TEXT
);
"""


def _with_rationale(body: str, rationale: str = "Added soft-delete column.") -> str:
    return f"{body.strip()}\n{RATIONALE_SENTINEL}\n{rationale}"


def test_drafts_valid_sql_from_intent() -> None:
    llm = CannedLLMClient(_with_rationale(_VALID_SQL))
    result = MigrationDrafter(llm).draft_from_intent(
        intent_text="add soft delete",
        dialect="sqlite",
    )
    assert "CREATE TABLE" in result.text
    assert result.warnings == ()
    assert result.rationale == "Added soft-delete column."


def test_warns_on_parse_failure() -> None:
    broken = "SELECT FROM ;;"
    llm = CannedLLMClient(_with_rationale(broken))
    result = MigrationDrafter(llm).draft_from_intent(
        intent_text="broken",
        dialect="sqlite",
    )
    assert result.text == broken.strip()
    assert len(result.warnings) >= 1


def test_warns_on_destructive_drop_table() -> None:
    sql = _with_rationale(
        "-- intent: drop users\nDROP TABLE users;\n",
        rationale="destructive",
    )
    llm = CannedLLMClient(sql)
    result = MigrationDrafter(llm).draft_from_intent(
        intent_text="drop",
        dialect="sqlite",
    )
    assert any("DROP TABLE" in w for w in result.warnings)


def test_handles_missing_rationale_sentinel() -> None:
    llm = CannedLLMClient(_VALID_SQL)
    result = MigrationDrafter(llm).draft_from_intent(
        intent_text="add column",
        dialect="sqlite",
    )
    assert result.rationale == ""
    assert "deleted_at" in result.text
