"""ContextVar binding :class:`BudgetGuard` to the active execution scope."""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pickled_core.llm.budget import BudgetGuard

_current_guard: ContextVar[BudgetGuard | None] = ContextVar(
    "pickled_budget_guard",
    default=None,
)


def active_budget_guard() -> BudgetGuard | None:
    return _current_guard.get()


def set_budget_guard(guard: BudgetGuard | None) -> None:
    _current_guard.set(guard)


__all__ = ["active_budget_guard", "set_budget_guard"]
