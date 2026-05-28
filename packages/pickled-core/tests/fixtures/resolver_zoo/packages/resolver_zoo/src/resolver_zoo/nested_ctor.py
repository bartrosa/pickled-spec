"""Constructor nested in constructor argument."""


class Builder:
    def build(self) -> str:
        return "built"


class Worker:
    def process(self, payload: str) -> str:
        return payload


def entry(x: str) -> str:
    return Worker(Builder(x).build()).process()
