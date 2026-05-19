from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def migration_file() -> Path:
    return FIXTURES / "migrations" / "001_create_users.sql"


@pytest.fixture
def expected_users_schema() -> Path:
    return FIXTURES / "expected_schemas" / "users.yaml"
