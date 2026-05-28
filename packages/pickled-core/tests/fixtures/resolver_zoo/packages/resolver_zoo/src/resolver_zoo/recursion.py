"""Recursion within one class."""


class A:
    def foo(self) -> None:
        self.foo()

    def bar(self) -> None:
        self.baz()

    def baz(self) -> None:
        self.foo()


def entry() -> None:
    A().foo()
