"""Constructor cycle A -> B -> A."""


class A:
    def foo(self) -> None:
        B().bar()


class B:
    def bar(self) -> None:
        A().foo()


def entry() -> None:
    A().foo()
