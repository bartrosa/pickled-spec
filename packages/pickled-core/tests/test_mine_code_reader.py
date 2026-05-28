"""Tests for mine code_reader."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pickled_core.mine.code_reader import (
    CalleeScope,
    SurfaceRef,
    collect_context,
    find_cycles,
    resolve_callees,
)

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "callgraph_target"
_PKG_SRC = _FIXTURE / "packages/callgraph_target/src"
_PEER_SRC = _FIXTURE / "packages/pickled_peer/src"


@pytest.fixture(autouse=True)
def _fixture_paths() -> None:
    for entry in (_PKG_SRC, _PEER_SRC):
        text = str(entry)
        if text not in sys.path:
            sys.path.insert(0, text)


def _ref(name: str, file: str, lineno: int) -> SurfaceRef:
    rel = f"packages/callgraph_target/src/callgraph_target/{file}"
    return SurfaceRef(
        surface_id=f"cg_{name.replace('.', '_')}",
        kind="function",
        package="callgraph-target",
        name=name,
        module="callgraph_target",
        file=rel,
        line=lineno,
    )


def test_body_depth_returns_root_body_only() -> None:
    surface = _ref("entry", "chain.py", 10)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="body",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    assert ctx.root is not None
    assert len(ctx.units) == 1
    assert "step_one" in ctx.root.source


def test_callgraph_depth_one_hop_collects_direct_callees() -> None:
    surface = _ref("entry", "chain.py", 10)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    names = {u.qualname for u in ctx.units}
    assert "entry" in names
    assert "step_one" in names
    assert "step_two" not in names


def test_callgraph_depth_two_hops() -> None:
    surface = _ref("entry", "chain.py", 10)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=2,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    names = {u.qualname for u in ctx.units}
    assert "step_two" in names


def test_cycle_does_not_infinite_loop() -> None:
    surface = _ref("ping", "cycle.py", 7)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=3,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    keys = [u.key for u in ctx.units]
    assert keys.count(ctx.root.key if ctx.root else "") <= 1
    assert len(keys) == len(set(keys))


def test_max_callees_cap_respected() -> None:
    surface = _ref("entry", "fanout.py", 40)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=3,
        max_code_lines=400,
        package="callgraph-target",
    )
    assert len(ctx.units) <= 3
    assert ctx.truncated


def test_max_code_lines_cap_respected() -> None:
    surface = _ref("entry", "fanout.py", 40)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=20,
        max_code_lines=5,
        package="callgraph-target",
    )
    total = sum(u.line_count for u in ctx.units)
    assert total <= 6
    assert ctx.truncated


def test_self_scope_resolves_same_class_methods() -> None:
    surface = _ref("Worker.run", "mixed.py", 14)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="self",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    names = {u.qualname for u in ctx.units}
    assert "Worker.helper" in names
    assert "entry" not in names


def test_same_package_scope_resolves_package_imports() -> None:
    surface = _ref("Worker.run", "mixed.py", 14)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    names = {u.qualname for u in ctx.units}
    assert "entry" in names


def test_any_pickled_scope_resolves_cross_package() -> None:
    surface = _ref("cross_entry", "cross_pkg.py", 7)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="any-pickled",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    modules = {u.module for u in ctx.units}
    assert any(m.startswith("pickled_peer") for m in modules)


def test_stdlib_calls_ignored() -> None:
    surface = _ref("Worker.run", "mixed.py", 14)
    root = collect_context(
        surface,
        _FIXTURE,
        depth="body",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    ).root
    assert root is not None
    refs = resolve_callees(
        root,
        scope="same-package",
        package="callgraph-target",
        target=_FIXTURE,
    )
    expressions = {r.expression for r in refs}
    assert "json.dumps" not in expressions


def test_protocol_dispatch_unresolved() -> None:
    surface = _ref("User.go", "protocol_demo.py", 12)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    assert any(
        not ref.resolved
        and ref.resolution_kind == "unresolved"
        and "protocol" in ref.reason.lower()
        for ref in ctx.unresolved
    )


def test_find_cycles_detects_ping_pong() -> None:
    edges = [
        ("callgraph_target:ping", "callgraph_target:pong"),
        ("callgraph_target:pong", "callgraph_target:ping"),
    ]
    cycles = find_cycles(edges)
    assert cycles


def _fixture_ref(qualname: str, rel_file: str, lineno: int) -> object:
    from pickled_core.mine.code_reader import SurfaceRef

    return SurfaceRef(
        surface_id="noise",
        kind="function",
        package="callgraph-target",
        name=qualname,
        module="callgraph_target",
        file=f"packages/callgraph_target/src/callgraph_target/{rel_file}",
        line=lineno,
    )


def test_stdlib_str_method_not_in_unresolved() -> None:
    surface = _fixture_ref("strip_only", "noise_demo.py", 13)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    expressions = {r.expression for r in ctx.unresolved}
    assert "text.strip" not in expressions
    assert not any("strip" in e for e in expressions)


def test_path_method_not_in_unresolved() -> None:
    surface = _fixture_ref("path_read", "noise_demo.py", 17)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    expressions = {r.expression for r in ctx.unresolved}
    assert not any("read_text" in e for e in expressions)


def test_decorator_call_not_a_callee() -> None:
    surface = _fixture_ref("entry", "decorator_demo.py", 14)
    root = collect_context(
        surface,
        _FIXTURE,
        depth="body",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    ).root
    assert root is not None
    refs = resolve_callees(
        root,
        scope="same-package",
        package="callgraph-target",
        target=_FIXTURE,
    )
    expressions = {r.expression for r in refs}
    assert "main.command" not in expressions


def test_literal_annotation_does_not_crash_resolver() -> None:
    surface = _fixture_ref("entry", "typing_literal.py", 8)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    assert ctx.root is not None


def test_own_method_still_resolved_despite_filter() -> None:
    surface = _fixture_ref("use_worker", "noise_demo.py", 22)
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=8,
        max_code_lines=400,
        package="callgraph-target",
    )
    names = {u.qualname for u in ctx.units}
    assert "Worker.process" in names


def test_find_cycles_empty_on_acyclic_chain() -> None:
    edges = [
        ("callgraph_target:entry", "callgraph_target:step_one"),
        ("callgraph_target:step_one", "callgraph_target:step_two"),
    ]
    assert find_cycles(edges) == []
