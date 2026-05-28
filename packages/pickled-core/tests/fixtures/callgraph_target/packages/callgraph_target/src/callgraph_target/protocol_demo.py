"""Protocol-style dispatch (unresolved)."""


class StubLLM:
    def complete(self) -> str:
        return "ok"


class User:
    def __init__(self) -> None:
        self._llm = StubLLM()

    def go(self) -> str:
        return self._llm.complete()
