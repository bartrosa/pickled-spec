"""Ambiguous receiver type."""


class Alpha:
    def run(self) -> str:
        return "a"


class Beta:
    def run(self) -> str:
        return "b"


def entry() -> str:
    return mystery.run()
