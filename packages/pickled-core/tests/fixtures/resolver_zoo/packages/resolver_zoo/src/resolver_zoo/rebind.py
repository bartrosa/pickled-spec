"""Rebound variable must refuse."""


class Worker:
    def process(self) -> str:
        return "w"


class Other:
    def process(self) -> str:
        return "o"


def entry() -> str:
    x = Worker()
    x = Other()
    return x.process()
