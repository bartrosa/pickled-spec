"""AST call-graph extraction for the mine code stage."""

from __future__ import annotations

import ast
import importlib
import inspect
import sys
import types
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import click

from pickled_core.mine.types import ResolutionKind

Depth = Literal["signature", "body", "callgraph"]
CalleeScope = Literal["self", "same-package", "any-pickled"]

_STDLIB_TOP_LEVEL = frozenset(
    {
        "abc",
        "ast",
        "asyncio",
        "collections",
        "contextlib",
        "dataclasses",
        "enum",
        "functools",
        "importlib",
        "inspect",
        "io",
        "itertools",
        "json",
        "logging",
        "os",
        "pathlib",
        "re",
        "sys",
        "textwrap",
        "typing",
        "uuid",
        "warnings",
    }
)
_THIRD_PARTY_TOP = frozenset({"click", "pydantic", "yaml", "httpx", "requests"})
_TRUNCATION_LINE = "# ...(truncated {n} lines)..."
_REASON_PROTOCOL = "protocol or unknown attribute type"
_REASON_CHAINED_RETURN = "receiver is a return value of unannotated callable"
_REASON_SUBSCRIPT = "receiver is a subscript expression"
_REASON_CONDITIONAL = "receiver is a conditional expression"
_REASON_GETATTR = "dynamic attribute access"
_REASON_INHERITED = "method not found on class; possibly inherited (base not resolved in v1)"
_REASON_REBINDING = "variable '{name}' reassigned; type not stable"
_REASON_COLLISION = "method name matches multiple classes; receiver type not pinned"
_REASON_PARSE = "source file failed to parse"
_TYPING_FORM_NAMES = frozenset(
    {
        "Literal",
        "Annotated",
        "Union",
        "Optional",
        "ClassVar",
        "Final",
        "TypeVar",
        "Any",
        "Callable",
        "TypeAlias",
        "Protocol",
        "TypedDict",
        "NamedTuple",
        "Generic",
        "Never",
        "Self",
        "Type",
    }
)


@dataclass(frozen=True, slots=True)
class SurfaceRef:
    """One mineable surface with optional code location hints."""

    surface_id: str
    kind: str
    package: str
    name: str
    module: str = ""
    file: str = ""
    line: int = 0


@dataclass(frozen=True, slots=True)
class CalleeRef:
    """A call site and optional resolved target."""

    expression: str
    name: str
    module: str
    file: str
    lineno: int
    resolved: bool
    reason: str = ""
    key: str = ""
    resolution_kind: ResolutionKind = "unresolved"


@dataclass(frozen=True, slots=True)
class _ClassRef:
    module: str
    class_name: str
    file: Path


@dataclass
class _VarState:
    class_ref: _ClassRef | None = None
    stable: bool = True
    binding_kind: ResolutionKind = "unresolved"


def _callee_key(*, resolved: bool, module: str, name: str, expression: str) -> str:
    if resolved:
        return unit_key(module, name)
    return expression


@dataclass(frozen=True, slots=True)
class CodeUnit:
    """Collected source for one definition."""

    key: str
    module: str
    qualname: str
    file: str
    lineno: int
    source: str
    line_count: int
    hop: int = 0


@dataclass
class CodeContext:
    """Collected code context for one surface."""

    surface: SurfaceRef
    depth: Depth
    scope: CalleeScope
    max_hops: int
    root: CodeUnit | None
    units: list[CodeUnit] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    unresolved: list[CalleeRef] = field(default_factory=list)
    truncated: bool = False
    no_definition: bool = False


@dataclass
class CycleReport:
    """Aggregate cycle findings."""

    cycles: list[list[str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.cycles)


def unit_key(module: str, qualname: str) -> str:
    return f"{module}:{qualname}"


def find_cycles(edges: list[tuple[str, str]]) -> list[list[str]]:
    """Return simple cycles as lists of node keys (stdlib DFS)."""
    adj: dict[str, list[str]] = {}
    nodes: set[str] = set()
    for src, dst in edges:
        nodes.add(src)
        nodes.add(dst)
        adj.setdefault(src, []).append(dst)

    cycles: list[list[str]] = []
    visited: set[str] = set()
    stack: list[str] = []
    on_stack: set[str] = set()

    def dfs(node: str) -> None:
        visited.add(node)
        stack.append(node)
        on_stack.add(node)
        for nxt in adj.get(node, []):
            if nxt not in visited:
                dfs(nxt)
            elif nxt in on_stack:
                start = stack.index(nxt)
                cycle = stack[start:] + [nxt]
                if cycle not in cycles:
                    cycles.append(cycle)
        stack.pop()
        on_stack.remove(node)

    for node in sorted(nodes):
        if node not in visited:
            dfs(node)
    return cycles


def _package_module_prefix(package: str) -> str:
    return package.replace("-", "_")


def _scope_allows_module(module: str, *, package: str, scope: CalleeScope) -> bool:
    if not module:
        return False
    pkg_prefix = _package_module_prefix(package)
    if module == pkg_prefix or module.startswith(f"{pkg_prefix}."):
        return True
    return scope == "any-pickled" and (
        module.startswith("pickled_") or module.split(".", 1)[0].startswith("pickled_")
    )


def _is_ignored_external(module: str) -> bool:
    top = module.split(".", 1)[0]
    return top in _STDLIB_TOP_LEVEL or top in _THIRD_PARTY_TOP or top in sys.stdlib_module_names


def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _node_source(file_text: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(file_text, node)
    if segment is not None:
        return segment
    lines = file_text.splitlines()
    start = getattr(node, "lineno", 1) - 1
    end = getattr(node, "end_lineno", start + 1)
    return "\n".join(lines[start:end])


def _signature_source(node: ast.FunctionDef | ast.AsyncFunctionDef, file_text: str) -> str:
    doc = ast.get_docstring(node)
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    args = ast.unparse(node.args)
    ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    header = f"{prefix}def {node.name}({args}){ret}"
    if doc:
        return f'{header}\n    """{doc}"""'
    return header


def _line_count(source: str) -> int:
    return len(source.splitlines()) if source else 0


class SourceFileNotFoundError(FileNotFoundError):
    """Raised when an inventory-recorded source path is missing on disk."""


def _parse_module(path: Path) -> tuple[str, ast.Module]:
    if not path.is_file():
        msg = f"source file not found: {path}"
        raise SourceFileNotFoundError(msg)
    text = _read_file(path)
    tree = ast.parse(text, filename=str(path))
    return text, tree


def _find_node_at_line(
    tree: ast.Module,
    *,
    lineno: int,
    qualname: str,
) -> ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | None:
    if "." in qualname:
        class_name, _, method_name = qualname.partition(".")
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if item.name == method_name and item.lineno == lineno:
                            return item
                        if item.name == method_name:
                            return item
        return None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == qualname and node.lineno == lineno:
                return node
            if node.name == qualname:
                return node
    return None


def _local_function(
    tree: ast.Module,
    name: str,
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    return None


def _build_code_unit(
    *,
    path: Path,
    module: str,
    qualname: str,
    node: ast.AST,
    depth: Depth,
    hop: int,
) -> CodeUnit:
    file_text, _ = _parse_module(path)
    if depth == "signature" and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        source = _signature_source(node, file_text)
    else:
        source = _node_source(file_text, node)
    key = unit_key(module, qualname)
    return CodeUnit(
        key=key,
        module=module,
        qualname=qualname,
        file=str(path),
        lineno=getattr(node, "lineno", 0),
        source=source,
        line_count=_line_count(source),
        hop=hop,
    )


def resolve_definition(
    surface: SurfaceRef,
    target: Path,
) -> CodeUnit | None:
    """Locate the AST node for a surface and build its root code unit."""
    if not surface.file:
        return None
    path = (target / surface.file).resolve()
    if not path.is_file():
        path = Path(surface.file).resolve()
    if not path.is_file():
        return None
    try:
        file_text, tree = _parse_module(path)
    except SyntaxError:
        return None
    qualname = surface.name
    if surface.kind == "gate" and "." in surface.name:
        qualname = surface.name
    node = _find_node_at_line(tree, lineno=surface.line or 0, qualname=qualname)
    if node is None:
        return None
    if isinstance(node, ast.ClassDef):
        return None
    module = surface.module or _module_name_from_path(path, target)
    return _build_code_unit(
        path=path,
        module=module,
        qualname=qualname,
        node=node,
        depth="body",
        hop=0,
    )


def _module_name_from_path(path: Path, target: Path) -> str:
    try:
        rel = path.resolve().relative_to(target.resolve())
    except ValueError:
        rel = path
    parts = list(rel.parts)
    if "src" in parts:
        idx = parts.index("src")
        parts = parts[idx + 1 :]
    if parts and parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def _import_bindings(tree: ast.Module) -> dict[str, tuple[str, str]]:
    bindings: dict[str, tuple[str, str]] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                bindings[local] = (alias.name, local)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                full = f"{base}.{alias.name}" if base else alias.name
                bindings[local] = (full, local)
    return bindings


def _enclosing_class(tree: ast.Module, lineno: int) -> ast.ClassDef | None:
    best: ast.ClassDef | None = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            if start <= lineno <= end:
                best = node
    return best


def _call_expression(func: ast.expr) -> str:
    try:
        return ast.unparse(func)
    except Exception:
        return "<call>"


def _is_nested_self_dispatch(func: ast.expr) -> bool:
    if not isinstance(func, ast.Attribute):
        return False
    cur: ast.expr = func.value
    depth = 0
    while isinstance(cur, ast.Attribute):
        depth += 1
        cur = cur.value
    return isinstance(cur, ast.Name) and cur.id == "self" and depth >= 1


def _expr(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "<expr>"


def _unwrap_expr(node: ast.expr) -> ast.expr:
    while isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        node = node.operand
    return node


def _local_class(tree: ast.Module, name: str) -> ast.ClassDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _annotation_class_name(ann: ast.expr | None) -> str | None:
    if ann is None:
        return None
    if isinstance(ann, ast.Subscript):
        return None
    if isinstance(ann, ast.Name):
        if ann.id in _TYPING_FORM_NAMES:
            return None
        return ann.id
    if isinstance(ann, ast.Attribute):
        if ann.attr in _TYPING_FORM_NAMES:
            return None
        return ann.attr
    return None


def _make_callee(
    *,
    expression: str,
    resolved: bool,
    resolution_kind: ResolutionKind,
    name: str = "",
    module: str = "",
    file: str = "",
    lineno: int = 0,
    reason: str = "",
) -> CalleeRef:
    return CalleeRef(
        expression=expression,
        name=name,
        module=module,
        file=file,
        lineno=lineno,
        resolved=resolved,
        reason=reason,
        resolution_kind=resolution_kind if resolved else "unresolved",
        key=_callee_key(
            resolved=resolved,
            module=module,
            name=name,
            expression=expression,
        ),
    )


@dataclass
class _ResolverCtx:
    tree: ast.Module
    file_path: Path
    file_text: str
    package: str
    scope: CalleeScope
    target: Path
    unit: CodeUnit
    bindings: dict[str, tuple[str, str]]
    func: ast.FunctionDef | ast.AsyncFunctionDef
    var_states: dict[str, _VarState]
    unannotated_params: set[str]


def _init_var_states(ctx: _ResolverCtx) -> None:
    for arg in ctx.func.args.args:
        if arg.annotation is None:
            ctx.unannotated_params.add(arg.arg)
            continue
        cls = _annotation_class_name(arg.annotation)
        if not cls:
            continue
        cref = _resolve_class_name(ctx, cls, kind_hint="annotated_param")
        if cref is not None:
            ctx.var_states[arg.arg] = _VarState(
                class_ref=cref, stable=True, binding_kind="annotated_param"
            )

    for stmt in ctx.func.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            cls = _annotation_class_name(stmt.annotation)
            if cls:
                cref = _resolve_class_name(ctx, cls, kind_hint="annotated_var")
                if cref is not None:
                    ctx.var_states[stmt.target.id] = _VarState(
                        class_ref=cref, stable=True, binding_kind="annotated_var"
                    )
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    _apply_assignment(ctx, target.id, stmt.value)


def _apply_assignment(ctx: _ResolverCtx, name: str, value: ast.expr) -> None:
    value = _unwrap_expr(value)
    new_cref = _class_from_constructor_expr(ctx, value)
    if name in ctx.var_states:
        prev = ctx.var_states[name]
        if (
            prev.class_ref is not None
            and new_cref is not None
            and prev.class_ref.class_name == new_cref.class_name
        ):
            ctx.var_states[name] = _VarState(
                class_ref=new_cref, stable=True, binding_kind="assigned_constructor"
            )
        else:
            ctx.var_states[name] = _VarState(
                class_ref=None, stable=False, binding_kind="unresolved"
            )
        return
    if new_cref is not None:
        ctx.var_states[name] = _VarState(
            class_ref=new_cref, stable=True, binding_kind="assigned_constructor"
        )
        return
    ctx.var_states[name] = _VarState(class_ref=None, stable=False, binding_kind="unresolved")


def _source_path_for_object(obj: object) -> Path | None:
    if not (
        isinstance(obj, types.ModuleType)
        or inspect.isclass(obj)
        or inspect.isfunction(obj)
        or inspect.ismethod(obj)
    ):
        return None
    try:
        file_path = inspect.getsourcefile(obj)
    except TypeError:
        return None
    if file_path is None:
        return None
    return Path(file_path)


def _resolve_class_name(
    ctx: _ResolverCtx,
    class_name: str,
    *,
    kind_hint: ResolutionKind,
) -> _ClassRef | None:
    if class_name in _TYPING_FORM_NAMES:
        return None
    local = _local_class(ctx.tree, class_name)
    if local is not None:
        return _ClassRef(ctx.unit.module, class_name, ctx.file_path)
    if class_name in ctx.bindings:
        imported, _ = ctx.bindings[class_name]
        mod = imported.rsplit(".", 1)[0] if "." in imported else imported
        resolved = _resolve_imported(
            mod,
            class_name,
            target=ctx.target,
            package=ctx.package,
            scope=ctx.scope,
        )
        if resolved is not None:
            mod_name, _, path = resolved
            return _ClassRef(mod_name.rsplit(".", 1)[0], class_name, path)
    return None


def _class_from_constructor_expr(ctx: _ResolverCtx, node: ast.expr) -> _ClassRef | None:
    node = _unwrap_expr(node)
    if not isinstance(node, ast.Call):
        return None
    return _class_from_constructor_call(ctx, node)


def _class_from_constructor_call(ctx: _ResolverCtx, call: ast.Call) -> _ClassRef | None:
    func = call.func
    if isinstance(func, ast.Name):
        name = func.id
        local = _local_class(ctx.tree, name)
        if local is not None:
            return _ClassRef(ctx.unit.module, name, ctx.file_path)
        if name in ctx.bindings:
            imported, _ = ctx.bindings[name]
            top = imported.split(".", 1)[0]
            if _is_ignored_external(top):
                return None
            mod_path = imported if "." not in imported else imported.rsplit(".", 1)[0]
            resolved = _resolve_imported(
                mod_path,
                name,
                target=ctx.target,
                package=ctx.package,
                scope=ctx.scope,
            )
            if resolved is not None:
                mod, _, path = resolved
                base_mod = mod.rsplit(".", 1)[0] if "." in mod else mod
                return _ClassRef(base_mod, name, path)
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        mod_alias = func.value.id
        if mod_alias in ctx.bindings:
            imported, _ = ctx.bindings[mod_alias]
            top = imported.split(".", 1)[0]
            if _is_ignored_external(top):
                return None
            resolved = _resolve_imported(
                imported,
                func.attr,
                target=ctx.target,
                package=ctx.package,
                scope=ctx.scope,
            )
            if resolved is not None:
                mod, qual, path = resolved
                class_name = func.attr
                if "." in qual:
                    class_name = qual.split(".")[-1]
                base_mod = mod.rsplit(".", 1)[0] if "." in mod else mod
                return _ClassRef(base_mod, class_name, path)
    return None


def _method_on_class(
    ctx: _ResolverCtx,
    class_ref: _ClassRef,
    method: str,
    *,
    resolution_kind: ResolutionKind,
) -> CalleeRef | None:
    path = class_ref.file
    try:
        _, tree = _parse_module(path)
    except SyntaxError:
        return None
    found = _find_method_in_class(tree, class_ref.class_name, method)
    if found is None:
        expr = f"{class_ref.class_name}().{method}"
        return _make_callee(
            expression=expr,
            resolved=False,
            resolution_kind="unresolved",
            reason=_REASON_INHERITED,
        )
    qual, lineno = found
    return _make_callee(
        expression=f"{class_ref.class_name}.{method}",
        resolved=True,
        resolution_kind=resolution_kind,
        name=qual,
        module=class_ref.module,
        file=str(path),
        lineno=lineno,
    )


def _find_method_in_class(
    tree: ast.Module,
    class_name: str,
    method: str,
) -> tuple[str, int] | None:
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method:
                return f"{class_name}.{method}", item.lineno
            if isinstance(item, ast.FunctionDef) and item.name == method:
                for dec in item.decorator_list:
                    dec_name = _decorator_name(dec)
                    if dec_name in {"property", "staticmethod", "classmethod"}:
                        return f"{class_name}.{method}", item.lineno
    return None


def _decorator_name(dec: ast.expr) -> str | None:
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Attribute):
        return dec.attr
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name):
        return dec.func.id
    if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
        return dec.func.attr
    return None


_PATH_METHODS = frozenset(
    {
        "read_text",
        "write_text",
        "exists",
        "resolve",
        "mkdir",
        "parent",
        "name",
        "suffix",
        "stem",
        "is_file",
        "is_dir",
        "glob",
        "iterdir",
    }
)
_STR_METHODS = frozenset(
    {
        "strip",
        "split",
        "rsplit",
        "join",
        "format",
        "lower",
        "upper",
        "startswith",
        "endswith",
        "replace",
        "encode",
        "decode",
    }
)
_BYTES_METHODS = frozenset({"decode", "split", "strip"})
_DICT_METHODS = frozenset({"get", "keys", "values", "items", "update", "pop"})
_LIST_METHODS = frozenset({"append", "extend", "pop", "insert", "sort"})
_STDLIB_CONSTRUCTORS = frozenset({"Path", "str", "dict", "list", "set", "tuple", "open", "bytes"})
_BUILTIN_METHODS = _STR_METHODS | _BYTES_METHODS | _DICT_METHODS | _LIST_METHODS | _PATH_METHODS


def _stdlib_constructor_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name) and func.id in _STDLIB_CONSTRUCTORS:
        return func.id
    if isinstance(func, ast.Attribute) and func.attr in _STDLIB_CONSTRUCTORS:
        return func.attr
    return None


def _receiver_is_intra_project(ctx: _ResolverCtx, receiver: ast.expr) -> bool:
    receiver = _unwrap_expr(receiver)
    if isinstance(receiver, ast.Name) and receiver.id == "self":
        return True
    if isinstance(receiver, ast.Name):
        var = receiver.id
        if ctx.scope != "self" and var in ctx.bindings:
            imported, _ = ctx.bindings[var]
            if not _is_ignored_external(imported.split(".", 1)[0]):
                return True
        state = ctx.var_states.get(var)
        if state is not None and state.stable and state.class_ref is not None:
            return True
        if var not in ctx.var_states and _local_class(ctx.tree, var) is not None:
            return True
    if isinstance(receiver, ast.Call) and _class_from_constructor_call(ctx, receiver):
        return True
    if (
        isinstance(receiver, ast.Attribute)
        and isinstance(receiver.value, ast.Name)
        and receiver.value.id in ctx.bindings
    ):
        imported, _ = ctx.bindings[receiver.value.id]
        if not _is_ignored_external(imported.split(".", 1)[0]):
            return True
    return False


def _should_drop_noise_call(ctx: _ResolverCtx, call: ast.Call) -> bool:
    """Drop stdlib-surface noise; never drop resolvable intra-project calls."""
    if not isinstance(call.func, ast.Attribute):
        return False
    method = call.func.attr
    receiver = _unwrap_expr(call.func.value)
    if _receiver_is_intra_project(ctx, receiver):
        return False
    if isinstance(receiver, ast.Constant):
        if isinstance(receiver.value, str) and method in _STR_METHODS:
            return True
        if isinstance(receiver.value, bytes) and method in _BYTES_METHODS:
            return True
    if isinstance(receiver, ast.Call):
        ctor = _stdlib_constructor_name(receiver.func)
        if ctor == "Path" and method in _PATH_METHODS:
            return True
        if ctor == "str" and method in _STR_METHODS:
            return True
        if ctor == "bytes" and method in _BYTES_METHODS:
            return True
        if ctor == "dict" and method in _DICT_METHODS:
            return True
        if ctor == "list" and method in _LIST_METHODS:
            return True
        if ctor == "open":
            return True
    return method in _BUILTIN_METHODS


def _receiver_refusal(receiver: ast.expr) -> str | None:
    receiver = _unwrap_expr(receiver)
    if isinstance(receiver, ast.Subscript):
        return _REASON_SUBSCRIPT
    if isinstance(receiver, ast.IfExp):
        return _REASON_CONDITIONAL
    if isinstance(receiver, ast.Call):
        inner = receiver.func
        if isinstance(inner, ast.Attribute):
            return _REASON_CHAINED_RETURN
        if isinstance(inner, ast.Name):
            return _REASON_CHAINED_RETURN
    return None


def _resolve_call_with_ctx(ctx: _ResolverCtx, call: ast.Call) -> CalleeRef | None:
    func = call.func
    expr = _call_expression(func)
    lineno = getattr(call, "lineno", 0)

    if isinstance(func, ast.Name) and func.id == "getattr":
        return _make_callee(
            expression=_expr(call),
            resolved=False,
            resolution_kind="unresolved",
            reason=_REASON_GETATTR,
        )
    if (
        isinstance(func, ast.Call)
        and isinstance(func.func, ast.Name)
        and func.func.id == "getattr"
    ):
        return _make_callee(
            expression=_expr(call),
            resolved=False,
            resolution_kind="unresolved",
            reason=_REASON_GETATTR,
        )

    if isinstance(func, ast.Attribute) and _is_nested_self_dispatch(func):
        return _make_callee(
            expression=expr,
            resolved=False,
            resolution_kind="unresolved",
            reason=_REASON_PROTOCOL,
        )

    if isinstance(func, ast.Name):
        name = func.id
        if _is_ignored_external(name):
            return None
        if ctx.scope != "self":
            local = _local_function(ctx.tree, name)
            if local is not None and _scope_allows_module(
                ctx.unit.module, package=ctx.package, scope=ctx.scope
            ):
                return _make_callee(
                    expression=expr,
                    resolved=True,
                    resolution_kind="free_function",
                    name=local.name,
                    module=ctx.unit.module,
                    file=str(ctx.file_path),
                    lineno=local.lineno,
                )
        if ctx.scope == "self":
            return None
        if name in ctx.bindings:
            imported, _ = ctx.bindings[name]
            top = imported.split(".", 1)[0]
            if _is_ignored_external(top):
                return None
            mod_base = imported if "." not in imported else imported.rsplit(".", 1)[0]
            attr = imported.rsplit(".", 1)[-1] if "." in imported else name
            resolved = _resolve_imported(
                mod_base,
                attr,
                target=ctx.target,
                package=ctx.package,
                scope=ctx.scope,
            )
            if resolved is None:
                return None
            mod, qual, path = resolved
            return _make_callee(
                expression=expr,
                resolved=True,
                resolution_kind="free_function",
                name=qual,
                module=mod,
                file=str(path),
                lineno=0,
            )
        return None

    if not isinstance(func, ast.Attribute):
        return None

    if isinstance(func.value, ast.Name) and _is_ignored_external(func.value.id):
        return None

    method = func.attr
    receiver = _unwrap_expr(func.value)

    if isinstance(receiver, ast.Call):
        inner_func = receiver.func
        class_ref = _class_from_constructor_call(ctx, receiver)
        if class_ref is not None:
            kind: ResolutionKind = "constructor_method"
            if isinstance(inner_func, ast.Attribute) and isinstance(
                inner_func.value, ast.Name
            ):
                kind = "module_constructor"
            return _method_on_class(ctx, class_ref, method, resolution_kind=kind)
        if isinstance(inner_func, ast.Attribute):
            refusal = _REASON_CHAINED_RETURN
        else:
            refusal = _REASON_CHAINED_RETURN
        return _make_callee(
            expression=_expr(call),
            resolved=False,
            resolution_kind="unresolved",
            reason=refusal,
        )

    receiver_refusal = _receiver_refusal(receiver)
    if receiver_refusal is not None:
        return _make_callee(
            expression=_expr(call),
            resolved=False,
            resolution_kind="unresolved",
            reason=receiver_refusal,
        )

    if isinstance(receiver, ast.Name) and receiver.id == "self":
        class_node = _enclosing_class(ctx.tree, getattr(call, "lineno", 0))
        if class_node is None:
            return None
        found = _find_method_in_class(ctx.tree, class_node.name, method)
        if found is None:
            return _make_callee(
                expression=expr,
                resolved=False,
                resolution_kind="unresolved",
                reason=_REASON_INHERITED,
            )
        qual, lineno_m = found
        return _make_callee(
            expression=expr,
            resolved=True,
            resolution_kind="self_method",
            name=qual,
            module=ctx.unit.module,
            file=str(ctx.file_path),
            lineno=lineno_m or lineno,
        )

    if isinstance(receiver, ast.Name):
        var = receiver.id
        if ctx.scope != "self" and var in ctx.bindings:
            imported, _ = ctx.bindings[var]
            top = imported.split(".", 1)[0]
            if not _is_ignored_external(top):
                resolved = _resolve_imported(
                    imported,
                    method,
                    target=ctx.target,
                    package=ctx.package,
                    scope=ctx.scope,
                )
                if resolved is not None:
                    mod, qual, path = resolved
                    return _make_callee(
                        expression=expr,
                        resolved=True,
                        resolution_kind="free_function",
                        name=qual,
                        module=mod,
                        file=str(path),
                        lineno=0,
                    )
        state = ctx.var_states.get(var)
        if state is None:
            local_cls = _local_class(ctx.tree, var)
            if local_cls is not None:
                cref = _ClassRef(ctx.unit.module, var, ctx.file_path)
                return _method_on_class(
                    ctx, cref, method, resolution_kind="free_function"
                )
        if state is None or not state.stable or state.class_ref is None:
            if state is not None and not state.stable:
                return _make_callee(
                    expression=expr,
                    resolved=False,
                    resolution_kind="unresolved",
                    reason=_REASON_REBINDING.format(name=var),
                )
            if var in ctx.unannotated_params:
                return _make_callee(
                    expression=expr,
                    resolved=False,
                    resolution_kind="unresolved",
                    reason=f"parameter '{var}' has no type annotation",
                )
            return _make_callee(
                expression=expr,
                resolved=False,
                resolution_kind="unresolved",
                reason=_REASON_COLLISION,
            )
        kind = state.binding_kind
        if kind == "unresolved":
            kind = "annotated_var"
        return _method_on_class(ctx, state.class_ref, method, resolution_kind=kind)

    if (
        isinstance(receiver, ast.Attribute)
        and isinstance(receiver.value, ast.Name)
        and receiver.value.id in ctx.bindings
    ):
        imported, _ = ctx.bindings[receiver.value.id]
        top = imported.split(".", 1)[0]
        if not _is_ignored_external(top):
            resolved = _resolve_imported(
                imported,
                receiver.attr,
                target=ctx.target,
                package=ctx.package,
                scope=ctx.scope,
            )
            if resolved is not None:
                mod, qual, path = resolved
                return _make_callee(
                    expression=expr,
                    resolved=True,
                    resolution_kind="module_constructor",
                    name=qual,
                    module=mod,
                    file=str(path),
                    lineno=0,
                )

    return _make_callee(
        expression=expr,
        resolved=False,
        resolution_kind="unresolved",
        reason=_REASON_COLLISION,
    )


def _resolve_imported(
    module_path: str,
    attr: str,
    *,
    target: Path,
    package: str,
    scope: CalleeScope,
) -> tuple[str, str, Path] | None:
    obj: object | None = None
    try:
        obj = importlib.import_module(module_path)
    except Exception:
        parts = module_path.split(".")
        if not parts:
            return None
        try:
            obj = importlib.import_module(parts[0])
        except Exception:
            return None
        for part in parts[1:]:
            obj = getattr(obj, part, None)
            if obj is None:
                return None
    for part in attr.split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    path = _source_path_for_object(obj)
    if path is None:
        return None
    resolved_module = getattr(obj, "__module__", module_path) or module_path
    if not _scope_allows_module(resolved_module, package=package, scope=scope):
        return None
    qual = getattr(obj, "__qualname__", attr)
    return resolved_module, qual, path


def _resolve_call_target(
    *,
    call: ast.Call,
    tree: ast.Module,
    file_path: Path,
    file_text: str,
    package: str,
    scope: CalleeScope,
    target: Path,
    unit: CodeUnit,
) -> CalleeRef | None:
    node = _find_node_at_line(tree, lineno=unit.lineno, qualname=unit.qualname)
    if node is None or not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    ctx = _ResolverCtx(
        tree=tree,
        file_path=file_path,
        file_text=file_text,
        package=package,
        scope=scope,
        target=target,
        unit=unit,
        bindings=_import_bindings(tree),
        func=node,
        var_states={},
        unannotated_params=set(),
    )
    _init_var_states(ctx)
    return _resolve_call_with_ctx(ctx, call)


def resolve_callees(
    unit: CodeUnit,
    *,
    scope: CalleeScope,
    package: str,
    target: Path,
) -> list[CalleeRef]:
    """Find callees invoked from a code unit's definition."""
    path = Path(unit.file)
    try:
        file_text, tree = _parse_module(path)
    except SyntaxError:
        return []
    node = _find_node_at_line(tree, lineno=unit.lineno, qualname=unit.qualname)
    if node is None or not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return []

    ctx = _ResolverCtx(
        tree=tree,
        file_path=path,
        file_text=file_text,
        package=package,
        scope=scope,
        target=target,
        unit=unit,
        bindings=_import_bindings(tree),
        func=node,
        var_states={},
        unannotated_params=set(),
    )
    _init_var_states(ctx)

    refs: list[CalleeRef] = []
    for block in node.body:
        for child in ast.walk(block):
            if not isinstance(child, ast.Call):
                continue
            if _should_drop_noise_call(ctx, child):
                continue
            ref = _resolve_call_with_ctx(ctx, child)
            if ref is not None:
                refs.append(ref)
    return refs


def load_code_unit(
    callee: CalleeRef,
    *,
    target: Path,
    depth: Depth,
    hop: int,
) -> CodeUnit | None:
    if not callee.resolved:
        return None
    path = Path(callee.file)
    if not path.is_file():
        return None
    _, tree = _parse_module(path)
    node = _find_node_at_line(tree, lineno=callee.lineno or 0, qualname=callee.name)
    if node is None:
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                n.name == callee.name.split(".")[-1]
            ):
                node = n
                break
    if node is None or isinstance(node, ast.ClassDef):
        return None
    return _build_code_unit(
        path=path,
        module=callee.module,
        qualname=callee.name,
        node=node,
        depth=depth,
        hop=hop,
    )


def collect_context(
    surface: SurfaceRef,
    target: Path,
    *,
    depth: Depth,
    scope: CalleeScope,
    max_hops: int,
    max_callees: int,
    max_code_lines: int,
    package: str,
) -> CodeContext:
    """BFS-collect source units for a surface with caps and cycle-safe visited set."""
    ctx = CodeContext(
        surface=surface,
        depth=depth,
        scope=scope,
        max_hops=max_hops,
        root=None,
    )
    root = resolve_definition(surface, target)
    if root is None:
        ctx.no_definition = True
        return ctx

    if depth == "signature":
        path = Path(root.file)
        file_text, tree = _parse_module(path)
        node = _find_node_at_line(tree, lineno=root.lineno, qualname=root.qualname)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = _signature_source(node, file_text)
            root = CodeUnit(
                key=root.key,
                module=root.module,
                qualname=root.qualname,
                file=root.file,
                lineno=root.lineno,
                source=sig,
                line_count=_line_count(sig),
                hop=0,
            )

    ctx.root = root
    visited: set[str] = set()
    collected: list[CodeUnit] = []
    edges: list[tuple[str, str]] = []
    unresolved: dict[str, CalleeRef] = {}
    total_lines = 0
    truncated = False

    queue: deque[tuple[CodeUnit, int]] = deque([(root, 0)])

    while queue and len(collected) < max_callees and total_lines < max_code_lines:
        unit, hop = queue.popleft()
        if unit.key in visited:
            continue
        visited.add(unit.key)

        unit_lines = unit.line_count
        if total_lines + unit_lines > max_code_lines and collected:
            truncated = True
            break
        if total_lines + unit_lines > max_code_lines:
            remaining = max_code_lines - total_lines
            lines = unit.source.splitlines()
            omitted = max(0, len(lines) - remaining)
            clipped = (
                "\n".join(lines[:remaining])
                + "\n"
                + _TRUNCATION_LINE.format(n=omitted)
            )
            unit = CodeUnit(
                key=unit.key,
                module=unit.module,
                qualname=unit.qualname,
                file=unit.file,
                lineno=unit.lineno,
                source=clipped,
                line_count=remaining + 1,
                hop=unit.hop,
            )
            truncated = True

        collected.append(unit)
        total_lines += unit.line_count

        if truncated:
            break

        if depth != "callgraph" or hop >= max_hops:
            continue

        for callee in resolve_callees(
            unit, scope=scope, package=package, target=target
        ):
            if not callee.resolved:
                unresolved[callee.expression] = callee
                continue
            edges.append((unit.key, callee.key))
            if callee.key in visited:
                continue
            if len(collected) + len(queue) >= max_callees:
                truncated = True
                continue
            loaded = load_code_unit(callee, target=target, depth=depth, hop=hop + 1)
            if loaded is not None:
                queue.append((loaded, hop + 1))

    if queue and not truncated:
        truncated = True

    ctx.units = collected
    ctx.edges = edges
    ctx.unresolved = list(unresolved.values())
    ctx.truncated = truncated
    return ctx


def resolve_cli_surface(
    *,
    package: str,
    command_full_name: str,
    scripts: dict[str, str],
    target: Path,
) -> SurfaceRef | None:
    """Resolve a Click command callback to a file/line surface ref."""
    for script_target in scripts.values():
        module_name, sep, attr = str(script_target).partition(":")
        if not sep:
            continue
        try:
            imported = importlib.import_module(module_name)
            root = getattr(imported, attr)
        except Exception:
            continue
        cmd = _find_click_command(root, command_full_name)
        if cmd is None:
            continue
        callback = cmd.callback
        if callback is None:
            continue
        file_path = inspect.getsourcefile(callback)
        if file_path is None:
            continue
        lines, start = inspect.getsourcelines(callback)
        rel = file_path
        try:
            rel = str(Path(file_path).resolve().relative_to(target.resolve()))
        except ValueError:
            rel = str(file_path)
        callback_module = str(
            getattr(callback, "__module__", module_name) or module_name
        )
        return SurfaceRef(
            surface_id="",
            kind="cli_command",
            package=package,
            name=command_full_name,
            module=callback_module,
            file=rel,
            line=start,
        )
    return None


def _find_click_command(root: click.Command, full_name: str) -> click.Command | None:
    parts = full_name.strip().split()
    cmd: click.Command = root
    for part in parts:
        if not isinstance(cmd, click.Group):
            return None
        nxt = cmd.commands.get(part)
        if nxt is None:
            return None
        cmd = nxt
    return cmd


def iter_surfaces_from_inventory(
    data: dict[str, object],
    target: Path,
) -> Iterator[SurfaceRef]:
    """Yield surfaces that may have code definitions."""
    from pickled_core.mine.stories_stage import (
        _is_significant_cli,
        _surface_id_cli,
        _surface_id_gate,
        _surface_id_mcp,
    )

    packages = data.get("packages", {})
    if not isinstance(packages, dict):
        return

    for pkg_name, pkg in packages.items():
        if not isinstance(pkg, dict):
            continue
        scripts = pkg.get("scripts", {})
        if not isinstance(scripts, dict):
            scripts = {}

        for tool in pkg.get("mcp_tools", []):
            if not isinstance(tool, dict):
                continue
            name = str(tool.get("name", ""))
            if not name:
                continue
            yield SurfaceRef(
                surface_id=_surface_id_mcp(name),
                kind="mcp_tool",
                package=str(pkg_name),
                name=name,
            )

        for cmd in pkg.get("cli_commands", []):
            if not isinstance(cmd, dict) or not _is_significant_cli(cmd):
                continue
            full = str(cmd.get("full_name", ""))
            ref = resolve_cli_surface(
                package=str(pkg_name),
                command_full_name=full,
                scripts={str(k): str(v) for k, v in scripts.items()},
                target=target,
            )
            if ref is None:
                yield SurfaceRef(
                    surface_id=_surface_id_cli(str(pkg_name), full),
                    kind="cli_command",
                    package=str(pkg_name),
                    name=full,
                )
            else:
                yield SurfaceRef(
                    surface_id=_surface_id_cli(str(pkg_name), full),
                    kind=ref.kind,
                    package=ref.package,
                    name=ref.name,
                    module=ref.module,
                    file=ref.file,
                    line=ref.line,
                )

        for gate in pkg.get("gates", []):
            if not isinstance(gate, dict):
                continue
            gate_name = str(gate.get("name", gate.get("class_name", "")))
            if not gate_name:
                continue
            yield SurfaceRef(
                surface_id=_surface_id_gate(str(pkg_name), gate_name),
                kind="gate",
                package=str(pkg_name),
                name=gate_name,
                module=str(gate.get("module", "")),
                file=str(gate.get("file", "")),
                line=int(gate.get("line", 0) or 0),
            )


__all__ = [
    "CalleeRef",
    "CalleeScope",
    "CodeContext",
    "CodeUnit",
    "CycleReport",
    "Depth",
    "SurfaceRef",
    "collect_context",
    "find_cycles",
    "iter_surfaces_from_inventory",
    "load_code_unit",
    "resolve_callees",
    "resolve_cli_surface",
    "resolve_definition",
    "SourceFileNotFoundError",
    "unit_key",
]
