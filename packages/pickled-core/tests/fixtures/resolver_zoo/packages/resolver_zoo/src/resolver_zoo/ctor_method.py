"""Constructor-then-method resolution."""


class Worker:
    def process(self) -> str:
        return "processed"


def entry(cfg: str) -> str:
    return Worker(cfg).process()


def entry_paren(cfg: str) -> str:
    return (Worker(cfg)).process()
