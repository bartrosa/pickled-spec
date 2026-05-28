"""Module-qualified constructor."""

from resolver_zoo import ctor_method as mod


def entry(cfg: str) -> str:
    return mod.Worker(cfg).process()
