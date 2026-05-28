"""Type-annotation based resolution."""


class Worker:
    def process(self) -> str:
        return "p"


def via_param(w: Worker) -> str:
    return w.process()


def via_var() -> str:
    x: Worker = Worker()
    return x.process()


def via_assign() -> str:
    x = Worker()
    return x.process()
