"""Inherited method not resolved in v1."""


class Base:
    def run(self) -> str:
        return "base"


class Child(Base):
    pass


def entry() -> str:
    return Child().run()
