from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TERRAFORM_AVAILABLE = shutil.which("terraform") is not None or shutil.which("tofu") is not None
TRIVY_AVAILABLE = shutil.which("trivy") is not None


@pytest.fixture
def users_rds_dir() -> Path:
    return FIXTURES / "terraform" / "users_rds"


@pytest.fixture
def insecure_s3_dir() -> Path:
    return FIXTURES / "terraform" / "insecure_s3"


@pytest.fixture
def empty_plan() -> dict:
    return json.loads((FIXTURES / "plans" / "empty.json").read_text(encoding="utf-8"))


@pytest.fixture
def create_plan() -> dict:
    return json.loads((FIXTURES / "plans" / "create_only.json").read_text(encoding="utf-8"))


@pytest.fixture
def delete_plan() -> dict:
    return json.loads((FIXTURES / "plans" / "delete.json").read_text(encoding="utf-8"))
