"""Method chain: first hop resolves, rest refuses."""


class Worker:
    def process(self) -> str:
        return "p"

    def finalize(self) -> str:
        return "f"


def entry(cfg: str) -> str:
    return Worker(cfg).process().finalize()
