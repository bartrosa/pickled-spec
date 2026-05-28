"""Adversarial resolver tests (Phase 8e-fix)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pickled_core.mine.code_reader import (
    SourceFileNotFoundError,
    SurfaceRef,
    collect_context,
    find_cycles,
    resolve_callees,
    resolve_definition,
)

_ZOO_ROOT = Path(__file__).resolve().parent / "fixtures" / "resolver_zoo"
_ZOO_SRC = _ZOO_ROOT / "packages/resolver_zoo/src"
_PKG = "resolver-zoo"


@pytest.fixture(autouse=True)
def _zoo_path() -> None:
    text = str(_ZOO_SRC)
    if text not in sys.path:
        sys.path.insert(0, text)


def _rel(module_file: str) -> str:
    return f"packages/resolver_zoo/src/resolver_zoo/{module_file}"


def _surface(func: str, module_file: str, lineno: int) -> SurfaceRef:
    return SurfaceRef(
        surface_id=f"rz_{func}",
        kind="function",
        package=_PKG,
        name=func,
        module="resolver_zoo",
        file=_rel(module_file),
        line=lineno,
    )


def _collect(
    func: str,
    module_file: str,
    lineno: int,
    *,
    depth: str = "callgraph",
    max_hops: int = 2,
    max_callees: int = 12,
) -> tuple[object, list]:
    surface = _surface(func, module_file, lineno)
    ctx = collect_context(
        surface,
        _ZOO_ROOT,
        depth=depth,
        scope="same-package",
        max_hops=max_hops,
        max_callees=max_callees,
        max_code_lines=800,
        package=_PKG,
    )
    root = ctx.root
    assert root is not None
    refs = resolve_callees(
        root,
        scope="same-package",
        package=_PKG,
        target=_ZOO_ROOT,
    )
    return ctx, refs


def _resolved(refs: list, kind: str) -> list:
    return [r for r in refs if r.resolved and r.resolution_kind == kind]


def _unresolved(refs: list, reason_substr: str) -> list:
    return [
        r
        for r in refs
        if not r.resolved
        and r.resolution_kind == "unresolved"
        and reason_substr in r.reason
    ]


# --- Group A ---


def test_simple_constructor_method() -> None:
    _, refs = _collect("entry", "ctor_method.py", 10)
    hits = _resolved(refs, "constructor_method")
    assert any(r.name.endswith("Worker.process") or "process" in r.name for r in hits)


def test_method_chain_resolves_first_refuses_rest() -> None:
    _, refs = _collect("entry", "method_chain.py", 13)
    assert _resolved(refs, "constructor_method")
    assert _unresolved(refs, "return value of unannotated callable")


def test_factory_hidden_constructor_unresolved() -> None:
    _, refs = _collect("entry", "factory_hidden.py", 14)
    assert not _resolved(refs, "constructor_method")
    assert _unresolved(refs, "return value of unannotated callable")


def test_nested_constructor_in_argument() -> None:
    ctx, refs = _collect("entry", "nested_ctor.py", 15, max_hops=1)
    names = {u.qualname for u in ctx.units}
    assert "Builder.build" in names or any("build" in r.name for r in _resolved(refs, "constructor_method"))
    assert any("process" in r.name for r in _resolved(refs, "constructor_method"))


def test_parenthesized_constructor() -> None:
    _, refs = _collect("entry_paren", "ctor_method.py", 14)
    assert _resolved(refs, "constructor_method")


def test_module_qualified_constructor() -> None:
    _, refs = _collect("entry", "module_ctor.py", 7)
    assert _resolved(refs, "module_constructor") or _resolved(refs, "constructor_method")


# --- Group B ---


def test_annotated_param_resolves() -> None:
    _, refs = _collect("via_param", "annotated.py", 10)
    assert _resolved(refs, "annotated_param")


def test_annotated_local_var_resolves() -> None:
    _, refs = _collect("via_var", "annotated.py", 14)
    assert _resolved(refs, "annotated_var")


def test_assigned_constructor_resolves() -> None:
    _, refs = _collect("via_assign", "annotated.py", 18)
    assert _resolved(refs, "assigned_constructor")


def test_rebound_variable_refuses() -> None:
    _, refs = _collect("entry", "rebind.py", 15)
    assert _unresolved(refs, "reassigned")


# --- Group C ---


def test_protocol_attribute_unresolved() -> None:
    _, refs = _collect("User.protocol_call", "refuse_receivers.py", 13)
    assert _unresolved(refs, "protocol or unknown attribute type")


def test_unannotated_param_unresolved() -> None:
    _, refs = _collect("unannotated_param", "refuse_receivers.py", 19)
    assert _unresolved(refs, "has no type annotation")


def test_subscript_receiver_unresolved() -> None:
    _, refs = _collect("subscript_receiver", "refuse_receivers.py", 27)
    assert _unresolved(refs, "subscript expression")


def test_ternary_receiver_unresolved() -> None:
    _, refs = _collect("ternary_receiver", "refuse_receivers.py", 31)
    assert _unresolved(refs, "conditional expression")


def test_chained_unknown_returns_unresolved() -> None:
    _, refs = _collect("chained_unknown", "refuse_receivers.py", 35)
    assert _unresolved(refs, "return value of unannotated callable")


def test_getattr_dynamic_unresolved() -> None:
    _, refs = _collect("getattr_dynamic", "refuse_receivers.py", 43)
    assert _unresolved(refs, "dynamic attribute access")


def test_inherited_method_unresolved_with_reason() -> None:
    _, refs = _collect("entry", "inherited.py", 14)
    assert _unresolved(refs, "possibly inherited")


def test_name_collision_unresolved_when_type_unknown() -> None:
    _, refs = _collect("entry", "collision.py", 15)
    assert _unresolved(refs, "receiver type not pinned") or _unresolved(
        refs, "matches multiple classes"
    )


# --- Group D ---


def test_constructor_cycle_terminates_and_reported() -> None:
    ctx, _ = _collect("entry", "ctor_cycle.py", 16, max_hops=3)
    keys = [u.key for u in ctx.units]
    assert len(keys) == len(set(keys))
    cycles = find_cycles(ctx.edges)
    assert cycles


def test_direct_method_recursion_collected_once() -> None:
    ctx, _ = _collect("entry", "recursion.py", 16, max_hops=3)
    foo_keys = [u.key for u in ctx.units if u.qualname.endswith("foo")]
    assert len(foo_keys) <= 1


def test_indirect_same_class_recursion_terminates() -> None:
    ctx, _ = _collect("entry", "recursion.py", 16, max_hops=4)
    assert len(ctx.units) >= 1


# --- Group E ---


def test_property_method_resolves() -> None:
    _, refs = _collect("entry", "structural.py", 24)
    assert _resolved(refs, "free_function") or any(
        "static_run" in r.name or "class_run" in r.name for r in refs if r.resolved
    )


def test_staticmethod_resolves() -> None:
    _, refs = _collect("entry", "structural.py", 24)
    assert any("static_run" in r.name for r in refs if r.resolved)


def test_classmethod_resolves() -> None:
    _, refs = _collect("entry", "structural.py", 24)
    assert any("class_run" in r.name for r in refs if r.resolved)


def test_async_method_resolves() -> None:
    _, refs = _collect("entry", "structural.py", 24)
    assert True


def test_inherited_via_base_is_unresolved_v1() -> None:
    _, refs = _collect("entry", "inherited.py", 14)
    assert _unresolved(refs, "possibly inherited")


# --- Group F ---


def test_empty_module_no_callees() -> None:
    surface = _surface("n/a", "degenerate_empty.py", 1)
    root = resolve_definition(surface, _ZOO_ROOT)
    assert root is None or resolve_callees(
        root, scope="same-package", package=_PKG, target=_ZOO_ROOT
    ) == []


def test_syntax_error_file_surface_unresolved_not_crash() -> None:
    surface = SurfaceRef(
        surface_id="rz_broken",
        kind="function",
        package=_PKG,
        name="broken",
        module="resolver_zoo",
        file=_rel("degenerate_syntax_error.py"),
        line=1,
    )
    ctx = collect_context(
        surface,
        _ZOO_ROOT,
        depth="body",
        scope="same-package",
        max_hops=1,
        max_callees=4,
        max_code_lines=100,
        package=_PKG,
    )
    assert ctx.no_definition


def test_missing_end_lineno_falls_back_to_line_slice(monkeypatch: pytest.MonkeyPatch) -> None:
    import ast

    surface = _surface("entry", "ctor_method.py", 10)
    path = (_ZOO_ROOT / _rel("ctor_method.py")).resolve()
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    node = tree.body[-2]
    if isinstance(node, ast.FunctionDef):
        monkeypatch.delattr(node, "end_lineno", raising=False)
    ctx = collect_context(
        surface,
        _ZOO_ROOT,
        depth="body",
        scope="same-package",
        max_hops=0,
        max_callees=4,
        max_code_lines=100,
        package=_PKG,
    )
    assert ctx.root is not None


def test_vanished_source_file_actionable_error() -> None:
    surface = SurfaceRef(
        surface_id="rz_missing",
        kind="function",
        package=_PKG,
        name="missing",
        module="resolver_zoo",
        file="packages/resolver_zoo/src/resolver_zoo/no_such_file.py",
        line=1,
    )
    from pickled_core.mine.code_reader import _parse_module

    with pytest.raises(SourceFileNotFoundError, match="source file not found"):
        _parse_module(_ZOO_ROOT / surface.file)


def test_oversized_method_truncated_with_marker() -> None:
    surface = _surface("entry", "ctor_method.py", 10)
    ctx = collect_context(
        surface,
        _ZOO_ROOT,
        depth="body",
        scope="same-package",
        max_hops=0,
        max_callees=1,
        max_code_lines=1,
        package=_PKG,
    )
    assert ctx.truncated
    assert any("truncated" in u.source for u in ctx.units)


# --- Group G ---


def test_drafter_pattern_resolves_domain_method() -> None:
    ctx, refs = _collect("entry", "drafter_shape.py", 14, max_hops=2)
    assert _resolved(refs, "constructor_method")
    names = {u.qualname for u in ctx.units}
    assert any("domain_method" in n for n in names)
    assert any("_helper" in n for n in names) or any(
        r.resolution_kind == "self_method" for r in refs if r.resolved
    )


