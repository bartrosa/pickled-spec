"""Calls that must stay unresolved."""


class StubLLM:
    def complete(self) -> str:
        return "ok"


class User:
    def __init__(self) -> None:
        self._llm = StubLLM()

    def protocol_call(self) -> str:
        return self._llm.complete()


def unannotated_param(w) -> str:
    return w.process()


class Worker:
    def process(self) -> str:
        return "p"


def subscript_receiver(items: list[Worker]) -> str:
    return items[0].process()


def ternary_receiver(flag: bool, a: Worker, b: Worker) -> str:
    return (a if flag else b).process()


def chained_unknown() -> str:
    return factory().build().run()


def factory():
    return Worker()


def getattr_dynamic(obj: object) -> str:
    fn = getattr(obj, "process")
    return fn()
