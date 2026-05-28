"""Factory return type unknown."""


class Worker:
    def process(self) -> str:
        return "p"


def get_worker() -> Worker:
    return Worker()


def entry() -> str:
    return get_worker().process()
