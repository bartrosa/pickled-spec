# Code context: run_all

- **Surface id:** pickled_diff_run_all
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 70 | **Truncated:** True

## Root: pickled_diff.gates_runner.run_all

```python
def run_all(workdir: Path | str) -> list[GateResult]:
    """Run differential oracle gate when ``pickled.diff.yaml`` is present."""
    root = Path(workdir).resolve()
    cfg = _load_config(root)
    if not cfg:
        return [
            GateResult(
                gate_name="diff.config",
                verdict=Verdict.WARN,
                notes="missing pickled.diff.yaml or diff/pickled.diff.yaml",
            )
        ]

    try:
        oracle_argv = _resolve_argv(_argv_list(cfg.get("oracle_command"), "oracle_command"), root)
        candidate_argv = _resolve_argv(
            _argv_list(cfg.get("candidate_command"), "candidate_command"), root
        )
        corpus_ref = cfg.get("corpus")
        if not isinstance(corpus_ref, str):
            raise ValueError('config key "corpus" must be a path string')
        comparator_name = str(cfg.get("comparator", "exact"))
        timeout = float(cfg.get("timeout_seconds", 30))
        corpus = _load_corpus(root, corpus_ref)
    except (ValueError, FileNotFoundError, json.JSONDecodeError, TypeError) as exc:
        return [
            GateResult(
                gate_name="diff.config",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        ]

    oracle_cmd = list(oracle_argv)
    candidate_cmd = list(candidate_argv)
    if oracle_cmd[0] in {"python", "python3"} and len(oracle_cmd) > 1:
        oracle_cmd[0] = sys.executable
    if candidate_cmd[0] in {"python", "python3"} and len(candidate_cmd) > 1:
        candidate_cmd[0] = sys.executable

    gate = DifferentialOracleGate(
        oracle=SubprocessRunner(
            oracle_cmd,
            name="oracle",
            timeout_seconds=timeout,
            cwd=root,
        ),
        candidate=SubprocessRunner(
            candidate_cmd,
            name="candidate",
            timeout_seconds=timeout,
            cwd=root,
        ),
        comparator=_comparator(comparator_name),
    )
    gr = gate.run(corpus)
    return [
        GateResult(
            gate_name="diff.differential_oracle",
            verdict=gr.verdict,
            findings=gr.findings,
            notes=gr.notes,
        )
    ]
```

## Callee: pickled_diff.gates_runner._load_config (hop 1)

```python
def _load_config(root: Path) -> dict[str, Any]:
    cfg_path = _find_config(root)
    if cfg_path is None:
        return {}
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}
```

## Notes

Collection stopped early because of --max-callees or --max-code-lines.
