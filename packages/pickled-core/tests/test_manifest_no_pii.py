from __future__ import annotations

import json
from pathlib import Path

from pickled_core.telemetry import start_run


def test_manifest_keys_subset_of_whitelist(tmp_path: Path) -> None:
    whitelist = {
        "run_id",
        "config_sha256",
        "pricing_sha256",
        "git_sha",
        "hostname_truncated_8",
        "python_version",
        "created_at_utc",
    }
    with start_run(runs_dir=tmp_path) as run:
        m = json.loads((run.run_dir / "manifest.json").read_text(encoding="utf-8"))
        assert set(m.keys()) <= whitelist
        for v in m.values():
            if isinstance(v, str):
                assert "@" not in v, "no email-like values"
                assert not v.startswith("/"), "no absolute paths"
                assert len(v) <= 64, "no long strings from env"
